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

Install the necessary packages listed in requirements.txt:

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

Navigate to http://127.0.0.1:5000/ in your browser to view the app.

## Project Structure

```bash
DETYS/
├── app/
│ ├── __init__.py # Application factory
│ ├── forms.py # All forms
│ ├── models.py # Database Models
│ ├── core/
│ │ ├── decorators.py # Custom decorators
│ │ ├── extensions.py # Flask extensions initialization
│ ├── routes/
│ │ ├── event_routes.py # Event-related routes
│ │ ├── club_routes.py # Club-related routes
│ │ ├── main_routes.py # Main application routes
│ ├── static/
│ │ ├── css/
│ │ │ ├── styles.css # CSS styles
│ │ ├── js/
│ │ │ ├── jquery-3.6.0.min.js # jQuery library
│ │ │ ├── socket.io.min.js # Socket.IO library
│ │ │ ├── scripts.js # Custom scripts
│ ├── templates/
│ │ ├── auth/
│ │ │ ├── login.html # Login template
│ │ │ ├── register.html # Registration template
│ │ ├── club/
│ │ │ ├── club_detail.html # Club detail template
│ │ │ ├── club_list.html # Club list template
│ │ │ ├── create_club.html # Create club template
│ │ │ ├── edit_club.html # Edit club template
│ │ │ ├── manage_members.html # Manage club members template
│ │ ├── event/
│ │ │ ├── create_event.html # Create event template
│ │ │ ├── event_detail.html # Event detail template
│ │ │ ├── event_list.html # Event list template
│ │ │ ├── manage_attendees.html # Manage event attendees template
│ │ │ ├── submit_feedback.html # Submit event feedback template
│ │ ├── main/
│ │ │ ├── contact.html # Contact form template
│ │ │ ├── create_post.html # Create post template
│ │ │ ├── dashboard.html # User dashboard template
│ │ │ ├── index.html # Home page template
│ │ │ ├── view_post.html # View post template
│ │ ├── base.html # Base template
├── instance/
│ ├── __init__.py
│ └── config.py # Configuration settings
├── migrations/
│ ├── alembic.ini
│ ├── env.py
│ ├── script.py.mako
│ └── versions/
├── requirements.txt # List of dependencies
├── run.py # Entry point to run the app
└── .flaskenv # Environment variables
```

## Common Commands

```bash
flask run                       Run the application
flask db init                   Initialize database migrations
flask db migrate -m "Message"   Create a new migration
flask db upgrade                Apply migrations to the database
```

## Additional Notes

- Database: The default database is SQLite (sqlite:///detys.db). Configure other databases in config.py.
- Environment Variables: For production, set FLASK_ENV=production and adjust the configuration accordingly.
- Deactivating the Virtual Environment: Run deactivate to exit the virtual environment.

## Troubleshooting

1. Flask Not Found: Ensure the virtual environment is activated (source venv/bin/activate).
2. No db Command: Confirm that Flask-Migrate is installed and properly set up.
3. Database Issues: Delete the migrations folder and detys.db, then re-run the migration steps.

This README provides the essential steps to set up and run the DETYS application. For further development or deployment, consult Flask Documentation or reach out with specific questions.

## Raw Project Roadmap

```bash
DETYS Project Roadmap
	1.	Initiation: Project Definition and Planning
	•	Define project requirements:
	•	Identify user roles (student, club manager, main admin) and their permissions.
	•	Outline the core system modules (User Management, Club/Event Management, Notifications, Reporting).
	•	Select technology stack:
	•	Backend: Flask or Django.
	•	Database: PostgreSQL or MySQL.
	•	Choose libraries for notifications and reporting.
	•	Task allocation and timeline: Assign tasks to teams or individuals, and set completion timelines for each phase.
	2.	User Management and Login Panel (Weeks 1-2)
	•	Develop the user management module:
	•	Create user login and registration API using Flask/Django.
	•	Set up database tables to store user data (name, role, password).
	•	Roles and Authorization System:
	•	Develop authorization based on roles (student, club manager, main admin).
	•	Design login and user panels:
	•	Design different login screens for each role and create a simple user interface.
	3.	Club and Membership Management (Weeks 3-4)
	•	Club Information Module:
	•	Set up database tables to store club information (name, description, president, contact details).
	•	Membership Management:
	•	Add membership processes for students to join clubs and for managers to approve/terminate members.
	•	Provide membership approval notifications and a simple user interface.
	•	Multithreading and Database Management:
	•	Use multithreading for high-demand processes to ensure efficient database operations.
	4.	Event Management Module (Weeks 5-6)
	•	Event Creation and Editing:
	•	Develop an API for club managers to create and update events.
	•	Implement a waiting list system based on event capacity limits.
	•	Event Details:
	•	Create an event details page for students to access information like date, time, and location.
	•	Use socket programming to send notifications to students on the waiting list.
	•	Multithreading and Concurrency:
	•	Improve performance with threading when event demand is high.
	5.	Registration and Notification System (Weeks 7-8)
	•	Registration and Waiting List Management:
	•	Enable students to register for events and join the waiting list.
	•	Notification System:
	•	Send event reminders and status updates via email or SMS.
	•	Create an asynchronous notification system using socket programming.
	•	File Operations:
	•	Store registration and waiting list data and generate data for notifications.
	6.	Event Feedback and Evaluation (Weeks 9-10)
	•	Evaluation Module:
	•	Add a feedback module for students to complete short surveys or ratings after events.
	•	Data Analysis:
	•	Collect and report student feedback through data analysis.
	•	File Operations and Data Manipulation:
	•	Apply file structures and data manipulation techniques to store and process feedback.
	7.	Reporting and Statistics Panel (Weeks 11-12)
	•	Participation and Popularity Statistics:
	•	Create reports for the main admin on student participation rates, most popular events, etc.
	•	Graphs and Visualization:
	•	Use Matplotlib or Plotly for graphical representation of statistical data.
	•	Downloadable Reports:
	•	Enable reports to be downloaded in PDF or HTML format.
	8.	Testing and Final Touches (Week 13)
	•	Module Testing:
	•	Conduct functionality and security tests for each module.
	•	Bug Fixing and Enhancements:
	•	Make final adjustments based on user feedback and implement minor improvements.
	•	Documentation:
	•	Prepare a project report and include usage instructions and module descriptions.

Nice-to-Have Features (Beyond Course Scope)
	1.	Enhanced Notification and Reminder Features
	•	Mobile Notifications:
	•	Integrate push notifications using Firebase or a similar service.
	•	Detailed Reminder Settings:
	•	Allow users to set specific reminder frequencies for events.
	2.	Advanced Algorithms for Event Evaluation
	•	AI-Based Feedback Analysis:
	•	A module to perform sentiment analysis on feedback.
	•	Recommendation Systems:
	•	Suggest events based on students’ past participation.
	3.	Blockchain for Membership and Attendance Verification
	•	Membership and Attendance Confirmation:
	•	Use blockchain technology to verify membership and attendance records.
	4.	Mobile Application Integration
	•	Mobile App with React Native or Flutter:
	•	Make DETYS accessible on mobile devices for a user-friendly experience.
	5.	Cloud Integration
	•	Use Cloud Storage for Database and File Management:
	•	Integrate storage and management systems on AWS or Google Cloud.

These additional features would make the project more comprehensive and suitable for real-world applications, requiring knowledge beyond the current course scope.
```

```bash
Updated Roadmap Completion Status

1. Initiation: Project Definition and Planning
	•	Define project requirements: Completed
	•	Identify user roles and permissions: Completed
	•	Outline core system modules: Completed
	•	Select technology stack (Flask + SQLite chosen): Completed
	•	Task allocation and timeline: Completed

2. User Management and Login Panel (Weeks 1-2)
	•	Develop the user management module (login/registration): Completed
	•	Database tables for users: Completed
	•	Roles and authorization system: Completed
	•	User interface for login and user panels: Completed

3. Club and Membership Management (Weeks 3-4)
	•	Club information module: Completed
	•	Membership processes (join/approve/terminate): Completed
	•	Membership approval notifications (basic notifications in place): Completed
	•	Simple UI: Completed
	•	Multithreading (basic use of eventlet and socket.io for concurrency): Completed

4. Event Management Module (Weeks 5-6)
	•	Event creation and editing by club managers: Completed
	•	Waiting list system for events: Completed
	•	Event details page: Completed
	•	Socket programming for notifications (socket.io integration): Completed
	•	Multithreading and concurrency (via eventlet): Completed

5. Registration and Notification System (Weeks 7-8)
	•	Event registration and waiting list: Completed
	•	Notification system (basic email or SMS not shown, but socket-based notifications implemented): Partially Completed
	•	Asynchronous notification system using socket programming: Completed
	•	File operations for registrations (Not fully demonstrated, but database storage is done): Partially Completed

6. Event Feedback and Evaluation (Weeks 9-10)
	•	Feedback module (short surveys/ratings): Completed
	•	Data analysis on feedback (basic average rating done): Partially Completed
	•	File operations and data manipulation (not fully implemented, but DB is used): Partially Completed

7. Reporting and Statistics Panel (Weeks 11-12)
	•	Participation and popularity statistics: Not Completed
	•	Graphs and visualization (Matplotlib/Plotly not integrated): Not Completed
	•	Downloadable reports (PDF/HTML): Not Completed

8. Testing and Final Touches (Week 13)
	•	Module testing: Partially Completed (basic tests exist)
	•	Bug fixing and enhancements: Ongoing
	•	Documentation (some inline doc and README placeholders): Partially Completed

Nice-to-Have Features (Beyond Course Scope)
	•	Enhanced notifications, AI-based feedback analysis, Blockchain verification, Mobile app integration, Cloud integration: Not Completed

```
