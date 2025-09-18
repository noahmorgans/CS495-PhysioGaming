using System;
using UnityEngine;

public class Jetpack : MonoBehaviour, IHasProgress
{
    private float fuelAmount = 1f;
    private bool isFuelBurning = false;
    private float fuelBurnRate = 0.1f; // Fuel burned per second
    private float fuelRefillRate = 0.05f; // Fuel refilled rate
    public event EventHandler<IHasProgress.OnProgressChangedEventArgs> OnProgressChanged;

    void Update()
    {
        if (isFuelBurning)
        {
            fuelAmount -= fuelBurnRate * Time.deltaTime;
            isFuelBurning = false; // Reset after burning fuel for this frame

            OnProgressChanged?.Invoke(this, new IHasProgress.OnProgressChangedEventArgs
            {
                progressNormalized = fuelAmount
            });
        }
    }

    public void BurnFuel()
    {
        isFuelBurning = true;
    }

    public void RefillFuel()
    {
        fuelAmount += fuelRefillRate;
        OnProgressChanged?.Invoke(this, new IHasProgress.OnProgressChangedEventArgs
        {
            progressNormalized = fuelAmount
        });
    }

    public float GetFuelAmount()
    {
        return fuelAmount;
    }
}
