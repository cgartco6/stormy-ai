FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for VLC, audio, etc.
RUN apt-get update && apt-get install -y \
    vlc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose API port
EXPOSE 5000

# Run the API server by default
CMD ["python", "-m", "stormy.api.routes"]
