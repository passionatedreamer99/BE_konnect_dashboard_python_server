from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound
# Import db from the main application file to ensure all models use the same SQLAlchemy instance
from extensions import db

users_bp = Blueprint('users', __name__)

# --- User Model ---
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    stockbroker = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "userId": self.user_id,
            "username": self.username,
            "stockbroker": self.stockbroker
        }

# --- User CRUD Endpoints ---

@users_bp.route('/users', methods=['POST'])
def create_user():
    """Creates a new user record."""
    data = request.get_json()
    if not data:
        raise BadRequest("Request body must be JSON.")

    required_fields = ['userId', 'username', 'stockbroker']
    if not all(field in data and data[field] is not None for field in required_fields):
        raise BadRequest(f"Missing or null required fields: {', '.join(required_fields)}")

    new_user = User(
        user_id=data['userId'],
        username=data['username'],
        stockbroker=data['stockbroker']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@users_bp.route('/users', methods=['GET'])
def get_all_users():
    """Returns all user IDs from the database."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@users_bp.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    """Returns a single user by their ID."""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@users_bp.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    """Updates a user record."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data:
        raise BadRequest("Request body must be JSON.")

    user.username = data.get('username', user.username)
    user.stockbroker = data.get('stockbroker', user.stockbroker)

    db.session.commit()
    return jsonify(user.to_dict()), 200

@users_bp.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletes a user record and returns the deleted record."""
    user = User.query.get_or_404(user_id)
    user_data = user.to_dict()
    db.session.delete(user)
    db.session.commit()
    return jsonify(user_data), 200