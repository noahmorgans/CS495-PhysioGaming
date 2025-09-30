import socket
import logging
import time
import numpy as np

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets

###### VARS
#TCP Socket
HOST = ''
PORT = 50007

isRunning = True

num_points = 0
sampleRate = 0

#Data
avg = 0
threshold = 1000
stateChange = True
state = 0
lastState = 0
sep = ''

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

    ##### TRANSMIT AND RECEIVE LOOP
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
            #Determine avg
            data = board.get_board_data()
            channel_data = data[1]

            if len(channel_data) > 0:
                avg = abs(np.mean(channel_data))
                print(f"Rolling Avg = {avg:.3f}")

            #Determine State
            if(avg > threshold):
                lastState = state
                state = 1
            else:
                lastState = state
                state = 0

            if(lastState != state):
                stateChange = 1

            txBytes = (str(state) + sep).encode('utf-8')
            print(txBytes)
            #txBytes = input().encode()
            conn.send(txBytes)

        except:
            a = 1
        time.sleep(0.1)  # poll every 100 ms
        #End of Loop


