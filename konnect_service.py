import uuid
from flask import Flask, jsonify, request
from extensions import db # Import db from extensions
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound, BadRequest
import os
import random # Keep random for seeding


# Create the Flask application
app = Flask(__name__)

# --- Database Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'konnect_db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Initialize db with the app instance

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to confirm the service is running.
    """
    return jsonify({"status": "ok"}), 200

# --- Global Error Handlers ---

@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    """Handles database integrity errors (e.g., unique constraint violations)."""
    db.session.rollback()
    # You could inspect e.orig to provide a more specific message
    return jsonify({"error": "Database integrity error. A record with this value may already exist."}), 409

@app.errorhandler(NotFound)
def handle_not_found(e):
    """Handles 404 Not Found errors, common with get_or_404."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    """Handles 400 Bad Request, often from malformed JSON."""
    return jsonify({"error": "Bad request. Check your request body or parameters."}), 400

@app.errorhandler(Exception)
def handle_generic_exception(e):
    """Handles all other unhandled exceptions as a 500 Internal Server Error."""
    # In a production environment, you would log the error `e` here.
    return jsonify({"error": "An unexpected internal server error occurred."}), 500

from users import users_bp, User
from alerts import alerts_bp, Alert
from config import config_bp, RefreshInterval
from signals import signals_bp, Signal

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(config_bp)
app.register_blueprint(signals_bp)

def seed_database():
    """Seeds the database with sample data if it's empty."""
    
    # Seed users
    if User.query.first() is None:
        print("User table is empty. Seeding with 10 users...")
        users_to_add = [
            User(user_id=f'user {i}', username=f'user name {i}', stockbroker=random.choice(['Zerodha', 'Upstox', 'Groww']))
            for i in range(1, 11)
        ]
        db.session.bulk_save_objects(users_to_add)
        db.session.commit()
        print("User table seeded successfully.")
    
    # Seed refresh interval
    if RefreshInterval.query.first() is None:
        print("Refresh interval table is empty. Seeding with default value...")
        db.session.add(RefreshInterval(interval_seconds=200))
        db.session.commit()
        print("Refresh interval seeded successfully.")

    # Seed alerts
    if Alert.query.first() is None:
        print("Alert table is empty. Seeding with 10 sample alerts...")
        alerts_to_add = []
        # Fetch existing user_ids to ensure valid foreign keys
        existing_user_ids = [user.user_id for user in User.query.all()]
        symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN", "BAJFINANCE", "BHARTIARTL", "KOTAKBANK"]

        for i in range(10):
            # Create unique combinations for the seed data
            alert = Alert(
                Date=f"2024-05-{10+i:02d}",
                user_id=random.choice(existing_user_ids), # Use actual user_ids
                Symbol=random.choice(symbols),
                OrderNo=str(random.randint(10000, 99999)),
                OrderStatus=random.choice(["Filled", "Pending", "Cancelled"]),
                Quantity=random.randint(1, 100),
                BuyPrice=round(random.uniform(100.0, 4000.0), 2),
                LastTradePrice=round(random.uniform(100.0, 4000.0), 2),
                ProfitLoss=round(random.uniform(-500.0, 500.0), 2),
                ProfitLossPercentage=round(random.uniform(-10.0, 10.0), 2),
                OCOOrderNo=str(random.randint(10000, 99999)),
                OCOStatus=random.choice(["Active", "Cancelled"]),
                OverallStatus=random.choice(["Open", "Closed"])
            )
            alerts_to_add.append(alert)
        
        try:
            db.session.bulk_save_objects(alerts_to_add)
            db.session.commit()
            print("Alert table seeded successfully.")
        except IntegrityError: # In case random generation creates a duplicate
            db.session.rollback()
            print("Could not seed alerts due to a duplicate entry. Please try restarting.")

    # Seed signals
    if Signal.query.first() is None:
        print("Signal table is empty. Seeding with 10 sample signals...")
        signals_to_add = []
        symbols = ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN"]
        strategies = ["Breakout", "MeanReversion", "Momentum", "Scalping"]

        for i in range(10):
            # Using a unique date for each entry to avoid violating the unique constraint
            signal = Signal(
                adate=f"2024-05-{20+i:02d}",
                asymbol=random.choice(symbols),
                astrategy=random.choice(strategies),
                aprice=round(random.uniform(100.0, 50000.0), 2),
                acounter=random.randint(1, 5),
                atime=f"{random.randint(9,14):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
            )
            signals_to_add.append(signal)
        
        db.session.bulk_save_objects(signals_to_add)
        db.session.commit()
        print("Signal table seeded successfully.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates the database and tables if they don't exist
        seed_database() # Add random data if the DB is empty

    # Note: In a production environment, use a proper WSGI server like Gunicorn or uWSGI.
    # Example: gunicorn --bind 0.0.0.0:5004 konnect_service:app
    app.run(host='0.0.0.0', port=5004, debug=True, use_reloader=False)