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
    category = db.Column(db.String(100), nullable=True)

# Initialize database
with app.app_context():
    db.create_all()

# Fetch all flashcards or filter by category with pagination
@app.route("/flashcards", methods=["GET"])
def get_flashcards():
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    query = Flashcard.query
    if category:
        query = query.filter_by(category=category)

    if sort_by in ['id', 'question', 'category']:
        if order == 'desc':
            query = query.order_by(getattr(Flashcard, sort_by).desc())
        else:
            query = query.order_by(getattr(Flashcard, sort_by).asc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    flashcards = paginated.items

    return jsonify({
        "flashcards": [{"id": fc.id, "question": fc.question, "answer": fc.answer, "category": fc.category} for fc in flashcards],
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page
    })

# Add a new flashcard
@app.route("/flashcards", methods=["POST"])
def add_flashcard():
    data = request.json
    if not data.get('question') or not data.get('answer'):
        return jsonify({"error": "Question and answer are required!"}), 400
    new_flashcard = Flashcard(
        question=data['question'], 
        answer=data['answer'], 
        category=data.get('category')
    )
    db.session.add(new_flashcard)
    db.session.commit()
    return jsonify({"message": "Flashcard added successfully!"}), 201

# Update an existing flashcard
@app.route("/flashcards/<int:id>", methods=["PUT"])
def update_flashcard(id):
    data = request.json
    flashcard = Flashcard.query.get_or_404(id)

    flashcard.question = data.get('question', flashcard.question)
    flashcard.answer = data.get('answer', flashcard.answer)
    flashcard.category = data.get('category', flashcard.category)
    
    db.session.commit()
    return jsonify({"message": "Flashcard updated successfully!"})

# Search flashcards by keyword in question or answer
@app.route("/search_flashcards", methods=["GET"])
def search_flashcards():
    query = request.args.get('query', '').lower()
    flashcards = Flashcard.query.filter(
        Flashcard.question.ilike(f"%{query}%") | 
        Flashcard.answer.ilike(f"%{query}%")
    ).all()
    return jsonify([{"id": fc.id, "question": fc.question, "answer": fc.answer, "category": fc.category} for fc in flashcards])

# Delete a flashcard
@app.route("/flashcards/<int:id>", methods=["DELETE"])
def delete_flashcard(id):
    flashcard = Flashcard.query.get_or_404(id)
    db.session.delete(flashcard)
    db.session.commit()
    return jsonify({"message": "Flashcard deleted successfully!"})

# Error handler for 404 errors
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found!"}), 404

# Error handler for 400 errors
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request!"}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
