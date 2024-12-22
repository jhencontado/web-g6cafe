document.addEventListener('DOMContentLoaded', function () {
    // Load the default category
    loadMenu('espresso');
    loadCart();

    // Handle category navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            const category = link.getAttribute('href').substring(1);
            loadMenu(category);
        });
    });

    // Handle add-to-cart form submission
    document.getElementById('add-to-cart-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const itemName = document.getElementById('modal-item-name').textContent;
        const itemPhoto = document.getElementById('modal-item-photo').src;
        const itemPriceText = document.getElementById('modal-item-price').textContent;
        const itemPrice = parseFloat(itemPriceText.replace('Price: P', '').trim());
        const quantity = parseInt(document.getElementById('quantity').value);
        const preferences = document.getElementById('preferences').value;

        const cartItem = {
            itemName,
            itemPhoto,
            itemPrice,
            quantity,
            preferences
        };

        addToCart(cartItem);
        closeModal();
    });

    // Call the function to update the order summary when the page loads
    const cartItems = JSON.parse(localStorage.getItem('cart')) || [];

    function updateOrderSummary() {
        if (cartItems.length === 0) {
            document.getElementById('order-summary').innerHTML = 'Your cart is empty.';
            return;
        }

        let totalItems = 0;
        let subtotal = 0;
        let vat = 0;
        let discount = 0;
        let totalAmount = 0;

        cartItems.forEach(item => {
            const itemSubtotal = item.quantity * item.itemPrice;
            subtotal += itemSubtotal;
            totalItems += item.quantity;
        });

        // Apply VAT (12%)
        vat = subtotal * 0.12;

        // Check if PWD/Senior discount is checked
        const isDiscountChecked = document.getElementById('discount-checkbox').checked;
        console.log("Discount checkbox checked:", isDiscountChecked);

        if (isDiscountChecked) {
            discount = subtotal * 0.20; // 20% discount for PWD/Senior
            totalAmount = subtotal - discount;  // Subtotal - Discount
            vat = 0
        } else {
            totalAmount = subtotal;  // Subtotal + VAT (no discount)
        }

        // Update the order summary fields
        document.getElementById('total-items').innerText = totalItems;
        document.getElementById('Subtotal').innerText = `P${subtotal.toFixed(2)}`;
        document.getElementById('vat').innerText = `P${vat.toFixed(2)}`;
        document.getElementById('discount').innerText = `P${discount.toFixed(2)}`;
        document.getElementById('amount-due').innerText = `P${totalAmount.toFixed(2)}`;

        }

        // Display the order items in the summary
        let orderSummaryHtml = '';
        cartItems.forEach(item => {
            const itemSubtotal = item.quantity * item.itemPrice;
            orderSummaryHtml += `
                <div>
                    <p>${item.itemName} - P${item.itemPrice.toFixed(2)} x ${item.quantity} = P${itemSubtotal.toFixed(2)}</p>
                </div>
            `;
        });

        document.getElementById('order-summary').innerHTML = orderSummaryHtml;
    }

    // Update the order summary on page load
    updateOrderSummary();

    // Listen for changes in the PWD/Senior discount checkbox and update the order summary
    document.getElementById('discount-checkbox').addEventListener('change', updateOrderSummary);

    // Handle the form submission to place the order
    document.getElementById('checkout-form').addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent form from submitting normally

        const formData = new FormData(this);

        // Get the form data including personal, delivery, and payment details
        const orderDetails = {
            option: formData.get('option'),
            name: formData.get('name'),
            email: formData.get('email'),
            contact: formData.get('contact'),
            delivery_address: formData.get('address') || '',
            discount_name: formData.get('discount_name') || '',
            discount_id_number: formData.get('discount_id_number') || '',
            payment_method: formData.get('payment'),
            cartItems: cartItems,
            is_discounted: document.getElementById('discount-checkbox').checked
        };

        // Send the order details to the backend API to save the data and generate the order receipt
        fetch('/api/place-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderDetails),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Your order has been placed successfully! Receipt number: ' + data.receiptNumber);
                // Optionally clear the cart after placing the order
                localStorage.removeItem('cart');
                window.location.href = '/';
            } else {
                alert('Failed to place order. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error placing order:', error);
            alert('An error occurred while placing the order. Please try again.');
        });
    });
});

function loadMenu(category) {
    fetch(`/api/menu?category=${category}`)
        .then(response => response.json())
        .then(data => {
            const menuContainer = document.getElementById('menu-items');
            menuContainer.innerHTML = ''; // Clear existing menu items

            data.forEach(item => {
                const menuItem = document.createElement('div');
                menuItem.classList.add('product-card');
                menuItem.id = item.category_name.toLowerCase().replace(' ', '-');

                const image = item.photo ? `<img src="${item.photo}" alt="${item.item_name}">` : '';
                menuItem.innerHTML = `
                    ${image}
                    <h4>${item.item_name}</h4>
                    <p>Category: ${item.category_name}</p>
                    <p>Price: P${parseFloat(item.unit_price).toFixed(2)}</p>
                    <button onclick="openModal('${item.item_name}', '${item.photo}', '${item.unit_price}')">Add to Cart</button>
                `;

                menuContainer.appendChild(menuItem);
            });
        })
        .catch(error => {
            console.error('Error fetching menu:', error);
            document.getElementById('menu-items').innerHTML = '<p>Error loading menu.</p>';
        });
}

function openModal(itemName, itemPhoto, itemPrice) {
    document.getElementById('modal-item-name').textContent = itemName;
    document.getElementById('modal-item-photo').src = itemPhoto;
    document.getElementById('modal-item-price').textContent = `Price: P${parseFloat(itemPrice).toFixed(2)}`;
    document.getElementById('cart-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('cart-modal').style.display = 'none';
}

function addToCart(cartItem) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];

    // Check if the item already exists in the cart with the same preferences
    const existingItemIndex = cart.findIndex(
        item => item.itemName === cartItem.itemName && item.preferences === cartItem.preferences
    );

    if (existingItemIndex !== -1) {
        // Update quantity if item exists
        cart[existingItemIndex].quantity += cartItem.quantity;
    } else {
        // Add new item to cart
        cart.push(cartItem);
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    alert(`${cartItem.quantity} x ${cartItem.itemName} added to cart!`);
    updateCartDisplay();
}

function loadCart() {
    const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
    const cartContainer = document.getElementById('cart-items');

    if (!cartContainer) return; // Prevent errors if cart-items element does not exist

    cartContainer.innerHTML = '';

    if (cartItems.length === 0) {
        cartContainer.innerHTML = '<tr><td colspan="4">Your cart is empty.</td></tr>';
    } else {
        let totalItems = 0;
        let totalPrice = 0;

        cartItems.forEach(item => {
            const subtotal = item.quantity * item.itemPrice;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><img src="${item.itemPhoto}" alt="${item.itemName}" width="50"> ${item.itemName}</td>
                <td>${item.quantity}</td>
                <td>P${item.itemPrice.toFixed(2)}</td>
                <td>P${subtotal.toFixed(2)}</td>
            `;
            cartContainer.appendChild(row);

            totalItems += item.quantity;
            totalPrice += subtotal;
        });

        document.getElementById('total-items').textContent = totalItems;
        document.getElementById('total-price').textContent = `P${totalPrice.toFixed(2)}`;
    }
}

function calculateTotal() {
    let priceInput = document.getElementById('price').value;
    let quantityInput = document.getElementById('quantity').value;

    // Convert inputs to numbers
    let price = parseFloat(priceInput);
    let quantity = parseInt(quantityInput);

    // Check for NaN
    if (isNaN(price) || isNaN(quantity)) {
        alert("Please enter valid numbers for price and quantity.");
        return;
    }

    // Calculate subtotal and total
    let subtotal = price * quantity;
    let tax = subtotal * 0.1; // Example tax calculation (10%)
    let total = subtotal;

    // Display the results
    document.getElementById('subtotal').innerText = subtotal.toFixed(2);
    document.getElementById('total').innerText = total.toFixed(2);
}

function updateCartDisplay() {
    if (document.getElementById('cart-items')) {
        loadCart();
    }
}
