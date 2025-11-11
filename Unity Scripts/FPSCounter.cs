using UnityEngine;
using TMPro;

public class FPSTracker : MonoBehaviour
{
    public static FPSTracker instance;

    [SerializeField] private TextMeshProUGUI fpsText;
    [SerializeField] private float updateInterval = 0.5f;

    private float _accumulatedTime = 0f;
    private int _frameCount = 0;
    private float _timeLeft;

    private void Awake()
    {
        instance = this;
    }

    void Start()
    {
        _timeLeft = updateInterval;
    }

    void Update()
    {
        _timeLeft -= Time.deltaTime;
        _accumulatedTime += Time.timeScale / Time.deltaTime;
        _frameCount++;

        if (_timeLeft <= 0f)
        {
            float fps = _accumulatedTime / _frameCount;
            int roundedFPS = Mathf.RoundToInt(fps);
            UpdateFPSText(roundedFPS);

            _timeLeft = updateInterval;
            _accumulatedTime = 0f;
            _frameCount = 0;
        }
    }

    private void UpdateFPSText(int fps)
    {
        if (fpsText != null)
        {
            fpsText.text = fps.ToString();
        }
    }
}
