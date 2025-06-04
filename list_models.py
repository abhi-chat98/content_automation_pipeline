import google.generativeai as genai

# Configure API key
GOOGLE_API_KEY = "your_api_key"
genai.configure(api_key=GOOGLE_API_KEY)

def list_models():
    try:
        models = genai.list_models()
        if not models:
            print("No models found.")
        for model in models:
            print(f"Model ID: {model.model_id}, Supported Methods: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
