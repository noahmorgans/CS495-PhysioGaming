using NUnit.Framework.Constraints;
using System;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;

public class GameInput : MonoBehaviour
{
    private InputSystem_Actions inputActions;
    [SerializeField] private FixedJoystick fixedJoystick;
    [SerializeField] private Image jumpButton;
    [SerializeField] private Image flyButton;
    [SerializeField] private bool isMobileTesting;
    private bool isMobile = false;
    private Vector2 inputVector;
    //public event EventHandler OnJump;

    private void Awake()
    {
        
        inputActions = new InputSystem_Actions();
        inputActions.Player.Enable();
        if (Application.isMobilePlatform || isMobileTesting)
        {
            isMobile = true;
            fixedJoystick.gameObject.SetActive(isMobile);
            jumpButton.gameObject.SetActive(isMobile);
            flyButton.gameObject.SetActive(isMobile);
        } else
        {
            fixedJoystick.gameObject.SetActive(false);
            jumpButton.gameObject.SetActive(false);
            flyButton.gameObject.SetActive(false);
        }

        //inputActions.Player.Jump.performed += Jump_Performed;
    }

    private Vector2 GetJoyStickMovmentNormalized()
    {
        float horizontal = fixedJoystick.Horizontal;
        float vertical = fixedJoystick.Vertical;
        Vector2 inputVector = new Vector2(horizontal, vertical);
        return inputVector.normalized;
    }
    public Vector2 GetMovementVectorNormlized()
    {
        if (isMobile || isMobileTesting)
        {
            inputVector = GetJoyStickMovmentNormalized();
        } else
        {
            inputVector = inputActions.Player.Move.ReadValue<Vector2>();
        }

        return inputVector.normalized;
    }

/*    public void Jump_Performed(UnityEngine.InputSystem.InputAction.CallbackContext obj)
    {
        OnJump?.Invoke(this, EventArgs.Empty);
    }*/

    public bool GetBurstHold()
    {
        return Convert.ToBoolean(inputActions.Player.Fly.ReadValue<float>());
    }
}
