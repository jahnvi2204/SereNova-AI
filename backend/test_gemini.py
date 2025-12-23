"""Test script to verify Gemini API connection."""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

print("=" * 50)
print("Testing Gemini API Connection")
print("=" * 50)
print(f"API Key: {'SET' if api_key else 'NOT SET'}")
print(f"Model: {model_name}")
print()

if not api_key:
    print("[ERROR] GEMINI_API_KEY is not set in .env file")
    exit(1)

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    print("[OK] Gemini API configured successfully")
    
    # Try to list available models
    print("\n[INFO] Fetching available models...")
    try:
        models = genai.list_models()
        model_list = list(models)
        print(f"[OK] Found {len(model_list)} available models")
        print("\nAvailable models:")
        for model in model_list:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
    except Exception as e:
        print(f"[WARN] Could not list models: {e}")
    
    # Try to use the model
    print(f"\n[TEST] Testing model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        print(f"[OK] Model '{model_name}' initialized successfully")
        
        # Test generation
        print("\n[TEST] Testing content generation...")
        test_prompt = "Say hello in one sentence."
        result = model.generate_content(test_prompt)
        
        if result and result.text:
            print(f"[OK] Generation successful!")
            print(f"Response: {result.text[:100]}...")
        else:
            print("[ERROR] Generation returned empty response")
            
    except Exception as model_error:
        print(f"[ERROR] Model error: {model_error}")
        
        # Try fallback
        print("\n[FALLBACK] Trying fallback model: gemini-2.5-flash")
        try:
            fallback_model = genai.GenerativeModel("gemini-2.5-flash")
            result = fallback_model.generate_content("Say hello.")
            if result and result.text:
                print(f"[OK] Fallback model works! Response: {result.text[:50]}...")
            else:
                print("[ERROR] Fallback model returned empty response")
        except Exception as fallback_error:
            print(f"[ERROR] Fallback model also failed: {fallback_error}")
            # Try second fallback
            print("\n[FALLBACK2] Trying second fallback: gemini-pro-latest")
            try:
                fallback2_model = genai.GenerativeModel("gemini-pro-latest")
                result = fallback2_model.generate_content("Say hello.")
                if result and result.text:
                    print(f"[OK] Second fallback works! Response: {result.text[:50]}...")
                else:
                    print("[ERROR] Second fallback returned empty response")
            except Exception as fallback2_error:
                print(f"[ERROR] Second fallback also failed: {fallback2_error}")
    
except Exception as e:
    print(f"[ERROR] Configuration error: {e}")
    print(f"Error type: {type(e).__name__}")

print("\n" + "=" * 50)

