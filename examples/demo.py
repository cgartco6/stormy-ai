#!/usr/bin/env python3
from stormy.core.ai_engine import AIEngine

def main():
    engine = AIEngine()
    print("Stormy: Hey there! I'm Stormy. What's up?")
    while True:
        user = input("You: ")
        if user.lower() in ['exit', 'quit']:
            break
        response = engine.generate_response(user)
        print(f"Stormy: {response}")

if __name__ == '__main__':
    main()
