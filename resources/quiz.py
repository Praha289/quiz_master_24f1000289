from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from models import Subject, Chapter, Quiz,Score, db
from flask import jsonify
app = Flask(__name__)
api = Api(app)

# Request Parsers for Input Validation
subject_parser = reqparse.RequestParser()
subject_parser.add_argument('name', type=str, required=True, help="Subject name is required")
class QuizResource(Resource):
    def get(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {"message": "Quiz not found"}, 404
        return {"id": quiz.id, "name": quiz.name}, 200
class SubjectsAPI(Resource):
    def get(self):
        subjects = Subject.query.all()
        if not subjects:
            return {"message": "No subjects found"}, 404
        return [{"id": s.id, "name": s.name} for s in subjects], 200

    def post(self):
        args = subject_parser.parse_args()
        new_subject = Subject(name=args['name'])
        db.session.add(new_subject)
        db.session.commit()
        return {"message": "Subject added successfully", "id": new_subject.id}, 201

class ChaptersAPI(Resource):
    def get(self, subject_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            return {"message": "Subject not found"}, 404

        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        if not chapters:
            return {"message": "No chapters found for this subject"}, 404

        return [{"id": c.id, "name": c.name} for c in chapters], 200

class QuizzesAPI(Resource):
    def get(self, chapter_id):
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return {"message": "Chapter not found"}, 404

        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        if not quizzes:
            return {"message": "No quizzes found for this chapter"}, 404

        return [{"id": q.id, "name": q.name} for q in quizzes], 200
class QuizScoresAPI(Resource):
    def get(self):
        quizzes = Quiz.query.all()
        if not quizzes:
            return {"message": "No quizzes found"}, 404

        quiz_scores = []
        for quiz in quizzes:
            scores = Score.query.filter_by(quiz_id=quiz.id).all()
            if scores:
                avg_score = sum([s.score for s in scores]) / len(scores)
                max_score = max([s.score for s in scores])
            else:
                avg_score, max_score = 0, 0  # No scores available

            quiz_scores.append({
                "quiz_name": quiz.title,
                "avg_score": round(avg_score, 2),
                "max_score": max_score
            })

        return quiz_scores, 200
@app.route("/api/quiz_attempts", methods=["GET"])
def get_quiz_attempts():
    quiz_attempts = db.session.query(Quiz.title, db.func.count(Score.id)).join(Score).group_by(Quiz.id).all()
    
    data = {"labels": [quiz[0] for quiz in quiz_attempts],  # Quiz names
            "attempts": [quiz[1] for quiz in quiz_attempts]}  # No. of attempts

    return jsonify(data)

api.add_resource(QuizScoresAPI, "/api/quiz-scores")


api.add_resource(SubjectsAPI, '/api/subjects')
api.add_resource(ChaptersAPI, '/api/subjects/<int:subject_id>/chapters')
api.add_resource(QuizzesAPI, '/api/chapters/<int:chapter_id>/quizzes')

if __name__ == '__main__':
    app.run(debug=True)
