import numpy as np
import cv2
from tensorflow import keras
import tensorflow as tf

# Load the trained CNN model
model = keras.models.load_model("HasPna_v2.keras")
class_labels = ['Neg', 'Pos']

# Prediction function
def analyse_xray(image_path):
    # Read and preprocess image
    image = cv2.imread(image_path)
    image = cv2.resize(image, (250, 250))  # match model input size
    image = np.array([image])  # add batch dimension

    # Make prediction
    logits = model.predict(image)[0]
    probs = tf.nn.softmax(logits).numpy()

    # Format the result
    result_text = (
        f"No pneumonia (Neg) certainty: {probs[0]:.4f}\n"
        f"Pneumonia (Pos) certainty: {probs[1]:.4f}\n"
    )

    if probs[0] > probs[1]:
        result_text += "Prediction: No signs of pneumonia."
    else:
        result_text += "Prediction: Signs of pneumonia detected."

    return result_text