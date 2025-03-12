document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.querySelector(".register-container form");
    const loginForm = document.querySelector(".login-container form");
    const logoutBtn = document.getElementById("logout-btn");

    function validatePassword(password) {
        const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return regex.test(password);
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm-password").value;

            if (!validatePassword(password)) {
                alert("Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.");
                return;
            }

            if (password !== confirmPassword) {
                alert("Passwords do not match.");
                return;
            }

            const response = await fetch("http://127.0.0.1:5000/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            alert(data.message);
            if (response.ok) window.location.href = "login.html";
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value;

            const response = await fetch("http://127.0.0.1:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            if (response.ok) {
                localStorage.setItem("token", data.token);
                window.location.href = "index.html";
            } else {
                alert(data.message);
            }
        });
    }

    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", async (event) => {
            const productId = event.target.dataset.productId;
            const token = localStorage.getItem("token");

            if (!token) {
                alert("Please log in first!");
                return;
            }

            const response = await fetch("http://127.0.0.1:5000/add-to-cart", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({ product_id: productId, quantity: 1 })
            });

            const data = await response.json();
            alert(data.message);
        });
    });

    // Logout Function
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("token"); // Remove token
            alert("Logged out successfully!");
            window.location.href = "login.html"; // Redirect to login page
        });
    }

    
});
