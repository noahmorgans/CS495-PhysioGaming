using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class CoinBag : MonoBehaviour
{
    private int _coinCount = 0;
    public static CoinBag instance;

    [SerializeField] private TextMeshProUGUI scoreText;
    [SerializeField] private AudioClip coinCollectSoundClip;  

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

        SoundFXManager.instance.PlaySoundClip(coinCollectSoundClip, transform, 1f);

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
