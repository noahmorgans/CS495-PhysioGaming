# The goal of this file is to obtain the rolling average of the EMG signal
# over a specified time window. This average will be used to determine whether
# the fist is clenched or relaxed. A method will return '1' if flexed and '0' if relaxed.
# This data will be passed to the Unity test environment to help us map
# a fist clench to jetpack activation.

from brainflow.board_shim import BoardShim, BrainFlowInputParams
import numpy as np
import time

N = 100 # number of samples to consider for rolling average
THRESHOLD = 200  # threshold for determining clenched vs relaxed

# configure board
BoardShim.enable_dev_board_logger()
logging.basicConfig(level=logging.DEBUG)

params = BrainFlowInputParams()
params.serial_port = "COM4"
params.timeout = 15
params.master_board = BoardIds.GANGLION_NATIVE_BOARD
    
board_shim = BoardShim(params.master_board, params)

board.prepare_session()
board.start_stream()

# get EEG channels (or whichever channels you need)
emg_channels = BoardShim.get_emg_channels(board_id)

while True:
    # fetch up to the last N data points (for each channel)
    data = board.get_current_board_data(N)  

    for ch in emg_channels:
        channel_data = data[ch]  # most recent <=N samples
        if len(channel_data) > 0:
            rolling_avg = np.mean(channel_data)
            print(f"Channel {ch}: Rolling Avg = {rolling_avg:.3f}")
            if rolling_avg > THRESHOLD:
                print("\t\tClenched")
            else:
                print("\t\tRelaxed")

    time.sleep(0.1)  # poll every 100 ms
