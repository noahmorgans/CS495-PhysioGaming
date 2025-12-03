using UnityEngine;
using UnityEngine.UI;

public class JetPackProgressBarUI : MonoBehaviour
{
    public enum ProgressBarType { Fuel, Overheat }

    [SerializeField] private GameObject hasProgressGameObject;
    [SerializeField] private Image barImage;
    [SerializeField] private ProgressBarType progressBarType;

    private Jetpack jetpack;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        jetpack = hasProgressGameObject.GetComponent<Jetpack>();
        if (jetpack == null)
        {
            Debug.LogError("Game Object " + hasProgressGameObject + " does not have a Jetpack component.");
            return;
        }

        switch (progressBarType)
        {
            case ProgressBarType.Fuel:
                jetpack.OnFuelChanged += OnProgressChanged;
                barImage.fillAmount = 1f;
                break;
            case ProgressBarType.Overheat:
                jetpack.OnOverheatChanged += OnProgressChanged;
                barImage.fillAmount = 0f;
                break;
        }
    }

    private void OnProgressChanged(object sender, IHasProgress.OnProgressChangedEventArgs e)
    {
        barImage.fillAmount = e.progressNormalized;
    }
}
