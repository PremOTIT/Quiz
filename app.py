from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate  # Import Migrate for database migrations
import requests

# Import the db object, User, and QuizResult from models.py
from models import db, User, QuizResult

# Flask app setup
app = Flask(__name__)
app.config.from_object('config.Config')  # Assuming you have a Config class for app config

# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate for migrations
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load user from session for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])  # Corrected to use default method (PBKDF2)

        # Check if the username or email already exists in the database
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for('register'))

        # Add new user to the database
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Check your credentials and try again.", "danger")
    return render_template('login.html')

# Dashboard route (after login)
@app.route('/dashboard')
@login_required
def dashboard():
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', results=results)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Fetch quiz questions (using the StackExchange API)
def fetch_stackexchange_questions(tag=None, num_questions=10):
    API_URL = "https://api.stackexchange.com/2.3/questions"
    params = {
        'site': 'stackoverflow',
        'order': 'desc',
        'sort': 'activity',
        'tagged': tag if tag else 'programming',
        'pagesize': num_questions,
        'filter': '!9_bDDxJY5'  # Filter to get only relevant fields
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    return data.get('items', [])

# Quiz route
@app.route('/quiz', methods=['GET'])
@login_required
def quiz():
    tag = request.args.get('tag', 'programming')
    num_questions = int(request.args.get('num_questions', 10))

    questions = fetch_stackexchange_questions(tag, num_questions)

    if not questions:
        flash("Sorry, no questions found. Please try again later.", "danger")
        return redirect(url_for('index'))

    return render_template('quiz.html', questions=questions)

# Submit quiz and store results
@app.route('/submit', methods=['POST'])
@login_required
def submit():
    answers = request.json['answers']
    correct_answers = 0
    total_questions = len(answers)

    # Here we can implement actual answer checking logic, for now, let's assume all answers are correct.
    correct_answers = total_questions  # Simulated correctness

    # Store the result in the database
    quiz_result = QuizResult(score=correct_answers, total=total_questions, user_id=current_user.id)
    db.session.add(quiz_result)
    db.session.commit()

    return jsonify({'score': correct_answers, 'total': total_questions})

if __name__ == '__main__':
    app.run(debug=True)
