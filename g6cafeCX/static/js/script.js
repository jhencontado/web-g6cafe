document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category') || 'promo'; // Default to 'espresso' if no category in URL

    // Ensure that the category element exists before trying to load it
    if (category) {
        loadMenu(category);
    }

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
    // Set modal item details
    document.getElementById('modal-item-name').textContent = itemName;
    document.getElementById('modal-item-photo').src = itemPhoto;
    document.getElementById('modal-item-price').textContent = `P${parseFloat(itemPrice).toFixed(2)}`;
    document.getElementById('cart-modal').style.display = 'block';

    const quantityInput = document.getElementById('edit-item-quantity');
    const totalEl = document.getElementById('modal-total-amount');
    const num = document.querySelector(".num");
    const plus = document.querySelector(".plus");
    const minus = document.querySelector(".minus");
    const price = parseFloat(itemPrice); // Parse the price as a number

    if (!quantityInput || !totalEl || !num || !plus || !minus) {
        console.error("Missing required elements in the modal.");
        return;
    }

    // Reset quantity and total amount
    let quantity = 1; // Use this as the source of truth
    quantityInput.value = quantity;
    num.innerText = quantity.toString().padStart(2, '0');
    totalEl.textContent = `P${price.toFixed(2)}`;

    // Update total amount and quantity display
    const updateDisplay = () => {
        num.innerText = quantity.toString().padStart(2, '0');
        totalEl.textContent = `P${(price * quantity).toFixed(2)}`;
        quantityInput.value = quantity; // Sync with input
    };

    // Remove existing event listeners to avoid duplication
    plus.replaceWith(plus.cloneNode(true));
    minus.replaceWith(minus.cloneNode(true));

    // Reassign event listeners
    document.querySelector(".plus").addEventListener("click", () => {
        quantity++;
        updateDisplay();
    });

    document.querySelector(".minus").addEventListener("click", () => {
        if (quantity > 1) {
            quantity--;
            updateDisplay();
        }
    });

    // Handle direct input changes
    quantityInput.addEventListener("input", () => {
        let inputVal = parseInt(quantityInput.value);
        if (isNaN(inputVal) || inputVal < 1) inputVal = 1; // Default to 1 if invalid
        quantity = inputVal; // Update the quantity variable
        updateDisplay();
    });
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

let map, userMarker;
let selectedMarker = null;

// Initialize Google Maps
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 14.565111, lng: 121.029889 },  // Default center
        zoom: 12
    });

}

// Event listener for store locator form
document.getElementById('storeLocatorForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const location = document.getElementById('locationInput').value;
    const resultsDiv = document.getElementById('store-results');

    // Clear old search results
    resultsDiv.innerHTML = '';

    // Clear the map of any previous markers (user's location and stores)
    if (userMarker) {
        userMarker.setMap(null);
    }

    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'address': location }, function(results, status) {
        if (status === 'OK') {
            const locationLatLng = results[0].geometry.location;

            // Set map center to the geocoded location
            map.setCenter(locationLatLng);
            map.setZoom(12);

            if (userMarker) {
                userMarker.setMap(null);
            }

            userMarker = new google.maps.Marker({
                position: locationLatLng,
                map: map,
                title: 'Your Location'
            });

            // Fetch nearby stores from Flask API
            fetch(`/api/nearby-stores?lat=${locationLatLng.lat()}&lng=${locationLatLng.lng()}`)
                .then(response => response.json())
                .then(data => {
                    const stores = data.stores;
                    resultsDiv.innerHTML = '';

                    if (stores.length > 0) {
                        stores.forEach(store => {
                            const storeDiv = document.createElement('div');
                            storeDiv.classList.add('store-info');
                            storeDiv.innerHTML = `<strong>${store.name}</strong>
                                <br>${store.address}<br>
                                <br>Open: ${store.business_hours}<br>
                                <em>${store.distance} km
                                <button onclick="selectdeliverystore('${store.name}', '${store.address}')">Select</button></em>`;
                            resultsDiv.appendChild(storeDiv);

                            const storeLatLng = new google.maps.LatLng(store.lat, store.lng);
                            const storeMarker = new google.maps.Marker({
                                position: storeLatLng,
                                map: map,
                                title: store.name
                            });

                            // Hover event for the store marker on the map
                            storeMarker.addListener('mouseover', function() {
                                map.setCenter(storeLatLng);
                                map.setZoom(14);
                            });

                            // Hover event for the store list item (highlight the store on map)
                            storeDiv.addEventListener('mouseover', function() {
                                map.setCenter(storeLatLng);
                                map.setZoom(14);
                            });

                            // Click event to show store details in an info window
                            storeMarker.addListener('click', function() {
                                new google.maps.InfoWindow({
                                    content: `<strong>${store.name}</strong><br>${store.address}`
                                }).open(map, this);
                            });
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
    });
});

function selectdeliverystore(storeName, storeLocation) {
    // Store the selected store's name and location in localStorage
    const selectedStore = {
        name: storeName,
        location: storeLocation
    };

    localStorage.setItem('selectedStore', JSON.stringify(selectedStore));

    // Optionally, you can show a message or redirect the user to the checkout page
    alert("Store selected: " + storeName);
    // Redirect to checkout page if needed (uncomment the next line if desired)
    window.location.href = "/menu";
}

        // Initialize map on page load
        window.onload = initMap;

function selectStore(storeName, storeLocation) {
    // Store the selected store's name and location in localStorage
    const selectedStore = {
        name: storeName,
        location: storeLocation
    };

    // Set the modal message
    const modalMessage = document.getElementById("modal-message");
    modalMessage.innerHTML = `${storeName} at ${storeLocation}. Do you want to proceed?`;

    // Get the modal and buttons
    const modal = document.getElementById("storeModal");
    const confirmBtn = document.getElementById("confirmBtn");
    const cancelBtn = document.getElementById("cancelBtn");

    // Show the modal
    modal.style.display = "block";

    // When the user clicks "OK", save the store and redirect
    confirmBtn.onclick = function() {
        localStorage.setItem('selectedStore', JSON.stringify(selectedStore));
        window.location.href = "/menu";  // Replace "/menu" with the correct URL for your menu page
    };

    // When the user clicks "Cancel", hide the modal
    cancelBtn.onclick = function() {
        modal.style.display = "none";
        console.log('Store selection cancelled');
    };

    // When the user clicks outside the modal, close it
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
}
