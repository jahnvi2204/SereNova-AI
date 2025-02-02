from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import random
import json
import os
import logging

# Disable oneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf  # Keep this if you actually use TF ops

# Setup Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)

# File paths (match your existing files)
model_path = './data/chatbot_model.pkl'
vectorizer_path = './data/vectorizer.pkl'
le_path = './data/label_encoder.pkl'
intents_path = './data/intents.json'

try:
    # Load model
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file {model_path} not found")
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)

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

except Exception as e:
    logging.error(f"Error loading files: {e}")
    exit(1)

response_map = {intent['tag']: intent['responses'] for intent in data['intents']}

def get_response(intent):
    return random.choice(response_map.get(intent, ["I'm not sure how to respond."]))

def predict_intent(text):
    # Transform input using the vectorizer
    text_vec = vectorizer.transform([text])
    pred = model.predict(text_vec)
    return le.inverse_transform(pred)[0]

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the Chatbot API!'})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    intent = predict_intent(user_input)
    response = get_response(intent)
    return jsonify({'intent': intent, 'response': response})

if __name__ == '__main__':
    app.run(debug=True)