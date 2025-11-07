using System;
using UnityEngine;
using UnityEngine.UIElements;
using static Station;
using System.Collections.Generic;

public class Station : MonoBehaviour
{
    [Serializable]
    public struct StationPoints
    {
        public Transform stationRay;
        public Transform stationTarget;
    }

    [SerializeField] private LayerMask agentLayer;
    [SerializeField] private List<StationPoints> stationPoints;
    private float rayDistance = 5f;

    private bool isOccupied(Transform rayTransform, float rayDistance)
    {
        bool isOccupied = Physics.Raycast(rayTransform.position, rayTransform.forward, out RaycastHit hit, rayDistance, agentLayer);
       
        return isOccupied;
    }

    public void GetAllPointStatus()
    {
        foreach (StationPoints stationPoint in stationPoints)
        {
            bool occupied = isOccupied(stationPoint.stationRay, rayDistance);
            //Debug.Log($"{stationPoint.stationRay.name}: status:{occupied}");
        }
    }

    public Transform GetAvailablePoint()
    {
        foreach (StationPoints stationPoint in stationPoints)
        {
            bool occupied = isOccupied(stationPoint.stationRay, rayDistance);
            if (!occupied)
            {
                //Debug.Log(stationPoint.stationRay.name + " is available.");
                Debug.DrawRay(stationPoint.stationRay.position, stationPoint.stationRay.forward * rayDistance, Color.green, 10f);
                return stationPoint.stationTarget;
            }
            else
            {
                Debug.Log(stationPoint.stationRay.name + " is occupied.");
            }
        }
        Debug.LogWarning("No available points at the station.");
        
        return null;
    }

    public Transform GetRandomPoint()
    {
        if (stationPoints.Count == 0)
        {
            Debug.LogWarning("No station points defined.");
            return null;
        }
        System.Random rand = new System.Random();
        int randomIndex = rand.Next(stationPoints.Count);
        return stationPoints[randomIndex].stationTarget;
    }
}
