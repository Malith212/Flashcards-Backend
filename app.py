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
    category = db.Column(db.String(100), nullable=True)  # Added category

# Initialize database
with app.app_context():
    db.create_all()

# Fetch all flashcards or filter by category
@app.route("/flashcards", methods=["GET"])
def get_flashcards():
    category = request.args.get('category')
    if category:
        flashcards = Flashcard.query.filter_by(category=category).all()
    else:
        flashcards = Flashcard.query.all()
    return jsonify([{"id": fc.id, "question": fc.question, "answer": fc.answer, "category": fc.category} for fc in flashcards])

# Add a new flashcard
@app.route("/flashcards", methods=["POST"])
def add_flashcard():
    data = request.json
    new_flashcard = Flashcard(question=data['question'], answer=data['answer'], category=data.get('category'))
    db.session.add(new_flashcard)
    db.session.commit()
    return jsonify({"message": "Flashcard added successfully!"})

# Search flashcards by keyword
@app.route("/search_flashcards", methods=["GET"])
def search_flashcards():
    query = request.args.get('query', '').lower()
    flashcards = Flashcard.query.filter(Flashcard.question.ilike(f"%{query}%")).all()
    return jsonify([{"id": fc.id, "question": fc.question, "answer": fc.answer, "category": fc.category} for fc in flashcards])

# Delete a flashcard
@app.route("/flashcards/<int:id>", methods=["DELETE"])
def delete_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)
    db.session.delete(flashcard)
    db.session.commit()
    return jsonify({"message": "Flashcard deleted successfully!"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
