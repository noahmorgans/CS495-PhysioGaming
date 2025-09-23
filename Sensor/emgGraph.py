import logging

import pyqtgraph as pg
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from pyqtgraph.Qt import QtWidgets, QtCore

# This Program Graphs EMG Signal Data from the OpenBCI Ganglion Board.
# In order to connect to the board you will need to open the Serial Port "COM 4" via your device manager (for MS windows)
# The connection process is simple. First turn the board on and wait for a blue flashing light. Next run the program.
# Once the connection is established the light should turn solid blue.
# The output data of the board is in micro volts.

class Graph:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.emg_channels = BoardShim.get_emg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 5
        self.num_points = self.window_size * self.sampling_rate

        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget(title='BrainFlow Plot', size=(800, 600), show=True)

        self._init_timeseries()

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.update_speed_ms)
        QtWidgets.QApplication.instance().exec()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        p = self.win.addPlot(row=0, col=0)
        p.showAxis('left', True)
        p.setMenuEnabled('left', False)
        p.showAxis('bottom', True)
        p.setMenuEnabled('bottom', False)
        p.setYRange(-1000, 1000)
        p.setTitle('TimeSeries Plot')
        self.plots.append(p)
        curve = p.plot()
        self.curves.append(curve)


    def update(self):
        data = self.board_shim.get_current_board_data(self.num_points)[1] #get channel 1
         # plot timeseries
        DataFilter.detrend(data, DetrendOperations.CONSTANT.value)
        DataFilter.perform_bandpass(data, self.sampling_rate, 3.0, 45.0, 4, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0) #allow 3hz to 45hz
        DataFilter.perform_bandstop(data, self.sampling_rate, 58.0, 62.0, 4, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0) #block 58hz to 62hz (mains freq i think)
        self.curves[0].setData(data.tolist())
        self.app.processEvents()


def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    params = BrainFlowInputParams()
    params.serial_port = "COM4"
    params.timeout = 15
    params.master_board = BoardIds.GANGLION_NATIVE_BOARD
    
    board_shim = BoardShim(params.master_board, params)
    try:
        board_shim.prepare_session()
        board_shim.start_stream(450000)
        Graph(board_shim)
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()


if __name__ == '__main__':
    main()