# rock_paper_scissors_emg.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib  # for saving model

# === 1. Load your EMG dataset ===
# Assume your CSV file has 4 EMG channels + label column
df = pd.read_csv("emg_signals.csv")

X = df.drop("label", axis=1).values
y = df["label"].values

# === 2. Normalize ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === 3. Split dataset ===
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# === 4. Train classifier ===
clf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
clf.fit(X_train, y_train)

# === 5. Evaluate ===
y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["Rest", "Rock", "Paper", "Scissors"]))

# === 6. Save model + scaler ===
joblib.dump(clf, "emg_rps_model.pkl")
joblib.dump(scaler, "emg_scaler.pkl")

print("Model and scaler saved successfully!")
