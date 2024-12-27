# DETYS Project

A Flask-based project for managing users, clubs, events, notifications, and reports.

## Prerequisites

- **Python 3.8+**
- **Virtual Environment** (recommended)
- **SQLite** (default database for testing)
- **Git** (optional, for version control)

## Getting Started

### 1. Clone the Repository

Clone this repository to your local machine (if using Git):

```bash
git clone https://github.com/your-username/detys.git
cd detys
```

### 2. Set Up the Virtual Environment

Create and activate a virtual environment to manage dependencies:

```bash
# Create the virtual environment
python -m venv venv
```

Activate the virtual environment:

```bash
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

Install the necessary packages listed in requirements.txt

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a .flaskenv file in the project root directory and add the following:

```bash
FLASK_APP=run.py
FLASK_ENV=development
```

Alternatively, set these variables in your terminal:

```bash
export FLASK_APP=run.py
export FLASK_ENV=development
```

### 5. Initialize the Database

Use Flask-Migrate to set up the database:

Initialize database migration environment:

```bash
flask db init
```

Generate an initial migration:

```bash
flask db migrate -m "Initial migration"
```

Apply the migration to create tables:

```bash
flask db upgrade
```

### 6. Run the Application

Start the Flask development server:

```bash
flask run
```

Navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser to view the app.

## Project Structure

```bash
DETYS/
├── app/
│   ├── __init__.py              # Application factory
│   ├── forms.py                 # All forms
│   ├── models.py                # Database Models
│   ├── core/
│   │   ├── analytics.py         # Analytics functions
│   │   ├── config.py            # Configuration settings
│   │   ├── data_processing.py   # Data processing functions
│   │   ├── decorators.py        # Custom decorators
│   │   ├── extensions.py        # Flask extensions initialization
│   │   ├── notifications.py     # Notification functions
│   │   ├── statistics.py        # Statistical functions
│   │   ├── visualizations.py    # Visualization functions
│   ├── routes/
│   │   ├── __init__.py          # Route initialization
│   │   ├── admin_routes.py      # Admin-related routes
│   │   ├── auth_routes.py       # Authentication-related routes
│   │   ├── bookmark_routes.py   # Bookmark-related routes
│   │   ├── category_routes.py   # Category-related routes
│   │   ├── club_routes.py       # Club-related routes
│   │   ├── event_resource_routes.py # Event resource-related routes
│   │   ├── event_routes.py      # Event-related routes
│   │   ├── main_routes.py       # Main application routes
│   │   ├── poll_routes.py       # Poll-related routes
│   │   ├── post_routes.py       # Post-related routes
│   │   ├── profile_routes.py    # Profile-related routes
│   │   ├── report_routes.py     # Report-related routes
│   │   ├── search_routes.py     # Search-related routes
│   ├── static/
│   │   ├── css/
│   │   │   ├── error.css        # Error page styles
│   │   │   ├── login.css        # Login page styles
│   │   │   ├── navbar.css       # Navbar styles
│   │   │   ├── styles.css       # General styles
│   │   ├── event_resources/     # Event resource files
│   │   ├── exports/             # Exported files
│   │   ├── images/              # Image files
│   │   ├── js/
│   │   │   ├── jquery-3.6.0.min.js # jQuery library
│   │   │   ├── socket.io.min.js # Socket.IO library
│   │   │   ├── scripts.js       # Custom scripts
│   │   ├── uploads/             # Uploaded files
│   ├── templates/
│   │   ├── admin/
│   │   │   ├── user_edit.html   # Admin user edit template
│   │   │   ├── user_list.html   # Admin user list template
│   │   ├── auth/
│   │   │   ├── login.html       # Login template
│   │   ├── base.html            # Base template
│   │   ├── category/
│   │   │   ├── create_category.html # Create category template
│   │   │   ├── edit_category.html   # Edit category template
│   │   │   ├── list_categories.html # List categories template
│   │   ├── club/
│   │   │   ├── club_detail.html # Club detail template
│   │   │   ├── club_list.html   # Club list template
│   │   │   ├── create_club.html # Create club template
│   │   │   ├── edit_club.html   # Edit club template
│   │   │   ├── manage_members.html # Manage club members template
│   │   ├── event/
│   │   │   ├── create_event.html # Create event template
│   │   │   ├── edit_event.html   # Edit event template
│   │   │   ├── event_detail.html # Event detail template
│   │   │   ├── event_list.html   # Event list template
│   │   │   ├── manage_attendees.html # Manage event attendees template
│   │   │   ├── submit_feedback.html # Submit event feedback template
│   │   ├── main/
│   │   │   ├── contact.html      # Contact form template
│   │   │   ├── dashboard.html    # User dashboard template
│   │   │   ├── error.html        # Error page template
│   │   │   ├── index.html        # Home page template
│   │   │   ├── navbar.html       # Navbar template
│   │   │   ├── notifications.html # Notifications template
│   │   ├── poll/
│   │   │   ├── create_poll.html  # Create poll template
│   │   │   ├── view_poll.html    # View poll template
│   │   ├── post/
│   │   │   ├── all_posts.html    # All posts template
│   │   │   ├── create_post.html  # Create post template
│   │   │   ├── edit_post.html    # Edit post template
│   │   │   ├── view_post.html    # View post template
│   │   ├── report/
│   │   │   ├── pdf_template.html # PDF report template
│   │   │   ├── report.html       # Report template
│   │   ├── search/
│   │   │   ├── results.html      # Search results template
│   │   ├── user/
│   │   │   ├── profile.html      # User profile template
├── instance/
│   ├── __init__.py
│   └── config.py                 # Configuration settings
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── requirements.txt              # List of dependencies
├── run.py                        # Entry point to run the app
└── .flaskenv                     # Environment variables
```

## Common Commands

```bash
flask run                       # Run the application
flask db init                   # Initialize database migrations
flask db migrate -m "Message"   # Create a new migration
flask db upgrade                # Apply migrations to the database
```

## Additional Notes

- **Database**: The default database is SQLite (`sqlite:///detys.db`). Configure other databases in `config.py`.
- **Environment Variables**: For production, set `FLASK_ENV=production` and adjust the configuration accordingly.
- **Deactivating the Virtual Environment**: Run `deactivate` to exit the virtual environment.

## Troubleshooting

1. **Flask Not Found**: Ensure the virtual environment is activated (`source venv/bin/activate`).
2. **No db Command**: Confirm that Flask-Migrate is installed and properly set up.
3. **Database Issues**: Delete the

migrations

folder and `detys.db`, then re-run the migration steps.

This README provides the essential steps to set up and run the DETYS application. For further development or deployment, consult Flask Documentation or reach out with specific questions.
