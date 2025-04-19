from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, Store, Product, Stock, StockMovement
from datetime import datetime
import threading
import time

app = Flask(__name__)

# --- App Configuration ---

# PostgreSQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:monarchofshadow@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Caching configuration
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 60  # in seconds

# Initialize extensions
db.init_app(app)
auth = HTTPBasicAuth()
cache = Cache(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

# Dummy user credentials for basic authentication
users = {
    "admin": "password123"
}

@auth.verify_password
def verify_password(username, password):
    return username if users.get(username) == password else None

# Automatically create all tables on app startup
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/store', methods=['POST'])
@auth.login_required
@limiter.limit("10 per minute")
def add_store():
    """Create a new store"""
    data = request.json
    store = Store(name=data['name'])
    db.session.add(store)
    db.session.commit()
    return jsonify({"message": "Store added", "id": store.id})


@app.route('/product', methods=['POST'])
@auth.login_required
@limiter.limit("10 per minute")
def add_product():
    """Create a new product"""
    data = request.json
    product = Product(name=data['name'])
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added", "id": product.id})


def async_save_stock(data):
    """
    Background thread to update stock asynchronously.
    Simulates a delay to represent processing time.
    """
    time.sleep(1)  # Simulate processing delay

    store_id = data['store_id']
    product_id = data['product_id']
    action = data['action']
    amount = data['amount']

    stock = Stock.query.filter_by(store_id=store_id, product_id=product_id).first()

    # If stock record doesn't exist, create it
    if not stock:
        stock = Stock(store_id=store_id, product_id=product_id, quantity=0)
        db.session.add(stock)

    # Apply the stock action
    if action == 'stock-in':
        stock.quantity += amount
    elif action in ['sale', 'remove']:
        stock.quantity -= amount

    # Log the movement
    movement = StockMovement(
        store_id=store_id,
        product_id=product_id,
        action=action,
        amount=amount,
        timestamp=datetime.utcnow()
    )

    db.session.add(movement)
    db.session.commit()


@app.route('/stock', methods=['POST'])
@auth.login_required
@limiter.limit("20 per minute")
def update_stock():
    """
    Trigger a stock update.
    Actual processing is done in a background thread.
    """
    data = request.json
    thread = threading.Thread(target=async_save_stock, args=(data,))
    thread.start()
    return jsonify({"message": f"Stock update for store {data['store_id']} accepted."})


@app.route('/inventory', methods=['GET'])
@auth.login_required
@limiter.limit("30 per minute")
@cache.cached(query_string=True)
def get_inventory():
    """
    Get current inventory for a specific store.
    Caching enabled for 60 seconds to reduce DB load.
    """
    store_id = request.args.get('store_id')
    if not store_id:
        return jsonify({"error": "Please provide store_id as query parameter"}), 400

    stocks = Stock.query.filter_by(store_id=store_id).all()

    return jsonify([
        {
            "product_id": stock.product_id,
            "store_id": stock.store_id,
            "quantity": stock.quantity
        } for stock in stocks
    ])


@app.route('/movements', methods=['GET'])
@auth.login_required
@limiter.limit("30 per minute")
def get_movements():
    """
    Retrieve stock movements for a store between two dates.
    Expected date format: YYYY-MM-DD
    """
    store_id = request.args.get('store_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not store_id or not start_date or not end_date:
        return jsonify({"error": "Please provide store_id, start_date, and end_date"}), 400

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Date format must be YYYY-MM-DD"}), 400

    movements = StockMovement.query.filter(
        StockMovement.store_id == store_id,
        StockMovement.timestamp >= start,
        StockMovement.timestamp <= end
    ).all()

    return jsonify([
        {
            "product_id": m.product_id,
            "store_id": m.store_id,
            "action": m.action,
            "amount": m.amount,
            "timestamp": m.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for m in movements
    ])


# --- App Entry Point ---

if __name__ == '__main__':
    app.run(debug=True)
