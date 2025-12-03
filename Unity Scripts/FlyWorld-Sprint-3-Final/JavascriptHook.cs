using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class JavascriptHook : MonoBehaviour
{
    [SerializeField] private SpriteRenderer circleSpriteRenderer;
    [SerializeField] TMP_Text textField;

    public void TintRed()
    {
        circleSpriteRenderer.color = Color.red;
    }

    public void TintGreen()
    {
        circleSpriteRenderer.color = Color.green;
    }
    public void TintColor(string value)
    {
          if (ColorUtility.TryParseHtmlString(value, out Color color))
    {
        circleSpriteRenderer.color = color;
    }
    else
    {
        Debug.LogError("Invalid color code: " + value);
    }
    }
    public void UpdateText(string newText)
    {
        textField.text = newText;
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.R))
        {
            TintRed();
        }

        if (Input.GetKeyDown(KeyCode.G))
        {
            TintGreen();
        }
    }

}
