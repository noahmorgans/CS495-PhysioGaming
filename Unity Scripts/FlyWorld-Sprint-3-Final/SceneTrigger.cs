using System.Collections;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

public class SceneTrigger : MonoBehaviour
{
    //##### VARS
    public string sceneName = "";
    bool isTriggered = false;

    // Start is called once before the first execution of Update after the MonoBehaviour is created



    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!isTriggered && other.tag == "Player" && sceneName != "")
        {
            Debug.Log("Triggered by player");
            StartCoroutine(LoadSceneAsync(sceneName));
            isTriggered = true;
        }

    }

    IEnumerator LoadSceneAsync(string name)
    {

        AsyncOperation asyncLoad = SceneManager.LoadSceneAsync(name);

        // Wait until the asynchronous scene fully loads
        while (!asyncLoad.isDone)
        {
            yield return null;
        }

    }


}
