import os
from google import genai


from dotenv import load_dotenv

# Load variables from the .env file into the system environment
load_dotenv()


def main():
    # 1. Initialize the client (automatically reads GEMINI_API_KEY from environment)
    client = genai.Client()

    print("--- Simple GenAI App (Gemini 3.6 Flash) [Type 'quit' to exit] ---")

    while True:
        user_prompt = input("\nYou: ")
        if user_prompt.lower() == 'quit':
            print("Exiting...")
            break
            
        if not user_prompt.strip():
            continue

        print("\nGemini: ", end="", flush=True)

        try:
            # 2. Update the model ID to 'gemini-3.6-flash'
            response = client.models.generate_content_stream(
                model='gemini-3.6-flash',
                contents=user_prompt
            )
            
            for chunk in response:
                print(chunk.text, end="", flush=True)
            print() 
            
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not found.")
    else:
        main()
