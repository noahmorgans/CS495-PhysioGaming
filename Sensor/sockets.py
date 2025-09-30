import socket
import logging

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets

###### VARS
HOST = ''
PORT = 50007

isRunning = True

num_points = 0
sampleRate = 0


##### INIT BOARD
BoardShim.enable_dev_board_logger()
logging.basicConfig(level=logging.DEBUG)
params = BrainFlowInputParams()
params.serial_port = "COM4"
params.timeout = 15
params.master_board = BoardIds.GANGLION_NATIVE_BOARD

board = BoardShim(params.master_board, params)
    
sampleRate = board.get_sampling_rate(params.master_board, 0)
num_points = sampleRate * 4


try:
    board.prepare_session()
    board.start_stream(450000)
except BaseException:
    logging.warning('Exception', exc_info=True)


##### INIT CONNECTION
sckt_base = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sckt_base.bind((HOST,PORT))

sckt_base.listen(1)

conn, addr = sckt_base.accept()
with conn:
    conn.setblocking(False)
    print('Connected by', addr)

    ##### TRANSMIT AND RECEIVE
    while isRunning:
        #RX
        
        try:
            rxBytes = conn.recv(1024)
            if(rxBytes.decode() == 'end'):
                isRunning = False
                break
        except:
            a = 1
        
        

        #TX
        try:
            txBytes = str(board.get_current_board_data(num_points)).encode()
            #txBytes = input().encode()
            conn.sendall(txBytes)
        except:
            a = 1



