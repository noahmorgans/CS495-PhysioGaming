using Google.Protobuf.WellKnownTypes;
using TMPro;
using Unity.VisualScripting.AssemblyQualifiedNameParser;
using UnityEngine;
using UnityEngine.UI;

public class TextUpdater : MonoBehaviour
{

    [SerializeField] PredictGesture gesturePredictor;
    [SerializeField] TMP_Text inputText;
    public void UpdateText(string newText)
    {
        if (float.TryParse(newText, out float parsedFloat))
        {
            float[] floatVal = new float[] { parsedFloat };
            inputText.text = newText;
            gesturePredictor.AddEmgSample(floatVal);
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