import os
import numpy as np
import tensorflow as tf
import tf2onnx
import onnx

# Match original directory setup
BASE_DIR = "EMG Files"
MODEL_DIR = os.path.join(BASE_DIR, "Model Files")

# Files from training / export steps
WEIGHTS_FILENAME = "emg_cnn_weights_4(new_electrode_placement).npz"
ONNX_FILENAME    = "emg_cnn_model_4(new_electrode_placement).onnx"

# match training script
WINDOW_SIZE = 100  # from train_model.py: window_size = 100

weights_path = os.path.join(MODEL_DIR, WEIGHTS_FILENAME)
onnx_path    = os.path.join(MODEL_DIR, ONNX_FILENAME)

print("Loading weights from:")
print(" ", weights_path)
data = np.load(weights_path)

# Ensure consistent ordering of arrays: arr_0, arr_1, ...
keys_sorted = sorted(data.files, key=lambda k: int(k.split('_')[1]))
weights_list = [data[k] for k in keys_sorted]

print(f"Loaded {len(weights_list)} weight arrays.")

# Infer n_channels from first Conv1D kernel: shape = (kernel_size, in_channels, filters)
first_kernel = weights_list[0]
kernel_size, n_channels, n_filters = first_kernel.shape
print(f"Inferred from first Conv1D kernel: kernel_size={kernel_size}, n_channels={n_channels}, filters={n_filters}")

# Infer number of classes from final Dense bias: shape = (n_classes,)
last_bias = weights_list[-1]
n_classes = last_bias.shape[0]
print(f"Inferred number of classes from final bias: n_classes={n_classes}")


def build_cnn_model(input_shape, n_classes):
    """
    Rebuilds the same architecture as in train_model.py:

        Sequential([
            Conv1D(16, kernel_size=5, activation='relu', padding='same', input_shape=input_shape),
            BatchNormalization(),
            MaxPooling1D(pool_size=2),
            Dropout(0.2),

            Conv1D(32, kernel_size=3, activation='relu', padding='same'),
            BatchNormalization(),
            GlobalAveragePooling1D(),
            Dropout(0.4),

            Dense(16, activation='relu'),
            Dropout(0.5),
            Dense(n_classes, activation='softmax')
        ])
    """
    keras = tf.keras
    layers = keras.layers

    model = keras.Sequential([
        # Block 1
        layers.Conv1D(
            16,
            kernel_size=5,
            activation='relu',
            padding='same',
            input_shape=input_shape
        ),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.2),

        # Block 2
        layers.Conv1D(32, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling1D(),
        layers.Dropout(0.4),

        # Dense layers
        layers.Dense(16, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(n_classes, activation='softmax', name="output")
    ])

    return model


print("\nRebuilding CNN architecture...")
input_shape = (WINDOW_SIZE, n_channels)  # (time_steps, channels)
model = build_cnn_model(input_shape, n_classes)
model.summary()

print("\nSetting weights...")
model.set_weights(weights_list)
print("Weights loaded successfully.")

# ==== Convert to ONNX ====
print("\nConverting model to ONNX...")

input_signature = [
    tf.TensorSpec(
        shape=(None, WINDOW_SIZE, n_channels),
        dtype=tf.float32,
        name="emg",   # input name for Unity/Barracuda
    )
]

onnx_model, _ = tf2onnx.convert.from_keras(
    model,
    input_signature=input_signature,
    opset=11  # safe choice for Unity/Barracuda
)

onnx.save(onnx_model, onnx_path)
print("\nFinished exporting ONNX model to:")
print(" ", onnx_path)