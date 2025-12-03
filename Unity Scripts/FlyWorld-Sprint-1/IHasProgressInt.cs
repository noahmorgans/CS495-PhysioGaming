using System;
public interface IHasProgressInt
{
    public class OnProgressChangedIntEventArgs : EventArgs
    {
        public int count;
    }

    public event EventHandler<OnProgressChangedIntEventArgs> OnProgressChanged;
}
