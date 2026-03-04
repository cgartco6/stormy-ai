import os
import yaml
import json

# Load personality config
with open(os.path.join(os.path.dirname(__file__), 'personality.yaml'), 'r') as f:
    PERSONALITY_CONFIG = yaml.safe_load(f)

# Load radio stations
with open(os.path.join(os.path.dirname(__file__), 'radio_stations.json'), 'r') as f:
    RADIO_STATIONS = json.load(f)

# API Keys (set as environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")

# Model selection
USE_OPENAI = True
OPENAI_MODEL = "gpt-4"
LOCAL_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"

# Voice settings
TTS_VOICE = "com.apple.speech.synthesis.voice.samantha"  # macOS example
STT_ENERGY_THRESHOLD = 300

# Agent settings
ENABLE_AGENTS = True
MAX_AGENT_DEPTH = 3

# Tool settings
ENABLE_TOOLS = True
TOOLS = [
    "web_search", "calculator", "weather", "current_time",
    "unit_converter", "make_phone_call", "play_radio",
    "play_music", "play_local_music"
]

# Memory settings
MEMORY_DIR = os.getenv("MEMORY_DIR", "./memory_store")
ENABLE_MEMORY = True

# Location settings
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "New York")

# Music settings
MUSIC_DIR = os.getenv("MUSIC_DIR", os.path.expanduser("~/Music"))
