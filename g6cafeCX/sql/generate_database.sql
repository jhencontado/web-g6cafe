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
    pwdsenior_name VARCHAR(100) NOT NULL,
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
    delivery_date DATETIME NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(50) NULL,
    contact_number INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

-- Table for order_payment_details 
DROP TABLE IF EXISTS order_payment_details;
CREATE TABLE order_payment_details (
	order_payment_details_id INT AUTO_INCREMENT NOT NULL primary key,
    order_id INT NOT NULL,
    payment_option VARCHAR(50) NOT NULL,
    gcash_ref_number INT NULL,
    change_for_cash INT NULL,
    card_name VARCHAR(100) NULL, 
    card_number INT NULL,
    car_exp_month INT NULL,
    card_exp_year INT NULL,
    card_cvv INT NULL,
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
('Pasta','Spaghetti Bolognaise','Spaghetti Bolognese.jpg"',185),
('Pasta','Lasagne','lasagna.jpg"',190),
('Pasta','Pasta Carbonara','Pasta Carbonara.jpg',150),
('Pasta','Ravioli','ravioli.jpg',200),
('Pasta','Spaghetti alle Vongole','Spaghetti alle Vongole.jpg',200),
('Pasta','Macaroni Cheese','Macaroni Cheese.jpg',190);

/* ---------------------------------------------- SAMPLE DATA---------------------------------------------------------- */
/* ----------------------------------------------sample 1---------------------------------------------------------- */
INSERT INTO orders (subtotal, vat_amount, discount_amount, net_amount, tender_amount, change_amount, receipt_number)
VALUES
(500.00, 50.00, 50.00, 500.00 - 50.00 + 50.00, 500.00, 0.00, 'REC001'); -- PWD customer (with discount)  
SET @order_id = (SELECT LAST_INSERT_ID());
 -- Insert items for order 1 (PWD customer)
INSERT INTO order_details (order_id, item_id, quantity,subtotal, order_preference)
VALUES
(@order_id, 1, 2,300,'No sugar'),  -- 2 Americano
(@order_id, 2, 1,150,'Extra foam');  -- 1 Cappuccino   

INSERT INTO pwdsenior_details (order_id, discount_type, customer_name, id_number, discount_amount)
VALUES	(@order_id, 'PWD', 'John Doe', 'PWD123456', 50.00);
    
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
(3, 5, 3,525,'Hot'),  -- 3 Macchiatos
(3, 6, 1,180,'Cold');  -- 1 Mocha

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





/* ---------------------------------------------- Display tables---------------------------------------------------------- */
    
select * from menu_details;   
select * from pwdsenior_details ;      
select * from orders; 
select * from order_details;
select distinct pwdsenior_details;
select distinct pwd_senior_id from pwdsenior_details;


/*-----------------store list---------------------*/
CREATE TABLE stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    lat DECIMAL(10, 8) NOT NULL,
    lng DECIMAL(11, 8) NOT NULL,
    address VARCHAR(255) NOT NULL,
    business_hours VARCHAR(50) NOT NULL);
    
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

