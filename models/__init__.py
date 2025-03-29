from database import db

# Import models in the correct order to resolve dependencies
from models.user import User  # User should be imported first
from models.subject import Subject  # Subject should be next
from models.associations import user_subjects  # Import association table AFTER User & Subject

from models.chapter import Chapter
from models.quiz import Quiz
from models.question import Question
from models.answer import Answer
from models.score import Score
from models.user_answer import UserAnswer
