Here’s the complete Markdown text for your README.md file:

# DETYS Project

A Flask-based project for managing users, clubs, events, notifications, and reports.

## Prerequisites

- **Python 3.7+**
- **Virtual Environment** (recommended)
- **SQLite** (default database for testing)
- **Git** (optional, for version control)

## Getting Started

### 1. Clone the Repository

Clone this repository to your local machine (if using Git):

```bash
git clone https://github.com/your-username/detys.git
cd detys

2. Set Up the Virtual Environment

Create and activate a virtual environment to manage dependencies.

# Create the virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

3. Install Dependencies

Install the necessary packages listed in requirements.txt:

pip install -r requirements.txt

4. Set Up Environment Variables

Create a .flaskenv file in the project root directory and add the following:

FLASK_APP=run.py
FLASK_ENV=development

Alternatively, set these variables in your terminal:

export FLASK_APP=run.py
export FLASK_ENV=development

5. Initialize the Database

Use Flask-Migrate to set up the database:

# Initialize database migration environment
flask db init

# Generate an initial migration
flask db migrate -m "Initial migration"

# Apply the migration to create tables
flask db upgrade

6. Run the Application

Start the Flask development server:

flask run

Navigate to http://127.0.0.1:5000/ in your browser to view the app.

Project Structure

DETYS/
├── app/
│   ├── __init__.py              # Application factory
│   ├── controllers/             # Handles routes and logic
│   ├── models/                  # Database models
│   ├── templates/               # HTML templates
│   ├── static/                  # Static files (CSS, JS, images)
│   └── utils/                   # Utility functions (email, database, etc.)
├── config.py                    # Configuration settings
├── requirements.txt             # List of dependencies
├── run.py                       # Entry point to run the app
└── .flaskenv                    # Environment variables

Common Commands

Command	Description
flask run	Run the application
flask db init	Initialize database migrations
flask db migrate -m "Message"	Create a new migration
flask db upgrade	Apply migrations to the database

Additional Notes

	•	Database: The default database is SQLite (sqlite:///detys.db). Configure other databases in config.py.
	•	Environment Variables: For production, set FLASK_ENV=production and adjust the configuration accordingly.
	•	Deactivating the Virtual Environment: Run deactivate to exit the virtual environment.

Troubleshooting

	1.	Flask Not Found: Ensure the virtual environment is activated (source venv/bin/activate).
	2.	No db Command: Confirm that Flask-Migrate is installed and properly set up.
	3.	Database Issues: Delete the migrations folder and detys.db, then re-run the migration steps.

This README provides the essential steps to set up and run the DETYS application. For further development or deployment, consult Flask Documentation or reach out with specific questions.

This Markdown file is now ready to be saved as `README.md`. It should display well-formatted instructions and tables when viewed on GitHub.
```
