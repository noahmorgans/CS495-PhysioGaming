using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;

public class Controls : MonoBehaviour
{
    //###### VARS
    public float speed = 50;
    GameObject player;
    Rigidbody body;

    
    int port = 50007;
    IPAddress ip = null;
    TcpClient client = null;
    NetworkStream netStream = null;


    TMP_Text textObj;

    byte[] endMsg = Encoding.UTF8.GetBytes("end");
    int numRec = 0;
    bool doRead = true;

    float thresh = 1000;
    float avg = 0;
    bool sensorState = false;

    //####### START
    void Start()
    {
        //Get player object and rigidbody
        player = GameObject.Find("Player");
        body = player.GetComponent<Rigidbody>();

        //Get text object
        textObj = GameObject.Find("Test Text").GetComponent<TMP_Text>();


        //Set up socket
        ip = IPAddress.Parse("127.0.0.1");
        client = new TcpClient();
        client.Connect(ip, port);
        netStream = client.GetStream();
    }

    // Update is called once per frame
    void Update()
    {
        if (doRead)
        {
            sensorState = ReadMessage();
        }

        //Basic Controls
        if (Input.GetKey(KeyCode.W))
            transform.position += transform.forward * speed * Time.deltaTime;
        if (Input.GetKey(KeyCode.Space) || sensorState )
            transform.position += transform.up * speed * Time.deltaTime;
        if (Input.GetKey(KeyCode.S))
            transform.position -= transform.forward * speed * Time.deltaTime;
        if (Input.GetKey(KeyCode.A))
            transform.position -= transform.right * speed * Time.deltaTime;
        if (Input.GetKey(KeyCode.D))
            transform.position += transform.right * speed * Time.deltaTime;
        if (Input.GetKey(KeyCode.Escape))
            doRead = false;
    }

    private void OnDestroy()
    {
        if (client.Connected)
        {
            netStream.Write(endMsg);
        }
    }



    //####### READ MESSAGE
    bool ReadMessage()
    {
        //Get Socket Input
        byte[] buffer = new byte[1024];
        int rx = netStream.Read(buffer);
        netStream.Flush();

        

        numRec++;

        string msg = Encoding.UTF8.GetString(buffer);
        //float avg = System.BitConverter.ToSingle(buffer);
        textObj.text = (msg);

        //avg = float.Parse(msg, CultureInfo.InvariantCulture.NumberFormat);
        if (msg.Contains("1"))
        {
            return true;
        }

        return false;
    }

}




