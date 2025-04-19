from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy (to be initialized in main app with app context)
db = SQLAlchemy()

# --- Models ---

class Store(db.Model):
    """Represents a physical or virtual store location."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Store {self.id} - {self.name}>"


class Product(db.Model):
    """Represents a product that can be stocked and sold."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Product {self.id} - {self.name}>"


class Stock(db.Model):
    """Tracks the quantity of a product available at a specific store."""
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)

    # Relationships (optional: helpful for ORM usage)
    store = db.relationship('Store', backref='stocks')
    product = db.relationship('Product', backref='stocks')

    def __repr__(self):
        return f"<Stock Store:{self.store_id} Product:{self.product_id} Qty:{self.quantity}>"


class StockMovement(db.Model):
    """
    Logs all stock actions such as additions, sales, and removals.
    Useful for tracking inventory history.
    """
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # Expected values: 'stock-in', 'sale', 'remove'
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (optional)
    product = db.relationship('Product', backref='movements')
    store = db.relationship('Store', backref='movements')

    def __repr__(self):
        return (
            f"<Movement Store:{self.store_id} Product:{self.product_id} "
            f"Action:{self.action} Amount:{self.amount} Time:{self.timestamp}>"
        )
