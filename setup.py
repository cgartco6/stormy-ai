from setuptools import setup, find_packages

setup(
    name="stormy-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "pyyaml>=6.0",
        "SpeechRecognition>=3.10.0",
        "pyttsx3>=2.90",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
        "twilio>=8.0.0",
        "chromadb>=0.4.0",
        "python-vlc>=3.0.0",
        "spotipy>=2.23.0",
        "ipinfo>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "stormy=stormy.cli.main:main",
        ],
    },
    author="Your Name",
    description="Stormy AI - An advanced AI assistant with attitude",
    license="MIT",
)
