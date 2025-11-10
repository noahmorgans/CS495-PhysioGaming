import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib
import os

# Define directory structure (same as above)
BASE_DIR = "EMG Files"
SIGNAL_DIR = os.path.join(BASE_DIR, "Signal Files")
MODEL_DIR = os.path.join(BASE_DIR, "Model Files")
ENCODER_DIR = os.path.join(BASE_DIR, "Encoder Files")
NORM_DIR = os.path.join(BASE_DIR, "Normalization Files")
TEMPLATE_DIR = os.path.join(BASE_DIR, "Templates")


# Create output directories
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(ENCODER_DIR, exist_ok=True)
os.makedirs(NORM_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Load data from signal directory
df = pd.read_csv(os.path.join(SIGNAL_DIR, "emg_signals_3(all_group_members).csv"))
window_size = 100  # ~400 ms at 200 Hz sampling rate
overlap = int(window_size * 0.25)  # 25% overlap

# Extract raw windows (no feature extraction needed for CNN)
X_windows = []
y_labels = []


for gesture in sorted(df['label'].unique()):
    subset = df[df['label'] == gesture].drop(['label', 'trial', 'timestamp'], axis=1, errors='ignore').values
    for i in range(0, len(subset) - window_size, overlap):
        window = subset[i:i+window_size, :]  # Shape: (samples, channels)
        X_windows.append(window)
        y_labels.append(gesture)

X_windows = np.array(X_windows)
y_labels = np.array(y_labels)

print(f"Total windows: {len(X_windows)}")
print(f"Window shape: {X_windows[0].shape}")
print(f"Label distribution: {np.unique(y_labels, return_counts=True)}")

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y_labels)
n_classes = len(label_encoder.classes_)

print(f"\nClasses: {label_encoder.classes_}")
print(f"Number of classes: {n_classes}")

# Normalize data (per channel)
X_mean = np.mean(X_windows, axis=(0, 1), keepdims=True)
X_std = np.std(X_windows, axis=(0, 1), keepdims=True)
X_normalized = (X_windows - X_mean) / (X_std + 1e-8)

#========================================================================================================
propulsion_mask = (y_labels == "propulsion")   # adjust label string if needed
rest_mask       = (y_labels == "rest")

propulsion_data = X_normalized[propulsion_mask]   # shape: (N_propulsion, window_size, channels)
rest_data       = X_normalized[rest_mask]         # shape: (N_rest, window_size, channels)

propulsion_template = propulsion_data.mean(axis=0)   # shape: (window_size, channels)
rest_template       = rest_data.mean(axis=0)
#==========================================================================================================

# Split data with larger test set for better evaluation
X_train, X_test, y_train, y_test = train_test_split(
    X_normalized, y_encoded, test_size=0.25, random_state=42, stratify=y_encoded
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# Convert labels to categorical
y_train_cat = keras.utils.to_categorical(y_train, n_classes)
y_test_cat = keras.utils.to_categorical(y_test, n_classes)

# Build CNN model with improved architecture
def build_cnn_model(input_shape, n_classes):
    model = keras.Sequential([
        # Block 1
        layers.Conv1D(16, kernel_size=5, activation='relu', padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.2),

        # Block 2
        layers.Conv1D(32, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling1D(),
        layers.Dropout(0.4),
        
        # Single dense layer
        layers.Dense(16, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(2, activation='softmax')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Create model
input_shape = (window_size, X_train.shape[2])  # (samples, channels)
model = build_cnn_model(input_shape, n_classes)

print("\nModel Architecture:")
model.summary()

# Training callbacks with data augmentation considerations
early_stopping = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=20,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=7,
    min_lr=1e-7,
    verbose=1
)

# Train model with data augmentation via random noise
print("\nStarting training with augmentation...")

# Create augmented training data by adding small random noise
def augment_data(X, y, noise_factor=0.05):
    """Add Gaussian noise to training data for augmentation"""
    X_aug = X + np.random.normal(0, noise_factor, X.shape)
    return np.vstack([X, X_aug]), np.hstack([y, y])

X_train_aug, y_train_aug = augment_data(X_train, y_train)
y_train_aug_cat = keras.utils.to_categorical(y_train_aug, n_classes)

print(f"Training samples after augmentation: {len(X_train_aug)}")

history = model.fit(
    X_train_aug, y_train_aug_cat,
    validation_data=(X_test, y_test_cat),
    epochs=150,
    batch_size=32,
    callbacks=[early_stopping, reduce_lr],
    verbose=1
)

# Evaluate model
test_loss, test_accuracy = model.evaluate(X_test, y_test_cat, verbose=0)
print(f"\nTest accuracy: {test_accuracy:.4f}")
print(f"Test loss: {test_loss:.4f}")

# Save model and preprocessing parameters
model.save(os.path.join(MODEL_DIR, "emg_cnn_model_3(TEMPLATES_TEST).keras"))
joblib.dump(label_encoder, os.path.join(ENCODER_DIR, "emg_label_encoder_3(TEMPLATES_TEST).pkl"))
joblib.dump({
    'mean': X_mean, 
    'std': X_std,
    'window_size': window_size,
    'overlap': overlap
}, os.path.join(NORM_DIR, "emg_normalization_3(TEMPLATES_TEST).pkl"))
np.save(os.path.join(TEMPLATE_DIR, "propulsion_template(TEMPLATES_TEST).npy"), propulsion_template)
np.save(os.path.join(TEMPLATE_DIR, "rest_template(TEMPLATES_TEST).npy"), rest_template)

print("\n Model training complete!")
print(f"Saved files:")
print(f"  - emg_cnn_model.keras")
print(f"  - emg_label_encoder.pkl")
print(f"  - emg_normalization.pkl")
print(f"\nLabel mapping: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")