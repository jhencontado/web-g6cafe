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
    const addToCartForm = document.getElementById('add-to-cart-form');
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const itemNameEl = document.getElementById('modal-item-name');
            const itemPhotoEl = document.getElementById('modal-item-photo');
            const itemPriceEl = document.getElementById('modal-item-price');
            const quantityInputEl = document.getElementById('edit-item-quantity');
            const preferencesEl = document.getElementById('preferences');

            if (!itemNameEl || !itemPhotoEl || !itemPriceEl || !quantityInputEl || !preferencesEl) {
                alert('Error: Modal elements missing.');
                return;
            }

            const itemName = itemNameEl.textContent;
            const itemPhoto = itemPhotoEl.src;
            const itemPrice = parseFloat(itemPriceEl.textContent.replace('P', '').trim());
            const quantity = parseInt(quantityInputEl.value);
            const preferences = preferencesEl.value;

            if (isNaN(itemPrice) || isNaN(quantity) || quantity <= 0) {
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
    }

    // Initial load of the cart
    loadCart();

    // Handle increment/decrement functionality
    const plus = document.querySelector(".plus");
    const minus = document.querySelector(".minus");
    const num = document.querySelector(".num");

    let a = 1;

    if (plus && minus && num) {
        num.innerText = a.toString().padStart(2, '0'); // Initial display

        plus.addEventListener("click", () => {
            a++;
            num.innerText = a.toString().padStart(2, '0'); // Update display
            document.getElementById('edit-item-quantity').value = a; // Sync quantity input
        });

        minus.addEventListener("click", () => {
            if (a > 1) {
                a--;
                num.innerText = a.toString().padStart(2, '0'); // Update display
                document.getElementById('edit-item-quantity').value = a; // Sync quantity input
            }
        });
    }
});

function loadMenu(category) {
    fetch(`/api/menu?category=${category}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const menuContainer = document.getElementById('menu-items');
            menuContainer.innerHTML = ''; // Clear existing menu items

            if (!data || data.length === 0) {
                menuContainer.innerHTML = '<p>No menu items found.</p>';
                return;
            }

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

    // Reset quantity in modal
    const quantityInput = document.getElementById('edit-item-quantity');
    if (quantityInput) {
        quantityInput.value = 1;
        const num = document.querySelector(".num");
        if (num) {
            num.innerText = '01';
        }
    }
}

function closeModal() {
    document.getElementById('cart-modal').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
            // Update cart count when the page loads
            updateCartCount();
        });

        function updateCartCount() {
            const cart = JSON.parse(localStorage.getItem('cart')) || [];
            const cartCountEl = document.getElementById('cart-count');
            if (cartCountEl) {
                const cartCount = cart.reduce((acc, item) => acc + item.quantity, 0);
                cartCountEl.textContent = cartCount;
            }
        }

        function addToCart(cartItem) {
            if (!cartItem || !cartItem.itemName || !cartItem.quantity || cartItem.quantity <= 0) {
                alert("Error: Invalid item or quantity.");
                return;
            }

            let cart = JSON.parse(localStorage.getItem('cart')) || [];
            const existingItemIndex = cart.findIndex(
                item => item.itemName === cartItem.itemName && item.preferences === cartItem.preferences
            );

            if (existingItemIndex !== -1) {
                cart[existingItemIndex].quantity += cartItem.quantity;
            } else {
                cart.push(cartItem);
            }

            localStorage.setItem('cart', JSON.stringify(cart));

            // Update cart count in UI
            updateCartCount();

            alert(`${cartItem.quantity} x ${cartItem.itemName} added to cart!`);
            updateCartDisplay();
        }

        function updateCartDisplay() {
            // Your code for updating the cart display (e.g., showing cart items, total price)
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

function updateCartDisplay() {
    if (document.getElementById('cart-items')) {
        loadCart();
    }
}

// Initialize OpenStreetMap with Leaflet
let map, userMarker;
function initMap() {
    map = L.map('map').setView([14.565111, 121.029889], 12); // Default center (replace with your desired location)

    // Tile layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}
// Function to handle store selection
function selectStore(storeName, storeLocation) {
    // Store the selected store's name and location in localStorage
    const selectedStore = {
        name: storeName,
        location: storeLocation
    };

    localStorage.setItem('selectedStore', JSON.stringify(selectedStore));

    // Optionally, you can show a message or redirect the user to the checkout page
    alert("Store selected: " + storeName);
    // Redirect to checkout page if needed (uncomment the next line if desired)
    // window.location.href = "/checkout";
}
