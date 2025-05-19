# Chatbot TensorFlow Model Training for Colab
# Updated to match your specific intents.json structure

# Install necessary packages
!pip install nltk scikit-learn tensorflow -q

import numpy as np
import json
import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.stem import WordNetLemmatizer
import random
import os
from google.colab import files

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)  # Open Multilingual WordNet

print("Loading your existing intents.json file...")

# Load your existing intents file
try:
    with open('intents.json', 'r') as f:
        intents_data = json.load(f)
    print("Successfully loaded your intents.json file.")
    
    # Check if the file structure matches the expected format
    if 'intents' in intents_data:
        intents = intents_data['intents']
    else:
        # If the file is already a list of intents
        intents = intents_data
        
except FileNotFoundError:
    print("Could not find intents.json in the current directory.")
    print("Please make sure your intents.json file is in the Colab file system.")
    raise
except json.JSONDecodeError:
    print("Error decoding the intents.json file. Please check that it's valid JSON.")
    raise

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

print("Preprocessing your intent data...")

# Preprocess training data
training_sentences = []
training_labels = []
labels = []
responses = {}

# Extract data from intents file
for intent in intents:
    if 'tag' not in intent or 'patterns' not in intent or 'responses' not in intent:
        print(f"Warning: Intent is missing required fields: {intent}")
        continue
        
    tag = intent['tag']
    patterns = intent['patterns']
    
    for pattern in patterns:
        if pattern.strip():  # Only add non-empty patterns
            training_sentences.append(pattern)
            training_labels.append(tag)
    
    responses[tag] = intent['responses']
    
    if tag not in labels:
        labels.append(tag)

print(f"Extracted {len(training_sentences)} training sentences with {len(labels)} unique intent labels.")

# Count samples per intent
intent_counts = {}
for label in labels:
    count = training_labels.count(label)
    intent_counts[label] = count
    print(f"  - '{label}': {count} patterns, {len(responses[label])} responses")

# Augment data for intents with only 1 example
augmented_sentences = []
augmented_labels = []

for i, (sentence, label) in enumerate(zip(training_sentences, training_labels)):
    if intent_counts[label] < 2:
        # Create variations by adding punctuation or small changes
        variations = [
            sentence + "?",
            sentence + ".",
            "Please " + sentence.lower(),
            "Can you " + sentence.lower(),
            "I want to " + sentence.lower()
        ]
        for variation in variations[:3]:  # Add just 3 variations
            augmented_sentences.append(variation)
            augmented_labels.append(label)
        
        print(f"Augmented data for intent '{label}' with 3 variations of: '{sentence}'")

# Add augmented data to training data
training_sentences.extend(augmented_sentences)
training_labels.extend(augmented_labels)

print(f"After augmentation: {len(training_sentences)} training sentences")

# Encode the labels
le = LabelEncoder()
le.fit(training_labels)
training_labels_encoded = le.transform(training_labels)

print("\nCreating TF-IDF vectorizer...")
# Create tf-idf vectorizer with adjusted parameters
vectorizer = TfidfVectorizer(
    max_features=500,     # Reduced features to prevent overfitting
    sublinear_tf=True,    # Apply sublinear tf scaling
    ngram_range=(1, 2),   # Include both unigrams and bigrams
    min_df=1              # Include terms that appear in at least 1 document
)

# Create training data
X = vectorizer.fit_transform(training_sentences)
y = tf.keras.utils.to_categorical(training_labels_encoded, num_classes=len(labels))

print(f"Training data shape: {X.shape}")
print(f"Training labels shape: {y.shape}")
print(f"Number of features (vocabulary size): {X.shape[1]}")

# Use a simple train/test split
from sklearn.model_selection import train_test_split

# Simple random split with small test size
X_train, X_test, y_train, y_test = train_test_split(
    X.toarray(), y, test_size=0.1, random_state=42, shuffle=True
)

print("\nBuilding TensorFlow model...")

# Define a simpler model architecture for small dataset
model = Sequential([
    Dense(64, input_shape=(X.shape[1],), activation='relu'),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.2),
    Dense(len(labels), activation='softmax')
])

# Compile model with a lower learning rate
model.compile(
    loss='categorical_crossentropy',
    optimizer=Adam(learning_rate=0.0005),
    metrics=['accuracy']
)

# Print model summary
model.summary()

# Define callbacks with increased patience for small dataset
callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.4,
        patience=3
    )
]

print("\nTraining model...")
# Train the model with more epochs but early stopping
history = model.fit(
    X_train, y_train,
    epochs=200,           # More epochs for small dataset
    batch_size=8,         # Very small batch size for better generalization
    validation_data=(X_test, y_test),
    callbacks=callbacks,
    verbose=1
)

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"\nTest accuracy: {accuracy*100:.2f}%")

print("\nSaving model and required files...")

# Save the TensorFlow model
model.save('chatbot_model.h5')
print("✓ TensorFlow model saved as 'chatbot_model.h5'")

# Save the vectorizer using pickle
with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
print("✓ Vectorizer saved as 'vectorizer.pkl'")

# Save the label encoder using pickle
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)
print("✓ Label encoder saved as 'label_encoder.pkl'")

# Save the original intents data in pickle format
with open('intents.pkl', 'wb') as f:
    pickle.dump(intents_data, f)
print("✓ Intents data saved as 'intents.pkl'")

# Create a model for pickle format (simplified version)
try:
    # Create a simple model wrapper for pickle compatibility
    class SimpleModel:
        def __init__(self, model):
            self.model = model
            
        def predict(self, X):
            return self.model.predict(X)
    
    simple_model = SimpleModel(model)
    
    # Save in pickle format
    with open('chatbot_model.pkl', 'wb') as f:
        pickle.dump(simple_model, f)
    print("✓ Simplified model saved in pickle format as 'chatbot_model.pkl'")
except Exception as e:
    print(f"⚠️ Could not save pickle version of model: {e}")
    print("  This is not critical - you can still use the TensorFlow .h5 model.")

print("\nTesting model with examples from your intents...")

# Test the model with a few examples
def predict_intent(text):
    # Transform the text using the vectorizer
    text_vector = vectorizer.transform([text]).toarray()
    
    # Get prediction from model
    pred = model.predict(text_vector)[0]
    pred_class = np.argmax(pred)
    pred_intent = le.inverse_transform([pred_class])[0]
    confidence = float(pred[pred_class])
    
    return pred_intent, confidence, pred

# Test with examples from your intents
print("\nTesting with samples from your training data:")
test_samples = []

# Select intents with more than 1 pattern for testing
for intent in intents:
    if len(intent.get('patterns', [])) >= 2:
        # Take first pattern from each such intent
        test_samples.append((intent['patterns'][0], intent['tag']))
        
        # If we have 10 samples, stop adding more
        if len(test_samples) >= 10:
            break

# If we have fewer than 5 test samples, add some more from any intent
if len(test_samples) < 5:
    for intent in intents:
        if len(intent.get('patterns', [])) > 0 and intent['tag'] not in [tag for _, tag in test_samples]:
            test_samples.append((intent['patterns'][0], intent['tag']))
            if len(test_samples) >= 5:
                break

# If still not enough samples, create some custom test inputs
if len(test_samples) < 5:
    # Add some common greetings or phrases as test samples
    common_inputs = [
        "Hello there",
        "How are you today?",
        "Thank you for your help",
        "Goodbye"
    ]
    for input_text in common_inputs:
        intent, confidence, _ = predict_intent(input_text)
        test_samples.append((input_text, None))  # No expected intent for these

# Display test results
for sample_text, expected_intent in test_samples:
    intent, confidence, probabilities = predict_intent(sample_text)
    
    if expected_intent:
        match = "✓" if intent == expected_intent else "✗"
        print(f"{match} Input: '{sample_text}'")
        print(f"  Expected: '{expected_intent}', Predicted: '{intent}' with confidence: {confidence:.4f}")
    else:
        print(f"Input: '{sample_text}'")
        print(f"  Predicted: '{intent}' with confidence: {confidence:.4f}")
    
    # Show top 3 predictions
    top3_indices = np.argsort(probabilities)[-3:][::-1]
    print("  Top 3 predictions:")
    for idx in top3_indices:
        pred_tag = le.inverse_transform([idx])[0]
        pred_conf = float(probabilities[idx])
        print(f"    - {pred_tag}: {pred_conf:.4f}")
    
    print("-" * 50)

# Download all the files
print("\nPreparing files for download...")
files.download('chatbot_model.h5')
files.download('vectorizer.pkl')
files.download('label_encoder.pkl')
files.download('chatbot_model.pkl')
files.download('intents.pkl')

print("\nDownload complete! Now updating your Flask application to use these files:")
print("""
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
vectorizer_path = './data/vectorizer.pkl'
le_path = './data/label_encoder.pkl'
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
""")

print("\nMake sure to place all the downloaded files in your './data/' directory!")