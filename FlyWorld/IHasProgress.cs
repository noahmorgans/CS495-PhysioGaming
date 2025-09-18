using System;

public interface IHasProgress
{
    public class OnProgressChangedEventArgs : EventArgs
    {
        public float progressNormalized;
    }

    public event EventHandler<OnProgressChangedEventArgs> OnProgressChanged;
}