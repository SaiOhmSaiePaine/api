from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def _validate_name(value):
    if not isinstance(value, str) or not value.strip():
        return False
    return True

#Define the Data model
class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120))

    def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description
            }

    def __repr__(self):
        return f'{self.name} - {self.description}'


# Root route
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Drink API!'})


# GET: Retrieve all drinks
@app.route('/drinks', methods=['GET'])
def get_drinks():
    query = Drink.query

    # Search by keyword: drinks?q=soda
    search = request.args.get('q')
    if search:
        query = query.filter(Drink.name.ilike(f'%{search}%'))

    #Pagination: drinks?page=1&per_page=10
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    per_page = min(max(per_page, 1), 100)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({'drinks': [drink.to_dict() for drink in paginated.items], 
                    'total': paginated.total,
                    'page': paginated.page,
                    'pages': paginated.pages})


# GET: Retrieve a single drink by ID
@app.route('/drinks/<int:id>')
def get_drink(id):
    drink = Drink.query.get_or_404(id)
    return jsonify(drink.to_dict())


# POST: Add a new drink
@app.route('/drinks', methods=['POST'])
def add_drink():
    data = request.get_json(silent=True) or {}
    if not _validate_name(data.get('name')):
        return jsonify({'error': 'Missing or invalid field: name'}), 400

    description = data.get('description', '')
    if description is not None and not isinstance(description, str):
        return jsonify({'error': 'Invalid field: description'}), 400

    drink = Drink(
        name=data['name'].strip(),
        description=description or ''
    )
    db.session.add(drink)
    db.session.commit()
    return jsonify({'id': drink.id}), 201


# DELETE: Remove a drink by ID
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drink(id):
    drink = db.session.get(Drink, id)
    if drink is None:
        return jsonify({'error': "not found"}), 404
    db.session.delete(drink)
    db.session.commit()
    return jsonify({'message': 'Drink deleted successfully'}), 200


# PUT / PATCH: Update a drink by ID
@app.route('/drinks/<int:id>', methods=['PUT', 'PATCH'])
def update_drink(id):
    drink = db.session.get(Drink, id)
    if drink is None:
        return jsonify({'error': "Drink not found"}), 404

    data = request.get_json(silent=True) or {}

    if request.method == 'PUT':
        # Put expect complete replacement: validate required fields
        if not _validate_name(data.get('name')):
            return jsonify({'error': 'Missing or invalid field: name'}), 400
        description = data.get('description', '')
        if description is not None and not isinstance(description, str):
            return jsonify({'error': 'Invalid field: description'}), 400
        drink.name = data['name'].strip()
        drink.description = description or ''
    else:
        if 'name' in data:
            if not _validate_name(data['name']):
                return jsonify({'error': 'Invalid field: name'}), 400
            drink.name = data['name'].strip()
        if 'description' in data:
            if data['description'] is not None and not isinstance(data['description'], str):
                return jsonify({'error': 'Invalid field: description'}), 400
            drink.description = data['description']

    db.session.commit()
    return jsonify(drink.to_dict()), 200


if __name__ == '__main__':
    app.run(debug=True)