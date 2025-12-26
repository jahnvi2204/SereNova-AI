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
    
    def get_spotify_playlist_recommendations(self, mood: str) -> dict:
        """
        Get Spotify playlist recommendations based on mood using Gemini API.
        
        Args:
            mood: User's current mood (e.g., "anxious", "sad", "happy", "calm", "stressed")
        
        Returns:
            dict with playlists containing name, description, and spotify_url
        """
        if not self.api_key:
            return {
                "playlists": [],
                "error": "AI service is not configured"
            }
        
        system_instructions = (
            "You are a music therapy assistant. Based on the user's mood, recommend 3-5 Spotify playlists "
            "that would help improve their mental wellbeing. For each playlist, provide:\n"
            "1. A descriptive name\n"
            "2. A brief description (1-2 sentences) explaining why it helps with this mood\n"
            "3. A Spotify playlist URL (format: https://open.spotify.com/playlist/PLAYLIST_ID or search URL)\n\n"
            "Format your response as JSON with this structure:\n"
            "{\n"
            '  "playlists": [\n'
            '    {\n'
            '      "name": "Playlist Name",\n'
            '      "description": "Why this helps",\n'
            '      "spotify_url": "https://open.spotify.com/playlist/...",\n'
            '      "mood": "target mood"\n'
            '    }\n'
            '  ]\n'
            '}\n\n'
            "If you don't have a specific playlist URL, provide a Spotify search URL like: "
            "https://open.spotify.com/search/[mood]%20playlist\n"
            "Make sure all URLs are valid Spotify links."
        )
        
        prompt = (
            f"{system_instructions}\n\n"
            f"User's current mood: {mood}\n\n"
            "Provide Spotify playlist recommendations in JSON format:"
        )
        
        try:
            model = None
            try:
                model = genai.GenerativeModel(self.model_name)
            except Exception:
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                except Exception:
                    model = genai.GenerativeModel("gemini-pro-latest")
            
            if not model:
                raise Exception("Failed to initialize Gemini model")
            
            result = model.generate_content(prompt)
            text = (result.text or "").strip() if result else ""
            
            if not text:
                raise ValueError("Empty response from Gemini")
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group(0)
                try:
                    playlist_data = json.loads(json_str)
                    playlists = playlist_data.get("playlists", [])
                    
                    # Validate and clean playlists
                    valid_playlists = []
                    for playlist in playlists:
                        if isinstance(playlist, dict) and "name" in playlist:
                            valid_playlists.append({
                                "name": playlist.get("name", "Unknown Playlist"),
                                "description": playlist.get("description", ""),
                                "spotify_url": playlist.get("spotify_url", ""),
                                "mood": playlist.get("mood", mood)
                            })
                    
                    if valid_playlists:
                        logger.info("Successfully generated %d Spotify playlist recommendations for mood: %s", len(valid_playlists), mood)
                        return {
                            "playlists": valid_playlists,
                            "mood": mood
                        }
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse JSON from Gemini response: %s", e)
            
            # Fallback: return default playlists if JSON parsing fails
            logger.warning("Using fallback playlists for mood: %s", mood)
            return self._get_fallback_playlists(mood)
            
        except Exception as e:
            logger.error("Spotify playlist recommendation error: %s", e)
            return self._get_fallback_playlists(mood)
    
    def _get_fallback_playlists(self, mood: str) -> dict:
        """Fallback playlists if Gemini API fails."""
        mood_lower = mood.lower()
        
        # Default playlists based on common moods
        default_playlists = {
            "anxious": [
                {
                    "name": "Peaceful Piano",
                    "description": "Calming piano melodies to help reduce anxiety and promote relaxation",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO",
                    "mood": "calm"
                },
                {
                    "name": "Nature Sounds",
                    "description": "Soothing nature sounds to help you feel grounded and peaceful",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DWZd79rJ6a7lp",
                    "mood": "calm"
                },
                {
                    "name": "Meditation & Mindfulness",
                    "description": "Guided meditation and mindfulness music to help manage anxiety",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DWZqd5JICZI0u",
                    "mood": "calm"
                }
            ],
            "sad": [
                {
                    "name": "Feel Good Indie",
                    "description": "Upbeat indie songs to lift your spirits and bring positivity",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DX2sUQwD7tbmL",
                    "mood": "happy"
                },
                {
                    "name": "Happy Hits",
                    "description": "Energetic and joyful songs to help improve your mood",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLT6C0",
                    "mood": "happy"
                },
                {
                    "name": "Indie Pop",
                    "description": "Catchy indie pop tunes to bring light and energy",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DX2sUQwD7tbmL",
                    "mood": "happy"
                }
            ],
            "stressed": [
                {
                    "name": "Chill Lofi Study Beats",
                    "description": "Relaxing lo-fi beats to help you unwind and destress",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn",
                    "mood": "calm"
                },
                {
                    "name": "Deep Focus",
                    "description": "Instrumental music designed to help you focus and relax",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ",
                    "mood": "calm"
                },
                {
                    "name": "Sleep",
                    "description": "Gentle sounds to help you relax and release stress",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DWZd79rJ6a7lp",
                    "mood": "calm"
                }
            ],
            "happy": [
                {
                    "name": "Today's Top Hits",
                    "description": "Current chart-toppers to keep the good vibes going",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
                    "mood": "happy"
                },
                {
                    "name": "Pop Rising",
                    "description": "Up-and-coming pop songs to maintain your positive energy",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DXcF6B6QPhFDv",
                    "mood": "happy"
                }
            ],
            "calm": [
                {
                    "name": "Ambient Relaxation",
                    "description": "Soothing ambient sounds for deep relaxation",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO",
                    "mood": "calm"
                },
                {
                    "name": "Jazz for Sleep",
                    "description": "Smooth jazz to help you unwind and find peace",
                    "spotify_url": "https://open.spotify.com/playlist/37i9dQZF1DX6J5NfMJS675",
                    "mood": "calm"
                }
            ]
        }
        
        # Find matching playlists or use default
        if mood_lower in default_playlists:
            playlists = default_playlists[mood_lower]
        else:
            # Use calm playlists as default
            playlists = default_playlists.get("calm", default_playlists["anxious"])
        
        return {
            "playlists": playlists,
            "mood": mood
        }


# Global Gemini service instance
gemini_service = GeminiService()

