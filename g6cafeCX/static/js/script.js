document.addEventListener('DOMContentLoaded', () => {
    loadMenu('espresso'); // Load the default category

    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            const category = link.getAttribute('href').substring(1);
            loadMenu(category);
        });
    });

    document.getElementById('add-to-cart-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const itemName = document.getElementById('modal-item-name').textContent;
        const itemPhoto = document.getElementById('modal-item-photo').src;
        const itemPrice = document.getElementById('modal-item-price').textContent.split(' ')[1];
        const quantity = document.getElementById('quantity').value;
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

    loadCart();
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
    document.getElementById('modal-item-photo').src = `/static/images/${itemPhoto}`;
    document.getElementById('modal-item-price').textContent = `Price: P${parseFloat(itemPrice).toFixed(2)}`;
    document.getElementById('cart-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('cart-modal').style.display = 'none';
}

function addToCart(cartItem) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart.push(cartItem);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartDisplay();
}

function loadCart() {
    const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
    const cartContainer = document.getElementById('cart-items');
    cartContainer.innerHTML = '';

    if (cartItems.length === 0) {
        cartContainer.textContent = 'No items in cart.';
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
        });
    }
}

function updateCartDisplay() {
    if (document.getElementById('cart-items')) {
        loadCart();
    }
}
