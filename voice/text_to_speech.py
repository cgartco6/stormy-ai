import pyttsx3
from config.settings import TTS_VOICE

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice.id == TTS_VOICE:
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 180)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
