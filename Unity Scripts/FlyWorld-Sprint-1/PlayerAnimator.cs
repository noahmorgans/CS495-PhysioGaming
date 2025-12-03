using UnityEngine;

public class PlayerAnimator : MonoBehaviour
{
    private enum MovementDefault
    {
        Walking,
        Running,
        Dead,
    }

    [SerializeField] MovementDefault defaultMovement;
    private const string IS_WALKING = "isWalking";
    private const string IS_RUNNING = "isRunning";
    private const string IS_DEAD = "isDead";
    private const string IS_FLYING = "isFlying";
    [SerializeField] private Player player;
    private Animator animator;

    private void Awake()
    {
        animator = GetComponent<Animator>();
    }
    private void StopAllAnimations()
    {
        animator.SetBool(IS_WALKING, false);
        animator.SetBool(IS_RUNNING, false);
        animator.SetBool(IS_FLYING, false);
        animator.SetBool(IS_DEAD, false);
        animator.SetBool(IS_WALKING, false);
    }

    private void Update()
    {
        if (defaultMovement == MovementDefault.Walking)
        {
            animator.SetBool(IS_WALKING, player.IsMoving());
        }

        else if (defaultMovement == MovementDefault.Running)
        {
            animator.SetBool(IS_RUNNING, player.IsMoving());
        }

        if (player.IsGrounded())
        {
            // Never trigger flying animation if grounded
            animator.SetBool(IS_FLYING, false);
        }

        if (player.IsDead())
        {
            StopAllAnimations();
            animator.SetBool(IS_DEAD, true);
            return;
        }

        if (player.IsFlying())
        {
            StopAllAnimations();
            animator.SetBool(IS_FLYING, true);
            return;
        }
    }
}
