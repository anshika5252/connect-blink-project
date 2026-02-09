# ===============================
# TRAINING SCRIPT FOR EYE STATE
# ===============================

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# -------------------------------
# 1. LOAD DATA
# -------------------------------

# Load CSV files (no header in your data)
data_open = pd.read_csv("training_data_class_0.csv", header=None)
data_closed = pd.read_csv("training_data_class_1.csv", header=None)

# Combine both classes
data = pd.concat([data_open, data_closed], ignore_index=True)

print("Total samples:", len(data))

# -------------------------------
# 2. SPLIT FEATURES & LABELS
# -------------------------------

# First 30 columns → EAR sequence
X = data.iloc[:, 0:30]

# Last column → label
y = data.iloc[:, 30]

print("Feature shape:", X.shape)
print("Label shape:", y.shape)

# -------------------------------
# 3. TRAIN–TEST SPLIT
# -------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -------------------------------
# 4. CREATE & TRAIN MODEL
# -------------------------------

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

print("Training completed.")

# -------------------------------
# 5. EVALUATE MODEL
# -------------------------------

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("\nAccuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------------------------------
# 6. SAVE MODEL
# -------------------------------

joblib.dump(model, "eye_state_model.pkl")

print("\nModel saved as eye_state_model.pkl")
