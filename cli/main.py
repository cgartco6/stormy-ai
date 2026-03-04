import argparse
import uuid
from stormy.core.ai_engine import AIEngine
from stormy.voice import SpeechToText, TextToSpeech

def main():
    parser = argparse.ArgumentParser(description="Stormy AI CLI")
    parser.add_argument('--voice', action='store_true', help="Enable voice mode")
    args = parser.parse_args()

    engine = AIEngine()
    stt = SpeechToText() if args.voice else None
    tts = TextToSpeech() if args.voice else None

    session_id = str(uuid.uuid4())

    print("Stormy AI (type 'exit' to quit)")
    while True:
        if args.voice:
            user_input = stt.listen()
            print(f"You said: {user_input}")
        else:
            user_input = input("You: ")

        if user_input.lower() in ['exit', 'quit']:
            break

        response = engine.generate_response(user_input, session_id=session_id)
        print(f"Stormy: {response}")

        if args.voice and tts:
            tts.speak(response)

if __name__ == '__main__':
    main()
