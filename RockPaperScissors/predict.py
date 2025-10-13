import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import logging
import joblib

# Load trained model
clf = joblib.load("emg_rps_model.pkl")
scaler = joblib.load("emg_scaler.pkl")

def predict_state(emg_sample):
    # emg_sample = [ch1, ch2, ch3, ch4]
    X = np.array(emg_sample).reshape(1, -1)
    X_scaled = scaler.transform(X)
    pred = clf.predict(X_scaled)[0]
    states = ["Rest", "Rock", "Paper", "Scissors"]
    return states[pred]

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

    while True:
        data = board.get_current_board_data(1)
        print(predict_state(emg_sample))





if __name__ == "__main__":
    main()