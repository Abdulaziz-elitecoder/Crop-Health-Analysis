import numpy as np
import tensorflow as tf
from tensorflow import keras

class NaNHandler(tf.keras.layers.Layer):
    """Custom layer to handle NaN placeholder values"""
    def call(self, inputs):
        return tf.where(inputs == -2, 0.0, inputs)

def load_model(model_path='InceptionModel.keras'):
    """Load model with custom layers"""
    return keras.models.load_model(
        model_path,
        custom_objects={'NaNHandler': NaNHandler}
    )

def predict(model, data):
    """Make prediction with proper input shaping"""
    # Ensure correct input dimensions
    if data.ndim == 3:
        data = np.expand_dims(data, axis=0)
    
    # Handle potential NaN values
    data = np.nan_to_num(data, nan=-2)
    
    # Predict and return results
    probs = model.predict(data, verbose=0)
    class_idx = np.argmax(probs)
    confidence = float(probs[0][class_idx])
    return class_idx, confidence