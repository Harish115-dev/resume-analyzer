from flask import Blueprint, request, jsonify
from flask import session
from auth.models import User


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    return jsonify({"message": "User registered successfully!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    # ... your login code ...
    return jsonify({"message": "Logged in successfully!"}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # ... your logout code ...
    return jsonify({"message": "Logged out successfully!"}), 200
