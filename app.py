from flask import Flask, render_template, redirect, url_for, request, session,flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models.user import User
from models.subject import Subject
from datetime import datetime,timedelta
from models.chapter import Chapter
from sqlalchemy.sql import text
from flask_migrate import Migrate
from flask import request, redirect
from collections import defaultdict
from flask_restful import Api
from resources.quiz import QuizResource
from models import*
from resources.quiz import QuizScoresAPI 
import requests  # <-- Add this line
from flask import Flask, render_template
from models.db_utils import get_user_scores
from sqlalchemy.sql import func  

from models.db_utils import get_user_scores1
from flask import session
import sqlite3
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

api = Api(app)
api.add_resource(QuizResource, "/api/quizzes/<int:quiz_id>")
api.add_resource(QuizScoresAPI, "/api/quiz_scores")
with app.app_context():
    db.create_all()
migrate = Migrate(app, db)  

# Home Page
@app.route('/')
def index():
    return render_template('indexprev.html')

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        print(f"Received username: '{username}'")  # Check if there are spaces
        print(f"Received password: '{password}'")

        correct_username = "admin"
        correct_password = "admin@123"

        print(f"Comparing with username: '{correct_username}'")
        print(f"Comparing with password: '{correct_password}'")

        if username == correct_username and password == correct_password:
            print("Admin login successful!")
            session["user_id"] = "admin"
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            print("Login failed!")
            return "Invalid admin credentials!"

    return render_template("admin_login.html")



# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('fullname')
        qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        hashed_password = generate_password_hash(password)

        if User.query.filter_by(email=email).first():
            return 'Email already registered! Please use a different email.'
        if User.query.filter_by(username=username).first():
            return 'Username already taken! Choose a different one.'

        new_user = User(username=username, email=email, password=hashed_password,
                        full_name=full_name, qualification=qualification, dob=dob, role="user")

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"

    return render_template('register.html')

# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["role"] = user.role
            return redirect(url_for("admin_dashboard" if user.role == "admin" else "user_dashboard"))
        else:
            return "Invalid username or password!"
    return render_template("login.html")

# Admin Dashboard
@app.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    
    search_query = request.args.get('search', '').lower()
    subjects = Subject.query.all()
    
    if search_query:
        subjects = [
            subject for subject in subjects if search_query in subject.name.lower() or 
            any(search_query in chapter.name.lower() for chapter in subject.chapters)
        ]
    
    return render_template("admin_dashboard.html", subjects=subjects, search_query=search_query)

@app.route("/add_subject", methods=["POST"])
def add_subject():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    
    subject_name = request.form.get("subject_name")
    subject_description = request.form.get("subject_description")

    # Check if the subject already exists
    existing_subject = Subject.query.filter_by(name=subject_name).first()

    if existing_subject:
        flash("Subject already exists!", "error")  # Display error message
    else:
        new_subject = Subject(name=subject_name, description=subject_description)
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject added successfully!", "success")  # Success message

    return redirect(url_for("admin_dashboard"))

# Delete Subject
@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
def delete_subject(subject_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
    
    return redirect(url_for("admin_dashboard"))

@app.route('/user_dashboard', methods=['GET'])
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    from models.db_utils import get_user_subjects, get_user_chapters, get_user_quizzes

    search_query = request.args.get('search', '').lower()

    subjects = get_user_subjects(user_id)
    chapters = get_user_chapters(user_id)
    quizzes = get_user_quizzes(user_id)

    # Filter subjects based on search query
    if search_query:
        subjects = [s for s in subjects if search_query in s.name.lower()]
        chapters = [c for c in chapters if c.subject_id in [s.id for s in subjects]]
        quizzes = [q for q in quizzes if q.chapter_id in [c.id for c in chapters]]

    # Structure Data
    subjects_data = []
    for subject in subjects:
        subject_chapters = [ch for ch in chapters if ch.subject_id == subject.id]
        for chapter in subject_chapters:
            chapter.quizzes = [q for q in quizzes if q.chapter_id == chapter.id]
        subjects_data.append({'id': subject.id, 'name': subject.name, 'chapters': subject_chapters})

    return render_template('user_dashboard.html', subjects=subjects_data, search_query=search_query)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

@app.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return "Quiz not found!"

    # Fetch all questions related to this quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        return "No questions found for this quiz!"

    # Store quiz start time in session
    if "quiz_start_time" not in session:
        session["quiz_start_time"] = datetime.now().isoformat()

    # Calculate remaining time
    start_time = datetime.fromisoformat(session["quiz_start_time"])
    end_time = start_time + timedelta(minutes=quiz.time_duration)
    current_time = datetime.now()

    # If time is over, auto-submit
    if current_time >= end_time:
        return redirect(url_for('submit_quiz', quiz_id=quiz_id))  

    return render_template("attempt_quiz.html", quiz=quiz, questions=questions, end_time=end_time)

@app.route("/add_chapter", methods=["GET", "POST"])
def add_chapter():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Unauthorized access. Please log in as an admin.", "error")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        # Handle form submission
        chapter_name = request.form.get("chapter_name")
        chapter_description = request.form.get("chapter_description")
        subject_id = request.form.get("subject_id")

        if not chapter_name or not subject_id:
            flash("Chapter name and subject ID are required.", "error")
            return redirect(url_for("add_chapter", subject_id=subject_id))  # Reload form with subject_id

        try:
            subject_id = int(subject_id)
        except ValueError:
            flash("Invalid subject ID.", "error")
            return redirect(url_for("admin_dashboard"))

        # Save new chapter
        new_chapter = Chapter(name=chapter_name, description=chapter_description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()

        flash("Chapter added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    # If GET request, render the form
    subject_id = request.args.get("subject_id")  # Get subject ID from URL
    return render_template("add_chapter.html", subject_id=subject_id)
@app.route("/delete_chapter/<int:chapter_id>", methods=["POST"])
def delete_chapter(chapter_id):
    if "user_id" not in session or session.get("role") != "admin":
        flash("Unauthorized access. Please log in as an admin.", "error")
        return redirect(url_for("admin_login"))

    chapter = db.session.get(Chapter, chapter_id)  
    if chapter:
        # Delete related quizzes manually
        Quiz.query.filter_by(chapter_id=chapter_id).delete()
        db.session.commit()

        # Now delete the chapter
        db.session.delete(chapter)
        db.session.commit()

        flash("Chapter and associated quizzes deleted successfully!", "success")
    else:
        flash("Chapter not found!", "error")

    return redirect(url_for("admin_dashboard"))

@app.route('/manage_questions/<int:chapter_id>/<int:quiz_id>', methods=['GET', 'POST'])
def manage_questions(chapter_id, quiz_id):
    """Handles adding and displaying questions for a quiz."""
    
    if request.method == 'POST':
        question_text = request.form['question_text']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']

        new_question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_answer=correct_answer
        )

        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully!', 'success')

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('manage_questions.html', chapter_id=chapter_id, quiz_id=quiz_id, questions=questions)

@app.route("/add_question", methods=["POST"])
def add_question():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    quiz_id = request.form.get("quiz_id")
    question_text = request.form.get("question_text")

    # Ensure session has the correct chapter_id
    chapter_id = session.get("chapter_id")
    if not chapter_id:
        flash("Chapter ID is missing!", "error")
        return redirect(url_for("admin_dashboard"))

    if not quiz_id or not question_text:
        flash("Missing quiz ID or question text", "error")
        return redirect(url_for("admin_dashboard"))

    new_question = Question(
        quiz_id=quiz_id,
        question_text=question_text,
        option1=request.form.get("option1"),
        option2=request.form.get("option2"),
        option3=request.form.get("option3"),
        option4=request.form.get("option4"),
        correct_answer=request.form.get("correct_answer"),
    )
    db.session.add(new_question)
    db.session.commit()
    
    flash("Question added successfully!", "success")
    return redirect(url_for("manage_questions", chapter_id=chapter_id, quiz_id=quiz_id))


@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    question = Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
        flash("Question deleted successfully!", "success")

    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route('/quiz/<int:quiz_id>', methods=['GET'])
def start_quiz(quiz_id):
    db.session.expire_all()  # Refresh database session
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Convert minutes to seconds
    quiz_duration_seconds = quiz.time_duration * 60  

    # **Reset the session start time on every new request**
    session[f'quiz_start_{quiz_id}'] = datetime.utcnow().timestamp()

    # Start time is the newly set session variable
    start_time = session[f'quiz_start_{quiz_id}']
    remaining_time = quiz_duration_seconds  # Always start from full duration

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions, remaining_time=remaining_time)
from flask import flash, redirect, url_for
from app import db  # Assuming db is initialized here

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if "user_id" not in session or session.get("role") != "admin":
        flash("Unauthorized access. Please log in as an admin.", "error")
        return redirect(url_for("admin_login"))

    try:
        # Fetch the quiz using SQLAlchemy
        quiz = Quiz.query.get(quiz_id)

        if quiz is None:
            flash("Quiz not found.", "error")
            return redirect(url_for("admin_dashboard"))

        # Delete the quiz (cascades will handle related questions and scores)
        db.session.delete(quiz)
        db.session.commit()

        flash("Quiz deleted successfully!", "success")
        return redirect(url_for("all_quiz_page"))  # Redirect to all quizzes page

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting quiz: {str(e)}", "error")
        return redirect(url_for("all_quiz_page"))  # Redirect to all quizzes page

def store_score(user_id, quiz_id, score):
    new_score = Score(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score,
        date_attempted=datetime.utcnow()
    )
    db.session.add(new_score)
    db.session.commit()

@app.route('/add_quiz_page', methods=['GET'])
def add_quiz_page():
    subject_id = request.args.get('subject_id')
    chapter_id = request.args.get('chapter_id')
    
    # Fetch chapter details for the form
    chapter = Chapter.query.get(chapter_id)

    if not chapter:
        return "Chapter not found", 404
    
    return render_template('add_quiz.html', chapter=chapter)
 
@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    score = sum(
        1 for question in questions
        if request.form.get(f'answer_{question.id}', '').strip().lower() == question.correct_answer.strip().lower()
    )

    store_score(user_id, quiz_id, score)

    flash(f'Quiz submitted! Your score: {score}/{len(questions)}', 'success')
    return redirect(url_for('view_quiz_scores', quiz_id=quiz_id))
@app.route('/add_quiz/<int:subject_id>/<int:chapter_id>', methods=['GET', 'POST'])

@app.route('/add_quiz', methods=['POST'])
def add_quiz():
    print("=== Form Data Received ===")
    print(request.form)  # This will show what Flask is getting
    print("==========================")

    subject_id = request.form.get('subject_id')
    chapter_id = request.form.get('chapter_id')
    quiz_title = request.form.get('quiz_name')  
    time_duration = request.form.get('time_duration')

    if not subject_id or not chapter_id or not quiz_title or not time_duration:
        flash("All fields are required!", "error")
        return redirect(url_for('admin_dashboard'))

    try:
        new_quiz = Quiz(
            subject_id=int(subject_id),
            chapter_id=int(chapter_id),
            title=quiz_title,
            time_duration=int(time_duration)
        )
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding quiz: {str(e)}", "error")

    return redirect(url_for('admin_dashboard'))


@app.route('/view_scores')
def view_scores():
    user_id = session.get('user_id')  # Ensure user is logged in
    if not user_id:
        return redirect(url_for('login'))

    # Fetch all scores for the user
    raw_scores = Score.query.filter_by(user_id=user_id).all()

    quiz_scores = {}  # Dictionary to store latest score per quiz

    for score in raw_scores:
        quiz_title = score.quiz.title  # Ensure quiz title exists in your model
        if quiz_title not in quiz_scores or score.date_attempted > quiz_scores[quiz_title]['date_attempted']:
            quiz_scores[quiz_title] = {
                'quiz_title': quiz_title,
                'score': score.score,  
                'date_attempted': score.date_attempted  # Keep original datetime
            }

    return render_template("view_scores.html", scores=list(quiz_scores.values()))


@app.route('/view_scores/<int:quiz_id>')
def view_quiz_scores(quiz_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    scores = Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).order_by(Score.date_attempted.desc()).all()

    return render_template('view_scores.html', scores=scores, quiz_id=quiz_id)
@app.route('/view_scoresadmin/<int:quiz_id>')
def view_scoresadmin(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    scores = Score.query.filter_by(quiz_id=quiz_id).all()
    
    scores_data = []
    for score in scores:
        user = User.query.get(score.user_id)
        print(f"User for score {score.id}: {user}")  # Debugging print statement
        scores_data.append((score, user))

    return render_template('view_scoresadmin.html', quiz=quiz, scores=scores_data)

@app.route('/quiz')
def quiz_page():
    return render_template("quiz.html")
@app.route("/summary")
def summary_page():
    response = requests.get("http://127.0.0.1:5000/api/quiz_scores")
    
    if response.status_code == 200:
        quiz_scores = response.json()  # Convert response to JSON
    else:
        quiz_scores = []  # Default empty list in case of failure

    return render_template("summary.html", quiz_scores=quiz_scores)
@app.route("/add_subject_page")
def add_subject_page():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Unauthorized access. Please log in as an admin.", "error")
        return redirect(url_for("admin_login"))
    
    return render_template("add_subject.html")
@app.route("/edit_chapter/<int:chapter_id>", methods=["GET", "POST"])
def edit_chapter(chapter_id):
    if "user_id" not in session or session.get("role") != "admin":
        flash("Unauthorized access. Please log in as an admin.", "error")
        return redirect(url_for("admin_login"))

    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

    if request.method == "POST":
        chapter.name = request.form.get("chapter_name")
        chapter.description = request.form.get("chapter_description")

        quiz_title = request.form.get("quiz_title")
        quiz_time = request.form.get("quiz_time")
        quiz_remarks = request.form.get("quiz_remarks")

        if quiz_title and quiz_time:
            new_quiz = Quiz(
                title=quiz_title,
                time_duration=int(quiz_time),
                remarks=quiz_remarks,
                subject_id=chapter.subject_id,
                chapter_id=chapter.id
            )
            db.session.add(new_quiz)

        db.session.commit()
        flash("Chapter and quiz updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_chapter.html", chapter=chapter, quizzes=quizzes)
# Assuming you're using Flask with SQLAlchemy and Chapter is a model
@app.route('/allquiz')
def all_quiz_page():
    quizzes = Quiz.query.all()
    subjects = Subject.query.all()
    chapters = Chapter.query.all()

    selected_chapter_id = request.args.get("chapter_id")
    chapter = None

    if selected_chapter_id:
        try:
            selected_chapter_id = int(selected_chapter_id)  # Convert safely
            chapter = Chapter.query.get(selected_chapter_id)
            quizzes = Quiz.query.filter_by(chapter_id=selected_chapter_id).all()  # Filter quizzes
        except ValueError:
            selected_chapter_id = None

    return render_template(
        'quiz.html',
        quizzes=quizzes,
        subjects=subjects,
        chapters=chapters,
        chapter=chapter,
        selected_chapter_id=selected_chapter_id
    )
@app.route('/manage_quizzes')
def manage_quizzes():
    quizzes = Quiz.query.all()
    chapters = Chapter.query.all()
    
    return render_template('manage_quizzes.html', quizzes=quizzes, chapters=chapters)

@app.route('/get_subject/<int:chapter_id>')
def get_subject(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if chapter:
        return jsonify({'subject_name': chapter.subject.name})
    return jsonify({'subject_name': ''})
@app.route('/api/quiz_attempts')
def quiz_attempts():
    results = db.session.query(Quiz.title, db.func.count(Score.id).label("attempts")) \
        .join(Score) \
        .group_by(Quiz.id) \
        .all()

    return jsonify({"labels": [r.title for r in results], "attempts": [r.attempts for r in results]})
@app.route('/user_quizzes')
def user_quizzes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Fetch all quizzes available for the user
    quizzes = Quiz.query.all()  
    
    return render_template('user_quizzes.html', quizzes=quizzes, user=user)
@app.route('/allscores')
def allscores():
    user_id = session.get('user_id')  # Get user_id from session
    print(f"User ID: {user_id}")  # ✅ Debugging

    if not user_id:
        return "User ID not found", 400  # Handle missing user_id

    scores = get_user_scores1(user_id)  # ✅ Ensure user_id is passed
    return render_template('allscores.html', scores=scores, user_id=user_id)
@app.route('/usersummary')
def user_summary():
    # Subject-wise quiz count
    subject_quiz_counts = (
        db.session.query(Quiz.subject_id, func.count(Quiz.id))
        .group_by(Quiz.subject_id)
        .all()
    )
    subject_data = {subject_id: count for subject_id, count in subject_quiz_counts}

    # Month-wise quiz attempts count
    monthly_attempts = (
        db.session.query(func.strftime('%Y-%m', Score.date_attempted), func.count(Score.id))
        .group_by(func.strftime('%Y-%m', Score.date_attempted))
        .all()
    )

    # Ensure data is correct
    month_data = {month: count for month, count in monthly_attempts}
    print("Month Data:", month_data)  # ✅ Debugging print

    return render_template("usersummary.html", subject_data=subject_data, month_data=month_data)

@app.route('/addquizdirect', methods=['POST'])
def addquizdirect():
    try:
        title = request.form.get("quiz_title")
        chapter_id = request.form.get("chapter_id")
        duration = request.form.get("duration")
        remarks = request.form.get("remarks")

        # Debugging: Print received data
        print(f"Received Data: {title}, {chapter_id}, {duration}, {remarks}")

        if not title or not chapter_id or not duration:
            return "Missing required fields", 400

        # Fetch subject_id using chapter_id
        chapter = Chapter.query.filter_by(id=int(chapter_id)).first()
        if not chapter:
            return "Chapter not found", 404

        subject_id = chapter.subject_id  # Get subject from chapter

        # Insert the quiz into the database
        new_quiz = Quiz(
            title=title,
            subject_id=subject_id,  # Assign fetched subject_id
            chapter_id=int(chapter_id),
            time_duration=int(duration),
            remarks=remarks
        )
        db.session.add(new_quiz)
        db.session.commit()

        return redirect(url_for('all_quiz_page'))  # Return a valid response

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred", 500

if __name__ == '__main__':
     
    
    app.run(debug=True)