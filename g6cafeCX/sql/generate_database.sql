/* ---------------------------------------------- DATABASE CREATION/DROP---------------------------------------------------------- */

drop database if exists g6cafe;
create database g6cafe;
use g6Cafe;

/* --------------------------------------------------TABLE CREATION SYNTAX------------------------------------------------------ */

-- Table for orders
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    date_time DATETIME DEFAULT NOW(),
    subtotal DECIMAL(10, 2) NOT NULL,  -- total before tax and discount
    vat_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NULL,
    net_amount DECIMAL(10, 2) NOT NULL,  -- total after tax and discount
    tender_amount DECIMAL(10, 2) NOT NULL,
    change_amount DECIMAL(10, 2) NOT NULL,
    receipt_number VARCHAR(50) NOT NULL UNIQUE
);

-- Table for pwdsenior_details (used for senior/PWD discount details)
DROP TABLE IF EXISTS pwdsenior_details;
CREATE TABLE pwdsenior_details (
    pwdsenior_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    order_id INT NULL,
    discount_type VARCHAR(50) NULL,
    customer_name VARCHAR(100) NOT NULL,
    id_number VARCHAR(100) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

-- Table for menu_details (menu items)
DROP TABLE IF EXISTS menu_details;
CREATE TABLE menu_details (
    item_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	category_name varchar(100) not null,
    item_name VARCHAR(100) NOT NULL,
    photo VARCHAR(255) NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Table for order_details (specific items in each order)
DROP TABLE IF EXISTS order_details;
CREATE TABLE order_details (
	order_item_id INT AUTO_INCREMENT NOT NULL primary key,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,/* quantity*unit_price*/
    order_preference TEXT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_details (item_id) ON DELETE CASCADE
);
-- Table for order_address (address of the customer)
DROP TABLE IF EXISTS order_address;
CREATE TABLE order_address (
	order_address_id INT AUTO_INCREMENT NOT NULL primary key,
    order_id INT NOT NULL,
    address TEXT NULL,
    pickup_date DATETIME NULL, 
    pickup_time TIME NULL,
    delivery_date DATETIME NULL, 
    delivery_time TIME NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(50) NULL,
    contact_number VARCHAR(15) NOT NULL,
    delivery_instruction TEXT NULL,
    order_type varchar(50) not null,

    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);
CREATE INDEX idx_order_type ON order_address(order_type);
-- Table for order_payment_details
DROP TABLE IF EXISTS order_payment_details;
CREATE TABLE order_payment_details (
	order_payment_details_id INT AUTO_INCREMENT NOT NULL primary key,
    order_id INT NOT NULL,
    payment_option VARCHAR(50) NOT NULL,
    gcash_ref_number LONG NULL,
    change_for_cash DECIMAL(10, 2) NULL NULL,
    card_name VARCHAR(100) NULL,
    card_number LONG NULL,
    card_exp_month INT NULL,
    card_exp_year INT NULL,
    card_cvv VARCHAR(50) NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);


/* ---------------------------------------------- ADD DATA IN MENU_DETAILS---------------------------------------------------------- */

INSERT INTO menu_details (category_name, item_name, photo, unit_price)
VALUES
('Espresso','Americano','americano.jpeg',150),
('Espresso','Cappuccino','cappucino.png',150),
('Espresso','Double Espresso','double espresso.png',125),
('Espresso','Latte','latte.png',175),
('Espresso','Macchiato','macchiato.png',175),
('Espresso','Mocha','mocha.png',180),
('Espresso','White Mocha','white mocha.png',150),
('Tea','Earl Grey','earl grey.png',120),
('Tea','English Breakfast','english breakfast.png',110),
('Tea','Green Tea','green tea.png',110),
('Tea','Jasmine Tea','jasmine tea.png',115),
('Tea','Black Tea','black tea.png',125),
('Tea','Red Tea','red tea.png',130),
('Ice Blended','Caramel','caramel.png',125),
('Ice Blended','Coffee Jelly','coffee jelly.png',130),
('Ice Blended','Cookies and Cream','cookies and cream.png',150),
('Ice Blended','Hazelnut Mocha','hazel nut mocha.png',155),
('Ice Blended','Matcha Cream','matcha cream.png',135),
('Ice Blended','Mint Chocolate Chip','mint chocolate chips.png',150),
('Ice Blended','Strawberry Cream'	,'strawberry cream.png',150),
('Ice Blended','Vanilla Bean','vanilla bean.jpg',135),
('Pastries','Bagels','bagels.jpg',90),
('Pastries','Donut','donut.jpg',70	),
('Pastries','Muffins','muffin.jpg',75),
('Pastries','Biscotto','biscotto.jpg',80),
('Pasta','Spaghetti Bolognaise','Spaghetti Bolognese.jpg',185),
('Pasta','Lasagne','lasagna.jpg',190),
('Pasta','Pasta Carbonara','Pasta Carbonara.jpg',150),
('Pasta','Ravioli','ravioli.jpg',200),
('Pasta','Spaghetti alle Vongole','Spaghetti alle Vongole.jpg',200),
('Pasta','Macaroni Cheese','Macaroni Cheese.jpg',190);

/* ---------------------------------------------- SAMPLE DATA---------------------------------------------------------- */
/* ----------------------------------------------sample 1---------------------------------------------------------- */
-- Insert into orders table
INSERT INTO orders (subtotal, vat_amount, discount_amount, net_amount, tender_amount, change_amount, receipt_number)
VALUES
(500.00, 50.00, 50.00, 500.00 - 50.00 + 50.00, 500.00, 0.00, 'REC006'); -- PWD customer (with discount)

-- Get the last inserted order ID
SET @order_id = (SELECT LAST_INSERT_ID());

-- Insert items for the order (PWD customer)
INSERT INTO order_details (order_id, item_id, quantity, subtotal, order_preference)
VALUES
(@order_id, 1, 2, 300, 'No sugar'),  -- 2 Americano
(@order_id, 2, 1, 150, 'Extra foam');  -- 1 Cappuccino

-- Insert into pwdsenior_details table
INSERT INTO pwdsenior_details (order_id, discount_type, customer_name, id_number, discount_amount)
VALUES
(@order_id, 'PWD', 'John Doe', 'PWD123456', 50.00);

-- Insert into order_address table
INSERT INTO order_address (
    order_id,
    address,
    pickup_date,
    delivery_date,
    contact_name,
    contact_email,
    contact_number,
    delivery_instruction,
    order_type
)
VALUES
(@order_id, '123 Elm Street, Springfield, IL', '2025-01-15 10:00:00', '2025-01-15 14:00:00', 'John Doe', 'johndoe@example.com', 1234567890, null,'delivery');

-- Insert payment details for a cash payment
INSERT INTO order_payment_details (
    order_id,
    payment_option,
    gcash_ref_number,
    change_for_cash,
    card_name,
    card_number,
    card_exp_month,
    card_exp_year,
    card_cvv
)
VALUES
(@order_id, 'Cash', NULL, 100, NULL, NULL, NULL, NULL, NULL), -- Cash payment with change

-- Insert payment details for a GCash payment
(@order_id, 'GCash', 123456789, NULL, NULL, NULL, NULL, NULL, NULL), -- GCash payment with reference number

-- Insert payment details for a card payment
(@order_id, 'Credit Card', NULL, NULL, 'John Doe', 1234567812345678, 12, 2025, 123); -- Card payment with all details
/* ----------------------------------------------sample 2---------------------------------------------------------- */


INSERT INTO orders (subtotal, vat_amount, discount_amount, net_amount, tender_amount, change_amount, receipt_number)
VALUES(400.00, 40.00, 30.00, 400.00 - 30.00 + 40.00, 400.00, 0.00, 'REC002');   -- Senior customer (with discount)
SET @order_id = (SELECT LAST_INSERT_ID());

-- Insert PWD and Senior discount details
INSERT INTO pwdsenior_details (order_id, discount_type, customer_name, id_number, discount_amount)
VALUES	(@order_id, 'Senior', 'Jane Smith', 'SEN987654', 30.00);
-- Senior customer with 30 discount

-- Insert items for order 2 (Senior customer)
INSERT INTO order_details (order_id, item_id, quantity,subtotal, order_preference)
VALUES
(@order_id, 3, 1,125,'No milk'),  -- 1 Double Espresso
(@order_id, 4, 2,350,'With milk');  -- 2 Lattes

/* ----------------------------------------------sample 3---------------------------------------------------------- */
-- Insert Orders with PWD, Senior, and Regular customers
INSERT INTO orders (subtotal, vat_amount, discount_amount, net_amount, tender_amount, change_amount, receipt_number)
VALUES (300.00, 30.00, 0.00, 300.00 + 30.00, 300.00, 0.00, 'REC003');

-- Insert items for order 3 (Regular customer)
INSERT INTO order_details (order_id, item_id, quantity,subtotal, order_preference)
VALUES
(@order_id, 5, 3,525,'Hot'),  -- 3 Macchiatos
(@order_id, 6, 1,180,'Cold');  -- 1 Mocha

/* ----------------------------------------------sample 4---------------------------------------------------------- */

-- Insert Orders with PWD, Senior, and Regular customers
INSERT INTO orders (subtotal, vat_amount, discount_amount, net_amount, tender_amount, change_amount, receipt_number)
VALUES
(600.00, 60.00, 0.00, 600.00 + 60.00, 600.00, 0.00, 'REC004'); -- Regular customer (no discount)
SET @order_id = (SELECT LAST_INSERT_ID());

-- Insert items for order 4 (Regular customer)
INSERT INTO order_details (order_id, item_id, quantity,subtotal, order_preference)
VALUES
(@order_id, 7, 2,300, 'No ice'),  -- 2 White Mochas
(@order_id, 8, 1,120, 'With honey');  -- 1 Earl Grey

/* ----------------------------------------------sample 5---------------------------------------------------------- */

-- Insert Orders with PWD, Senior, and Regular customers
INSERT INTO orders (subtotal, vat_amount, discount_amount, net_amount, tender_amount, change_amount, receipt_number)
VALUES
(700.00, 70.00, 70.00, 700.00 - 70.00 + 70.00, 700.00, 0.00, 'REC005');  -- PWD customer (with discount)
SET @order_id = (SELECT LAST_INSERT_ID());

-- Insert items for order 5 (PWD customer)
INSERT INTO order_details (order_id, item_id, quantity,subtotal, order_preference)
VALUES
(@order_id, 9, 2,220, 'With milk'),  -- 2 Red Teas
(@order_id, 10, 1,110, 'Black');  -- 1 Green Tea

INSERT INTO pwdsenior_details (order_id, discount_type, customer_name, id_number, discount_amount)
VALUES	(@order_id, 'Senior', 'Alan Walker', 'SEN9976987', 30.00);

INSERT into pwdsenior_details (order_id, discount_type, customer_name, id_number, discount_amount)
VALUES	(@order_id, 'Senior', 'Alan Walker', 'SEN9976987', 30.00);

CREATE TABLE stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    lat DECIMAL(10, 8) NOT NULL,
    lng DECIMAL(11, 8) NOT NULL,
    address VARCHAR(255) NOT NULL,
    business_hours VARCHAR(50) NOT NULL
);

INSERT INTO stores (name, lat, lng, address, business_hours) VALUES
('G6 Cafe Hotel Sogo - EDSA Guadalupe', 14.564667, 121.045167, '17B Epifanio de los Santos Ave, Makati, 1554 Metro Manila', '8am-10pm'),
('G6 Cafe Makati Ave.', 14.565111, 121.029889, '7850 Makati Ave, Makati, Metro Manila', '10am-10pm'),
('G6 Cafe Timog Ave., Quezon City', 14.634907, 121.037490, 'J2MQ+W2J, Ushio building, Scout Torillo, corner Timog Avenue, Brgy, Quezon City', '8am-10pm'),
('G6 Cafe UST', 14.611944, 120.988250, 'Unit 102 1211 Don Jose Building V. Concepcion St, Dapitan St, Sampaloc, Manila, 1015 Metro Manila', '6am-11pm'),
('G6 Cafe Caloocan', 14.651833, 120.977083, '94 10th Ave, Grace Park West, Manila, Metro Manila', '8am-10pm'),
('G6 Cafe Karuhatan Valenzuela City', 14.683806, 120.977361, 'MacArthur Hwy, Valenzuela, 1440 Metro Manila', '8am-10pm'),
('G6 Cafe Valenzuela', 14.705417, 120.989417, '104 Paso de Blas Rd, Valenzuela, Metro Manila', '10am-10pm'),
('G6 Cafe Tondo, Manila', 14.607000, 120.966861, '560 Lakandula St, Tondo, Manila, 1013 Metro Manila', '10am-10pm'),
('G6 Cafe Malabon', 14.660417, 120.951389, '59 Gen. Luna St, Malabon, 1470 Metro Manila', '8am-10pm'),
('G6 Cafe Marilao', 14.765313, 120.963039, '9013 (Stall, 2 MacArthur Hwy, Marilao, 3019 Bulacan', '6am-11pm'),
('G6 Cafe Maginhawa', 14.646462, 121.059941, '101 Maginhawa, Diliman, Lungsod Quezon, 1101 Kalakhang Maynila', '8am-10pm'),
('G6 Cafe Eastwood, Quezon City', 14.610477, 121.081375, 'GF Unit 3E, Eastwood, Citywalk 2, Quezon City, 1110 Metro Manila', '10am-10pm'),
('G6 Cafe Tomas Morato Ave., Quezon City', 14.637358, 121.035747, 'Scout Borromeo, corner Tomas Morato Ave, Quezon City, 1103 Metro Manila', '10am-10pm'),
('G6 Cafe East Kapitolyo, Pasig City', 14.569904, 121.060237, 'No. 46 E Capitol Dr, Pasig, 1603 Metro Manila', '8am-10pm'),
('G6 Cafe Fairview Terraces, Quezon City', 14.735938, 121.060000, 'Upper Ground Central Garden Ayala Fairview Terraces Maligaya corn, Quirino Hwy, Quezon City, 1118 Metro Manila', '10am-10pm');

use g6cafe;

INSERT INTO menu_details (category_name, item_name, photo, unit_price)
VALUES ('Promo', 'Macha + Carbonara', 'promo1.jpg', 265),
('Promo', 'Macchiato + Bagels', 'promo2.jpg', 245),
('Promo', 'Van Bean + Mac Cheese ', 'promo3.jpg', 305),
('Promo', 'Macchiato + Lasagne', 'promo4.jpg', 345),
('Promo', 'Latte + Muffins', 'promo5.jpg', 230),
('Promo', 'Macha Cream + Ravioli', 'promo6.jpg', 315),
('Promo', 'G6 Thumbler White', 'white.jpg', 450),
('Promo', 'G6 Thumbler Pink', 'pink.jpg', 450),
('Promo', 'G6 Thumbler Black', 'black.jpg', 450);


-- Table for delivery riders
DROP TABLE IF EXISTS delivery_rider;
CREATE TABLE delivery_rider (
	delivery_rider_id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	vehicle_plate_number VARCHAR(50) NOT NULL,
	vehicle_model VARCHAR(255) NOT NULL,
	vehicle_color VARCHAR(50) NOT NULL,
	store_id INT NOT NULL,
    FOREIGN KEY (store_id) REFERENCES stores (id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS admins;
CREATE TABLE admins (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	username VARCHAR(50) NOT NULL UNIQUE,
	email VARCHAR(100) NOT NULL UNIQUE,
	password VARCHAR(200) NOT NULL
);
ALTER TABLE admins ADD COLUMN store_id INT,
ADD CONSTRAINT fk_store_id FOREIGN KEY (store_id) REFERENCES stores(id);



INSERT INTO admins (username, email, password, store_id)
VALUES
  ('admin_1', 'admin1@example.com', 'Admin@1', 1),
  ('admin_2', 'admin2@example.com', 'Admin@2',2),
  ('admin_3', 'admin3@example.com', 'Admin@3', 3),
  ('admin_4', 'admin4@example.com', 'Admin@4', 4),
  ('admin_5', 'admin5@example.com', 'Admin@5', 5),
  ('admin_6', 'admin6@example.com', 'Admin@6', 6),
  ('admin_7', 'admin7@example.com', 'Admin@7', 7),
  ('admin_8', 'admin8@example.com', 'Admin@8', 8),
  ('admin_9', 'admin9@example.com', 'Admin@9', 9),
  ('admin_10', 'admin10@example.com', 'Admin@10', 10),
  ('admin_11', 'admin11@example.com', 'Admin@11', 11),
  ('admin_12', 'admin12@example.com', 'Admin@12', 12),
  ('admin_13', 'admin13@example.com', 'Admin@13', 13),
  ('admin_14', 'admin14@example.com', 'Admin@14', 14),
  ('admin_15', 'admin15@example.com', 'Admin@15', 15);



    -- Insert values into delivery_rider table
INSERT INTO delivery_rider (name, vehicle_plate_number, vehicle_model, vehicle_color, store_id)
VALUES
    ('John Doe', 'ABC1234', 'Yamaha NMAX', 'Black', 1),
    ('Jane Smith', 'XYZ5678', 'Honda Click', 'White', 2),
    ('Michael Johnson', 'MNO9876', 'Suzuki Raider', 'Red', 3),
    ('Emily Davis', 'JKL5432', 'Yamaha Aerox', 'Blue', 4),
    ('Chris Brown', 'DEF2468', 'Honda Beat', 'Green', 5),
    ('Sarah Wilson', 'GHI1357', 'Kawasaki Ninja', 'Black', 6),
    ('David Lee', 'TUV8642', 'Yamaha Mio', 'Gray', 7),
    ('Anna Martinez', 'QRS5791', 'Suzuki Skydrive', 'Black', 8),
    ('Paul Anderson', 'WXY3214', 'Honda XRM', 'White', 9),
    ('Laura Hernandez', 'ZXC8529', 'Yamaha Sniper', 'Blue', 10),
    ('James Carter', 'BNM6547', 'Suzuki Burgman', 'Red', 11),
    ('Jessica Walker', 'RTY7412', 'Honda PCX', 'Green', 12),
    ('Brian Harris', 'UIO9638', 'Kymco Like', 'Yellow', 13),
    ('Olivia Moore', 'PLM2583', 'Vespa Primavera', 'Pink', 14),
    ('Daniel Lewis', 'FGH7531', 'SYM Jet X', 'Orange', 15);

-- Table for trackdetails
DROP TABLE IF EXISTS trackdetails;
CREATE TABLE trackdetails (
	track_id INT AUTO_INCREMENT PRIMARY KEY,
	order_id INT NOT NULL,
	store_id INT NOT NULL,
	order_status ENUM('pending', 'preparing', 'ready for pick-up ','picked-up','out for delivery', 'delivered', 'cancelled') NOT NULL,
    order_type varchar(50)not null,
	delivery_rider_id INT NOT NULL,
	FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
	FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (order_type) REFERENCES order_address(order_type) ON DELETE CASCADE,
	FOREIGN KEY (delivery_rider_id) REFERENCES delivery_rider(delivery_rider_id)
);


INSERT INTO trackdetails (order_id, store_id,order_status,order_type,delivery_rider_id)
values (@order_id, 1,'pending','delivery',1),
(@order_id, 1,'pending','delivery',1),
(@order_id, 2,'pending','delivery',2),
(@order_id, 2,'pending','delivery',2),
(@order_id, 3,'pending','delivery',2),
(@order_id, 3,'pending','delivery',2);



/* ---------------------------------------------- Display tables---------------------------------------------------------- */
use g6cafe;
select * from menu_details;
select * from pwdsenior_details ;
select * from order_address;
select * from orders;
select * from order_details;
select distinct * from pwdsenior_details;
SELECT * FROM ORDER_PAYMENT_DETAILS;
SELECT * FROM ORDER_ADDRESS;
select *from stores;
select * from delivery_rider;
select* from trackdetails;
select * from Admins;