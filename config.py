from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
# Import db from the main application file
from extensions import db

config_bp = Blueprint('config', __name__)

# --- RefreshInterval Model ---
class RefreshInterval(db.Model):
    __tablename__ = 'refresh_interval'
    id = db.Column(db.Integer, primary_key=True)
    interval_seconds = db.Column(db.Integer, nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "interval_seconds": self.interval_seconds
        }

# --- Refresh Interval CRUD Endpoints ---

@config_bp.route('/config/refresh-interval', methods=['GET'])
def get_refresh_interval():
    """Returns the configured refresh interval from the database."""
    # Fetches the first available setting.
    interval_setting = RefreshInterval.query.first()
    if interval_setting:
        return jsonify({"interval_seconds": interval_setting.interval_seconds}), 200
    else:
        # Provide a fallback default if the table is empty
        return jsonify({"error": "No refresh interval configured", "interval_seconds": 300}), 404

@config_bp.route('/config/refresh-intervals', methods=['POST'])
def create_refresh_interval():
    """Creates a new refresh interval. Best used if table is empty."""
    data = request.get_json()
    if not data or 'interval_seconds' not in data:
        raise BadRequest("Missing 'interval_seconds' in request body")

    if not isinstance(data['interval_seconds'], int):
        raise BadRequest("'interval_seconds' must be an integer")

    new_interval = RefreshInterval(interval_seconds=data['interval_seconds'])
    db.session.add(new_interval)
    db.session.commit()
    return jsonify(new_interval.to_dict()), 201

@config_bp.route('/config/refresh-intervals/<int:id>', methods=['PUT'])
def update_refresh_interval(id):
    """Updates the refresh interval value."""
    interval_setting = RefreshInterval.query.get_or_404(id)
    data = request.get_json()
    if not data or 'interval_seconds' not in data:
        raise BadRequest("Missing 'interval_seconds' in request body")

    if not isinstance(data['interval_seconds'], int):
        raise BadRequest("'interval_seconds' must be an integer")

    interval_setting.interval_seconds = data['interval_seconds']
    db.session.commit()
    return jsonify(interval_setting.to_dict()), 200
