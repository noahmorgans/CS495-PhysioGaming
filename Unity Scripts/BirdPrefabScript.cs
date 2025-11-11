using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class BirdMovement : MonoBehaviour
{
    private Vector3 direction;
    private float speed;
    private Rigidbody rb;
    private float lifetime = 10f;

    public void Initialize(Vector3 dir, float spd)
    {
        direction = dir.normalized;
        speed = spd;
        rb = GetComponent<Rigidbody>();
        Destroy(gameObject, lifetime);
    }

    void FixedUpdate()
    {
        // Move the bird using physics (respects collisions)
        Vector3 move = direction * speed * Time.fixedDeltaTime;
        rb.MovePosition(rb.position + move);

        // Face direction of movement if moving fast enough
        if (direction != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(direction, Vector3.up);
            rb.MoveRotation(Quaternion.Slerp(rb.rotation, targetRotation, Time.fixedDeltaTime * 5f));
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        // Reflect direction using the collision normal (so it bounces off)
        direction = Vector3.Reflect(direction, collision.contacts[0].normal);
    }
}
