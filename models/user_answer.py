from database import db
from models.user import User
from models.answer import Answer 
# Import after User to avoid circular import

class UserAnswer(db.Model):
    __tablename__ = 'user_answer'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False) 
    answer_text = db.Column(db.String(255))

    # Relationships
    user = db.relationship('User', back_populates='answers')
    answer = db.relationship('Answer', back_populates='user_answers')