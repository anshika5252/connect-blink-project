import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# -----------------------
# LOAD DATA
# -----------------------
d0 = pd.read_csv("blink_data_0.csv", header=None)
d1 = pd.read_csv("blink_data_1.csv", header=None)
d2 = pd.read_csv("blink_data_2.csv", header=None)

data = pd.concat([d0, d1, d2], ignore_index=True)

X = data.iloc[:, :-1].values   # EAR sequences
y = data.iloc[:, -1].values   # labels

# -----------------------
# RESHAPE FOR LSTM
# -----------------------
X = X.reshape((X.shape[0], X.shape[1], 1))
y = to_categorical(y, num_classes=3)

# -----------------------
# TRAIN / TEST SPLIT
# -----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------
# BUILD MODEL
# -----------------------
model = Sequential([
    LSTM(64, input_shape=(X.shape[1], 1)),
    Dropout(0.3),
    Dense(32, activation="relu"),
    Dense(3, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# -----------------------
# TRAIN
# -----------------------
model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=16,
    validation_data=(X_test, y_test)
)

# -----------------------
# SAVE MODEL
# -----------------------
model.save("blink_lstm_model.keras")
print("Blink LSTM model saved.")
