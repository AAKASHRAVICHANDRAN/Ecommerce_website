// Get cart from localStorage
function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}

// Save cart to localStorage
function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Add product to cart
function addToCart(productId) {
    let cart = getCart();
    let found = cart.find(item => item.id === productId);
    if (found) {
        found.quantity += 1;
    } else {
        cart.push({id: productId, quantity: 1});
    }
    saveCart(cart);
    alert("Added to cart!");
}

// Display cart items
function displayCart() {
    let cart = getCart();
    let container = document.getElementById('cart-items');
    container.innerHTML = '';
    if (cart.length === 0) {
        container.innerHTML = '<p>Your cart is empty.</p>';
        return;
    }

    cart.forEach(item => {
        container.innerHTML += `<p>Product ID: ${item.id} | Quantity: ${item.quantity}</p>`;
    });
}

// Checkout using Stripe
async function checkout() {
    let cart = getCart();
    if (cart.length === 0) {
        alert("Cart is empty!");
        return;
    }

    // Fetch product details from API to send to Stripe
    let lineItems = [];
    for (let item of cart) {
        let response = await fetch(`/api/products/${item.id}/`);
        let data = await response.json();
        lineItems.push({
            title: data.title,
            price: data.price,
            quantity: item.quantity
        });
    }

    // Create checkout session
    let res = await fetch('/api/create-checkout-session/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({items: lineItems})
    });
    let session = await res.json();

    // Redirect to Stripe Checkout
    const stripe = Stripe('{{ stripe_public_key }}');
    stripe.redirectToCheckout({ sessionId: session.id });
}

// Run displayCart on cart page
if (document.getElementById('cart-items')) {
    displayCart();
}
