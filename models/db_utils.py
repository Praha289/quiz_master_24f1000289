from models.subject import Subject
from models.quiz import Quiz
from models.score import Score
from database import db
from models import db, Chapter
def get_user_scores1(user_id):
    return Score.query.filter_by(user_id=user_id).all()

def get_user_chapters1(user_id):
    """Fetch all chapters related to the subjects chosen by the user."""
    from models import UserSubjects, Chapter

    user_subjects = UserSubjects.query.filter_by(user_id=user_id).all()
    subject_ids = [us.subject_id for us in user_subjects]

    return Chapter.query.filter(Chapter.subject_id.in_(subject_ids)).all()

def get_user_chapters(user_id):
    """Fetch all chapters available to the user based on subjects they have access to."""
    return Chapter.query.all()  # Modify this based on your database structure

def get_user_subjects(user_id):
    """Fetch subjects available to the user."""
    return Subject.query.all()  # Modify if subjects are user-specific

def get_user_quizzes(user_id):
    """Fetch quizzes based on subjects the user has access to."""
    subjects = get_user_subjects(user_id)
    subject_ids = [subject.id for subject in subjects] or [-1]  # Prevent empty filter
    return Quiz.query.filter(Quiz.subject_id.in_(subject_ids)).all()

def get_user_scores(quiz_id, user_id):
    """Retrieve scores for a user in a given quiz."""
    return Score.query.filter_by(user_id=user_id, quiz_id=quiz_id).all()

def store_score(user_id, quiz_id, score_data):
    """Calculate and store the total quiz score."""
    user_score = sum(1 for q in score_data if q['user_answer'] == q['correct_answer'])

    # Save the total score in Score table
    new_score = Score(user_id=user_id, quiz_id=quiz_id, score=user_score)
    db.session.add(new_score)
    db.session.commit()
def get_quiz_questions(quiz_id):
    return Question.query.filter_by(quiz_id=quiz_id).all()