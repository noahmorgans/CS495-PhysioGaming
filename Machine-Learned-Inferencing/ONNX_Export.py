import os
import tensorflow as tf
import tf2onnx
import onnx

BASE_DIR = "EMG Files"
MODEL_DIR  = os.path.join(BASE_DIR, "Model Files")
ONNX_NAME  = "emg_cnn_model.onnx"

window_size   = 50          # same as in training
n_channels    = 1           # or however many you actually used

# 1. Load trained Keras model
keras_model = tf.keras.models.load_model(
    os.path.join(MODEL_DIR, "emg_cnn_model_3(all_group_members)_(50_window_size).keras")
)

# 2. Define input signature: (batch, time, channels)
input_signature = [
    tf.TensorSpec(
        shape=(None, window_size, n_channels),  # None = any batch size
        dtype=tf.float32,
        name="emg"
    )
]

# 3. Convert to ONNX
onnx_model, _ = tf2onnx.convert.from_keras(
    keras_model,
    input_signature=input_signature,
    opset=11
)

onnx_path = os.path.join(MODEL_DIR, "emg_cnn_model.onnx")
onnx.save(onnx_model, onnx_path)
print("Finished exporting...")
