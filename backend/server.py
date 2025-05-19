from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import random
import json
import os
import logging
import numpy as np

# Disable oneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf

# Setup Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

# File paths
model_path = './data/chatbot_model.h5'
vectorizer_path = './data/vectorizer_1.pkl'
le_path = './data/label_encoder_1.pkl'
intents_path = './data/intents.json'

try:
    # Load TensorFlow model
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")
    model = tf.keras.models.load_model(model_path)
    logging.info("TensorFlow model loaded successfully")

    # Load vectorizer
    if not os.path.exists(vectorizer_path):
        raise FileNotFoundError(f"Vectorizer file {vectorizer_path} not found")
    with open(vectorizer_path, 'rb') as vec_file:
        vectorizer = pickle.load(vec_file)

    # Load label encoder
    if not os.path.exists(le_path):
        raise FileNotFoundError(f"Label encoder file {le_path} not found")
    with open(le_path, 'rb') as le_file:
        le = pickle.load(le_file)

    # Load intents
    if not os.path.exists(intents_path):
        raise FileNotFoundError(f"Intents file {intents_path} not found")
    with open(intents_path, 'r') as f:
        data = json.load(f)
        
    # Extract responses for each intent
    if 'intents' in data:
        intents = data['intents']
    else:
        intents = data
        
    response_map = {intent['tag']: intent['responses'] for intent in intents}

except Exception as e:
    logging.error(f"Error loading files: {e}")
    exit(1)

def get_response(intent):
    return random.choice(response_map.get(intent, ["I'm not sure how to respond."]))

def predict_intent(text):
    # Transform input using the vectorizer
    text_vec = vectorizer.transform([text]).toarray()
    
    # Get prediction from TensorFlow model
    pred_probs = model.predict(text_vec)[0]
    pred_class = np.argmax(pred_probs)
    confidence = float(pred_probs[pred_class])
    
    # Convert numeric prediction to intent label
    intent = le.inverse_transform([pred_class])[0]
    
    return intent, confidence

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the TensorFlow Chatbot API!'})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    intent, confidence = predict_intent(user_input)
    response = get_response(intent)
    
    # Return both the intent and the confidence score
    return jsonify({
        'intent': intent, 
        'response': response,
        'confidence': confidence
    })

if __name__ == '__main__':
    app.run(debug=True)
