import logging
import google.generativeai as genai
from config import Config


logger = logging.getLogger(__name__)


class GeminiService:
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL_NAME
        self._configure()
    
    def _configure(self):
        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY is not set. AI responses will return a configuration error."
            )
        else:
            try:
                genai.configure(api_key=self.api_key)
                logger.info("Gemini configured with model '%s'", self.model_name)
            except Exception as e:
                logger.error("Failed to configure Gemini: %s", e)
    
    def generate_mental_health_response(self, user_input: str) -> dict:
       
        if not self.api_key:
            return {
                "intent": "configuration_error",
                "response": (
                    "The AI service is not configured yet. Please contact the system "
                    "administrator to set up the Gemini API key."
                ),
                "confidence": 0.0,
            }
        
        system_instructions = (
            "You are SeraNova, a compassionate, supportive mental health assistant. "
            "You provide empathetic, non-judgmental support, offer coping strategies, "
            "and encourage seeking professional help when appropriate. You are NOT a "
            "replacement for a doctor or therapist and you never give medical diagnoses. "
            "If the user mentions self-harm, suicide, or a crisis, respond with strong "
            "empathy and urge them to contact local emergency services or a trusted "
            "professional immediately. Keep responses concise and conversational. "
            "IMPORTANT: Use emojis naturally throughout your responses to make them more "
            "warm, friendly, and engaging. Use emojis like 💙 🫂 🌟 💚 🤗 🌸 ☀️ 💜 🎯 ✨ "
            "to express emotions and make the conversation feel more human and supportive."
        )
        
        prompt = (
            f"{system_instructions}\n\n"
            f"User message (about their mental and emotional wellbeing):\n"
            f"\"{user_input}\"\n\n"
            "Assistant response:"
        )
        
        try:
            # Try to use the configured model, fallback to gemini-2.5-flash if model not found
            model = None
            try:
                model = genai.GenerativeModel(self.model_name)
                logger.info("Using model: %s", self.model_name)
            except Exception as model_error:
                logger.warning("Model '%s' not available, falling back to 'gemini-2.5-flash': %s", self.model_name, model_error)
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    logger.info("Using fallback model: gemini-2.5-flash")
                except Exception as fallback_error:
                    logger.error("Fallback model also failed: %s", fallback_error)
                    # Try one more fallback
                    try:
                        model = genai.GenerativeModel("gemini-pro-latest")
                        logger.info("Using second fallback model: gemini-pro-latest")
                    except Exception as second_fallback_error:
                        logger.error("All fallback models failed: %s", second_fallback_error)
                        raise Exception(f"All models failed. Original: {model_error}, First fallback: {fallback_error}, Second fallback: {second_fallback_error}")
            
            if not model:
                raise Exception("Failed to initialize any Gemini model")
            
            result = model.generate_content(prompt)
            text = (result.text or "").strip() if result else ""
            
            if not text:
                raise ValueError("Empty response from Gemini")
            
            logger.info("Successfully generated response (length: %d)", len(text))
            return {
                "intent": "mental_health_support",
                "response": text,
                "confidence": 0.9,
            }
        except Exception as e:
            error_msg = str(e)
            logger.error("Gemini generation error: %s", error_msg)
            logger.error("Error type: %s", type(e).__name__)
            
            # Provide more helpful error messages
            if "API key" in error_msg or "authentication" in error_msg.lower():
                error_response = (
                    "The AI service authentication failed. Please contact the administrator. "
                    "If you are in crisis, contact local emergency services immediately."
                )
            elif "model" in error_msg.lower() or "not found" in error_msg.lower():
                error_response = (
                    "The AI model is not available. Please try again later. "
                    "If you are in crisis, contact local emergency services immediately."
                )
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                error_response = (
                    "The AI service quota has been exceeded. Please try again later. "
                    "If you are in crisis, contact local emergency services immediately."
                )
            else:
                error_response = (
                    f"I'm having trouble connecting to my AI service right now. "
                    f"Error: {error_msg[:100]}. Please try again later. "
                    "If you are in crisis, contact local emergency services or a trusted professional immediately."
                )
            
            return {
                "intent": "error",
                "response": error_response,
                "confidence": 0.0,
            }


# Global Gemini service instance
gemini_service = GeminiService()

