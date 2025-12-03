using UnityEngine;

public class RotateObject : MonoBehaviour
{
    [Header("Rotation Settings")]
    [SerializeField] private float rotationSpeed = 50f; // Degrees per second

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        // Rotate the object around the Y-axis based on the rotation speed
        transform.Rotate(0f, rotationSpeed * Time.deltaTime, 0f);
    }
}
