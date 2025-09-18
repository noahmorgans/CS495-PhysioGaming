using UnityEngine;

public class LivingObject : MonoBehaviour
{
    [SerializeField] private LayerMask groundLayer;
    private float groundRaycastDistance = 0.6f;
    public float jumpForce = 7f;
    private bool isMoving = false;
    private bool isDead = false;
    private bool isFlying = false;
    private Rigidbody rigid;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        //rigid = gameObject.GetComponent<Rigidbody>();
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

    public void Fly()
    {
        //rigid.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        rigid.linearVelocity = new Vector3(rigid.linearVelocity.x, jumpForce, rigid.linearVelocity.z);
    }
    public bool IsFlying()
    {
        return isFlying;
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
