using System;
using UnityEngine;

public class CoinBag : MonoBehaviour, IHasProgressInt
{
    private int _coinCount = 0;
    public event EventHandler<IHasProgressInt.OnProgressChangedIntEventArgs> OnProgressChanged;

    public void AddCoin()
    {
        _coinCount++;
        OnProgressChanged?.Invoke(this, new IHasProgressInt.OnProgressChangedIntEventArgs
        {
            count = _coinCount
        });
    }

    public void RemoveCoin()
    {
        if (_coinCount > 0)
        {
            _coinCount--;
            OnProgressChanged?.Invoke(this, new IHasProgressInt.OnProgressChangedIntEventArgs
            {
                count = _coinCount
            });
        }
    }
}
