# Stormy AI

Stormy is an advanced AI assistant with a bold, unfiltered personality. She can be cocky, flirty, mean, funny, and even make phone calls, play music, remember everything, and adapt to your mood and location.

## Mobile-First Design

Stormy now features a beautiful, responsive web interface that works perfectly on phones, tablets, and desktops. Just run the server and open the URL in any browser.

## One-Click Installers

We provide automated installers for all major operating systems:

- **Windows**: Double-click `install_windows.bat`
- **macOS**: Run `./install_macos.sh` in Terminal
- **Linux**: Run `./install_linux.sh`

These scripts will:
1. Check for Python 3.8+
2. Create a virtual environment
3. Install all dependencies
4. Set up a `.env` file (you'll need to add your API keys)
5. Guide you to start the web server

After installation, run `./run_web.sh` (or `run_web.bat` on Windows) and visit `http://localhost:5000`.

## Docker

```bash
docker-compose up
