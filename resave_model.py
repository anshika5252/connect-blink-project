from tensorflow.keras.models import load_model

# Load legacy model (ignore compile)
model = load_model("blink_lstm_model.h5", compile=False)

# Save in new Keras format
model.save("blink_lstm_model.keras")

print("Model successfully resaved in new format.")
