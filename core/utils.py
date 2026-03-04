import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level
    )

def clean_text(text):
    return text.strip()
