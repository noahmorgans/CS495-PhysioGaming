import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import numpy as np
import time
import pandas as pd

# How long to record per gesture (in seconds)
RECORD_DURATION = 5  
SAVE_FILE = "emg_signals.csv"

# Gestures and their numeric labels
GESTURES = {
    "rest": 0,
    "rock": 1,
    "paper": 2,
    "scissors": 3
}

def collect_data_for_gesture(board, gesture_name, duration=5):
    """
    Record EMG data for one gesture for the given duration.
    Returns a numpy array of shape (samples, channels + 1[label]).
    """
    print(f"\nGet ready for: {gesture_name.upper()} — starting in 3 seconds...")
    time.sleep(3)
    print(f"Recording {gesture_name} for {duration} seconds...")
    
    board.start_stream()
    time.sleep(duration)
    board.stop_stream()
    
    data = board.get_board_data()
    emg_channels = BoardShim.get_emg_channels(board.get_board_id())
    emg_data = data[emg_channels]
    
    # Transpose to (samples, channels)
    emg_data = emg_data.T
    labels = np.full((emg_data.shape[0], 1), GESTURES[gesture_name])
    labeled_data = np.hstack((emg_data, labels))
    
    print(f"Recorded {emg_data.shape[0]} samples for {gesture_name}.")
    return labeled_data

def main():
    # configure board
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    params = BrainFlowInputParams()
    params.serial_port = "COM4"
    params.timeout = 15
    params.master_board = BoardIds.GANGLION_NATIVE_BOARD
        
    board = BoardShim(params.master_board, params)

    board.prepare_session()

    all_data = []

    # Loop through all gestures
    for gesture in GESTURES.keys():
        samples = collect_data_for_gesture(board, gesture, RECORD_DURATION)
        all_data.append(samples)

    board.release_session()

    # === Combine and save all data ===
    dataset = np.vstack(all_data)
    columns = [f"ch{i+1}" for i in range(dataset.shape[1] - 1)] + ["label"]
    df = pd.DataFrame(dataset, columns=columns)
    df.to_csv(SAVE_FILE, index=False)

    print(f"\n✅ Data collection complete! Saved to {SAVE_FILE}")

if __name__ == "__main__":
    main()

