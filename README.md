# DETYS

Here’s a basic step-by-step README for running your Flask application from scratch:

DETYS Project

This is a Flask-based project for managing users, clubs, events, notifications, and reports. Follow the steps below to set up and run the application.

Prerequisites

    •	Python 3.7+ installed on your system.
    •	Virtual Environment setup (recommended).
    •	SQLite (default database for testing).
    •	Git (optional, for version control).

Getting Started

Step 1: Clone the Repository

Clone this repository to your local machine (if using Git):

git clone https://github.com/your-username/detys.git
cd detys

Step 2: Set Up the Virtual Environment

Create and activate a virtual environment. This will help manage dependencies.

# Create the virtual environment (name it "venv" or another name of your choice)

python -m venv venv

# Activate the virtual environment

# On macOS/Linux:

source venv/bin/activate

# On Windows:

venv\Scripts\activate

Step 3: Install Dependencies

Install the necessary packages listed in requirements.txt.

pip install -r requirements.txt

Step 4: Set Up the Environment Variables

Create a .flaskenv file in the project root directory and add the following lines:

FLASK_APP=run.py
FLASK_ENV=development

Alternatively, you can set these variables directly in your terminal:

export FLASK_APP=run.py
export FLASK_ENV=development

Step 5: Initialize the Database

Set up the database using Flask-Migrate to create and apply migrations.

# Initialize the database migration environment

flask db init

# Generate an initial migration

flask db migrate -m "Initial migration"

# Apply the migration to create tables in the database

flask db upgrade

Step 6: Run the Application

Now, start the Flask development server:

flask run

By default, the application will run on http://127.0.0.1:5000/. Open this address in your browser to view the app.

Project Structure

Here’s a brief overview of the project structure:

DETYS/
├── app/
│ ├── **init**.py # Application factory
│ ├── controllers/ # Handles routes and logic
│ ├── models/ # Database models
│ ├── templates/ # HTML templates
│ ├── static/ # Static files (CSS, JS, images)
│ └── utils/ # Utility functions (email, database, etc.)
├── config.py # Configuration settings
├── requirements.txt # List of dependencies
├── run.py # Entry point to run the app
└── .flaskenv # Environment variables

Common Commands

    •	Run the Application: flask run
    •	Initialize Database Migrations: flask db init
    •	Create a New Migration: flask db migrate -m "Migration message"
    •	Apply Migrations: flask db upgrade

Additional Notes

    •	Database: The default database is SQLite (sqlite:///detys.db). You can configure other databases in config.py.
    •	Environment Variables: For production, set FLASK_ENV=production and adjust the configuration accordingly.
    •	Deactivating the Virtual Environment: Run deactivate to exit the virtual environment.

Troubleshooting

    1.	Flask Not Found: Ensure the virtual environment is activated (source venv/bin/activate).
    2.	No db Command: Make sure Flask-Migrate is installed and properly set up.
    3.	Database Issues: Delete the migrations folder and detys.db, then re-run the migration steps.

This README should guide you through setting up and running the DETYS application locally. For further development or deployment, consult Flask documentation or reach out with specific questions.
