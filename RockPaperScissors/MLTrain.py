import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib

# Load data
df = pd.read_csv("emg_signals5.csv")
window_size = 80  # ~400 ms at 200 Hz sampling rate
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
        # First convolutional block - capture high-level features
        layers.Conv1D(32, kernel_size=7, activation='relu', padding='same', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.Conv1D(64, kernel_size=5, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.25),
        
        # Second convolutional block - deeper feature extraction
        layers.Conv1D(128, kernel_size=5, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv1D(128, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.3),
        
        # Third convolutional block - fine-grained patterns
        layers.Conv1D(256, kernel_size=3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling1D(),
        layers.Dropout(0.4),
        
        # Dense layers with more capacity
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.4),
        layers.Dense(n_classes, activation='softmax')
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
model.save("emg_cnn_model5.keras")
joblib.dump(label_encoder, "emg_label_encoder5.pkl")
joblib.dump({
    'mean': X_mean, 
    'std': X_std,
    'window_size': window_size,
    'overlap': overlap
}, "emg_normalization5.pkl")

print("\n✅ Model training complete!")
print(f"Saved files:")
print(f"  - emg_cnn_model.keras")
print(f"  - emg_label_encoder.pkl")
print(f"  - emg_normalization.pkl")
print(f"\nLabel mapping: {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")