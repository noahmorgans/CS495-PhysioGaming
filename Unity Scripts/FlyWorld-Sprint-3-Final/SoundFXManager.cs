using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Audio;

public class SoundFXManager : MonoBehaviour
{
    public static SoundFXManager instance;
    [SerializeField] private AudioSource soundFXObject;

    private void Awake()
    {
        if (instance == null) 
        { 
            instance = this;
        }
    }

    public AudioSource PlaySoundClip(AudioClip audioClip, Transform spawnTransform, float volume)
    {
        AudioSource audioSource = Instantiate(soundFXObject, spawnTransform.position, Quaternion.identity);

        audioSource.clip = audioClip;

        audioSource.volume = volume/2;

        audioSource.Play();

        return audioSource;
    }

    //public void StartSoundLoop(AudioClip loopClip, Transform spawnTransform, float volume)
    //{
    //    if (activeLoopSource.isPlaying) { return; }
    //    activeLoopSource = Instantiate(soundFXObject, spawnTransform);
    //    activeLoopSource.clip = loopClip;
    //    activeLoopSource.volume = volume;
    //    activeLoopSource.loop = true;
    //    activeLoopSource.Play();
    //}

    public void FadeOut(AudioSource audioSource, float FadeTime)
    {
        float startVolume = audioSource.volume;
        
        while (audioSource.volume > 0)
        {
            audioSource.volume -= startVolume * Time.deltaTime / FadeTime;
        }

        audioSource.Stop();
        audioSource.volume = startVolume;
    }

}

