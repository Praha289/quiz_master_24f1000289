from database import db

class Answer(db.Model):
    __tablename__ = 'answer'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.String(255), nullable=False)

    # Relationship
    user_answers = db.relationship("UserAnswer", back_populates="answer", lazy="dynamic")