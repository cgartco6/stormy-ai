import speech_recognition as sr
from config.settings import STT_ENERGY_THRESHOLD

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = STT_ENERGY_THRESHOLD

    def listen(self, timeout=5):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source, timeout=timeout)
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Speech recognition service unavailable."
