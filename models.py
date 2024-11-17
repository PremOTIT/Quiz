# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize the database
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

    # Add the is_active column for Flask-Login compatibility
    is_active = db.Column(db.Boolean, default=True)  # True by default to allow login

    def __repr__(self):
        return f'<User {self.username}>'

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<QuizResult {self.id} - {self.score}/{self.total}>'
