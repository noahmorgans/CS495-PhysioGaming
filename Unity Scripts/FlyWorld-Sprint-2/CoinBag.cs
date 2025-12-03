using System;
using UnityEngine;
using TMPro;

public class CoinBag : MonoBehaviour
{
    private int _coinCount = 0;
    public static CoinBag instance;

    [SerializeField] private TextMeshProUGUI scoreText;

    private void Awake()
    {
        instance = this;
    }

    void Start()
    {
        UpdateScoreText();
    }

    public void AddCoin()
    {
        _coinCount++;
        UpdateScoreText();
    }

    public void RemoveCoin()
    {
        if (_coinCount > 0)
        {
            _coinCount--;
            UpdateScoreText();
        }
    }

    private void UpdateScoreText()
    {
        if (scoreText != null)
            scoreText.text = _coinCount.ToString("D3");
    }
}
