using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using TMPro;
using UnityEditor.PackageManager;
using UnityEngine;
using UnityEngine.UI;

public class Socket_Test : MonoBehaviour
{
    //###### VARS
    int port = 50007;
    IPAddress ip = null;
    TcpClient client = null;
    NetworkStream netStream = null;

    TMP_Text textObj;

    byte[] endMsg = Encoding.UTF8.GetBytes("end");

    //####### START
    void Start()
    {
        //Get text object
        textObj = GameObject.Find("Test Text").GetComponent<TMP_Text>();


        //Set up socket
        ip = IPAddress.Parse("127.0.0.1");
        client = new TcpClient();
        client.Connect(ip, port);
        netStream = client.GetStream();
    }

    // ######### UPDATE
    void Update()
    {
        if (client.Available > 0)
        {
            byte[] buffer = new byte[1024];
            int rx = netStream.Read(buffer);

            string msg = Encoding.UTF8.GetString(buffer);
            textObj.text = msg;
            //Debug.Log(msg);
        }

    }


    private void OnDestroy()
    {
        if (client.Connected)
        {
            netStream.Write(endMsg);
        }
    }
}
