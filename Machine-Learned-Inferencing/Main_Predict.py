import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes
from scipy.signal import iirnotch, filtfilt, butter, lfilter, welch
import logging
import joblib
import time
from collections import deque
import tensorflow as tf
import os

# Define directory structure (same as above)
BASE_DIR = "EMG Files"
MODEL_DIR = os.path.join(BASE_DIR, "Model Files")
ENCODER_DIR = os.path.join(BASE_DIR, "Encoder Files")
NORM_DIR = os.path.join(BASE_DIR, "Normalization Files")

# Load files from appropriate directories
model = tf.keras.models.load_model(os.path.join(MODEL_DIR, "emg_cnn_model_2(200_window).keras"))
label_encoder = joblib.load(os.path.join(ENCODER_DIR, "emg_label_encoder_2(200_window).pkl"))
norm_params = joblib.load(os.path.join(NORM_DIR, "emg_normalization_2(200_window).pkl"))

ACTIVE_CHANNELS = [0]  # EMG channels to use

X_mean = norm_params['mean'].squeeze()  # Remove extra dimensions
X_std = norm_params['std'].squeeze()  # Remove extra dimensions
window_size = norm_params['window_size']

# Map numeric predictions to gesture names
GESTURE_NAMES = {0: "Propulsion", 1: "Rest"}

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

def apply_highpass_filter(data, fs, cutoff=20.0, order=4):
    """
    Apply a highpass filter to remove low-frequency noise and motion artifacts.
    This is more appropriate for low sampling rates.
    """
    x = np.asarray(data, dtype=float).ravel()
    nyq = 0.5 * fs
    high = cutoff / nyq
    b, a = butter(order, high, btype='high')
    padlen_needed = 3 * (max(len(a), len(b)) - 1)
    if x.size <= padlen_needed:
        return lfilter(b, a, x)
    return filtfilt(b, a, x)

def analyze_signal_frequency(signal, fs):
    """
    Analyze the frequency content of a signal using Welch's method.
    Returns dominant frequency and power spectrum info.
    """
    # Use Welch's method to estimate power spectral density
    freqs, psd = welch(signal, fs=fs, nperseg=min(256, len(signal)))
    
    # Find dominant frequency (excluding DC component)
    dominant_idx = np.argmax(psd[1:]) + 1  # Skip DC (0 Hz)
    dominant_freq = freqs[dominant_idx]
    
    # Calculate power in different frequency bands
    def band_power(freqs, psd, fmin, fmax):
        idx = np.logical_and(freqs >= fmin, freqs <= fmax)
        return np.trapezoid(psd[idx], freqs[idx])
    
    total_power = np.trapezoid(psd, freqs)
    low_freq_power = band_power(freqs, psd, 0, 20)  # 0-20 Hz (motion artifacts)
    emg_power = band_power(freqs, psd, 20, 90)  # 20-90 Hz (useful EMG)
    high_freq_power = band_power(freqs, psd, 90, fs/2)  # Above 90 Hz
    
    return {
        'dominant_freq': dominant_freq,
        'total_power': total_power,
        'low_freq_power': low_freq_power,
        'emg_power': emg_power,
        'high_freq_power': high_freq_power,
        'low_freq_percent': (low_freq_power / total_power) * 100,
        'emg_percent': (emg_power / total_power) * 100,
        'high_freq_percent': (high_freq_power / total_power) * 100
    }

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
    active_channel_indices = [emg_channels[i] for i in ACTIVE_CHANNELS]
    sampling_rate = board.get_sampling_rate(board.get_board_id())
    n_channels = len(ACTIVE_CHANNELS)
    
    print(f"EMG channels: {emg_channels}")
    print(f"Sampling rate: {sampling_rate} Hz")
    print(f"Nyquist frequency (max detectable): {sampling_rate/2} Hz")
    print(f"Window size: {window_size} samples")
    print("\nStarting real-time prediction with signal analysis...")
    print("Press Ctrl+C to stop.\n")

    BUFFER_SECONDS = 1
    # Buffer to store incoming data
    data_buffer = deque(maxlen=int(BUFFER_SECONDS * sampling_rate))
    
    # Counter for periodic detailed analysis
    analysis_counter = 0
    ANALYSIS_INTERVAL = 20  # Print detailed analysis every N predictions
    
    try:
        while True:
            # Get recent data
            data = board.get_current_board_data(200)
            
            if data.shape[1] > 0:
                # Extract EMG data and add to buffer
                for i in range(data.shape[1]):
                    sample = data[active_channel_indices, i]
                    data_buffer.append(sample)
                
                # Once we have enough data, make prediction
                if len(data_buffer) >= window_size:
                    # Convert buffer to array
                    window = np.array(list(data_buffer)[-window_size:])  # Shape: (window_size, n_channels)
                    
                    # Raw signal statistics
                    raw_min = np.min(window)
                    raw_max = np.max(window)
                    raw_mean = np.mean(window)
                    raw_std = np.std(window)
                    
                    # Apply filters to each channel
                    filtered_window = np.zeros_like(window)
                    for ch_idx in range(window.shape[1]):
                        filtered_window[:, ch_idx] = apply_highpass_filter(
                            window[:, ch_idx], sampling_rate
                        )
                        filtered_window[:, ch_idx] = apply_notch_filter(
                            filtered_window[:, ch_idx], sampling_rate
                        )
                    
                    gesture_name, confidence, all_probs = predict_gesture(filtered_window)
                    
                    # Periodic detailed frequency analysis
                    analysis_counter += 1
                    if analysis_counter % ANALYSIS_INTERVAL == 0:
                        print("\n" + "="*80)
                        print("DETAILED SIGNAL ANALYSIS")
                        print("="*80)
                        
                        # Analyze each channel
                        for ch_idx in range(window.shape[1]):
                            print(f"\nChannel {ch_idx + 1}:")
                            print(f"  Raw Signal:")
                            print(f"    Range: [{np.min(window[:, ch_idx]):.2f}, {np.max(window[:, ch_idx]):.2f}]")
                            print(f"    Mean: {np.mean(window[:, ch_idx]):.2f}, Std: {np.std(window[:, ch_idx]):.2f}")
                            
                            # Frequency analysis on raw signal
                            freq_info = analyze_signal_frequency(window[:, ch_idx], sampling_rate)
                            print(f"  Frequency Content (Raw):")
                            print(f"    Dominant frequency: {freq_info['dominant_freq']:.1f} Hz")
                            print(f"    Power distribution:")
                            print(f"      0-20 Hz (artifacts): {freq_info['low_freq_percent']:.1f}%")
                            print(f"      20-90 Hz (EMG):      {freq_info['emg_percent']:.1f}%")
                            print(f"      90-100 Hz (high):    {freq_info['high_freq_percent']:.1f}%")
                            
                            # Frequency analysis on filtered signal
                            freq_info_filt = analyze_signal_frequency(filtered_window[:, ch_idx], sampling_rate)
                            print(f"  Frequency Content (Filtered):")
                            print(f"    Dominant frequency: {freq_info_filt['dominant_freq']:.1f} Hz")
                            print(f"    EMG band power: {freq_info_filt['emg_percent']:.1f}%")
                        
                        print("="*80 + "\n")
                    
                    # Display prediction with signal stats
                    print(f"\rPredicted: {gesture_name:10s} | Conf: {confidence:.2%} | "
                          f"Raw: [{raw_min:6.1f}, {raw_max:6.1f}] μ={raw_mean:6.1f} σ={raw_std:5.1f} | "
                          f"[P:{all_probs[0]:.2f} R:{all_probs[1]:.2f}]", 
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