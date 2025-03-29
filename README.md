# Quiz Master - V1

## Author
**Mangipudi Uma Mani Praharshitha**  
**Roll Number:** 24F1000289  
**Email:** 24f1000289@ds.study.iitm.ac.in  
A passionate software engineer aspirant with a strong interest in web development and AI-driven applications. Enthusiastic about problem-solving and building scalable software solutions.

## Description
The **Quiz Master App** enables quiz masters to create and manage quizzes under different subjects and chapters. Users can take quizzes, track their scores, and visualize performance analytics through an intuitive and engaging interface.

## Technologies Used
### Backend
- **Flask**: Micro web framework for handling HTTP requests and responses.
- **Flask-Migrate**: Manages database migrations using Alembic.
- **Flask-RESTful**: Helps in building RESTful APIs.
- **Flask-SQLAlchemy**: Provides ORM support for database interactions.
- **Flask-Session**: Manages user sessions across requests.
- **Flask-Flash**: Displays temporary messages (success, error notifications).
- **Werkzeug**: Provides security features like password hashing.
- **Requests**: Handles HTTP requests to external APIs.
- **Collections**: Used for handling structured data like dictionaries and lists efficiently.
- **Datetime**: Manages date and time operations, such as user DOB and quiz timestamps.

### Frontend
- **HTML, CSS, Bootstrap, JavaScript**: Used for the UI and interactivity.
- **Chart.js**: JavaScript library for creating interactive and responsive charts.

### Database
- **SQLite**: Lightweight database used for storing user and subject data.
- **SQLAlchemy**: ORM for handling database queries and relationships.

### API & Data Format
- **REST API**: Used for communication between frontend and backend.
- **JSON**: Data format for structuring API responses and requests.

## Architecture Overview
```
app.py        - Main Flask entry point, handles routing.
database.py   - Configures database connection.
/models       - Contains database models (user.py, quiz.py, score.py, etc.).
/templates    - Stores HTML files (index.html, login.html, admin_dashboard.html, etc.).
/static       - Holds CSS for styling.
/resources    - Manages API (api.py).
/instance     - Stores quiz.db for SQLite database.
/migrations   - Handles database schema changes using Flask-Migrate.
```

## Features
### Admin Features
- Manage quiz structure by adding, deleting, and editing subjects and chapters.
- Assign questions to each quiz under a chapter.
- Set time limits for quizzes.
- View user scores for each quiz and attempt.
- Generate summary charts using Chart.js.

### User Features
- Attempt quizzes based on available subjects.
- View past quiz scores.
- Access summary charts for quiz performance using Chart.js.

## Data Model
- **User & Role**: Manages user access.
- **Subject & Chapter**: Organizes quizzes efficiently.
- **Quiz**: Links subjects/chapters with time limits.
- **Question & Answer**: Ensures flexibility and validation.
- **User Answer & Score**: Tracks responses and performance.
- **User Subjects**: Manages user preferences.

