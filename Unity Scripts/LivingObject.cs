using UnityEngine;
using System.Collections;

public class LivingObject : MonoBehaviour
{
    [SerializeField] private LayerMask groundLayer;
    private float groundRaycastDistance = 0.6f;
    public float jumpForce = 4.75f;
    public float lungeSpeed = 8f;
    private bool isMoving = false;
    private bool isDead = false;
    private bool isFlying = false;
    private bool isLunging = false;
    private bool isLungeReady = true;
    private Rigidbody rigid;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        //rigid = gameObject.GetComponent<Rigidbody>();
    }

    void FixedUpdate()
    {
        // Only apply thrust while flying
        if (isFlying)
            Fly();
    }

    public bool IsGrounded()
    {
        RaycastHit hit;
        Debug.DrawRay(transform.position, Vector3.down * groundRaycastDistance, Color.red);
        bool isGrounded = Physics.Raycast(transform.position, Vector3.down, out hit, groundRaycastDistance, groundLayer);
        //Debug.Log($"Is Grounded: {isGrounded}, Hit Point: {hit.point}, Distance: {hit.distance}");
        return isGrounded;
    }
    private void Die()
    {
        UpdateAliveState(false);
    }

    public void Lunge()
    {
        if (isLungeReady)
        {
            // Start the coroutine so we can time how long isLunging stays true
            StartCoroutine(LungeRoutine());
        }
    }

    private IEnumerator LungeRoutine()
    {
        isLungeReady = false;
        isLunging = true;
        yield return new WaitForSeconds(5f);
        isLunging = false;
        yield return new WaitForSeconds(5f);
        isLungeReady = true;
    }

    public void Fly()
    {
        if (isLunging)
        {
            // Go forward (in facing direction) and slightly up
            Vector3 forwardDirection = transform.forward.normalized;
            Vector3 lungeDirection = (forwardDirection + Vector3.up * 0.15f).normalized; // tweak 0.3f to control upward angle

            rigid.linearVelocity = lungeDirection * lungeSpeed;
        }
        //rigid.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        else
        {
            rigid.AddForce(Vector3.up * jumpForce, ForceMode.Acceleration);
        }
    }
    public bool IsFlying()
    {
        return isFlying;
    }

    public bool IsLunging()
    {
        return isLunging;
    }
    public bool IsLungeReady()
    {
        return isLungeReady;
    }

    public bool IsMoving()
    {
        return isMoving;
    }
    public bool IsDead()
    {
        return isDead;
    }
    public void UpdateFlyState(bool flyState)
    {
        isFlying = flyState;
    }

    public void UpdateAliveState(bool aliveState)
    {
        isDead = aliveState;
    }

    public void UpdateMoveState(bool moveState)
    {
        isMoving = moveState;
    }

    public Rigidbody GetRigidBody()
    {
        return rigid;
    }

    public void SetRayCastDistance(float groundRaycastDistanceParam)
    {
        groundRaycastDistance = groundRaycastDistanceParam;
    }

    public void SetRigidBody(Rigidbody rigidBodyParam)
    {
        rigid  = rigidBodyParam;
    }
}
