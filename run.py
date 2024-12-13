import os
from app import create_app

# Set Flask environment variables
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_DEBUG"] = "1"

app = create_app()

if __name__ == "__main__":
    # Explicitly run the app if needed for debugging, but `flask run` will pick up this configuration.
    app.run(debug=True)
