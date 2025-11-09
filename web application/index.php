<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Petite Pâtisserie</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap"
      rel="stylesheet"
    />

    <!-- Bootstrap CSS -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />

    <style>
      /* CSS Custom Properties / Design Tokens */
      :root {
        --bg: #faf8f5;
        --surface: #ffffff;
        --ink: #1a1a1a;
        --muted-ink: #706f6c;
        --accent: #d4af37;
        --accent-dark: #b8941f;
        --accent-light: #f0e5c5;
        --accent-2: #2c2c2c;
        --success: #5d7f6d;
        --border: #e8e4df;
        --border-dark: #d0cbc4;
        --focus: #d4af37;

        /* Typography Scale */
        --text-11: 11px;
        --text-13: 13px;
        --text-15: 15px;
        --text-17: 17px;
        --text-20: 20px;
        --text-28: 28px;
        --text-36: 36px;
        --text-56: 56px;

        /* Spacing Scale */
        --space-8: 8px;
        --space-12: 12px;
        --space-16: 16px;
        --space-20: 20px;
        --space-24: 24px;
        --space-32: 32px;
        --space-40: 40px;
        --space-48: 48px;

        /* Corner Radius */
        --radius-card: 8px;
        --radius-pill: 999px;

        /* Shadows */
        --shadow-s1: 0 2px 8px rgba(0, 0, 0, 0.06);
        --shadow-s2: 0 8px 24px rgba(0, 0, 0, 0.08);
        --shadow-s3: 0 16px 40px rgba(0, 0, 0, 0.12);
        --shadow-gold: 0 4px 16px rgba(212, 175, 55, 0.25);

        /* Typography */
        --font-serif: "Cormorant Garamond", Georgia, serif;
        --font-sans: "Montserrat", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      /* Base Styles */
      * {
        box-sizing: border-box;
      }

      body {
        font-family: var(--font-sans);
        font-size: var(--text-15);
        font-weight: 400;
        color: var(--ink);
        background-color: var(--bg);
        background-image: 
          repeating-linear-gradient(
            90deg,
            transparent,
            transparent 2px,
            rgba(212, 175, 55, 0.02) 2px,
            rgba(212, 175, 55, 0.02) 4px
          ),
          repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(212, 175, 55, 0.02) 2px,
            rgba(212, 175, 55, 0.02) 4px
          ),
          linear-gradient(
            180deg,
            #faf8f5 0%,
            #f5f2ed 100%
          );
        min-height: 100vh;
        padding: var(--space-48);
        margin: 0;
        line-height: 1.65;
        letter-spacing: 0.01em;
      }

      /* Typography */
      h1,
      h2,
      h3 {
        font-family: var(--font-serif);
        font-weight: 600;
        margin: 0;
        letter-spacing: 0.02em;
      }

      h1 {
        font-size: var(--text-56);
        margin-bottom: var(--space-16);
        color: var(--ink);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        position: relative;
        text-shadow: 0 2px 12px rgba(212, 175, 55, 0.15);
      }

      h1::after {
        content: '';
        position: absolute;
        bottom: -12px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
      }

      h2 {
        font-size: var(--text-36);
        margin-bottom: var(--space-20);
      }

      h3 {
        font-size: var(--text-28);
        font-weight: 500;
      }

      /* Container */
      .app-container {
        max-width: 1200px;
        margin: 0 auto;
      }

      /* Header */
      .app-header {
        text-align: center;
        margin-bottom: 64px;
        padding-bottom: var(--space-40);
        border-bottom: 1px solid var(--border-dark);
        position: relative;
        background: linear-gradient(180deg, rgba(255,255,255,0.8) 0%, transparent 100%);
        padding-top: var(--space-24);
      }

      .app-header::before {
        content: '✦';
        display: block;
        font-size: var(--text-28);
        color: var(--accent);
        margin-bottom: var(--space-16);
        font-weight: 300;
      }

      .app-header::after {
        content: none;
      }

      .app-subtitle {
        font-size: var(--text-17);
        color: var(--muted-ink);
        margin-bottom: 0;
        font-weight: 400;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-family: var(--font-sans);
        margin-top: var(--space-20);
      }

      /* Product Grid */
      .products-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
        gap: 32px;
        margin-bottom: 64px;
        padding: 8px;
      }

      /* Product Card */
      .product-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        box-shadow: var(--shadow-s2);
        padding: 24px;
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        display: flex;
        flex-direction: column;
        height: 100%;
        overflow: hidden;
      }

      .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
        opacity: 0;
        transition: opacity 300ms ease;
      }

      .product-card:hover {
        transform: translateY(-8px);
        box-shadow: var(--shadow-s3), var(--shadow-gold);
        border-color: var(--accent-light);
      }

      .product-card:hover::before {
        opacity: 1;
      }

      .product-image {
        width: 100%;
        height: 240px;
        object-fit: cover;
        border-radius: var(--radius-card);
        margin-bottom: var(--space-20);
        background: linear-gradient(135deg, #f8f7f5 0%, #f0eeea 100%);
        border: 1px solid var(--border);
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
      }

      .product-card:hover .product-image {
        transform: scale(1.03);
        border-color: var(--accent-light);
      }

      /* Special styling for specific images that need contain instead of cover */
      [data-product-id="4"] .product-image,
      [data-product-id="5"] .product-image {
        object-fit: contain;
        padding: 8px;
      }

      .popular-badge {
        position: absolute;
        top: 32px;
        right: 32px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        color: var(--surface);
        padding: 8px 18px;
        border-radius: var(--radius-pill);
        font-size: var(--text-11);
        font-weight: 700;
        box-shadow: var(--shadow-gold);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border: 1px solid rgba(255, 255, 255, 0.3);
      }

      .product-name {
        font-family: var(--font-serif);
        font-size: var(--text-20);
        font-weight: 500;
        margin-bottom: 16px;
        color: var(--ink);
        min-height: 56px;
        display: flex;
        align-items: center;
        line-height: 1.4;
        letter-spacing: 0.02em;
      }

      .product-price {
        font-size: 22px;
        font-weight: 600;
        color: var(--accent-dark);
        margin-bottom: var(--space-20);
        height: 32px;
        display: flex;
        align-items: center;
        font-family: var(--font-sans);
        letter-spacing: 0.03em;
      }

      /* Quantity Stepper */
      .quantity-control {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-12);
        margin-bottom: var(--space-8);
        min-height: 48px;
        margin-top: auto;
      }

      .quantity-stepper {
        display: flex;
        align-items: center;
        background: var(--bg);
        border: 1px solid var(--border-dark);
        border-radius: var(--radius-pill);
        overflow: hidden;
        min-height: 48px;
        flex-shrink: 0;
        transition: all 200ms ease;
      }

      .quantity-stepper:focus-within {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
      }

      .qty-btn {
        background: transparent;
        border: none;
        color: var(--ink);
        font-size: 20px;
        font-weight: 600;
        width: 48px;
        height: 48px;
        cursor: pointer;
        transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .qty-btn:hover {
        background: var(--accent);
        color: var(--surface);
      }

      .qty-btn:active {
        transform: scale(0.95);
        transition: transform 100ms ease-in;
      }

      .qty-btn:focus {
        outline: none;
        background: var(--accent-light);
        z-index: 1;
      }

      .qty-btn:disabled {
        opacity: 0.3;
        cursor: not-allowed;
      }

      .qty-input {
        border: none;
        background: transparent;
        text-align: center;
        width: 56px;
        height: 48px;
        font-size: 17px;
        font-weight: 600;
        color: var(--ink);
        padding: 0;
        font-family: var(--font-sans);
      }

      .qty-input:focus {
        outline: none;
      }

      .qty-input::-webkit-inner-spin-button,
      .qty-input::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
      }

      .qty-input[type="number"] {
        -moz-appearance: textfield;
        appearance: textfield;
      }

      /* Error Message */
      .error-message {
        color: #c41e3a;
        font-size: var(--text-13);
        margin-top: 6px;
        display: none;
        font-weight: 500;
      }

      .error-message.visible {
        display: block;
      }

      .has-error .quantity-stepper {
        border-color: #c41e3a;
        background: rgba(196, 30, 58, 0.03);
      }

      /* Controls Section */
      .controls-section {
        background: var(--surface);
        border: 1px solid var(--border-dark);
        border-radius: var(--radius-card);
        padding: 40px;
        margin-bottom: 64px;
        box-shadow: var(--shadow-s2);
        position: relative;
        overflow: hidden;
      }

      .controls-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
      }

      .discount-toggle {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 32px;
        padding: 20px 24px;
        background: var(--bg);
        border-radius: var(--radius-card);
        border: 1px solid var(--border);
        transition: all 250ms ease;
      }

      .discount-toggle:hover {
        border-color: var(--accent-light);
        background: rgba(212, 175, 55, 0.03);
        box-shadow: var(--shadow-s1);
      }

      /* Custom Switch */
      .switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 32px;
      }

      .switch input {
        opacity: 0;
        width: 0;
        height: 0;
      }

      .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--border-dark);
        transition: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: var(--radius-pill);
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      .slider:before {
        position: absolute;
        content: "";
        height: 26px;
        width: 26px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 50%;
        box-shadow: var(--shadow-s1);
      }

      input:checked + .slider {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        box-shadow: var(--shadow-gold);
      }

      input:checked + .slider:before {
        transform: translateX(28px);
      }

      input:focus + .slider {
        box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.15);
      }

      input:focus:not(:focus-visible) + .slider {
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      input:checked:focus + .slider {
        box-shadow: var(--shadow-gold), 0 0 0 4px rgba(212, 175, 55, 0.15);
      }

      .toggle-label {
        font-size: 16px;
        font-weight: 500;
        color: var(--ink);
        cursor: pointer;
        user-select: none;
        letter-spacing: 0.01em;
      }

      /* Calculate Button */
      .btn-calculate {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        color: var(--surface);
        border: none;
        padding: 22px var(--space-40);
        font-size: 18px;
        font-weight: 600;
        border-radius: var(--radius-pill);
        cursor: pointer;
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-gold);
        width: 100%;
        min-height: 64px;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-family: var(--font-sans);
        border: 1px solid rgba(255, 255, 255, 0.2);
      }

      .btn-calculate:hover:not(:disabled) {
        background: linear-gradient(135deg, var(--accent-dark) 0%, var(--accent) 100%);
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(212, 175, 55, 0.35);
      }

      .btn-calculate:active:not(:disabled) {
        transform: translateY(-2px);
        transition: transform 100ms ease-in;
      }

      .btn-calculate:focus {
        outline: none;
        box-shadow: var(--shadow-gold), 0 0 0 4px rgba(212, 175, 55, 0.2);
      }

      .btn-calculate:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }

      /* Global Error Alert */
      .global-error {
        background: rgba(196, 30, 58, 0.05);
        border: 1px solid rgba(196, 30, 58, 0.3);
        color: #c41e3a;
        padding: var(--space-20);
        border-radius: var(--radius-card);
        margin-top: var(--space-20);
        display: none;
        font-size: var(--text-15);
        font-weight: 500;
      }

      .global-error.visible {
        display: block;
      }

      /* Responsive */
      @media (max-width: 768px) {
        h1 {
          font-size: 40px;
          letter-spacing: 0.1em;
        }

        .products-grid {
          grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
          gap: 24px;
          padding: 4px;
        }

        body {
          padding: var(--space-24);
        }

        .controls-section {
          padding: 28px;
        }

        .app-header {
          margin-bottom: 48px;
        }

        .product-card {
          padding: 20px;
        }

        .product-image {
          height: 200px;
        }
      }

      @media (min-width: 1400px) {
        .products-grid {
          grid-template-columns: repeat(4, 1fr);
        }
      }

      /* Smooth Scroll */
      html {
        scroll-behavior: smooth;
      }

      /* Selection Color */
      ::selection {
        background-color: var(--accent-light);
        color: var(--ink);
      }

      /* Focus Visible Styling */
      *:focus-visible {
        outline: 2px solid var(--accent);
        outline-offset: 3px;
        border-radius: 4px;
      }
    </style>
  </head>
  <body>
    <div class="app-container">
      <!-- Header -->
      <header class="app-header">
        <h1>Petite Pâtisserie</h1>
        <p class="app-subtitle">Artisan Pastries & Desserts</p>
      </header>

      <!-- Products Grid -->
      <div class="products-grid" id="productsGrid">
        <!-- Products will be rendered here by JavaScript -->
      </div>

      <!-- Controls Section -->
      <section class="controls-section">
        <div class="discount-toggle">
          <label class="switch">
            <input
              type="checkbox"
              id="discountToggle"
              aria-label="Late-evening 50% discount"
            />
            <span class="slider"></span>
          </label>
          <label for="discountToggle" class="toggle-label"
            >Late-evening 50% discount</label
          >
        </div>

        <button
          class="btn-calculate"
          id="calculateBtn"
          onclick="calculateBill()"
        >
          Calculate Bill
        </button>

        <div
          class="global-error"
          id="globalError"
          role="alert"
          aria-live="assertive"
        ></div>
      </section>

      <!-- Hidden form to submit receipt data -->
      <form id="receiptForm" method="POST" action="receipt.php" style="display: none;">
        <input type="hidden" name="receiptData" id="receiptDataInput">
      </form>
    </div>

    <script>
      // Product Data - 8 dessert items
      const products = [
        {
          id: 1,
          name: "Chocolate Lava Cake",
          price: 16.0,
          image: "images/Chocolate Lava Cake.png",
        },
        {
          id: 2,
          name: "Strawberry Cheesecake",
          price: 13.5,
          image: "images/Strawberry Cheesecake.png",
        },
        {
          id: 3,
          name: "Tiramisu Cup",
          price: 12.0,
          image: "images/Tiramisu Cup.png",
        },
        {
          id: 4,
          name: "Matcha Roll Cake",
          price: 10.5,
          image: "images/Matcha Roll Cake.png",
        },
        {
          id: 5,
          name: "Blueberry Muffin",
          price: 7.0,
          image: "images/Blueberry Muffin.png",
        },
        {
          id: 6,
          name: "Macaron Set (3 pcs)",
          price: 13.5,
          image: "images/Macaron Set (3 pcs).png",
        },
        {
          id: 7,
          name: "Ice Cream Sundae",
          price: 9.5,
          image: "images/Ice Cream Sundae.png",
        },
        {
          id: 8,
          name: "Mango Pudding",
          price: 8.0,
          image: "images/Mango Pudding.png",
        },
      ];

      // Render products on page load
      function renderProducts() {
        const grid = document.getElementById("productsGrid");

        products.forEach((product) => {
          const card = document.createElement("div");
          card.className = "product-card";
          card.setAttribute("data-product-id", product.id);

          card.innerHTML = `
          <img src="${product.image}" alt="${product.name}" class="product-image">
          <h3 class="product-name">${product.name}</h3>
          <p class="product-price">RM${product.price.toFixed(2)}</p>
          <div class="quantity-control">
            <div class="quantity-stepper">
              <button 
                class="qty-btn" 
                onclick="decrementQty(${product.id})"
                aria-label="Decrease quantity for ${product.name}"
                type="button">−</button>
              <input 
                type="number" 
                class="qty-input" 
                id="qty-${product.id}"
                value="0"
                min="0"
                step="1"
                aria-label="Quantity for ${product.name}"
                onchange="validateQuantity(${product.id})"
                oninput="validateQuantity(${product.id})">
              <button 
                class="qty-btn" 
                onclick="incrementQty(${product.id})"
                aria-label="Increase quantity for ${product.name}"
                type="button">+</button>
            </div>
          </div>
          <div class="error-message" id="error-${
            product.id
          }" role="alert" aria-live="polite">
            Please enter a valid non-negative number
          </div>
        `;

          grid.appendChild(card);
        });
      }

      // Quantity Control Functions
      function incrementQty(productId) {
        const input = document.getElementById(`qty-${productId}`);
        let currentValue = parseInt(input.value) || 0;
        input.value = currentValue + 1;
        validateQuantity(productId);
      }

      function decrementQty(productId) {
        const input = document.getElementById(`qty-${productId}`);
        let currentValue = parseInt(input.value) || 0;
        if (currentValue > 0) {
          input.value = currentValue - 1;
          validateQuantity(productId);
        }
      }

      // Validate quantity input (must be non-negative integer)
      function validateQuantity(productId) {
        const input = document.getElementById(`qty-${productId}`);
        const errorMsg = document.getElementById(`error-${productId}`);
        const card = input.closest(".product-card");
        const value = input.value.trim();

        // Check if value is empty, negative, or not an integer
        const isValid =
          value !== "" &&
          !isNaN(value) &&
          Number.isInteger(parseFloat(value)) &&
          parseFloat(value) >= 0;

        if (!isValid && value !== "") {
          errorMsg.classList.add("visible");
          card.classList.add("has-error");
          return false;
        } else {
          errorMsg.classList.remove("visible");
          card.classList.remove("has-error");

          // Ensure value is integer
          if (value === "") {
            input.value = 0;
          } else {
            input.value = Math.max(0, Math.floor(parseFloat(value)));
          }
          return true;
        }
      }

      // Calculate Bill
      function calculateBill() {
        // Reset global error
        const globalError = document.getElementById("globalError");
        globalError.classList.remove("visible");
        globalError.textContent = "";

        // Validate all quantities
        let hasError = false;
        products.forEach((product) => {
          if (!validateQuantity(product.id)) {
            hasError = true;
          }
        });

        if (hasError) {
          globalError.textContent =
            "⚠️ Please correct invalid quantities before calculating.";
          globalError.classList.add("visible");
          return;
        }

        // Check if at least one item has quantity > 0
        let hasItems = false;
        products.forEach((product) => {
          const qty =
            parseInt(document.getElementById(`qty-${product.id}`).value) || 0;
          if (qty > 0) {
            hasItems = true;
          }
        });

        if (!hasItems) {
          globalError.textContent = "⚠️ Please select at least one item.";
          globalError.classList.add("visible");
          return;
        }

        // Get discount status
        const hasDiscount = document.getElementById("discountToggle").checked;
        const discountMultiplier = hasDiscount ? 0.5 : 1.0;

        // Calculate line items and subtotal
        let originalSubtotal = 0;
        let subtotal = 0;
        const lineItems = [];

        products.forEach((product) => {
          const qty =
            parseInt(document.getElementById(`qty-${product.id}`).value) || 0;
          if (qty > 0) {
            // Calculate original line total (without discount)
            const originalLineTotal =
              Math.round(product.price * qty * 100) / 100;
            originalSubtotal =
              Math.round((originalSubtotal + originalLineTotal) * 100) / 100;

            // Calculate discounted line total
            const lineTotal =
              Math.round(product.price * qty * discountMultiplier * 100) / 100;
            subtotal = Math.round((subtotal + lineTotal) * 100) / 100;

            lineItems.push({
              name: product.name,
              price: product.price,
              qty: qty,
              lineTotal: originalLineTotal,
            });
          }
        });

        // Calculate discount amount
        const discountAmount = hasDiscount
          ? Math.round((originalSubtotal - subtotal) * 100) / 100
          : 0;

        // Calculate SST (6% on discounted subtotal)
        const sst = Math.round(subtotal * 0.06 * 100) / 100;

        // Calculate Grand Total
        const grandTotal = Math.round((subtotal + sst) * 100) / 100;

        // Submit to receipt page
        submitReceipt(
          lineItems,
          originalSubtotal,
          discountAmount,
          subtotal,
          sst,
          grandTotal,
          hasDiscount
        );
      }

      // Submit Receipt Data
      function submitReceipt(
        lineItems,
        originalSubtotal,
        discountAmount,
        subtotal,
        sst,
        grandTotal,
        hasDiscount
      ) {
        // Get current date
        const now = new Date();
        const dateString = now.toLocaleString("en-MY", {
          dateStyle: "medium",
          timeStyle: "short",
        });

        // Prepare receipt data
        const receiptData = {
          lineItems: lineItems,
          originalSubtotal: originalSubtotal,
          discountAmount: discountAmount,
          subtotal: subtotal,
          sst: sst,
          grandTotal: grandTotal,
          hasDiscount: hasDiscount,
          date: dateString
        };

        // Set form data and submit
        document.getElementById('receiptDataInput').value = JSON.stringify(receiptData);
        document.getElementById('receiptForm').submit();
      }

      // Initialize app on page load
      document.addEventListener("DOMContentLoaded", () => {
        renderProducts();
      });
    </script>
  </body>
</html>
