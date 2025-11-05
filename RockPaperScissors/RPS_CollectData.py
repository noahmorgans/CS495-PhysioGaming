import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes
import numpy as np
import time
import pandas as pd
from scipy.signal import iirnotch, filtfilt, butter
import os

# Define directory structure
BASE_DIR = "EMG Files"
SIGNAL_DIR = os.path.join(BASE_DIR, "Signal Files")
# Create directories if they don't exist
os.makedirs(SIGNAL_DIR, exist_ok=True)
# Update save path
SAVE_FILE = os.path.join(SIGNAL_DIR, "emg_signals_6(200_window).csv")


# How long to record per gesture (in seconds)
RECORD_DURATION = 5
NUM_TRIALS = 10  # Number of trials per gesture
ACTIVE_CHANNELS = [0]  # EMG channels to record

# Gestures and their numeric labels
GESTURES = {
    "rock": 0,
    "paper": 1,
    "scissors": 2
}

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
    b, a = iirnotch(notch_freq, quality_factor, fs)
    return filtfilt(b, a, data)

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

def collect_data_for_gesture(board, gesture_name, trial_num, duration=5):
    """
    Record EMG data for one gesture for the given duration.
    Applies bandpass and notch filters to remove noise.
    Returns a pandas DataFrame with columns: [ch1, ch2, ..., label, trial, timestamp]
    """
    print(f"\nGet ready for: {gesture_name.upper()} (Trial {trial_num}) — starting in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print(f"🔴 Recording {gesture_name} for {duration} seconds...")
    
    board.start_stream()
    time.sleep(duration)
    board.stop_stream()
    
    data = board.get_board_data()
    # Extract only active EMG channels
    emg_channels = BoardShim.get_emg_channels(board.get_board_id())
    active_channel_indices = [emg_channels[i] for i in ACTIVE_CHANNELS]
    
    print(f"  Using channels: {ACTIVE_CHANNELS} (indices: {active_channel_indices})")
    
    # Apply filters only to active channels
    for ch in active_channel_indices:
        try:
            data[ch] = apply_bandpass_filter(data[ch], sampling_rate, lowcut=20.0)
            data[ch] = apply_notch_filter(data[ch], sampling_rate)
        except Exception as e:
            print(f"  Warning: Filter failed for channel {ch}: {e}")
    
    # Extract only active channels
    emg_data = data[active_channel_indices].T  # Transpose to (samples, channels)
    
    # Create DataFrame with only active channels
    n_channels = len(ACTIVE_CHANNELS)
    columns = [f"ch{i+1}" for i in ACTIVE_CHANNELS]
    df = pd.DataFrame(emg_data, columns=columns)
    df['label'] = GESTURES[gesture_name]
    df['trial'] = trial_num
    df['timestamp'] = time.time()
    
    print(f"  ✓ Recorded {len(df)} samples for {gesture_name}")
    return df

def main():
    # Configure board
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.INFO)

    params = BrainFlowInputParams()
    params.serial_port = "COM4"
    params.timeout = 15
    params.master_board = BoardIds.GANGLION_NATIVE_BOARD
        
    board = BoardShim(params.master_board, params)
    
    print("Preparing session...")
    board.prepare_session()
    
    emg_channels = BoardShim.get_emg_channels(board.get_board_id())
    sampling_rate = board.get_sampling_rate(board.get_board_id())
    print(f"Board ready! EMG channels: {emg_channels}, Sampling rate: {sampling_rate} Hz")
    print(f"\nWill collect {NUM_TRIALS} trials of {RECORD_DURATION} seconds for each gesture.")
    print("Gestures:", list(GESTURES.keys()))
    
    input("\nPress Enter to start data collection...")

    all_dataframes = []
    trial_counter = 0

    # Loop through all gestures and collect multiple trials
    for gesture in GESTURES.keys():
        print(f"\n{'='*60}")
        print(f"Gesture: {gesture.upper()}")
        print(f"{'='*60}")
        
        for trial in range(NUM_TRIALS):
            df = collect_data_for_gesture(board, gesture, trial_counter, RECORD_DURATION)
            all_dataframes.append(df)
            trial_counter += 1
            
            # Rest between trials
            if trial < NUM_TRIALS - 1:
                print(f"  Rest for 3 seconds before next trial...")
                time.sleep(3)
        
        # Longer rest between gestures
        if gesture != list(GESTURES.keys())[-1]:
            print(f"\n  ⏸️  Rest for 5 seconds before next gesture...")
            time.sleep(5)

    board.release_session()

    # Combine and save all data
    print(f"\n{'='*60}")
    print("Combining and saving data...")
    dataset = pd.concat(all_dataframes, ignore_index=True)
    
    # Verify data
    print(f"Total samples: {len(dataset)}")
    print(f"Samples per label:\n{dataset['label'].value_counts().sort_index()}")
    print(f"Trials: {dataset['trial'].nunique()}")
    
    dataset.to_csv(SAVE_FILE, index=False)
    print(f"\n✅ Data collection complete! Saved to {SAVE_FILE}")
    print(f"Dataset shape: {dataset.shape}")

if __name__ == "__main__":
    main()