from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound
from extensions import db

signals_bp = Blueprint('signals', __name__)

# --- Signal Model ---
# Based on the provided SQL schema
class Signal(db.Model):
    __tablename__ = 'signals'
    my_row_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    adate = db.Column(db.String(10), nullable=False)
    asymbol = db.Column(db.String(30), nullable=False)
    astrategy = db.Column(db.String(30), nullable=False)
    aprice = db.Column(db.Float, nullable=True)
    acounter = db.Column(db.Integer, nullable=True)
    atime = db.Column(db.String(8), nullable=True)

    __table_args__ = (db.UniqueConstraint('adate', 'astrategy', 'asymbol', name='uc_signal'),)

    def to_dict(self):
        return {
            "my_row_id": self.my_row_id,
            "adate": self.adate,
            "asymbol": self.asymbol,
            "astrategy": self.astrategy,
            "aprice": self.aprice,
            "acounter": self.acounter,
            "atime": self.atime
        }

# --- Signal CRUD Endpoints ---

@signals_bp.route('/signals', methods=['POST'])
def create_signal():
    """Creates a new signal record."""
    data = request.get_json()
    if not data:
        raise BadRequest("Request body must be JSON.")

    required_fields = ['adate', 'asymbol', 'astrategy']
    if not all(field in data for field in required_fields):
        raise BadRequest(f"Missing required fields: {', '.join(required_fields)}")

    new_signal = Signal(
        adate=data['adate'],
        asymbol=data['asymbol'],
        astrategy=data['astrategy'],
        aprice=data.get('aprice'),
        acounter=data.get('acounter'),
        atime=data.get('atime')
    )
    db.session.add(new_signal)
    db.session.commit()
    return jsonify(new_signal.to_dict()), 201

@signals_bp.route('/signals', methods=['GET'])
def get_all_signals():
    """Returns all signal records."""
    signals = Signal.query.all()
    return jsonify([signal.to_dict() for signal in signals]), 200

@signals_bp.route('/signals/<int:id>', methods=['GET'])
def get_signal(id):
    """Returns a single signal by its ID."""
    signal = Signal.query.get_or_404(id)
    return jsonify(signal.to_dict()), 200

@signals_bp.route('/signals/<int:id>', methods=['PUT'])
def update_signal(id):
    """Updates an existing signal record."""
    signal = Signal.query.get_or_404(id)
    data = request.get_json()
    if not data:
        raise BadRequest("Request body must be JSON.")

    # Update fields if they are provided in the request
    signal.adate = data.get('adate', signal.adate)
    signal.asymbol = data.get('asymbol', signal.asymbol)
    signal.astrategy = data.get('astrategy', signal.astrategy)
    signal.aprice = data.get('aprice', signal.aprice)
    signal.acounter = data.get('acounter', signal.acounter)
    signal.atime = data.get('atime', signal.atime)

    db.session.commit()
    return jsonify(signal.to_dict()), 200

@signals_bp.route('/signals/<int:id>', methods=['DELETE'])
def delete_signal(id):
    """Deletes a signal record."""
    signal = Signal.query.get_or_404(id)
    signal_data = signal.to_dict() # Capture data before deleting
    db.session.delete(signal)
    db.session.commit()
    return jsonify(signal_data), 200