from database import db

class Subject(db.Model):
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    chapters = db.relationship('Chapter', back_populates='subject', lazy=True, cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', back_populates='subject', lazy=True, cascade="all, delete-orphan")