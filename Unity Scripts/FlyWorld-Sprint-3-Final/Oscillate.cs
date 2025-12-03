using UnityEngine;

public class Oscillate : MonoBehaviour
{
    //#### VARS
    Vector3 startPos;
    public Vector3 endPos;
    public float speed = 10f;
    bool reverse = false;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        startPos = transform.position;
    }

    // Update is called once per frame
    void Update()
    {
        if (reverse)
        {
            //Move to start pos
            transform.position = Vector3.MoveTowards(transform.position, startPos, speed * Time.deltaTime);
        }
        else
        {
            //Move to end pos
            transform.position = Vector3.MoveTowards(transform.position, endPos, speed * Time.deltaTime);
        }

        if (reverse && Vector3.Distance(transform.position, startPos) <= 0)
        {
            reverse = false;
        }

        if (!reverse && Vector3.Distance(transform.position, endPos) <= 0)
        {
            reverse = true;
        }
    }
}
