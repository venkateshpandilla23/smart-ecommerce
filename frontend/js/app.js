const API_URL = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("access_token");
}

function getAuthHeaders() {
    const token = getToken();

    if (!token) {
        return {};
    }

    return {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };
}


/* Load products */
async function loadProducts() {

    const grid = document.getElementById("productGrid");

    if (!grid) {
        return;
    }

    const category = document.getElementById("categoryFilter")?.value || "";
    const minPrice = document.getElementById("minPrice")?.value || "";
    const maxPrice = document.getElementById("maxPrice")?.value || "";
    const sort = document.getElementById("sortFilter")?.value || "";

    let url = `${API_URL}/products?`;

    if (category) {
        url += `category=${encodeURIComponent(category)}&`;
    }

    if (minPrice) {
        url += `min_price=${minPrice}&`;
    }

    if (maxPrice) {
        url += `max_price=${maxPrice}&`;
    }

    if (sort === "popularity") {
        url += "sort=popularity&";
    }

    try {

        grid.innerHTML = "<p>Loading products...</p>";

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Unable to load products");
        }

        const data = await response.json();

        const products = data.products || [];

        displayProducts(products);

        loadCategories(products);

    } catch (error) {

        console.error(error);

        grid.innerHTML = `
            <div class="error">
                Unable to connect to the FastAPI server.
                Please make sure FastAPI is running on port 8000.
            </div>
        `;
    }
}


/* Display products */
function displayProducts(products) {

    const grid = document.getElementById("productGrid");

    if (!grid) {
        return;
    }

    if (!products || products.length === 0) {

        grid.innerHTML = `
            <p>No products found.</p>
        `;

        return;
    }

    grid.innerHTML = "";

    products.forEach(product => {

        const image = product.image
            ? `http://127.0.0.1:8001/media/${product.image.replace(/^\/+/, "")}`
            : "https://via.placeholder.com/300x200?text=Product";

        const card = document.createElement("div");

        card.className = "product-card";

        card.innerHTML = `
            <img src="${image}" alt="${product.name}">

            <h3>${product.name}</h3>

            <p>
                ${product.description || "No description available"}
            </p>

            <p class="price">
                ₹${Number(product.price).toFixed(2)}
            </p>

            <p>
                Category: ${product.category || "General"}
            </p>

            <p class="stock">
                Stock: ${product.stock}
            </p>

            <button
                class="btn"
                onclick="addToCart(${product.id})"
                ${product.stock <= 0 ? "disabled" : ""}
            >
                ${product.stock > 0 ? "Add to Cart" : "Out of Stock"}
            </button>
        `;

        grid.appendChild(card);
    });
}


/* Load categories */
function loadCategories(products) {

    const categorySelect =
        document.getElementById("categoryFilter");

    if (!categorySelect) {
        return;
    }

    const categories = [
        ...new Set(
            products
                .map(product => product.category)
                .filter(category => category)
        )
    ];

    const currentValue = categorySelect.value;

    categorySelect.innerHTML = `
        <option value="">All Categories</option>
    `;

    categories.forEach(category => {

        const option = document.createElement("option");

        option.value = category;
        option.textContent = category;

        categorySelect.appendChild(option);
    });

    categorySelect.value = currentValue;
}


/* Add product to cart */
async function addToCart(productId) {

    const token = getToken();

    if (!token) {

        alert("Please login before adding products to cart.");

        window.location.href = "/shop/login/";

        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/cart`,
            {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Unable to add product to cart."
            );

            return;
        }

        alert("Product added to cart successfully! 🛒");

    } catch (error) {

        console.error(error);

        alert(
            "Unable to connect to the FastAPI server."
        );
    }
}


/* Search products */
function searchProducts() {

    const searchInput =
        document.getElementById("searchInput");

    if (!searchInput) {
        return;
    }

    const searchText =
        searchInput.value.toLowerCase();

    const cards =
        document.querySelectorAll(".product-card");

    cards.forEach(card => {

        const productName =
            card.querySelector("h3")
                ?.textContent
                .toLowerCase() || "";

        if (productName.includes(searchText)) {

            card.style.display = "";

        } else {

            card.style.display = "none";
        }
    });
}


/* Login / Logout status */
function updateLoginLink() {

    const loginLink =
        document.getElementById("loginLink");

    if (!loginLink) {
        return;
    }

    if (getToken()) {

        /* User is logged in */

        loginLink.textContent = "Logout";

        loginLink.href = "#";

        loginLink.onclick = function (event) {

            event.preventDefault();

            localStorage.removeItem("access_token");

            window.location.href = "/shop/";
        };

    } else {

        /* User is logged out */

        loginLink.textContent = "Login";

        loginLink.href = "/shop/login/";

        loginLink.onclick = null;
    }
}


/* Page load */
document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateLoginLink();

        loadProducts();

        const searchInput =
            document.getElementById("searchInput");

        if (searchInput) {

            searchInput.addEventListener(
                "input",
                searchProducts
            );
        }
    }
);