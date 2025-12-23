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
            "professional immediately. Keep responses concise and conversational."
        )
        
        prompt = (
            f"{system_instructions}\n\n"
            f"User message (about their mental and emotional wellbeing):\n"
            f"\"{user_input}\"\n\n"
            "Assistant response:"
        )
        
        try:
            model = genai.GenerativeModel(self.model_name)
            result = model.generate_content(prompt)
            text = (result.text or "").strip() if result else ""
            
            if not text:
                raise ValueError("Empty response from Gemini")
            
            return {
                "intent": "mental_health_support",
                "response": text,
                "confidence": 0.9,
            }
        except Exception as e:
            logger.error("Gemini generation error: %s", e)
            return {
                "intent": "error",
                "response": (
                    "I'm having trouble connecting to my AI service right now. "
                    "Please try again later, and if you are in crisis, contact "
                    "local emergency services or a trusted professional immediately."
                ),
                "confidence": 0.0,
            }


# Global Gemini service instance
gemini_service = GeminiService()

