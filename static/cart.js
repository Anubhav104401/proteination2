document.addEventListener("DOMContentLoaded", async function () {
    const cartItemsContainer = document.getElementById("cart-items");
    const token = localStorage.getItem("token");

    if (!token) {
        cartItemsContainer.innerHTML = "<p>You need to log in to view your cart.</p>";
        return;
    }

    async function fetchCart() {
        const response = await fetch("http://127.0.0.1:5000/get-cart", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const data = await response.json();
        renderCart(data.cart);
    }

    function renderCart(cart) {
        cartItemsContainer.innerHTML = "";

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = "<p>Your cart is empty.</p>";
            return;
        }

        cart.forEach((item, index) => {
            const div = document.createElement("div");
            div.innerHTML = `
                <p>${item.name} - ₹${item.price} (Qty: ${item.quantity})</p>
                <button onclick="removeItem('${item.product_id}')">Remove</button>
            `;
            cartItemsContainer.appendChild(div);
        });
    }

    window.removeItem = async function (productId) {
        const response = await fetch("http://127.0.0.1:5000/remove-from-cart", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId })
        });

        const data = await response.json();
        alert(data.message);
        fetchCart(); // Refresh the cart
    };

    document.getElementById("clear-cart").addEventListener("click", async function () {
        const response = await fetch("http://127.0.0.1:5000/clear-cart", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const data = await response.json();
        alert(data.message);
        fetchCart();
    });

    fetchCart();
});
