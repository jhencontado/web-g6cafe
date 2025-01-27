import decimal
import logging
import os



from flask import Flask, render_template, jsonify, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy,session
from flask_cors import CORS
from geopy.distance import geodesic
import math
from flask import session
import datetime
from flask_mail import Mail, Message
from sqlalchemy import Enum

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.urandom(24)

# Configure MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:MySql.Admin@localhost/g6Cafe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'G6cafe.customerservice@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'tgzq dalx pwwj tgdm'  # Replace with your Gmail password or app password
app.config['MAIL_DEFAULT_SENDER'] = 'G6cafe.customerservice@gmail.com'  # Default sender email

mail = Mail(app)

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
    discount_type = db.Column(db.String(50))
    customer_name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(100), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)


class OrderPaymentDetails(db.Model):
    __tablename__ = 'order_payment_details'
    order_payment_details_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    payment_option = db.Column(db.String(50))
    gcash_ref_number = db.Column(db.Integer)
    change_for_cash = db.Column(db.Numeric(10, 2), nullable=False)
    card_name = db.Column(db.String(100))
    card_number = db.Column(db.BigInteger)
    card_exp_month = db.Column(db.Integer)
    card_exp_year = db.Column(db.Integer)
    card_cvv = db.Column(db.String(50))

class OrderAddress(db.Model):
    __tablename__ = 'order_address'
    order_address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    address = db.Column(db.Text)
    pickup_date = db.Column(db.DateTime)
    pickup_time = db.Column(db.Time)
    delivery_date = db.Column(db.DateTime)
    delivery_time = db.Column(db.Time)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(50))
    contact_number = db.Column(db.String(15), nullable=False)
    delivery_instruction = db.Column(db.Text)
    order_type = db.Column(db.String(50), nullable=True)

class Stores(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    business_hours = db.Column(db.String(255), nullable=False)



class DeliveryRider(db.Model):
    __tablename__ = 'delivery_rider'

    delivery_rider_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vehicle_plate_number = db.Column(db.String(50), nullable=False)
    vehicle_model = db.Column(db.String(255), nullable=False)
    vehicle_color = db.Column(db.String(50), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)


from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum as PyEnum


# Define the OrderStatusEnum class as a Python Enum
class OrderStatusEnum(PyEnum):
    pending = 'pending'
    preparing = 'preparing'
    ready_for_pick_up = 'ready for pick-up'
    picked_up = 'picked-up'
    out_for_delivery = 'out for delivery'
    delivered = 'delivered'
    cancelled = 'cancelled'


# TrackDetails model
class TrackDetails(db.Model):
    __tablename__ = 'trackdetails'

    track_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)

    order_status = db.Column(
        db.Enum('pending', 'preparing', 'ready for pick-up', 'picked-up', 'out for delivery', 'delivered', 'cancelled'),
        nullable=False
    )
    order_type = db.Column(db.String(50), db.ForeignKey('order_address.order_type'), nullable=False)
    delivery_rider_id = db.Column(db.Integer, db.ForeignKey('delivery_rider.delivery_rider_id'), nullable=False)

    # Relationships (use string references for delayed evaluation)
    order = db.relationship('Order', backref='trackdetails', lazy=True)
    stores = db.relationship('Stores', backref='trackdetails', lazy=True)
    rider = db.relationship('DeliveryRider', backref='trackdetails', lazy=True)



    def __repr__(self):
        return f'<TrackDetails {self.track_id} {self.order_status}>'



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
    stores = Stores.query.all()

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
        menu_items = MenuDetails.quer.all()

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

    stores = Stores.query.all()

    # Calculate distance between user location and store
    nearby_stores = []
    for store in stores:
        store_location = (store.lat, store.lng)
        user_location = (user_lat, user_lng)
        distance = geodesic(user_location, store_location).km  # In kilometers

        # Only add stores within the 5-7 km range
        if 0 <= distance <= 5:
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
    search_option = request.form.get('search_option')

    if not order_id:
        return "Order ID is required", 400

    if search_option == 'order_id':
        # Redirect to the receipt page with the order_id
        return redirect(url_for('receipt', order_id=order_id))
    elif search_option == 'track_order':
        # Redirect to the order tracking page
        return redirect(url_for('track_order', order_id=order_id))

    return "Invalid search option", 400

def generate_receipt_number():
    """
    Generates a unique receipt number using current timestamp and a random component.

    Returns:
        str: The generated receipt number.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    # Add a random component for further uniqueness (optional)
    import random
    random_part = str(random.randint(1000, 9999))
    return f"REC{timestamp}-{random_part}"

def get_item_id(item_name):
    try:
        item = MenuDetails.query.filter_by(item_name = item_name).first()
        if item:
            return item.item_id
        else:
            return jsonify({'message': 'item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_delivery_rider_id(store_id):
    try:
        item = DeliveryRider.query.filter_by(store_id = store_id).first()
        if item:
            return item.delivery_rider_id
        else:
            return jsonify({'message': 'item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_store_id(store_name):
    try:
        item = Stores.query.filter_by(name = store_name).first()
        if item:
            return item.id
        else:
            return jsonify({'message': 'item not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proceed-checkout', methods=['POST'])
def proceed_checkout():
    try:
        # region Insert Order
        subtotal = request.form.get('subtotal')
        vat_amount = request.form.get('vat')
        discount_amount = request.form.get('discount')
        net_amount = request.form.get('amount_due')

        if request.form.get('payment') != 'cash':
            tender_amount = net_amount
        else:
            tender_amount = request.form.get('tendered_amount')

        if len (tender_amount) ==0:
            tender_amount = 0
        change_value = request.form.get('change_value')

        if len (change_value) ==0:
            change_value = 0

        receipt_number = generate_receipt_number()
        new_order = Order(
            subtotal = subtotal,
            vat_amount = vat_amount,
            discount_amount = discount_amount,
            net_amount = net_amount,
            tender_amount = tender_amount,
            change_amount = change_value,
            receipt_number = receipt_number
        )
        db.session.add(new_order)
        db.session.commit()

        #get the last inserted order id
        last_inserted_id = new_order.order_id
        # endregion


        #region insert to order_details
        item_names = request.form.getlist("item-name")
        item_subtotals = request.form.getlist("item-subtotal")
        item_prices = request.form.getlist("item-price")
        item_quantities = request.form.getlist("item-quantity")
        item_preferences = request.form.getlist("item-preference")

        index = 0
        for item_name in item_names:
            item_id = get_item_id(item_name)
            qty = int(item_quantities[index])
            amount = decimal.Decimal(item_prices[index])
            subtotal = decimal.Decimal(item_subtotals[index])
            new_order_details = OrderDetails(
                order_id = last_inserted_id,
                item_id = item_id,
                quantity = qty,
                subtotal = subtotal,
                order_preference = item_preferences[index]
            )

            db.session.add(new_order_details)
            db.session.commit()

            index += 1
        #endregion

        #region insert PwdSeniorDetails
        discount = request.form.get('discount-option')
        if discount == 'PWD':
            discount_type = 'PWD'
        elif discount == 'Senior':
            discount_type = 'Senior'
        else:
            discount_type = None

        new_pwdsenior_details = PwdSeniorDetails(
            order_id = last_inserted_id,
            discount_type = discount_type,
            customer_name = request.form.get('discount_name'),
            id_number = request.form.get('discount_id_number'),
            discount_amount = discount_amount
        )

        db.session.add(new_pwdsenior_details)
        db.session.commit()
        #endregion

        #region insert to order_payment_details
        payment_option = request.form.get('payment')
        gcash_number = request.form.get('gcash-number')
        card_name = request.form.get('card_name')
        card_number = request.form.get('card_number')
        expiration_month = request.form.get('expiration_month')
        expiration_year = request.form.get('expiration_year')
        card_cvv = request.form.get('cvv')

        new_order_payment_details = OrderPaymentDetails(
            order_id = last_inserted_id,
            payment_option = payment_option,
            gcash_ref_number = gcash_number,
            change_for_cash = tender_amount,
            card_name = card_name,
            card_number = card_number,
            card_exp_month = expiration_month,
            card_exp_year = expiration_year,
            card_cvv = card_cvv
        )

        db.session.add(new_order_payment_details)
        db.session.commit()
        #endregion

        #region insert to order_address
        address = request.form.get('address')

        order_type = request.form.get('order_type')
        option = request.form.get('option')
        delivery_date = None
        delivery_time = None
        pickup_date = None
        pickup_time = None

        if order_type == 'delivery':
            if option == 'deliver_now':
                delivery_date = datetime.datetime.now()
                delivery_time = datetime.datetime.now().time()
            else:
                delivery_date = request.form.get('delivery_date')
                delivery_time = request.form.get('delivery_time')
        else: 
            if option == 'standard':
                pickup_date = datetime.datetime.now()
                pickup_time = datetime.datetime.now().time()
            else:
                pickup_date = request.form.get('pickup_date')
                pickup_time = request.form.get('pickup_time')

        contact_name = request.form.get('name')
        contact_email = request.form.get('email')
        contact_number = request.form.get('contact')
        delivery_instruction = request.form.get('delivery-instruction')

        new_address = OrderAddress(
            order_id = last_inserted_id,
            address = address,
            pickup_date = pickup_date,
            pickup_time = pickup_time,
            delivery_date = delivery_date,
            delivery_time = delivery_time,
            contact_name = contact_name,
            contact_email = contact_email,
            contact_number = contact_number,
            delivery_instruction = delivery_instruction,
            order_type  = order_type
        )

        db.session.add(new_address)
        db.session.commit()
        #endregion

        #region insert in trackdetails
        store_name = request.form.get('store_name')
        store_id = get_store_id(store_name)
        rider_id = get_delivery_rider_id(store_id)


        new_trackdetails = TrackDetails(
            order_id = last_inserted_id,
            store_id = store_id,
            order_status = 'pending',
            delivery_rider_id = rider_id,
            order_type = order_type
        )

        db.session.add(new_trackdetails)
        db.session.commit()
        #endregion

        # Prepare email content
        recipient_email = request.form.get('email')  # Assuming you collect the user's email in the form
        subject = f"G6 Cafe - Order Confirmation (Order ID #{last_inserted_id})"
        message_body = f"""
                        Dear {contact_name},

                        Thank you for your order! Here are your order details:
                
                        Order Number: {last_inserted_id}
                        Receipt Number: {receipt_number}
                        Date & Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                        Total Amount: {net_amount}

                        If you have any questions, please contact us at support@example.com.

                        Regards,
                        G6 Cafe
                        """

        # Send the email
        msg = Message(subject, recipients=[recipient_email], body=message_body)
        mail.send(msg)

        return redirect(url_for('track_order', order_id=last_inserted_id))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    payment_details = OrderPaymentDetails.query.filter_by ( order_id=order.order_id ).first ()
    # Prepare order dictionary for template
    order_data = {
        'order_id' : order.order_id,
        'receipt_number': order.receipt_number,
        'payment_option': payment_details.payment_option,
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
        'order_type': address.order_type.strip().lower() if address and address.order_type else "N/A",

    }

    # Add PWD details if available
    if pwd_details:
        order_data.update({
            'pwd_name': pwd_details.customer_name,
            'pwd_id_number': pwd_details.id_number,
            'pwd_discount_type': pwd_details.discount_type,

        })


    return render_template('receipt.html', order=order_data, items=items)


import logging

@app.route('/track-order/<int:order_id>')
def track_order(order_id):
    try:
        # Fetch the order details based on order_id
        order = TrackDetails.query.filter_by(order_id=order_id).first()

        if order:
            # Define the statuses based on order_type
            if order.order_type == "pick_up":
                status_steps = ["pending", "preparing", "ready for pick-up", "picked-up", "cancelled"]
            elif order.order_type == "delivery":
                status_steps = ["pending", "preparing", "out for delivery", "delivered", "cancelled"]
            else:
                status_steps = []  # Undefined order type

            # Check if order_status is valid before proceeding
            if order.order_status in status_steps:
                completed_steps = status_steps[:status_steps.index(order.order_status) + 1]
                current_step = order.order_status
            else:
                # If order_status is invalid, log and handle gracefully
                completed_steps = []
                current_step = None

            # Pass status data to the template
            return render_template(
                'track_order.html',
                order_status=order.order_status,
                completed_steps=completed_steps,
                current_step=current_step,
                order_id=order_id,
                order_type=order.order_type,  # Pass the order_type
                store_name="Cafe G6",  # Store details (can be fetched dynamically)
                store_email="support@g6cafe.com",
                store_phone="123-456-7890"
            )
        else:
            return render_template('tracker.html', error="Order not found!")

    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"Error tracking order {order_id}: {str(e)}")
        return render_template('tracker.html', error=f"An error occurred: {str(e)}")


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate admin credentials (implement your logic here)
        if username == 'admin' and password == 'admin123':  # Example validation
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('admin_login.html')


from sqlalchemy.sql import text


@app.route('/process_login', methods=['POST'])
def process_login():
    username = request.form['username']
    password = request.form['password']

    # Example authentication logic (replace with your actual authentication logic)
    sql = text("""
        SELECT * FROM admins 
        WHERE username = :username AND password = :password
    """)

    admins = db.session.execute(
        sql,
        {'username': username, 'password': password}  # Consider hashing passwords
    ).fetchone()

    if admins:
        # Store admin user and store_id in session
        session['admin_id'] = admins.id
        session['store_id'] = admins.store_id  # Storing the store_id for further use

        flash('Login successful!', 'success')
        return redirect(url_for('admin_update_status'))
    else:
        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('admin_login'))


# Example of using raw SQL with text()
def get_order_details(order_id):
    sql = """
        SELECT o.order_id, o.pickup_date, o.delivery_date, o.order_status, r.delivery_rider_id 
        FROM orders o 
        LEFT JOIN delivery_rider r ON o.delivery_rider_id = r.delivery_rider_id
        WHERE o.order_id = :order_id
    """
    # Using SQLAlchemy's text() function to wrap the raw SQL query
    result = db.session.execute(text(sql), {'order_id': order_id})

 #Define the valid statuses based on order type
def get_valid_statuses(order_type):
    if order_type == 'pick_up':
        return ["pending", "preparing", "ready for pick-up", "picked-up", "cancelled"]
    elif order_type == 'delivery':
        return ["pending", "preparing", "out for delivery", "delivered", "cancelled"]
    else:
        return []  # Return empty list if order type is neither 'pick_up' nor 'delivery'




@app.route('/admin_update_status', methods=['GET', 'POST'])
def admin_update_status():
    # Check if the admin is logged in
    if 'admin_id' not in session:
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('admin_login'))

    store_id = session.get('store_id')  # Get store_id from session

    # Define column names for orders and riders
    order_columns = [
        "order_id", "pickup_date", "delivery_date", "order_type", "order_status", "delivery_rider_id"
    ]
    rider_columns = ["delivery_rider_id", "name"]

    # Fetch required data
    orders_result = db.session.execute(
        text(""" 
            SELECT 
                o.order_id, 
                oa.pickup_date, 
                oa.delivery_date,
                oa.order_type,
                t.order_status, 
                t.delivery_rider_id
            FROM orders o
            LEFT JOIN order_address oa ON o.order_id = oa.order_id
            LEFT JOIN trackdetails t ON o.order_id = t.order_id
            WHERE t.store_id = :store_id
        """),
        {'store_id': store_id}
    ).fetchall()

    # Fetch delivery riders
    riders_result = db.session.execute(
        text("""
            SELECT delivery_rider_id, name
            FROM delivery_rider
        """)
    ).fetchall()

    # Convert results into dictionaries
    orders = [dict(zip(order_columns, row)) for row in orders_result]
    riders = [dict(zip(rider_columns, row)) for row in riders_result]

    # Filter out orders with status 'delivered' or 'picked-up'
    orders = [order for order in orders if order['order_status'] not in ['delivered', 'picked-up']]

    if request.method == 'POST':
        # Process the form data for individual order updates
        order_id = request.form.get('update_order_id')

        # If order_id is found in the form data, update it
        if order_id:
            order_status = request.form.get(f'order_status[{order_id}]')
            delivery_rider_id = request.form.get(f'delivery_rider_id[{order_id}]')

            # Update the trackdetails table
            db.session.execute(
                text("""
                    UPDATE trackdetails 
                    SET order_status = :status, 
                        delivery_rider_id = :rider_id 
                    WHERE order_id = :order_id AND store_id = :store_id
                """),
                {'status': order_status, 'rider_id': delivery_rider_id, 'order_id': order_id, 'store_id': store_id}
            )

            db.session.commit()
            # Fetch customer details
            customer_details = db.session.execute(
                text("""
                    SELECT oa.contact_email, oa.contact_name
                    FROM order_address oa
                    WHERE oa.order_id = :order_id
                """),
                {'order_id': order_id}
            ).mappings().fetchone()

            if customer_details:
                recipient_email = customer_details['contact_email']
                contact_name = customer_details['contact_name']

                # Prepare email content based on the new status
                if order_status == 'preparing':
                    subject = "Order Update: Your order is being prepared!"
                    message_body = f"""
                    Dear {contact_name},

                    We are excited to let you know that your order #{order_id} is currently being prepared. 

                    We’ll notify you once it’s ready for pickup or out for delivery. Thank you for your patience!

                    Best regards,
                    G6 Cafe
                    """
                elif order_status == 'ready for pickup':
                    subject = "Order Update: Your order is ready for pickup!"
                    message_body = f"""
                    Dear {contact_name},

                    Your order #{order_id} is now ready for pickup! 

                    Please visit our store during business hours to collect it. If you have any questions, feel free to contact us.

                    Best regards,
                    G6 Cafe
                    """
                elif order_status == 'picked-up':
                    subject = "Order Picked-Up: Thank you for ordering with us!"
                    message_body = f"""
                    Dear {contact_name},

                    We are delighted to let you know that your order #{order_id} has been successfully picked up.

                    Thank you for choosing G6 Cafe. We hope you enjoy your order and look forward to serving you again soon!

                    Best regards,
                    G6 Cafe
                    """
                elif order_status == 'out for delivery':
                    subject = "Order Update: Your order is on its way!"
                    message_body = f"""
                    Dear {contact_name},

                    Good news! Your order #{order_id} is now out for delivery. 

                    Please ensure someone is available to receive it. If you have any questions, feel free to contact us.

                    Best regards,
                    G6 Cafe
                    """
                elif order_status == 'delivered':
                    subject = "Order Delivered: Thank you for ordering with us!"
                    message_body = f"""
                    Dear {contact_name},

                    We are thrilled to let you know that your order #{order_id} has been successfully delivered.

                    Thank you for choosing G6 Cafe. We hope you enjoy your order and look forward to serving you again soon!

                    Best regards,
                    G6 Cafe
                    """
                else:
                    # No email is sent for other statuses
                    subject = None
                    message_body = None

                # Send the email if subject and body are set
                if subject and message_body:
                    msg = Message(subject, recipients=[recipient_email], body=message_body)
                    mail.send(msg)
            flash('Order status updated successfully!', 'success')

            # Re-fetch and re-filter orders after updating
            orders_result = db.session.execute(
                text(""" 
                    SELECT 
                        o.order_id, 
                        oa.pickup_date, 
                        oa.delivery_date,
                        oa.order_type,
                        t.order_status, 
                        t.delivery_rider_id
                    FROM orders o
                    LEFT JOIN order_address oa ON o.order_id = oa.order_id
                    LEFT JOIN trackdetails t ON o.order_id = t.order_id
                    WHERE t.store_id = :store_id
                """),
                {'store_id': store_id}
            ).fetchall()

            # Convert rows to dictionaries again and filter orders
            orders = [dict(zip(order_columns, row)) for row in orders_result]
            orders = [order for order in orders if order['order_status'] not in ['delivered', 'picked-up']]

    return render_template('admin_update_status.html', orders=orders, riders=riders)


if __name__ == '__main__':
    app.run(debug=True)
