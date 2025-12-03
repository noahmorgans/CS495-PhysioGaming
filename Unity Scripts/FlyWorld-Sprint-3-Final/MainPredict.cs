using brainflow;
using System;
using Unity.Barracuda;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Timeline;

public class PredictGesture : MonoBehaviour
{
    [Header("ONNX Model")]
    [Tooltip("ONNX model asset: emg_cnn_model_3(TEMPLATES_TEST).onnx imported as NNModel")]
    public NNModel onnxModelAsset;

    [Header("EMG Settings")]
    [Tooltip("Window size in samples (must match training: 100).")]
    public int windowSize = 100;

    [Tooltip("Number of EMG channels used (Python used ACTIVE_CHANNELS = [0] ? 1 channel).")]
    public int nChannels = 1;

    [Header("Normalization (from Python norm_params)")]
    [Tooltip("Per-channel mean from training (X_mean.squeeze()). Length = nChannels.")]
    public float[] channelMean;

    [Tooltip("Per-channel std from training (X_std.squeeze()). Length = nChannels.")]
    public float[] channelStd;

    [Header("Gesture Labels")]
    [Tooltip("Output class names in index order. Python: 0=Propulsion, 1=Rest.")]
    public string[] gestureNames = new string[] { "Propulsion", "Rest" };

    // Internal model/worker
    private Model _runtimeModel;
    private IWorker _worker;
    String gestureName = "Rest";

    // Ring buffer for EMG samples (time x channels)
    private float[,] _windowBuffer;
    private int _bufferIndex = 0;
    private int _bufferCount = 0;

    private const float EPSILON = 1e-8f;

    private void Awake()
    {
        if (onnxModelAsset == null)
        {
            Debug.LogError("PredictGesture: ONNX model asset not assigned.");
            return;
        }

        _runtimeModel = ModelLoader.Load(onnxModelAsset);
        _worker = WorkerFactory.CreateWorker(WorkerFactory.Type.Auto, _runtimeModel);

        _windowBuffer = new float[windowSize, nChannels];

        if (channelMean == null || channelStd == null ||
            channelMean.Length != nChannels || channelStd.Length != nChannels)
        {
            Debug.LogWarning("PredictGesture: channelMean/channelStd not set or length mismatch. " +
                             "Please copy per-channel mean/std from Python.");
        }
    }

    private void OnDestroy()
    {
        _worker?.Dispose();
    }

    /// <summary>
    /// Call this whenever you have a new EMG sample for each active channel.
    /// For your current setup, you only have 1 channel (channel 0).
    /// </summary>
    /// <param name="samplePerChannel">Array of length nChannels with raw (or pre-filtered) EMG values.</param>
    public void AddEmgSample(float[] samplePerChannel)
    {
        if (samplePerChannel == null || samplePerChannel.Length != nChannels)
        {
            Debug.LogError($"PredictGesture.AddEmgSample: expected {nChannels} values, got " +
                           (samplePerChannel == null ? "null" : samplePerChannel.Length.ToString()));
            return;
        }
        
        // Store in ring buffer
        for (int ch = 0; ch < nChannels; ch++)
        {
            _windowBuffer[_bufferIndex, ch] = samplePerChannel[ch];
        }

        _bufferIndex = (_bufferIndex + 1) % windowSize;
        _bufferCount = Mathf.Min(_bufferCount + 1, windowSize);

        // Only predict once we have a full window
        if (_bufferCount == windowSize)
        {
            PredictFromCurrentWindow();
        }
    }

    /// <summary>
    /// Builds the current window, normalizes it, runs ONNX model, logs prediction.
    /// </summary>
    private void PredictFromCurrentWindow()
    {
        // 1. Build window in temporal order: last windowSize samples.
        float[,] window = new float[windowSize, nChannels];
        int idx = _bufferIndex; // _bufferIndex points to "next write", so it's the oldest sample
        for (int t = 0; t < windowSize; t++)
        {
            for (int ch = 0; ch < nChannels; ch++)
            {
                window[t, ch] = _windowBuffer[idx, ch];
            }
            idx = (idx + 1) % windowSize;
        }

        // 2. Normalize: (x - mean) / (std + EPSILON)
        float[] inputData = new float[windowSize * nChannels];
        for (int t = 0; t < windowSize; t++)
        {
            for (int ch = 0; ch < nChannels; ch++)
            {
                float raw = window[t, ch];

                float mean = (channelMean != null && channelMean.Length > ch) ? channelMean[ch] : 0f;
                float std = (channelStd != null && channelStd.Length > ch) ? channelStd[ch] : 1f;

                float norm = (raw - mean) / (std + EPSILON);

                int index = t * nChannels + ch;
                inputData[index] = norm;
            }
        }

        // 3. Create Barracuda tensor: shape [1, windowSize, nChannels, 1]
        Tensor inputTensor = new Tensor(1, windowSize, nChannels, 1, inputData);

        // 4. Run inference
        _worker.Execute(inputTensor);
        Tensor outputTensor = _worker.PeekOutput();

        int numClasses = outputTensor.length;
        float[] probabilities = new float[numClasses];
        for (int i = 0; i < numClasses; i++)
        {
            probabilities[i] = outputTensor[i];
        }

        inputTensor.Dispose();
        outputTensor.Dispose();
        Debug.Log($"Probabilities: {probabilities}");

        // 5. Argmax
        int bestIndex = 0;
        float bestValue = probabilities[0];
        for (int i = 1; i < numClasses; i++)
        {
            if (probabilities[i] > bestValue)
            {
                bestValue = probabilities[i];
                bestIndex = i;
            }
        }

        gestureName = (gestureNames != null && gestureNames.Length > bestIndex)
            ? gestureNames[bestIndex]
            : $"Class {bestIndex}";

        // 6. Log result (you can hook this into movement / UI / etc.)
        Debug.Log($"[EMG] Predicted: {gestureName}");
    }

    public String GetGestureName()
    {
        return gestureName;
    }
}