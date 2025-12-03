using brainflow;
using brainflow.math;
using System;
using System.Collections;
using System.Threading;
using UnityEngine;

public class SensorInput : MonoBehaviour
{
    //################ VARS
    private BoardShim board_shim = null;
    private int sampling_rate = 0;
    int[] emg_channels;
    bool isBoardConnected = false;

    //################ START
    void Start()
    {
        //Try to connect to ganglion native board
        try
        {
            BoardShim.set_log_file("brainflow_log.txt");
            BoardShim.enable_dev_board_logger();

            BrainFlowInputParams input_params = new BrainFlowInputParams();

            input_params.serial_port = "COM4";
            input_params.timeout = 15;
            input_params.master_board = (int)BoardIds.GANGLION_NATIVE_BOARD;

            int board_id = (int)BoardIds.GANGLION_NATIVE_BOARD;
            board_shim = new BoardShim(board_id, input_params);
            board_shim.prepare_session();
            board_shim.start_stream(450000);
            sampling_rate = BoardShim.get_sampling_rate(board_id);

            emg_channels = BoardShim.get_emg_channels(board_id);

            Debug.Log("Brainflow streaming was started");
            isBoardConnected = true;
        }
        catch (BrainFlowError e)
        {
            Debug.Log(e);
        }
    }

    //################ UPDATE
    void Update()
    {
        //Read board data if connected
        if (isBoardConnected && board_shim != null)
        {
            int number_of_data_points = sampling_rate * 4;
            double[,] data_raw = board_shim.get_current_board_data(number_of_data_points);



            //Temporary avg for debug

            double avg = 0;
            int count = 0;

            foreach (var index in emg_channels)
            {
                double[] row = data_raw.GetRow(index);

                foreach (var value in row)
                {
                    avg += value;
                    count++;
                }

            }

            avg /= count;

            Debug.Log("Sensor Average: " + avg);

            //
        }

    }

    private void OnDestroy()
    {
        if (isBoardConnected && board_shim != null)
        {
            try
            {
                board_shim.release_session();
            }
            catch (BrainFlowError e)
            {
                Debug.Log(e);
            }
            Debug.Log("Brainflow streaming was stopped");
        }
    }
}
