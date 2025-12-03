using UnityEngine;

public class BirdSpawner : MonoBehaviour
{
    [Header("Spawn Settings")]
    public GameObject birdPrefab;
    public int maxBirds = 100;
    public float spawnInterval = .1f;

    [Header("Spawn Bounds")]
    public Vector3 minBounds = new Vector3(-128.5f, 14.44f, 5f);
    public Vector3 maxBounds = new Vector3(43.4f, 59.7f, 213.46f);

    [Header("Bird Settings")]
    public float minSpeed = 2f;
    public float maxSpeed = 5f;

    private float timer;

    void Update()
    {
        timer += Time.deltaTime;

        if (timer >= spawnInterval)
        {
            SpawnBird();
            timer = 0f;
        }
    }

    void SpawnBird()
    {
        if (birdPrefab == null) return;

        Vector3 spawnPos = new Vector3(
            Random.Range(minBounds.x, maxBounds.x),
            Random.Range(minBounds.y, maxBounds.y),
            Random.Range(minBounds.z, maxBounds.z)
        );

        GameObject bird = Instantiate(birdPrefab, spawnPos, Quaternion.identity);

        Vector3 randomDir = new Vector3(
            Random.Range(-1f, 1f),
            Random.Range(-0.1f, 0.1f), // small vertical variance
            Random.Range(-1f, 1f)
        ).normalized;
        float speed = Random.Range(minSpeed, maxSpeed);

        bird.GetComponent<BirdMovement>().Initialize(randomDir, speed);
    }

    void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.cyan;
        Vector3 size = maxBounds - minBounds;
        Gizmos.DrawWireCube((minBounds + maxBounds) / 2f, size);
    }
}
