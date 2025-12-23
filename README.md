**SereNova AI**

## Project Overview

This repository contains a Flask-based REST API that serves as a backend for a mental health chatbot. The chatbot uses a TensorFlow neural network model trained on various mental health-related intents to provide appropriate responses to user messages.

## Technical Architecture

### Core Components

1. **TensorFlow Neural Network Model**
   - Architecture: Feedforward neural network with 2 hidden layers
   - Input Layer: Matches the TF-IDF vector size (500 features)
   - Hidden Layers: 64 units (with 30% dropout) → 32 units (with 20% dropout)
   - Output Layer: Softmax activation matching the number of intent categories (82)
   - Optimizer: Adam optimizer with learning rate of 0.0005
   - Loss Function: Categorical cross-entropy
   - Training: Early stopping with patience of 10 epochs, reducing learning rate on plateau

2. **Text Processing Pipeline**
   - Vectorization: TF-IDF (Term Frequency-Inverse Document Frequency)
   - Features: 500 max features, unigrams and bigrams (1-2 word combinations)
   - Text Normalization: Sublinear TF scaling

3. **Backend API**
   - Framework: Flask with RESTful endpoint design
   - CORS: Enabled for cross-origin requests
   - Endpoint: `/predict` for intent classification and response generation

### Data Files

- `chatbot_model.h5`: TensorFlow model in HDF5 format
- `vectorizer.pkl`: Serialized TF-IDF vectorizer
- `label_encoder.pkl`: Serialized label encoder for intent mapping
- `intents.json`: JSON file containing intent patterns and responses
- `chatbot_model.pkl`: Backup pickled version of the model (for compatibility)

### Intent Structure

The model is trained on a diverse set of intents (82 categories) with the following distribution:
- Conversation starters (greeting, goodbye, thanks)
- Emotional states (sad, stressed, happy, anxious, etc.)
- Mental health facts
- Help requests and support responses
- Time-specific greetings (morning, afternoon, evening)

Each intent follows this JSON structure:
```json
{
  "tag": "intent_name",
  "patterns": ["Example user input 1", "Example user input 2"],
  "responses": ["Possible bot response 1", "Possible bot response 2"]
}
```

## Model Performance

- **Training Data**: 248+ patterns across 82 intent categories (augmented for categories with limited examples)
- **Vocabulary Size**: 267 features after TF-IDF processing
- **Accuracy**: Approximately 95-98% on the validation set
- **Response Generation**: Random selection from predefined responses for the predicted intent

## API Endpoints

### GET /
- **Description**: Home endpoint to verify API is running
- **Response**: `{"message": "Welcome to the TensorFlow Chatbot API!"}`

### POST /predict
- **Description**: Processes user message and returns appropriate response
- **Request Body**:
  ```json
  {
    "message": "User message here"
  }
  ```
- **Response**:
  ```json
  {
    "intent": "detected_intent",
    "response": "Bot response based on intent",
    "confidence": 0.95
  }
  ```

## Model Training Process

The model was trained using the following approach:

1. **Data Preparation**:
   - Collection of user message patterns for each intent
   - Organization into tag-based categories
   - Data augmentation for categories with limited examples

2. **Text Vectorization**:
   - Conversion of text patterns to numerical features using TF-IDF
   - Feature engineering with unigram and bigram extraction

3. **Model Training**:
   - Batch size of 8 for better generalization with limited data
   - Learning rate of 0.0005 with reduction on plateau
   - Early stopping to prevent overfitting
   - 90-10 train-test split

4. **Optimization**:
   - Dropout layers to prevent overfitting (30% and 20%)
   - Regularization through early stopping
   - Adaptive learning rate adjustment

## Installation and Deployment

### Prerequisites
- Python 3.7+
- TensorFlow 2.x
- Flask
- scikit-learn
- NLTK

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/mental-health-chatbot.git
   cd mental-health-chatbot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure all model files are in the `./data/` directory:
   - `chatbot_model.h5`
   - `vectorizer.pkl`
   - `label_encoder.pkl`
   - `intents.json`

4. Start the Flask server:
   ```
   python app.py
   ```

The server will be available at `http://localhost:5000`.

### Production Deployment Recommendations

For production deployment:

1. Use a production WSGI server like Gunicorn or uWSGI
2. Set `debug=False` in the Flask application
3. Implement proper error handling and logging
4. Add authentication for API endpoints
5. Consider containerizing the application with Docker
6. Set up HTTPS for secure communication

## Model Limitations and Considerations

1. **Limited Training Data**: The model performs best with patterns similar to its training data. Unusual phrasings may result in lower confidence predictions.

2. **Fixed Response Set**: The chatbot selects from predefined responses rather than generating new ones.

3. **No Conversation Memory**: The current implementation doesn't maintain conversation context between requests.

4. **Mental Health Context**: This chatbot is designed to provide supportive responses but is not a replacement for professional mental health services.

5. **Security Considerations**: The pickle files should be handled securely as they can potentially execute arbitrary code if tampered with.

## Future Improvements

1. **Enhanced Model Architecture**: Implement transformer-based models (BERT, RoBERTa) for better understanding of user intents

2. **Conversation Memory**: Add session management to maintain context across multiple messages

3. **Dynamic Response Generation**: Implement more sophisticated response generation rather than template-based responses

4. **Personalization**: Adapt responses based on user history and preferences

5. **Multi-language Support**: Expand the model to handle multiple languages

