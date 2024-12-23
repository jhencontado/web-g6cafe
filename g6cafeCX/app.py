from flask import Flask, render_template, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:MySql.Admin@localhost/g6Cafe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MenuDetails(db.Model):
    __tablename__ = 'menu_details'
    item_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(255))
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    vat_amount = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2))
    net_amount = db.Column(db.Numeric(10, 2), nullable=False)
    tender_amount = db.Column(db.Numeric(10, 2), nullable=False)
    change_amount = db.Column(db.Numeric(10, 2), nullable=False)
    receipt_number = db.Column(db.String(50), nullable=False, unique=True)

class OrderDetails(db.Model):
    __tablename__ = 'order_details'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_details.item_id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    order_preference = db.Column(db.Text)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/stores')
def stores():
    return render_template('stores.html')

@app.route('/tracker')
def tracker():
    return render_template('tracker.html')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    category = request.args.get('category')
    if category:
        menu_items = MenuDetails.query.filter_by(category_name=category).all()
    else:
        menu_items = MenuDetails.query.all()

    menu_list = [{
        'item_id': item.item_id,
        'item_name': item.item_name,
        'category_name': item.category_name,
        'unit_price': str(item.unit_price),
        'photo': url_for('static', filename=f'images/{item.photo}') if item.photo else None
    } for item in menu_items]
    return jsonify(menu_list)

if __name__ == '__main__':
    app.run(debug=True)