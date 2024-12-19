document.addEventListener('DOMContentLoaded', loadCart);

function loadCart() {
    const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
    const cartContainer = document.getElementById('cart-items');
    const cartTotalElement = document.getElementById('cart-total');
    cartContainer.innerHTML = '';

    let total = 0;

    if (cartItems.length === 0) {
        cartContainer.textContent = 'No items in cart.';
        cartTotalElement.textContent = 'Total: P0.00';
    } else {
        cartItems.forEach(item => {
            const cartItemElement = document.createElement('div');
            cartItemElement.classList.add('cart-item');
            cartItemElement.innerHTML = `
                <img src="${item.itemPhoto}" alt="${item.itemName}">
                <h4>${item.itemName}</h4>
                <p>Price: P${parseFloat(item.itemPrice).toFixed(2)}</p>
                <p>Quantity: ${item.quantity}</p>
                <p>Preferences: ${item.preferences}</p>
            `;
            cartContainer.appendChild(cartItemElement);

            total += parseFloat(item.itemPrice) * item.quantity;
        });

        cartTotalElement.textContent = `Total: P${total.toFixed(2)}`;
    }
}

function addToCart(cartItem) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.push(cartItem);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartDisplay();
}

function updateCartDisplay() {
    if (document.getElementById('cart-items')) {
        loadCart();
    }
}

function checkout() {
    // Redirect to checkout.html
    window.location.href = 'checkout.html';
}
