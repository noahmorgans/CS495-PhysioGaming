using TMPro;
using UnityEngine;

public class SensorUpdate : MonoBehaviour
{
    [SerializeField] TMP_Text inputText;
    [SerializeField] Player player;
    

    public void UpdateText(string newText)
    {
        inputText.text = newText;

        if (float.TryParse(newText, out float parsedFloat))
        {
            player.SetSensorVal(parsedFloat);
        }
        else
        {
            Debug.LogWarning($"TextUpdater: Could not parse '{newText}' into float.");
        }

    }

    public void UpdateTest(string newText)
    {
    }
}
