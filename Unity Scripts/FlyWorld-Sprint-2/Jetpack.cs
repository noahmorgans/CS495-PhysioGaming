using System;
using System.Collections;
using UnityEngine;

public class Jetpack : MonoBehaviour
{
    private float fuelAmount = 1f;
    private float fuelCap = 1f;

    private bool isFuelBurning = false;
    private float fuelBurnRate = 0.1f; // fuel burned per second
    private float fuelRefillRate = 0.05f; // fuel refill rate

    private float overheatAmount = 0f;
    private float overheatCap = 1f;
    private float overheatRate = 0.5f;   // how fast it heats up
    private float coolRate = 0.8f;       // how fast it cools per second
    private float cooldownDelay = 3f;    // delay before cooling starts

    private Coroutine cooldownCoroutine;

    public event EventHandler<IHasProgress.OnProgressChangedEventArgs> OnFuelChanged;
    public event EventHandler<IHasProgress.OnProgressChangedEventArgs> OnOverheatChanged;

    void Update()
    {
        if (isFuelBurning)
        {
            // Burn fuel and add heat
            fuelAmount -= fuelBurnRate * Time.deltaTime;
            overheatAmount += overheatRate * Time.deltaTime;

            fuelAmount = Mathf.Clamp(fuelAmount, 0f, fuelCap);
            overheatAmount = Mathf.Clamp(overheatAmount, 0f, overheatCap);

            // Notify listeners (UI, etc.)
            OnFuelChanged?.Invoke(this, new IHasProgress.OnProgressChangedEventArgs
            {
                progressNormalized = fuelAmount / fuelCap
            });

            OnOverheatChanged?.Invoke(this, new IHasProgress.OnProgressChangedEventArgs
            {
                progressNormalized = overheatAmount / overheatCap
            });

            // Reset after this frame
            isFuelBurning = false;

            // If we're heating again, cancel any active cooldown
            if (cooldownCoroutine != null)
            {
                StopCoroutine(cooldownCoroutine);
                cooldownCoroutine = null;
            }
        }
        else
        {
            // Start cooldown timer if not already running
            if (cooldownCoroutine == null)
            {
                cooldownCoroutine = StartCoroutine(CooldownRoutine());
            }
        }
    }

    private IEnumerator CooldownRoutine()
    {
        // Wait for delay before starting to cool down
        yield return new WaitForSeconds(cooldownDelay);

        // Slowly cool until overheat = 0 or fuel starts burning again
        while (!isFuelBurning && overheatAmount > 0f)
        {
            overheatAmount -= coolRate * Time.deltaTime;
            overheatAmount = Mathf.Max(overheatAmount, 0f);

            OnOverheatChanged?.Invoke(this, new IHasProgress.OnProgressChangedEventArgs
            {
                progressNormalized = overheatAmount / overheatCap
            });

            yield return null;
        }

        cooldownCoroutine = null;
    }

    public void BurnFuel()
    {
        isFuelBurning = true;
    }

    public void ResetCooldown()
    {
        overheatAmount = 0f;

        OnOverheatChanged?.Invoke(this, new IHasProgress.OnProgressChangedEventArgs
        {
            progressNormalized = overheatAmount / overheatCap
        });
    }

    public void RefillFuel(float refuelAmt)
    {
        fuelAmount += refuelAmt;
        fuelAmount = Mathf.Min(fuelAmount, fuelCap);

        OnFuelChanged?.Invoke(this, new IHasProgress.OnProgressChangedEventArgs
        {
            progressNormalized = fuelAmount / fuelCap
        });
    }

    public float GetFuelAmount()
    {
        return fuelAmount;
    }

    public float GetOverheatAmount()
    {
        return overheatAmount;
    }
}
