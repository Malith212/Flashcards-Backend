from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flashcard model
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(200), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

@app.route("/flashcards", methods=["GET"])
def get_flashcards():
    flashcards = Flashcard.query.all()
    return jsonify([{"id": fc.id, "question": fc.question, "answer": fc.answer} for fc in flashcards])

@app.route("/flashcards", methods=["POST"])
def add_flashcard():
    data = request.json
    new_flashcard = Flashcard(question=data['question'], answer=data['answer'])
    db.session.add(new_flashcard)
    db.session.commit()
    return jsonify({"message": "Flashcard added successfully!"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
