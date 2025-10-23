import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes
from scipy.signal import iirnotch, filtfilt, butter, lfilter
import logging
import joblib
import time
from collections import deque
import tensorflow as tf

# Load trained model and preprocessing parameters
model = tf.keras.models.load_model("emg_cnn_model.keras")
label_encoder = joblib.load("emg_label_encoder.pkl")
norm_params = joblib.load("emg_normalization.pkl")

X_mean = norm_params['mean'].squeeze()  # Remove extra dimensions
X_std = norm_params['std'].squeeze()  # Remove extra dimensions
window_size = norm_params['window_size']

# Map numeric predictions to gesture names
GESTURE_NAMES = {0: "Rock", 1: "Paper", 2: "Scissors"}

def apply_notch_filter(data, fs, notch_freq=60.0, quality_factor=30.0):
    """
    Apply a notch filter to remove powerline noise (e.g., 60 Hz).
    Args:
        data: 1D array of signal data
        fs: Sampling frequency (Hz)
        notch_freq: Frequency to remove (Hz)
        quality_factor: Quality factor for the notch filter
    Returns:
        Filtered signal
    """
    x = np.asarray(data, dtype=float).ravel()
    b, a = iirnotch(notch_freq, quality_factor, fs)
    padlen_needed = 3 * (max(len(a), len(b)) - 1)
    if x.size <= padlen_needed:
        return lfilter(b, a, x)
    return filtfilt(b, a, x)

def apply_bandpass_filter(data, fs, lowcut=20.0, highcut=99.0, order=4):
    """
    Apply a bandpass filter to EMG data.
    Args:
        data: 1D array of signal data
        fs: Sampling frequency (Hz)
        lowcut: Low cutoff frequency (Hz)
        highcut: High cutoff frequency (Hz)
        order: Filter order
    Returns:
        Filtered signal
    """
    x = np.asarray(data, dtype=float).ravel()
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    padlen_needed = 3 * (max(len(a), len(b)) - 1)
    if x.size <= padlen_needed:
        return lfilter(b, a, x)
    return filtfilt(b, a, x)

def predict_gesture(window):
    """
    Predict gesture from a window of EMG data.
    Args:
        window: numpy array of shape (window_size, n_channels)
    Returns:
        Predicted gesture name and confidence
    """
    # Ensure window is the right shape
    window = np.array(window)
    if window.ndim != 2:
        raise ValueError(f"Window must be 2D, got shape {window.shape}")
    
    # Normalize using training statistics
    window_normalized = (window - X_mean) / (X_std + 1e-8)
    
    # Add batch dimension: (window_size, n_channels) -> (1, window_size, n_channels)
    window_batch = window_normalized.reshape(1, window_size, -1)
    
    # Predict
    predictions = model.predict(window_batch, verbose=0)[0]
    predicted_class = np.argmax(predictions)
    confidence = predictions[predicted_class]
    
    # Get gesture name
    gesture_label = label_encoder.inverse_transform([predicted_class])[0]
    gesture_name = GESTURE_NAMES.get(int(gesture_label), f"Unknown ({gesture_label})")
    
    return gesture_name, confidence, predictions

def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.INFO)

    params = BrainFlowInputParams()
    params.serial_port = "COM4"
    params.timeout = 15
    params.master_board = BoardIds.GANGLION_NATIVE_BOARD
        
    board = BoardShim(params.master_board, params)
    board.prepare_session()
    board.start_stream()

    emg_channels = BoardShim.get_emg_channels(board.get_board_id())
    sampling_rate = board.get_sampling_rate(board.get_board_id())
    n_channels = len(emg_channels)
    
    print(f"EMG channels: {emg_channels}")
    print(f"Sampling rate: {sampling_rate} Hz")
    print(f"Window size: {window_size} samples")
    print("\nStarting real-time prediction...")
    print("Press Ctrl+C to stop.\n")


    BUFFER_SECONDS = 0.4
    # Buffer to store incoming data
    data_buffer = deque(maxlen=int(BUFFER_SECONDS * sampling_rate))
    filtered_buffer = deque(maxlen=int(BUFFER_SECONDS * sampling_rate))
    
    try:
        while True:
            # Get recent data
            data = board.get_current_board_data(80)
            
            if data.shape[1] > 0:
                # Extract and filter EMG data
                for i in range(data.shape[1]):
                    sample = data[emg_channels, i]
                    data_buffer.append(sample)
                
                # Once we have enough data, make prediction
                if len(data_buffer) == window_size:

                    for i in range(data.shape[1]):
                        sample = apply_bandpass_filter(sample, sampling_rate)
                        sample = apply_notch_filter(sample, sampling_rate)
                        filtered_buffer.append(sample)

                    window = np.array(filtered_buffer)  # Shape: (window_size, n_channels)
                    
                    gesture_name, confidence, all_probs = predict_gesture(window)
                    
                    # Display prediction with better formatting
                    print(f"\rPredicted: {gesture_name:10s} | Confidence: {confidence:.2%} | " + 
                          f"[Rock: {all_probs[0]:.2f}, Paper: {all_probs[1]:.2f}, " +
                          f"Scissors: {all_probs[2]:.2f}]", 
                          end='', flush=True)
            
            # Control loop speed
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\nStopping stream...")

    finally:
        board.stop_stream()
        board.release_session()
        print("✅ Stream stopped and session released.")

if __name__ == "__main__":
    main()