# freeze.py
from flask_frozen import Freezer
from stormy.api.routes import app

app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = 'build'
freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()
    print("Static site generated in ./build")
