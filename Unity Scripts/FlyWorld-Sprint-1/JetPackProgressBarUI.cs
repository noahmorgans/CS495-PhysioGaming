using UnityEngine;
using UnityEngine.UI;

public class JetPackProgressBarUI : MonoBehaviour
{
    [SerializeField] private GameObject hasProgressGameObject;
    [SerializeField] private Image barImage;
    private IHasProgress hasProgress;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        hasProgress = hasProgressGameObject.GetComponent<IHasProgress>();
        if (hasProgress == null)
        {
            Debug.LogError("Game Object " + hasProgressGameObject + " does not implement IHasProgress.");
        }

        hasProgress.OnProgressChanged += HasProgress_OnProgressChanged;
        barImage.fillAmount = 1f;
    }

    private void HasProgress_OnProgressChanged(object sender, IHasProgress.OnProgressChangedEventArgs e)
    {
        barImage.fillAmount = e.progressNormalized;
    }
}
