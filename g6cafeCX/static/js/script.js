document.addEventListener('DOMContentLoaded', () => {
    // Load the default category
    loadMenu('espresso');

    // Handle category navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            const category = link.getAttribute('href').substring(1);
            loadMenu(category);
        });
    });

    // Handle add-to-cart form submission
    document.getElementById('add-to-cart-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const itemName = document.getElementById('modal-item-name').textContent;
        const itemPhoto = document.getElementById('modal-item-photo').src;
        const itemPriceText = document.getElementById('modal-item-price').textContent;
        const itemPrice = parseFloat(itemPriceText.replace('P', '').trim());
        const quantity = parseInt(document.getElementById('edit-item-quantity').value);
        const preferences = document.getElementById('preferences').value;

        console.log("Debugging Values:");
        console.log({ itemName, itemPhoto, itemPriceText, itemPrice, quantity, preferences });

        if (isNaN(itemPrice) || isNaN(quantity)) {
            alert('Error: Invalid price or quantity. Please check your input.');
            return;
        }

        const cartItem = {
            itemName,
            itemPhoto,
            itemPrice,
            quantity,
            preferences,
        };

        addToCart(cartItem);
        closeModal();
    });

    // Initial load of the cart
    loadCart();

    // Handle increment/decrement functionality
    const plus = document.querySelector(".plus");
    const minus = document.querySelector(".minus");
    const num = document.querySelector(".num");

    let a = 1;

    // Check if all the elements exist before adding event listeners
    if (plus && minus && num) {
        plus.addEventListener("click", () => {
            a++;
            a = a < 10 ? "0" + a : a;
            num.innerText = a;
            document.getElementById('edit-item-quantity').value = a; // Sync quantity input
        });

        minus.addEventListener("click", () => {
            if (a > 1) {
                a--;
                a = a < 10 ? "0" + a : a;
                num.innerText = a;
                document.getElementById('edit-item-quantity').value = a; // Sync quantity input
            }
        });
    }
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
                    <p>P${parseFloat(item.unit_price).toFixed(2)}</p>
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
    document.getElementById('modal-item-price').textContent = `P${parseFloat(itemPrice).toFixed(2)}`;
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
    let total = subtotal + tax;

    // Display the results
    document.getElementById('subtotal').innerText = subtotal.toFixed(2);
    document.getElementById('total').innerText = total.toFixed(2);
}

function updateCartDisplay() {
    if (document.getElementById('cart-items')) {
        loadCart();
    }
}
