import requests
import json
import math
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config.settings import (
    WEATHER_API_KEY, GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ENGINE_ID,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER,
    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, RADIO_STATIONS,
    MUSIC_DIR
)

_music_cache = None

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "web_search": {
                "function": self.web_search,
                "description": "Search the web for current information. Use when you need up-to-date data or facts.",
                "parameters": {"query": "string - the search query"}
            },
            "calculator": {
                "function": self.calculator,
                "description": "Perform mathematical calculations. Use for arithmetic, algebra, etc.",
                "parameters": {"expression": "string - mathematical expression to evaluate (e.g., '2+2', 'sqrt(16)')"}
            },
            "weather": {
                "function": self.get_weather,
                "description": "Get current weather for a location.",
                "parameters": {"location": "string - city name or coordinates"}
            },
            "current_time": {
                "function": self.current_time,
                "description": "Get the current date and time.",
                "parameters": {}
            },
            "unit_converter": {
                "function": self.unit_converter,
                "description": "Convert between units (length, weight, temperature, etc.).",
                "parameters": {
                    "value": "number - the value to convert",
                    "from_unit": "string - unit to convert from (e.g., 'm', 'kg', 'C')",
                    "to_unit": "string - unit to convert to (e.g., 'ft', 'lb', 'F')"
                }
            },
            "make_phone_call": {
                "function": self.make_phone_call,
                "description": "Make a phone call to a given number. Stormy will speak the provided message.",
                "parameters": {
                    "to_number": "string - the phone number to call (E.164 format, e.g., +1234567890)",
                    "message": "string - the message to say during the call"
                }
            },
            "play_radio": {
                "function": self.play_radio,
                "description": "Play an internet radio station. If station name is given, find and play it.",
                "parameters": {
                    "station_name": "string - name of the radio station (e.g., 'Bok Radio FM98.8')"
                }
            },
            "play_music": {
                "function": self.play_music,
                "description": "Play music from Spotify (if configured) or a local file.",
                "parameters": {
                    "query": "string - song name, artist, or album to play"
                }
            },
            "play_local_music": {
                "function": self.play_local_music,
                "description": "Play music from your local music library. Can play a specific song, artist, album, or playlist.",
                "parameters": {
                    "query": "string - song name, artist, album, or playlist name"
                }
            }
        }

    def get_tool_descriptions(self):
        desc = "Available tools:\n"
        for name, info in self.tools.items():
            desc += f"- {name}: {info['description']}\n"
            if info.get('parameters'):
                desc += f"  Parameters: {json.dumps(info['parameters'])}\n"
        return desc

    def call_tool(self, tool_name, **kwargs):
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        try:
            result = self.tools[tool_name]["function"](**kwargs)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    # Web Search
    def web_search(self, query):
        if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
            return "Web search is not configured (missing API keys)."
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': GOOGLE_SEARCH_API_KEY,
            'cx': GOOGLE_SEARCH_ENGINE_ID,
            'num': 3
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if items:
                results = []
                for item in items:
                    results.append({
                        'title': item.get('title'),
                        'snippet': item.get('snippet'),
                        'link': item.get('link')
                    })
                return json.dumps(results)
            else:
                return "No results found."
        else:
            return f"Search failed with status {response.status_code}"

    # Calculator
    def calculator(self, expression):
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        allowed_names.update({"abs": abs, "round": round})
        try:
            code = compile(expression, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    return f"Error: Use of '{name}' is not allowed."
            result = eval(code, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Calculation error: {str(e)}"

    # Weather
    def get_weather(self, location):
        if not WEATHER_API_KEY:
            return "Weather service is not configured (missing API key)."
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            weather = {
                'location': data.get('name'),
                'country': data.get('sys', {}).get('country'),
                'description': data['weather'][0]['description'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
            return json.dumps(weather)
        else:
            return f"Weather lookup failed: {response.status_code}"

    # Current Time
    def current_time(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    # Unit Converter
    def unit_converter(self, value, from_unit, to_unit):
        try:
            value = float(value)
        except:
            return "Error: value must be a number."

        # Temperature
        temp_units = ['C', 'F', 'K']
        if from_unit in temp_units and to_unit in temp_units:
            if from_unit == 'F':
                celsius = (value - 32) * 5/9
            elif from_unit == 'K':
                celsius = value - 273.15
            else:
                celsius = value
            if to_unit == 'F':
                result = celsius * 9/5 + 32
            elif to_unit == 'K':
                result = celsius + 273.15
            else:
                result = celsius
            return f"{value} {from_unit} = {result:.4f} {to_unit}"

        # Length
        length_units = {
            'm':1, 'km':1000, 'cm':0.01, 'mm':0.001,
            'ft':0.3048, 'in':0.0254, 'mi':1609.34, 'yd':0.9144
        }
        if from_unit in length_units and to_unit in length_units:
            base = value * length_units[from_unit]
            result = base / length_units[to_unit]
            return f"{value} {from_unit} = {result:.4f} {to_unit}"

        # Weight
        weight_units = {
            'kg':1, 'g':0.001, 'mg':0.000001, 'lb':0.453592, 'oz':0.0283495
        }
        if from_unit in weight_units and to_unit in weight_units:
            base = value * weight_units[from_unit]
            result = base / weight_units[to_unit]
            return f"{value} {from_unit} = {result:.4f} {to_unit}"

        return f"Unsupported unit conversion: {from_unit} to {to_unit}"

    # Make Phone Call
    def make_phone_call(self, to_number, message):
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            return "Phone call service is not configured (missing Twilio credentials)."
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            response = VoiceResponse()
            response.say(message, voice='alice')
            call = client.calls.create(
                twiml=str(response),
                to=to_number,
                from_=TWILIO_PHONE_NUMBER
            )
            return f"Call initiated with SID: {call.sid}"
        except Exception as e:
            return f"Failed to make call: {str(e)}"

    # Play Radio
    def play_radio(self, station_name):
        stations = RADIO_STATIONS.get('stations', [])
        station = None
        for s in stations:
            if station_name.lower() in s['name'].lower():
                station = s
                break
        if not station:
            return f"Station '{station_name}' not found in database."

        stream_url = station['stream_url']
        try:
            if sys.platform == "win32":
                subprocess.Popen(['vlc', stream_url], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(['open', '-a', 'VLC', stream_url])
            else:
                subprocess.Popen(['vlc', stream_url])
            return f"Now playing {station['name']}."
        except FileNotFoundError:
            try:
                if sys.platform == "linux":
                    subprocess.Popen(['mpv', stream_url])
                elif sys.platform == "darwin":
                    subprocess.Popen(['afplay', stream_url])
                else:
                    return "VLC not found. Please install VLC to play radio."
            except:
                return "Could not play radio: audio player not available."
        except Exception as e:
            return f"Error playing radio: {str(e)}"

    # Play Music (Spotify)
    def play_music(self, query):
        if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET
                )
                sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                results = sp.search(q=query, type='track', limit=1)
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    track_url = track['external_urls']['spotify']
                    import webbrowser
                    webbrowser.open(track_url)
                    return f"Opening {track['name']} by {track['artists'][0]['name']} in Spotify."
                else:
                    return "No track found on Spotify."
            except Exception as e:
                return f"Spotify error: {str(e)}"
        else:
            return "Music playback via Spotify not configured. Please set Spotify API keys."

    # Play Local Music
    def play_local_music(self, query):
        global _music_cache
        if _music_cache is None:
            _music_cache = self._scan_music_library()

        if not _music_cache['songs'] and not _music_cache['playlists']:
            return "No music found in your library. Please add music to your MUSIC_DIR."

        query_lower = query.lower()
        # Check playlists
        for playlist in _music_cache['playlists']:
            if query_lower in playlist['name'].lower():
                return self._play_playlist(playlist)

        # Check artist
        artist_matches = []
        for song in _music_cache['songs']:
            if query_lower in song['artist'].lower():
                artist_matches.append(song)
        if artist_matches:
            return self._play_file(artist_matches[0]['path'], f"Playing {artist_matches[0]['title']} by {artist_matches[0]['artist']}")

        # Check album
        album_matches = {}
        for song in _music_cache['songs']:
            if query_lower in song['album'].lower():
                if song['album'] not in album_matches:
                    album_matches[song['album']] = []
                album_matches[song['album']].append(song)
        if album_matches:
            album_name = list(album_matches.keys())[0]
            songs = album_matches[album_name]
            return self._play_file(songs[0]['path'], f"Playing {songs[0]['title']} from album {album_name}")

        # Check song title
        for song in _music_cache['songs']:
            if query_lower in song['title'].lower():
                return self._play_file(song['path'], f"Playing {song['title']} by {song['artist']}")

        return f"Sorry, I couldn't find '{query}' in your music library."

    def _scan_music_library(self):
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.ogg', '.aac'}
        playlist_extensions = {'.m3u', '.m3u8', '.pls'}
        songs = []
        playlists = []
        music_path = Path(MUSIC_DIR)
        if not music_path.exists():
            return {'songs': [], 'playlists': []}
        for file_path in music_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in audio_extensions:
                    filename = file_path.stem
                    parts = filename.split(' - ', 1)
                    if len(parts) == 2:
                        artist, title = parts
                    else:
                        artist = "Unknown"
                        title = filename
                    songs.append({
                        'path': str(file_path),
                        'title': title,
                        'artist': artist,
                        'album': "Unknown",
                        'filename': filename
                    })
                elif ext in playlist_extensions:
                    playlists.append({
                        'path': str(file_path),
                        'name': file_path.stem
                    })
        return {'songs': songs, 'playlists': playlists}

    def _play_file(self, file_path, message):
        try:
            if sys.platform == "win32":
                subprocess.Popen(['vlc', file_path], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(['open', '-a', 'VLC', file_path])
            else:
                subprocess.Popen(['vlc', file_path])
            return message
        except FileNotFoundError:
            try:
                if sys.platform == "win32":
                    os.startfile(file_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(['open', file_path])
                else:
                    subprocess.Popen(['xdg-open', file_path])
                return message + " (using default player)"
            except:
                return "Could not play file: no suitable media player found."

    def _play_playlist(self, playlist):
        try:
            if sys.platform == "win32":
                subprocess.Popen(['vlc', playlist['path']], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(['open', '-a', 'VLC', playlist['path']])
            else:
                subprocess.Popen(['vlc', playlist['path']])
            return f"Now playing playlist: {playlist['name']}"
        except FileNotFoundError:
            return "VLC not found. Please install VLC to play playlists."
