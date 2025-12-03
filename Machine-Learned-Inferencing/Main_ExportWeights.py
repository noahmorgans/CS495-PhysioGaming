
import os
import numpy as np
import keras  

# Directory structure (same as in train_model.py)
BASE_DIR = "EMG Files"
MODEL_DIR = os.path.join(BASE_DIR, "Model Files")

# Model you saved in train_model.py
MODEL_FILENAME = "emg_cnn_model_4(new_electrode_placement).keras"
WEIGHTS_FILENAME = "emg_cnn_weights_4(new_electrode_placement).npz"

model_path = os.path.join(MODEL_DIR, MODEL_FILENAME)
weights_path = os.path.join(MODEL_DIR, WEIGHTS_FILENAME)

print("Loading trained Keras model from:")
print(" ", model_path)

model = keras.models.load_model(model_path)
model.summary()

# Get raw weights as a list of numpy arrays
weights = model.get_weights()
print(f"\nNumber of weight arrays: {len(weights)}")

# Save as a portable .npz
np.savez(weights_path, *weights)
print("\nSaved weights to:")
print(" ", weights_path)