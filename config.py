# config.py
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quizapp.db'  # Change this if you're using a different DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key_here'  # Change this to a real secret key