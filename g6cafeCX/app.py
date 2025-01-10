from flask import Flask, render_template, jsonify, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy,session
from flask_cors import CORS
from geopy.distance import geodesic
import math
from flask import session


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

    # Relationship with OrderDetails
    order_items = db.relationship('OrderDetails', back_populates='menu_item', cascade='all, delete-orphan')


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

    # Relationship with MenuDetails
    menu_item = db.relationship('MenuDetails', back_populates='order_items')


class PwdSeniorDetails(db.Model):
    __tablename__ = 'pwdsenior_details'
    pwdsenior_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'))
    discount_type = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(100), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)

class OrderAddress(db.Model):
    __tablename__ = 'order_address'
    order_address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    address = db.Column(db.Text)
    pickup_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(50))
    contact_number = db.Column(db.String(15), nullable=False)

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


@app.route ( '/menu' )
def menu ():
    category = request.args.get ( 'category' )  # Get the 'category' query parameter from the URL
    if category:
        menu_items = MenuDetails.query.filter_by ( category_name=category ).all ()  # Fetch items for the given category
    else:
        menu_items = MenuDetails.query.all ()  # If no category is provided, fetch all items

    return render_template ( 'menu.html',category=category,menu_items=menu_items )

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
        if 0 <= distance <= 7:
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

@app.route('/search-receipt', methods=['POST'])
def search_receipt():
    order_id = request.form.get('order_id')
    if not order_id:
        return "Order ID is required", 400

    # Redirect to the receipt page with the order_id
    return redirect(url_for('receipt', order_id=order_id))


@app.route('/receipt/<int:order_id>')
def receipt(order_id):
    # Fetch order details
    order = Order.query.filter_by(order_id=order_id).first()

    if not order:
        return "Order not found", 404

    # Fetch related address
    address = OrderAddress.query.filter_by(order_id=order_id).first()

    # Fetch order items
    order_items = (
        db.session.query(OrderDetails, MenuDetails)
        .join(MenuDetails, MenuDetails.item_id == OrderDetails.item_id)
        .filter(OrderDetails.order_id == order_id)
        .all()
    )

    # Fetch PWD details
    pwd_details = PwdSeniorDetails.query.filter_by(order_id=order_id).first()

    # Prepare items for display
    items = [
        {
            'item_name': item.MenuDetails.item_name,
            'quantity': item.OrderDetails.quantity,
            'subtotal': item.OrderDetails.subtotal,
            'preference': item.OrderDetails.order_preference

        }
        for item in order_items
    ]

    # Prepare order dictionary for template
    order_data = {
        'receipt_number': order.receipt_number,
        'date_time': order.date_time.strftime('%Y-%m-%d %H:%M:%S'),
        'subtotal': float(order.subtotal),
        'vat_amount': float(order.vat_amount),
        'discount_amount': float(order.discount_amount or 0),
        'net_amount': float(order.net_amount),
        'tender_amount': float(order.tender_amount),
        'change_amount': float(order.change_amount),
        'contact_name': address.contact_name if address else "N/A",
        'contact_number': address.contact_number if address else "N/A",
        'address': address.address if address else "N/A",
    }

    # Add PWD details if available
    if pwd_details:
        order_data.update({
            'pwd_name': pwd_details.customer_name,
            'pwd_id_number': pwd_details.id_number,
            'pwd_discount_type': pwd_details.discount_type,

        })

    return render_template('receipt.html', order=order_data, items=items)

if __name__ == '__main__':
    app.run(debug=True)