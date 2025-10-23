from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound
# Import db from the main application file to ensure all models use the same SQLAlchemy instance
from extensions import db

alerts_bp = Blueprint('alerts', __name__)

# --- Alert Model ---
class Alert(db.Model):
    __tablename__ = 'alert_file'
    my_row_id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True, autoincrement=True)
    Date = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.String(100), db.ForeignKey('user.user_id'), nullable=False) # Foreign key to User table
    Symbol = db.Column(db.String(30), nullable=False)
    OrderNo = db.Column(db.String(30), nullable=False)
    OrderStatus = db.Column(db.String(30), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    BuyPrice = db.Column(db.Float, nullable=False)
    LastTradePrice = db.Column(db.Float, nullable=False)
    ProfitLoss = db.Column(db.Float, nullable=False)
    ProfitLossPercentage = db.Column(db.Float, nullable=False)
    OCOOrderNo = db.Column(db.String(30), nullable=True)
    OCOStatus = db.Column(db.String(30), nullable=True)
    OverallStatus = db.Column(db.String(30), nullable=False)

    __table_args__ = (db.UniqueConstraint('Date', 'user_id', 'Symbol', name='uc_alert'),)

    def to_dict(self):
        return {
            "my_row_id": self.my_row_id,
            "Date": self.Date,
            "userId": self.user_id,
            "Symbol": self.Symbol,
            "Order No.": self.OrderNo,
            "Order Status": self.OrderStatus,
            "Quantity": self.Quantity,
            "Buy Price": self.BuyPrice,
            "Last Trade Price": self.LastTradePrice,
            "Profit/Loss": self.ProfitLoss,
            "Profit/Loss %": self.ProfitLossPercentage,
            "OCO Order No.": self.OCOOrderNo,
            "OCO Status": self.OCOStatus,
            "Overall Status": self.OverallStatus
        }

# --- Alert CRUD Endpoints ---

@alerts_bp.route('/alerts', methods=['POST'])
def create_alert():
    """Creates a new alert. Handles unique constraint violations."""
    data = request.get_json()
    if not data:
        raise BadRequest("Request body must be JSON.")

    required_fields = ['Date', 'userId', 'Symbol', 'Order No.', 'Order Status', 'Quantity', 'Buy Price', 'Last Trade Price', 'Profit/Loss', 'Profit/Loss %', 'Overall Status']
    if not all(field in data for field in required_fields):
        raise BadRequest(f"Missing required fields: {', '.join(required_fields)}")

    new_alert = Alert(
        Date=data['Date'],
        user_id=data['userId'],
        Symbol=data['Symbol'],
        OrderNo=data['Order No.'],
        OrderStatus=data['Order Status'],
        Quantity=data['Quantity'],
        BuyPrice=data['Buy Price'],
        LastTradePrice=data['Last Trade Price'],
        ProfitLoss=data['Profit/Loss'],
        ProfitLossPercentage=data['Profit/Loss %'],
        OCOOrderNo=data.get('OCO Order No.'),
        OCOStatus=data.get('OCO Status'),
        OverallStatus=data['Overall Status']
    )
    db.session.add(new_alert)
    db.session.commit()
    return jsonify(new_alert.to_dict()), 201

@alerts_bp.route('/alerts', methods=['GET'])
def get_all_alerts():
    """Returns all alerts from the database."""
    alerts = Alert.query.all()
    return jsonify([alert.to_dict() for alert in alerts]), 200

@alerts_bp.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    """Returns a single alert by its my_row_id."""
    alert = Alert.query.get_or_404(id)
    return jsonify(alert.to_dict()), 200

@alerts_bp.route('/alerts/<int:id>', methods=['PUT'])
def update_alert(id):
    """Updates an existing alert."""
    alert = Alert.query.get_or_404(id)
    data = request.get_json()
    if not data:
        raise BadRequest("Request body must be JSON.")

    alert.Date = data.get('Date', alert.Date)
    alert.user_id = data.get('userId', alert.user_id)
    alert.Symbol = data.get('Symbol', alert.Symbol)
    alert.OrderNo = data.get('Order No.', alert.OrderNo)
    alert.OrderStatus = data.get('Order Status', alert.OrderStatus)
    alert.Quantity = data.get('Quantity', alert.Quantity)
    alert.BuyPrice = data.get('Buy Price', alert.BuyPrice)
    alert.LastTradePrice = data.get('Last Trade Price', alert.LastTradePrice)
    alert.ProfitLoss = data.get('Profit/Loss', alert.ProfitLoss)
    alert.ProfitLossPercentage = data.get('Profit/Loss %', alert.ProfitLossPercentage)
    alert.OCOOrderNo = data.get('OCO Order No.', alert.OCOOrderNo)
    alert.OCOStatus = data.get('OCO Status', alert.OCOStatus)
    alert.OverallStatus = data.get('Overall Status', alert.OverallStatus)

    db.session.commit()
    return jsonify(alert.to_dict()), 200

@alerts_bp.route('/alerts/<int:id>', methods=['DELETE'])
def delete_alert(id):
    """Deletes an alert by its my_row_id and returns the deleted record."""
    alert = Alert.query.get_or_404(id)
    alert_data = alert.to_dict()
    db.session.delete(alert)
    db.session.commit()
    return jsonify(alert_data), 200