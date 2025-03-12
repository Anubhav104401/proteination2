document.addEventListener("DOMContentLoaded", () => {
    const header = document.getElementById("main-header");

    document.querySelectorAll("nav a").forEach(link => {
        link.addEventListener("click", function (event) {
            const color = this.getAttribute("data-color"); // Get color from data attribute
            if (color) {
                header.style.backgroundColor = color; // Apply color change
            }
        });
    });
});


document.querySelectorAll(".add-to-cart").forEach(button => {
    button.addEventListener("click", async function () {
        const productId = this.getAttribute("data-product");
        const token = localStorage.getItem("token"); // Get JWT Token

        if (!token) {
            alert("You need to log in first!");
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/add-to-cart", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`  // Send token for authentication
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });

        const data = await response.json();
        alert(data.message);
    });
});

