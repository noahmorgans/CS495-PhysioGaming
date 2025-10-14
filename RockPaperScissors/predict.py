import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import logging
import joblib
import time

# Load trained model
clf = joblib.load("emg_rps_model.pkl")
scaler = joblib.load("emg_scaler.pkl")

def predict_state(emg_sample):
    # emg_sample = [ch1, ch2, ch3, ch4]
    X = np.array(emg_sample).reshape(1, -1)
    X_scaled = scaler.transform(X)
    pred = clf.predict(X_scaled)[0]
    states = ["Rest", "Rock", "Paper", "Scissors"]
    return states[int(pred)]

def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    params = BrainFlowInputParams()
    params.serial_port = "COM4"
    params.timeout = 15
    params.master_board = BoardIds.GANGLION_NATIVE_BOARD
        
    board = BoardShim(params.master_board, params)

    board.prepare_session()
    board.start_stream()

    emg_channels = BoardShim.get_emg_channels(board.get_board_id())

    try:
        while True:
            # Get the most recent sample (1 data point per channel)
            data = board.get_current_board_data(1)
            emg_data = data[emg_channels, :].flatten()

            if emg_data.size > 0:
                state = predict_state(emg_data)
                print(f"Predicted: {state}")

            # Control loop speed (adjust as needed)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping stream...")

    finally:
        board.stop_stream()
        board.release_session()
        print("✅ Stream stopped and session released.")

if __name__ == "__main__":
    main()