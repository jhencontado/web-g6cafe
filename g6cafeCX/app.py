from flask import Flask, render_template, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy,session
from flask_cors import CORS
from geopy.distance import geodesic
import math

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

class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    business_hours = db.Column(db.String(255), nullable=False)

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


@app.route('/storespick')
def storespick():
    # Fetch all stores from the database
    stores = Store.query.all()

    # Prepare a list of stores with relevant data (name, address, business_hours)
    store_list = [{
        'name': store.name,
        'address': store.address,
        'business_hours': store.business_hours
    } for store in stores]

    # Pass store_list to the template
    return render_template('storespick.html', stores=store_list)

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


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in km

# API to fetch nearby stores
@app.route('/api/nearby-stores', methods=['GET'])
def get_nearby_stores():
    user_lat = float(request.args.get('lat'))
    user_lng = float(request.args.get('lng'))

    stores = Store.query.all()

    # Calculate distance between user location and store
    nearby_stores = []
    for store in stores:
        store_location = (store.lat, store.lng)
        user_location = (user_lat, user_lng)
        distance = geodesic(user_location, store_location).km  # In kilometers

        # Only add stores within the 5-7 km range
        if 5 <= distance <= 7:
            nearby_stores.append({
                'name': store.name,
                'address': store.address,
                'distance': round(distance, 2),
                'lat': store.lat,
                'lng': store.lng,
                'business_hours': store.business_hours
            })

    return jsonify({'stores': nearby_stores})

@app.route('/stores')
def get_stores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT name, address, business_hours FROM STORE')
    stores = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(stores)  # return the stores data as JSON

@app.route ( '/add-to-cart',methods=['POST'] )
def add_to_cart ():
    item = request.json  # assuming you send the item data as JSON
    cart = session.get ( 'cart',[] )

    # Add the item to the cart
    cart.append ( item )

    # Save the updated cart back to the session
    session['cart'] = cart

    return jsonify ( {'message': 'Item added to cart','cart_count': len ( cart )} )

@app.route('/cart-count', methods=['GET'])
def cart_count():
    # Example: Fetch the cart from the session or database
    cart = session.get('cart', [])
    return jsonify({'count': len(cart)})


if __name__ == '__main__':
    app.run(debug=True)