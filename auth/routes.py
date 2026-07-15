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
    
    if not name or not email or not password:
        return render_template("register.html", error="All fields are required.")
    
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")
    if User.objects(email=email).first():
        return render_template("register.html", error="An account with that email already exists.")
    
    user = User(name=name, email=email)
    user.set_password(password)
    user.save()
    
    #auto login after registration

    session["user_id"] = str(user.id)
    session["user_name"] = user.name
    return redirect(url_for("analysis.index"))


#login route
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template("login.html")

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    
    generic_error="invalid email or password"
    
    if not email or not password:
        return render_template("login.html", error=generic_error)
    user = User.objects(email=email).first()
    if not user or not user.check_password(password):
        return render_template("login.html", error=generic_error)

    session["user_id"] = str(user.id)
    session["user_name"] = user.name

    return redirect(url_for("analysis.index"))



@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for("auth.login_page"))