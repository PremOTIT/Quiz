from app import app, db, User  # Import app, db, and User from your main app

# Make sure to push the application context before interacting with the database
with app.app_context():
    user = User.query.first()  # Get the first user in the database
    print(user)  # Print the user object or inspect it