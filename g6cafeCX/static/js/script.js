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

    // Initial load of the cart
    loadCart();

    // Event listener for store locator form
    document.getElementById('storeLocatorForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const location = document.getElementById('locationInput').value;
        const resultsDiv = document.getElementById('store-results');

        // Use geocoding service to find coordinates
        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${location}`)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    const locationLatLng = [data[0].lat, data[0].lon];
                    map.setView(locationLatLng, 12);

                    // Remove old user marker if exists
                    if (userMarker) {
                        userMarker.remove();
                    }

                    // Display marker for entered location
                    userMarker = L.marker(locationLatLng).addTo(map)
                        .bindPopup("Your Location")
                        .openPopup();

                    // Fetch nearest store from Flask API
                    fetch(`/find_nearest_store`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ address: location })
                    })
                    .then(response => response.json())
                    .then(data => {
                        const stores = data.nearestStore ? [data.nearestStore] : [];

                        resultsDiv.innerHTML = '';
                        if (stores.length > 0) {
                            stores.forEach(store => {
                                const storeDiv = document.createElement('div');
                                storeDiv.classList.add('store-info');
                                storeDiv.innerHTML = `<strong>${store.name}</strong><br>${store.address}<br><em>${store.distance} km</em>`;
                                resultsDiv.appendChild(storeDiv);

                                // Add marker for each store
                                L.marker([store.lat, store.lng]).addTo(map)
                                    .bindPopup(`<strong>${store.name}</strong><br>${store.address}`)
                                    .openPopup();
                            });
                        } else {
                            resultsDiv.innerHTML = '<p>No nearby stores found.</p>';
                        }
                    })
                    .catch(error => {
                        console.log('Error fetching stores:', error);
                        resultsDiv.innerHTML = `<p>Error fetching nearby stores.</p>`;
                    });
                } else {
                    resultsDiv.innerHTML = '<p>Location not found.</p>';
                }
            })
            .catch(error => {
                console.log('Error with geocoding:', error);
            });
    });

    // Initialize map on page load
    initMap();
});

// Initialize OpenStreetMap with Leaflet
let map, userMarker;
function initMap() {
    map = L.map('map').setView([14.565111, 121.029889], 12); // Default center (replace with your desired location)

    // Tile layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

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


function updateCartDisplay() {
    if (document.getElementById('cart-items')) {
        loadCart();
    }
}


function selectStore(storeName) {
    alert(`You selected: ${storeName}`);
    // Optionally, you could redirect the user to the next step or perform other actions here
}
