#!/bin/bash
# Activate virtual environment and start Flask app
source venv/bin/activate
python -m stormy.api.routes
