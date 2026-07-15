from functools import wraps

from flask import Blueprint, request, session, redirect, url_for, render_template, flash

from auth.models import User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated

#register route

@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template("register.html")



@auth_bp.route('/register', methods=['POST'])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")








    return jsonify({"message": "User registered successfully!"}), 201

#login route

@auth_bp.route('/login', methods=['POST'])
def login():
    # ... your login code ...
    return jsonify({"message": "Logged in successfully!"}), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # ... your logout code ...
    return jsonify({"message": "Logged out successfully!"}), 200
