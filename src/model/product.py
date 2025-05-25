from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
from src import app, db

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', backref='product', lazy=True)
    image = db.Column(db.String(100), nullable=False, default='default.jpg')


    def __repr__(self):
            """
            String representation of a Product object, useful for debugging.
            Now includes the image filename.
            """
            return f"Product('{self.name}', ${self.price:.2f}', Image: '{self.image}')"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        """
        String representation of an Order object.
        """
        return f"Order(ID: {self.id}, Product ID: {self.product_id}, Quantity: {self.quantity}, Date: {self.order_date.strftime('%Y-%m-%d %H:%M:%S')})"

if __name__ == '__main__':
    with app.app_context():
        print('Creating database...')
        db.create_all()