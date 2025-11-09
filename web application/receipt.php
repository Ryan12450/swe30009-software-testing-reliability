<?php
// Start session to store/retrieve order data
session_start();

// Check if this is a POST request with receipt data
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['receiptData'])) {
    // Decode and store the receipt data in session
    $receiptData = json_decode($_POST['receiptData'], true);
    $_SESSION['receipt_data'] = $receiptData;
    
    // Redirect to GET request to prevent form resubmission
    header('Location: receipt.php');
    exit();
}

// Check if receipt data exists in session
if (!isset($_SESSION['receipt_data'])) {
    header('Location: index.php');
    exit();
}

$receiptData = $_SESSION['receipt_data'];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Receipt - Petite Pâtisserie</title>

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
        font-size: 14px;
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
        padding: 4px 6px;
        margin: 0;
        line-height: 1.45;
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
        font-size: 32px;
        margin-bottom: 10px;
        color: var(--ink);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
      }

      h2 {
        font-size: 24px;
        margin-bottom: 10px;
      }

      /* Container */
      .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 15px;
      }

      /* Receipt Section */
      .receipt-section {
        background: var(--surface);
        border: 1px solid var(--border-dark);
        border-radius: var(--radius-card);
        padding: 24px 20px;
        box-shadow: var(--shadow-s3);
        position: relative;
        overflow: hidden;
      }

      .receipt-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
      }

      .receipt-section::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
      }

      .receipt-header {
        text-align: center;
        margin-bottom: 16px;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--border-dark);
        position: relative;
      }

      .receipt-header::before {
        content: "✦";
        font-size: 24px;
        display: block;
        margin-bottom: 10px;
        color: var(--accent);
        font-weight: 300;
      }

      .receipt-title {
        font-family: var(--font-serif);
        font-size: 24px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 600;
      }

      .receipt-date {
        font-size: 12px;
        color: var(--muted-ink);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
      }

      .receipt-items {
        margin-bottom: 16px;
      }

      .receipt-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-bottom: 16px;
        display: table;
        font-size: 13px;
      }

      .receipt-table thead {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        color: var(--surface);
        position: sticky;
        top: 0;
        z-index: 10;
      }

      .receipt-table th {
        padding: 12px 8px;
        text-align: left;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border-bottom: 2px solid var(--accent-dark);
        font-family: var(--font-sans);
      }

      .receipt-table thead tr th:first-child {
        border-top-left-radius: var(--radius-card);
      }

      .receipt-table thead tr th:last-child {
        border-top-right-radius: var(--radius-card);
      }

      .receipt-table th:first-child {
        text-align: center;
        width: 55px;
      }

      .receipt-table th:nth-child(3),
      .receipt-table th:nth-child(4) {
        text-align: right;
        width: 90px;
      }

      .receipt-table td {
        padding: 10px 8px;
        border-bottom: 1px solid var(--border);
        background: var(--surface);
        font-size: 13px;
        line-height: 1.4;
        word-break: break-word;
      }

      .receipt-table tbody tr:last-child td {
        border-bottom: 2px solid var(--border-dark);
      }

      .receipt-table tbody tr:hover td {
        background: rgba(212, 175, 55, 0.03);
      }

      .receipt-table td:first-child {
        text-align: center;
        font-weight: 600;
        color: var(--muted-ink);
        font-size: 13px;
      }

      .receipt-table td:nth-child(3),
      .receipt-table td:nth-child(4) {
        text-align: right;
        font-weight: 600;
        font-family: var(--font-sans);
        font-size: 13px;
        letter-spacing: 0.02em;
        white-space: nowrap;
      }

      .receipt-table td:nth-child(2) {
        font-weight: 500;
        font-size: 13px;
      }

      .receipt-totals {
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid var(--border-dark);
        background: linear-gradient(180deg, transparent 0%, rgba(212, 175, 55, 0.02) 100%);
        padding: 16px 12px;
        border-radius: var(--radius-card);
      }

      .receipt-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        font-size: 13px;
        font-family: var(--font-sans);
      }

      .receipt-row .receipt-value {
        font-family: var(--font-sans);
        font-weight: 600;
        letter-spacing: 0.02em;
      }

      .receipt-row.subtotal {
        font-weight: 500;
        font-size: 14px;
      }

      .receipt-row.subtotal .receipt-value {
        font-weight: 600;
      }

      .receipt-row.discount {
        color: #c41e3a;
        font-weight: 500;
        font-size: 14px;
      }

      .receipt-row.discount .receipt-value {
        color: #c41e3a;
        font-weight: 600;
      }

      .receipt-row.sst {
        font-weight: 500;
        font-size: 14px;
      }

      .receipt-row.sst .receipt-label {
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }

      .receipt-row.sst .receipt-value {
        font-weight: 600;
      }

      .receipt-row.grand-total {
        font-size: 20px;
        font-weight: 700;
        padding-top: 12px;
        border-top: 2px solid var(--accent);
        margin-top: 12px;
        font-family: var(--font-sans);
        color: var(--accent-dark);
      }

      .receipt-row.grand-total .receipt-value {
        text-shadow: 0 2px 8px rgba(212, 175, 55, 0.2);
        letter-spacing: 0.03em;
      }

      .discount-notice {
        background: linear-gradient(135deg, var(--accent-light) 0%, #f5ecd0 100%);
        padding: 14px;
        border-radius: var(--radius-card);
        margin-bottom: 14px;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        box-shadow: var(--shadow-s1);
        border: 1px solid var(--accent);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--accent-dark);
      }

      /* Buttons */
      .button-container {
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid var(--border);
      }

      .btn-back {
        border: none;
        padding: 12px 28px;
        font-size: 13px;
        font-weight: 600;
        border-radius: var(--radius-card);
        cursor: pointer;
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        min-height: 44px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        text-decoration: none;
        font-family: var(--font-sans);
        position: relative;
        overflow: hidden;
      }

      .btn-back::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 600ms ease-out;
      }

      .btn-back:hover::before {
        left: 100%;
      }

      .btn-back {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        color: var(--surface);
        box-shadow: var(--shadow-gold);
        border: 2px solid rgba(255, 255, 255, 0.3);
      }

      .btn-back:hover {
        background: linear-gradient(135deg, var(--accent-dark) 0%, #a6841a 100%);
        transform: translateY(-2px);
        box-shadow: 0 16px 40px rgba(212, 175, 55, 0.4);
        color: var(--surface);
      }

      .btn-back:active {
        transform: translateY(0px);
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.3);
        transition: transform 100ms ease-in;
      }

      .btn-back:focus {
        outline: none;
        box-shadow: var(--shadow-gold), 0 0 0 4px rgba(212, 175, 55, 0.25);
      }

      .btn-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        font-size: 14px;
        font-weight: 700;
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
      }

      .btn-back:hover .btn-icon {
        background: rgba(255, 255, 255, 0.3);
        transform: rotate(90deg);
      }

      .btn-text {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.12em;
      }

      /* Print Styles */
      @media print {
        body {
          background: white;
          padding: 0;
        }

        .button-container {
          display: none !important;
        }

        .receipt-section {
          box-shadow: none;
          border: 1px solid #ccc;
        }

        .receipt-section::before,
        .receipt-section::after {
          display: none;
        }
      }

      /* Responsive */
      @media (max-width: 768px) {
        h1 {
          font-size: 28px;
          letter-spacing: 0.1em;
        }

        body {
          padding: 4px 4px;
        }

        .container {
          padding: 0 8px;
        }

        .receipt-section {
          padding: 20px 16px;
        }

        .receipt-table th,
        .receipt-table td {
          padding: 8px 6px;
          font-size: 12px;
        }

        .receipt-row.grand-total {
          font-size: 18px;
        }

        .btn-back {
          padding: 11px 22px;
          min-height: 42px;
          font-size: 12px;
        }

        .btn-text {
          font-size: 12px;
        }

        .btn-icon {
          width: 18px;
          height: 18px;
          font-size: 13px;
        }
      }
    </style>
</head>
<body>
    <div class="container">
      <!-- Receipt Section -->
      <section class="receipt-section" role="region" aria-label="Receipt">
        <div class="receipt-header">
          <h2 class="receipt-title">Receipt</h2>
        </div>

        <div class="receipt-items">
          <table class="receipt-table">
            <thead>
              <tr>
                <th>QTY</th>
                <th>Description</th>
                <th>Unit Price</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              <?php foreach ($receiptData['lineItems'] as $item): ?>
              <tr>
                <td><?php echo $item['qty']; ?></td>
                <td><?php echo htmlspecialchars($item['name']); ?></td>
                <td><?php echo number_format($item['price'], 2); ?></td>
                <td><?php echo number_format($item['lineTotal'], 2); ?></td>
              </tr>
              <?php endforeach; ?>
            </tbody>
          </table>
        </div>

        <div class="receipt-totals">
          <?php if ($receiptData['hasDiscount']): ?>
          <div class="receipt-row subtotal">
            <span class="receipt-label">Subtotal:</span>
            <span class="receipt-value">RM<?php echo number_format($receiptData['originalSubtotal'], 2); ?></span>
          </div>
          <div class="receipt-row discount">
            <span class="receipt-label">Late-evening Discount (50%):</span>
            <span class="receipt-value">-RM<?php echo number_format($receiptData['discountAmount'], 2); ?></span>
          </div>
          <div class="receipt-row subtotal">
            <span class="receipt-label">Discounted Subtotal:</span>
            <span class="receipt-value">RM<?php echo number_format($receiptData['subtotal'], 2); ?></span>
          </div>
          <?php else: ?>
          <div class="receipt-row subtotal">
            <span class="receipt-label">Subtotal:</span>
            <span class="receipt-value">RM<?php echo number_format($receiptData['subtotal'], 2); ?></span>
          </div>
          <?php endif; ?>
          
          <div class="receipt-row sst">
            <span class="receipt-label">SST (6%):</span>
            <span class="receipt-value">RM<?php echo number_format($receiptData['sst'], 2); ?></span>
          </div>
          <div class="receipt-row grand-total">
            <span class="receipt-label">Grand Total:</span>
            <span class="receipt-value">RM<?php echo number_format($receiptData['grandTotal'], 2); ?></span>
          </div>
        </div>

        <div class="button-container">
          <a href="index.php" class="btn-back">
            <span class="btn-icon">+</span>
            <span class="btn-text">New Order</span>
          </a>
        </div>
      </section>
    </div>
</body>
</html>
