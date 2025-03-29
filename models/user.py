from database import db
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')

    # Relationships
    scores = db.relationship('Score', back_populates='user', lazy=True, cascade="all, delete-orphan")
    answers = db.relationship('UserAnswer', back_populates='user', lazy="dynamic")