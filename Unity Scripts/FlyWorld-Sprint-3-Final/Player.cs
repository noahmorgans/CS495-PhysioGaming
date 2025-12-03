using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using Unity.Cinemachine;
using UnityEngine;

public class Player : LivingObject
{
    [SerializeField] private GameInput gameInput;
    [SerializeField] private float speed = 5f;
    [SerializeField] private float rotationSpeed = 5f;
    [SerializeField] private float hp = 100f;
    [SerializeField] private float holdVal;
    [SerializeField] private GameObject jetPackParticles;
    [SerializeField] private GameObject jetPackLungeParticles;
    [SerializeField] private Jetpack jetpack;
    [SerializeField] private CoinBag coinBag;
    [SerializeField] private float fuelLevel;
    [SerializeField] private int coinsCollected;
    [SerializeField] private float gravityModifier = 1; //Should probably move this out of player script
    [SerializeField] private AudioClip flySoundClip;
    [SerializeField] private AudioClip fuelEmptySoundClip;
    [SerializeField] private AudioClip overheatedSoundClip;

    [SerializeField] private PredictGesture predictGesture;


    private AudioSource playerAudioSource;

    private string coinTag = "Coin";
    private string fuelTag = "Fuel";
    private string cooldownTag = "Cooldown";
    private string respawnTag = "Lvl1Respawn";
    private string gasStationTag = "7-11";

    private float tiltOffset = 0f;
    private Vector2 inputVector;
    private Vector3 inputDir;
    private Vector3 moveDir;

    Rigidbody rb;
    CharacterController charCtlr;

    private bool takeFallDmg = false;
    float relVel = 0f;
    float fallDmgThreshold = 7; //units / second
    float fallDmgModifier = 1f;

    private float detectionRadius = 4f;

    private bool hpChanged = true;
    private bool wasFuelBurnt = false;

    private float sensorVal = 0f;
    private float sensorThreshold = 1;

    private void Start()
    {
        charCtlr = gameObject.GetComponentInChildren<CharacterController>();
        rb = gameObject.GetComponent<Rigidbody>();
        SetRigidBody(rb);
        jetpack.OnFuelChanged += Jetpack_OnFuelChanged;
        jetpack.OnOverheatChanged += Jetpack_OnOverheatChanged;
        Physics.gravity = new Vector3(0, Physics2D.gravity.y * gravityModifier, 0);
        playerAudioSource = GetComponent<AudioSource>();
    }

    private void CoinBag_OnProgressChanged(object sender, IHasProgressInt.OnProgressChangedIntEventArgs e)
    {
        coinsCollected = e.count;
    }

    private void Jetpack_OnFuelChanged(object sender, IHasProgress.OnProgressChangedEventArgs e)
    {
        fuelLevel = e.progressNormalized;
    }

    private void Jetpack_OnOverheatChanged(object sender, IHasProgress.OnProgressChangedEventArgs e)
    {
        float overheatLevel = e.progressNormalized;
    }

    private void Update()
    {
        inputVector = gameInput.GetMovementVectorNormlized();
        inputDir = new Vector3(inputVector.x, 0f, inputVector.y);
        moveDir = transform.forward * inputDir.z + transform.right * inputDir.x;
        transform.position += moveDir * speed * Time.deltaTime;
        bool _isMoving = moveDir != Vector3.zero;
        UpdateMoveState(_isMoving);
        UpdateFlyState(!IsGrounded());
        CheckForNearbyObjects();
        transform.rotation = Quaternion.Euler(tiltOffset, transform.rotation.eulerAngles.y, transform.rotation.eulerAngles.z);

        if (inputDir != Vector3.back)
        {
            // Input direction is not directly backwards

            Vector3 slerpVal = Vector3.Slerp(transform.forward, moveDir, rotationSpeed * Time.deltaTime);
            transform.forward = slerpVal;
        }

        if (Input.GetKey(KeyCode.LeftControl)){
            Lunge();
        }

        if (Input.GetKey(KeyCode.LeftShift) || gameInput.GetBurstHold() || sensorVal >= sensorThreshold || predictGesture.GetGestureName() == "Propulsion")
        {
            // Shift is being held down
            if (jetpack.GetFuelAmount() > 0 && jetpack.GetOverheatAmount() < 1)
            {
                Fly();
                jetpack.BurnFuel();
                jetPackLungeParticles.SetActive(IsLunging());
                jetPackParticles.SetActive(!IsLunging());
                if (!wasFuelBurnt)
                {
                    playerAudioSource = SoundFXManager.instance.PlaySoundClip(flySoundClip, transform, 0.2f);
                }
                wasFuelBurnt = true;
            }
            else
            {
                SoundFXManager.instance.FadeOut(playerAudioSource, 100);
                if (jetpack.GetFuelAmount() <= 0 && wasFuelBurnt == true)
                {
                    SoundFXManager.instance.PlaySoundClip(fuelEmptySoundClip, transform, 1f);
                }
                if (jetpack.GetOverheatAmount() >= 1 && wasFuelBurnt == true)
                {
                    SoundFXManager.instance.PlaySoundClip(overheatedSoundClip, transform, 0.5f);
                }
                jetPackParticles.SetActive(false);
                jetPackLungeParticles.SetActive(false);
                wasFuelBurnt = false;
            }
        }
        else
        {
            jetPackParticles.SetActive(false);
            jetPackLungeParticles.SetActive(false);
            SoundFXManager.instance.FadeOut(playerAudioSource, 100);
            wasFuelBurnt = false;
        }

        //Fall Damage
        if (takeFallDmg && relVel > fallDmgThreshold) {
            //dmg = velocity * fallDmgMod
            float damage = relVel * fallDmgModifier;
            //Debug.Log("Amt: " + damage);
            hp -= damage;
            hpChanged = true;
            takeFallDmg = false;
        }


        //Update hp
        if (hpChanged) {
            //TMP_Text txt = GameObject.Find("text_hp").GetComponent<TMP_Text>();
            //txt.text = "HP: " + hp;
            hpChanged = false;
        }

    }

    public void SetSensorVal(float val)
    {
        sensorVal = val;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.CompareTag(coinTag))
        {
            Destroy(other.gameObject);
            coinBag.AddCoin();
        }
        else if (other.gameObject.CompareTag(fuelTag))
        {
            jetpack.RefillFuel(.5f);
            Destroy(other.gameObject);
        }
        else if (other.gameObject.CompareTag(respawnTag))
        {
            transform.position = new Vector3(-43.99f, 3.49f, 186.37f);
            jetpack.ResetCooldown();
        }
        else if (other.gameObject.CompareTag(cooldownTag))
        {
            jetpack.ResetCooldown();
            Destroy(other.gameObject);
        }
    }

    private void CheckForNearbyObjects()
    {
        // Find all colliders within the detection radius
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, detectionRadius);

        foreach (Collider hitCollider in hitColliders)
        {
            // Check if the nearby object has the gas station tag
            if (hitCollider.CompareTag(gasStationTag))
            {
                if(jetpack.GetFuelAmount() < 1f)
                {
                    jetpack.RefillFuel(.02f);
                }
                break; // Call once per frame if at least one tagged object is nearby
            }
        }
    }


    private void OnCollisionEnter(Collision collision) {
        //Might need to modify to not get fall damage on every object
        takeFallDmg = true;
        relVel = collision.relativeVelocity.magnitude;
        //Debug.Log("Relative Velocity: " + relVel);
        
    }

    private void TakeDmg(float amt) {
        //This function reduces player hp and displays the damage

    }
}


    