using UnityEngine;
using TMPro;

public class TextUpdater : MonoBehaviour
{
    [SerializeField] TMP_Text textField;

    public void UpdateText(string newText)
    {
        textField.text = newText;
    }

    public void UpdateTest(string newText)
    {
        textField.text = newText;
    }
}