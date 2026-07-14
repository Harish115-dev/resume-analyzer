import os
from flask import Flask, session, render_template, jsonify
from flask_wtf.csrf import CSRFProtect
from db.mongodb import db
from auth.routes import auth_bp
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["MONGODB_SETTINGS"] = {
        "host": os.environ.get("MONGO_URI", "mongodb://localhost:27017/resume_analyzer_db")
    }

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    
    
    is_debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")

    if not is_debug and not app.config["SECRET_KEY"]:
        raise ValueError("CRITICAL SECURITY ERROR: SECRET_KEY environment variable is missing!")

    app.config.update(
        SESSION_COOKIE_SECURE=not is_debug,      
        SESSION_COOKIE_HTTPONLY=True,    
        SESSION_COOKIE_SAMESITE='Lax',   
    )

    db.init_app(app)
    CSRFProtect(app) 


    app.register_blueprint(auth_bp, url_prefix='/auth')
    



    @app.route("/")
    def home():
        return jsonify({"status": "healthy", "service": "Resume Analyzer API"}), 200
    return app


if __name__ == "__main__":

    is_debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    app = create_app()
    app.run(debug=is_debug, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
