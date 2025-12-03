using System;
using UnityEngine;
using UnityEngine.AI;
using static Station;
using System.Collections.Generic;

public class Agent : MonoBehaviour
{
    [SerializeField] private NavMeshAgent m_Agent;
    //[SerializeField] private Station station;
    [SerializeField] private Station[] stations;

    public enum AgentState
    {
        Idle,
        MovingToStation,
        AtStation,
        MovingFromStation
    }

   //private float agentTimer;
   private float workingTimer;
    private float workingTimerMax = 5f;
    private float idleTimer;
    private float idleTimerMax = 2f;
    private AgentState agentState;


    //RaycastHit m_HitInfo = new RaycastHit();
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        //m_Agent = GetComponent<NavMeshAgent>();
        agentState = AgentState.Idle;
    }

    private Transform GetRandomPoint()
    {
        System.Random rand = new System.Random();
        int randomIndex = rand.Next(stations.Length);
        Station station = stations[randomIndex];
        return station.GetRandomPoint();
    }

    // Update is called once per frame
    void Update()
    {

        switch (agentState)
        {
            case AgentState.Idle:
                idleTimer += Time.deltaTime;
                if (idleTimer >= idleTimerMax)
                {
                    Transform availablePoint = GetRandomPoint();
                    if (availablePoint != null)
                    {
                        m_Agent.destination = availablePoint.position;
                        agentState = AgentState.MovingToStation;
                        idleTimer = 0f;
                        //Debug.Log("Agent is moving to station.");
                    }
                }
                break;
            case AgentState.MovingToStation:
                if (!m_Agent.hasPath || m_Agent.velocity.sqrMagnitude == 0f)
                {
                    agentState = AgentState.AtStation;
                    //Debug.Log("Agent has arrived at station.");
                }
                break;
            case AgentState.AtStation:
                // Simulate working at the station
                workingTimer += Time.deltaTime;
                if (workingTimer > workingTimerMax)
                {
                    stations[0].GetAllPointStatus();
                    Transform availablePoint = GetRandomPoint();
                    if (availablePoint != null)
                    {
                        m_Agent.destination = availablePoint.position;
                        agentState = AgentState.MovingToStation;
                        workingTimer = 0f;
                        //Debug.Log("Agent is moving to new station.");
                    }
                }
                break;
        }
        /*
        if (Input.GetMouseButtonDown(0))
        {
            //Transform availablePoint = station.GetAvailablePoint();
            //if (availablePoint != null)
            //{
            //    m_Agent.destination = availablePoint.position;
            //}
            //Transform availablePoint = station.GetAvailablePoint();
            //if (availablePoint != null)
            //{
            //    m_Agent.destination = availablePoint.position;
            //}
            //Debug.Log("Click");
            //var ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            //if (Physics.Raycast(ray.origin, ray.direction, out m_HitInfo))
            //{
            //    m_Agent.destination = m_HitInfo.point;
            //    Debug.Log("Destination set to " + m_HitInfo.point);
            //}

        }
        */
    }
}
