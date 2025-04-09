from flask import Flask
from flask_cors import CORS
from routes import api
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api)
    return app
    
app = create_app()

# For local development
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host='0.0.0.0', port=port)