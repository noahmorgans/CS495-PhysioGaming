using UnityEngine;

public class FPSLimiter : MonoBehaviour
{
    public int targetFPS = 60; // Set your desired target FPS here

    void Awake()
    {
        QualitySettings.vSyncCount = 0; // Disable VSync
        Application.targetFrameRate = targetFPS;
    }
}
