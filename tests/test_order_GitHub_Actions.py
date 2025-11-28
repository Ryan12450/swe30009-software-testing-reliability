import time
import csv
import os  
import sys
import argparse
import traceback
import unittest
import html
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager  # NEW

# Global Settings for GitHub Actions
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/index.php")
SCREENSHOT_DIR = os.path.join("test_screenshots")
ERROR_LOG_FILE = os.path.join("test_screenshots", "error_log.txt")
REPORT_FILE = "test_report.html" 

# Helper function for safe decimal comparison
def d(value):
    """Convert to Decimal with 2 decimal places for reliable comparison."""
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# Maps CSV column names to their corresponding HTML input IDs
ITEM_MAPPING = {
    'Chocolate_Lava_Cake': 'qty-1',
    'Strawberry_Cheesecake': 'qty-2',
    'Tiramisu_Cup': 'qty-3',
    'Matcha_Roll_Cake': 'qty-4',
    'Blueberry_Muffin': 'qty-5',
    'Macaron_Set': 'qty-6',
    'Ice_Cream_Sundae': 'qty-7',
    'Mango_Pudding': 'qty-8'
}

def log_error_to_file(test_id, error):
    """Logs full error details to a persistent error log file."""
    try:
        os.makedirs(os.path.dirname(ERROR_LOG_FILE) if os.path.dirname(ERROR_LOG_FILE) else ".", exist_ok=True)
        with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n{'='*70}\n")
            f.write(f"[{timestamp}] Test Case: {test_id}\n")
            f.write(f"{'-'*70}\n")
            f.write(f"{error}\n")
    except Exception as e:
        print(f"⚠️ Could not write to error log: {e}")


class DessertOrderTestCase(unittest.TestCase):
    """Unit test class for testing dessert ordering system using Selenium in GitHub Actions."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - runs once before all tests."""
        print("Setting up the browser for GitHub Actions (headless mode)...")
        options = Options()
        
        # Chrome arguments
        # Use the new headless mode if available (works with Chrome ≥ 109)
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-first-run")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Use WebDriver Manager to automatically download a compatible ChromeDriver
        print("Using webdriver-manager to install a compatible ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)
        
        # Create screenshot directory relative to this script's location
        # (Script runs from 'tests/' dir in workflow)
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
        # Load test cases from CSV
        cls.test_cases = []
        try:
            with open('dessert_test_cases.csv', mode='r', encoding='utf-8-sig') as file:
                csv_reader = csv.DictReader(file)
                cls.test_cases = list(csv_reader)
            print(f"✅ Loaded {len(cls.test_cases)} test cases from CSV")
        except FileNotFoundError:
            print("ERROR: 'dessert_test_cases.csv' not found. Please make sure it's in the same folder.")
            cls.test_cases = []
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test class - runs once after all tests."""
        print("\nAll tests finished. Closing browser...")
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def setUp(self):
        """Set up for each individual test - runs before each test method."""
        pass
    
    def tearDown(self):
        """Clean up after each individual test - runs after each test method."""
        pass
    
    def run_single_test_case(self, row):
        """Execute a single test case from CSV data."""
        test_id = row['Test_ID']
        description = row['Description']
        
        print(f"\n--- Running Test Case: {test_id} ({description}) ---")
        
        self.driver.get(BASE_URL)
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'calculateBtn')))

        # Fill in quantities
        for csv_key, input_id in ITEM_MAPPING.items():
            quantity = row[csv_key]
            if int(quantity) >= 0:
                qty_input = wait.until(EC.presence_of_element_located((By.ID, input_id)))
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", qty_input)
                self.driver.execute_script("arguments[0].value = arguments[1];", qty_input, quantity)
        
        total_items = 0
        for csv_key in ITEM_MAPPING.keys():
            total_items += int(row[csv_key])
        print(f"🛒 Total items in order: {total_items}")
        
        # Handle the discount toggle
        discount_needed = row['Discount_Enabled']
        discount_checkbox = wait.until(EC.presence_of_element_located((By.ID, 'discountToggle')))
        discount_slider = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.discount-toggle .slider')))
        is_checked = discount_checkbox.is_selected()

        if discount_needed == 'Yes' and not is_checked:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", discount_slider)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.discount-toggle .slider')))
            self.driver.execute_script("arguments[0].click();", discount_slider)
            wait.until(lambda driver: discount_checkbox.is_selected())
            self.assertTrue(discount_checkbox.is_selected(), "Discount toggle failed to enable")
        elif discount_needed == 'No' and is_checked:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", discount_slider)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.discount-toggle .slider')))
            self.driver.execute_script("arguments[0].click();", discount_slider)
            wait.until(lambda driver: not discount_checkbox.is_selected())
            self.assertFalse(discount_checkbox.is_selected(), "Discount toggle failed to disable")
        
        print(f"💰 Discount: {'Enabled' if discount_needed == 'Yes' else 'Disabled'} ✓")
            
        final_state = discount_checkbox.is_selected()
        expected_state = (discount_needed == 'Yes')
        self.assertEqual(final_state, expected_state, 
                        f"Discount toggle state mismatch: Expected {expected_state}, got {final_state}")

        # Click the "Calculate Bill" button
        calculate_button = wait.until(EC.element_to_be_clickable((By.ID, 'calculateBtn')))
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", calculate_button)
        self.driver.execute_script("arguments[0].click();", calculate_button)
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".receipt-row.subtotal .receipt-value")))
        
        # Extract actual values
        subtotal_spans = self.driver.find_elements(By.CSS_SELECTOR, ".receipt-row.subtotal .receipt-value")
        self.assertTrue(len(subtotal_spans) > 0, "Could not find subtotal on receipt page.")

        if discount_needed == 'Yes' and len(subtotal_spans) > 1:
            subtotal_text = subtotal_spans[-1].text
        else:
            subtotal_text = subtotal_spans[0].text

        actual_subtotal = subtotal_text.replace('RM', '').strip()
        actual_sst = self.driver.find_element(By.CSS_SELECTOR, ".receipt-row.sst .receipt-value").text.replace('RM', '').strip()
        actual_grand_total = self.driver.find_element(By.CSS_SELECTOR, ".receipt-row.grand-total .receipt-value").text.replace('RM', '').strip()

        # Get expected values
        expected_subtotal = row['Expected_Subtotal']
        expected_sst = row['Expected_SST']
        expected_grand_total = row['Expected_Grand_Total']

        # Verify values
        self.assertEqual(d(expected_subtotal), d(actual_subtotal), 
                        f"Subtotal mismatch: Expected '{expected_subtotal}' but got '{actual_subtotal}'")
        self.assertEqual(d(expected_sst), d(actual_sst), 
                        f"SST mismatch: Expected '{expected_sst}' but got '{actual_sst}'")
        self.assertEqual(d(expected_grand_total), d(actual_grand_total), 
                        f"Grand Total mismatch: Expected '{expected_grand_total}' but got '{actual_grand_total}'")
        
        print(f"✅ Subtotal: RM{actual_subtotal} | SST: RM{actual_sst} | Grand Total: RM{actual_grand_total}")

        # Test passed - save screenshot
        print(f"✅ Test Case {test_id}: PASS")
        timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")
        screenshot_file = os.path.join(SCREENSHOT_DIR, f"{test_id}_PASS_{timestamp}.png")
        self.driver.save_screenshot(screenshot_file)
        print(f"📸 Screenshot saved to {screenshot_file}")

    # HTML Report Generation
    def generate_html_report(self, results, total_duration):
        """Generates an HTML test report with statistics and visualizations."""
        print(f"\nGenerating HTML test report...")
        
        # Calculate statistics
        passed_count = sum(1 for r in results if r['status'] == 'PASS')
        failed_count = sum(1 for r in results if r['status'] == 'FAIL')
        total_tests = len(results)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate percentages for charts
        pass_percentage = (passed_count / total_tests * 100) if total_tests > 0 else 0
        fail_percentage = (failed_count / total_tests * 100) if total_tests > 0 else 0
        
        # Prepare percentage text for bar display (hide if too small)
        pass_text = f'{pass_percentage:.1f}%' if pass_percentage >= 5 else ''
        fail_text = f'{fail_percentage:.1f}%' if fail_percentage >= 5 else ''
        
        # Calculate overall success rate
        success_rate = pass_percentage
        
        # Calculate SVG circle parameters for donut chart
        radius = 70
        circumference = 2 * 3.14159 * radius
        pass_offset = circumference - (pass_percentage / 100 * circumference)
        fail_offset = circumference - (fail_percentage / 100 * circumference)
        
        # Build table rows for each test result
        table_rows_html = ""
        for r in results:
            status_badge = "pass-badge" if r['status'] == 'PASS' else "fail-badge"
            row_highlight = "fail-row" if r['status'] == 'FAIL' else ""
            icon = "✓" if r['status'] == 'PASS' else "✗"
            
            error_display = (
                f"<div class='error-box'>{html.escape(r['details'])}</div>" 
                if r['status'] == 'FAIL' 
                else '<span class="no-error">—</span>'
            )
            
            table_rows_html += f"""
                <tr class='data-row {row_highlight}'>
                    <td class='test-id'>{html.escape(r['id'])}</td>
                    <td><span class='badge {status_badge}'>{icon} {r['status']}</span></td>
                    <td class='duration-cell'>{r['duration']:.2f}s</td>
                    <td class='details-cell'>{error_display}</td>
                </tr>
            """
        
        # HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Report - Petite Pâtisserie</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                :root {{
                    --primary-color: #2563eb;
                    --primary-dark: #1e40af;
                    --success-color: #10b981;
                    --success-light: #d1fae5;
                    --danger-color: #ef4444;
                    --danger-light: #fee2e2;
                    --gray-50: #f9fafb;
                    --gray-100: #f3f4f6;
                    --gray-200: #e5e7eb;
                    --gray-300: #d1d5db;
                    --gray-400: #9ca3af;
                    --gray-500: #6b7280;
                    --gray-600: #4b5563;
                    --gray-700: #374151;
                    --gray-800: #1f2937;
                    --gray-900: #111827;
                    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
                    --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
                    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
                    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: var(--gray-50);
                    color: var(--gray-900);
                    line-height: 1.6;
                    padding: 2rem 1rem;
                }}
                
                .report-container {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                
                /* Header Section */
                .header {{
                    background: white;
                    padding: 2.5rem 2rem;
                    border-radius: 12px;
                    margin-bottom: 2rem;
                    box-shadow: var(--shadow);
                    border-left: 4px solid var(--primary-color);
                }}
                
                .header h1 {{
                    font-size: 2rem;
                    font-weight: 700;
                    color: var(--gray-900);
                    margin-bottom: 0.5rem;
                }}
                
                .header .subtitle {{
                    font-size: 1rem;
                    color: var(--gray-600);
                    font-weight: 500;
                    margin-bottom: 1rem;
                }}
                
                .timestamp {{
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.5rem 1rem;
                    background: var(--gray-100);
                    color: var(--gray-700);
                    border-radius: 6px;
                    font-size: 0.875rem;
                    font-weight: 500;
                }}
                
                /* Stats Grid */
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }}
                
                .stat-card {{
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    box-shadow: var(--shadow);
                    border-left: 4px solid;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-lg);
                }}
                
                .stat-card.total {{
                    border-color: var(--primary-color);
                }}
                
                .stat-card.passed {{
                    border-color: var(--success-color);
                }}
                
                .stat-card.failed {{
                    border-color: var(--danger-color);
                }}
                
                .stat-card.time {{
                    border-color: var(--gray-500);
                }}
                
                .stat-card .label {{
                    font-size: 0.875rem;
                    font-weight: 600;
                    color: var(--gray-600);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 0.5rem;
                }}
                
                .stat-card .value {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: var(--gray-900);
                    line-height: 1;
                }}
                
                /* Charts Section */
                .charts-section {{
                    display: grid;
                    grid-template-columns: 1fr 1.5fr;
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }}
                
                @media (max-width: 968px) {{
                    .charts-section {{
                        grid-template-columns: 1fr;
                    }}
                }}
                
                .chart-card {{
                    background: white;
                    border-radius: 12px;
                    padding: 2rem;
                    box-shadow: var(--shadow);
                }}
                
                .chart-card h3 {{
                    font-size: 1.25rem;
                    font-weight: 700;
                    color: var(--gray-900);
                    margin-bottom: 1.5rem;
                }}
                
                /* Donut Chart */
                .donut-chart {{
                    position: relative;
                    width: 200px;
                    height: 200px;
                    margin: 2rem auto;
                }}
                
                .donut-chart svg {{
                    transform: rotate(-90deg);
                }}
                
                .donut-chart circle {{
                    fill: none;
                    stroke-width: 20;
                }}
                
                .donut-bg {{
                    stroke: var(--gray-200);
                }}
                
                .donut-pass {{
                    stroke: var(--success-color);
                    stroke-dasharray: {circumference};
                    stroke-dashoffset: {pass_offset};
                    stroke-linecap: round;
                    transition: stroke-dashoffset 1s ease;
                }}
                
                .donut-center {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                }}
                
                .donut-center .percentage {{
                    font-size: 2.5rem;
                    font-weight: 800;
                    color: var(--gray-900);
                }}
                
                .donut-center .label {{
                    font-size: 0.875rem;
                    color: var(--gray-600);
                    font-weight: 600;
                    margin-top: 0.25rem;
                }}
                
                .chart-legend {{
                    display: flex;
                    justify-content: center;
                    gap: 2rem;
                    margin-top: 1.5rem;
                }}
                
                .legend-item {{
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: var(--gray-700);
                }}
                
                .legend-dot {{
                    width: 14px;
                    height: 14px;
                    border-radius: 50%;
                }}
                
                .legend-dot.pass {{
                    background: var(--success-color);
                }}
                
                .legend-dot.fail {{
                    background: var(--danger-color);
                }}
                
                /* Bar Charts */
                .bar-item {{
                    margin-bottom: 2rem;
                }}
                
                .bar-item:last-child {{
                    margin-bottom: 0;
                }}
                
                .bar-header {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 0.5rem;
                    font-weight: 600;
                    color: var(--gray-700);
                    font-size: 0.875rem;
                }}
                
                .bar-track {{
                    height: 32px;
                    background: var(--gray-100);
                    border-radius: 8px;
                    overflow: hidden;
                    position: relative;
                }}
                
                .bar-track.empty::after {{
                    content: '0%';
                    position: absolute;
                    left: 1rem;
                    top: 50%;
                    transform: translateY(-50%);
                    color: var(--gray-500);
                    font-size: 0.875rem;
                    font-weight: 600;
                }}
                
                .bar-track.empty .bar-fill {{
                    display: none;
                }}
                
                .bar-fill {{
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    padding: 0 1rem;
                    color: white;
                    font-weight: 600;
                    font-size: 0.875rem;
                    transition: width 1s cubic-bezier(0.65, 0, 0.35, 1);
                    border-radius: 8px;
                }}
                
                .bar-fill.pass {{
                    background: var(--success-color);
                }}
                
                .bar-fill.fail {{
                    background: var(--danger-color);
                }}
                
                /* Results Table */
                .results-section {{
                    margin-top: 2rem;
                }}
                
                .results-section h2 {{
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--gray-900);
                    margin-bottom: 1.5rem;
                }}
                
                .table-container {{
                    background: white;
                    border-radius: 12px;
                    box-shadow: var(--shadow);
                    overflow: hidden;
                }}
                
                .results-table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                
                .results-table thead {{
                    background: var(--gray-50);
                    border-bottom: 2px solid var(--gray-200);
                }}
                
                .results-table th {{
                    padding: 1rem 1.5rem;
                    text-align: left;
                    font-weight: 600;
                    font-size: 0.875rem;
                    color: var(--gray-700);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }}
                
                .results-table td {{
                    padding: 1rem 1.5rem;
                    border-bottom: 1px solid var(--gray-200);
                }}
                
                .data-row {{
                    transition: background 0.15s ease;
                }}
                
                .data-row:hover {{
                    background: var(--gray-50);
                }}
                
                .data-row:last-child td {{
                    border-bottom: none;
                }}
                
                .data-row.fail-row {{
                    background: var(--danger-light);
                }}
                
                .data-row.fail-row:hover {{
                    background: #fecaca;
                }}
                
                .test-id {{
                    font-weight: 600;
                    color: var(--primary-color);
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                }}
                
                .badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 0.375rem;
                    padding: 0.375rem 0.75rem;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 0.875rem;
                }}
                
                .pass-badge {{
                    background: var(--success-light);
                    color: #065f46;
                }}
                
                .fail-badge {{
                    background: var(--danger-light);
                    color: #991b1b;
                }}
                
                .duration-cell {{
                    font-family: 'Courier New', monospace;
                    font-weight: 600;
                    color: var(--gray-700);
                    font-size: 0.9rem;
                }}
                
                .no-error {{
                    color: var(--gray-400);
                    font-size: 1.2rem;
                }}
                
                .error-box {{
                    background: white;
                    border: 1px solid var(--danger-color);
                    border-left: 3px solid var(--danger-color);
                    padding: 0.75rem 1rem;
                    border-radius: 6px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.813rem;
                    color: var(--gray-800);
                    white-space: pre-wrap;
                    word-break: break-word;
                    line-height: 1.5;
                }}
                
                @media print {{
                    body {{
                        background: white;
                        padding: 0;
                    }}
                    
                    .stat-card,
                    .chart-card,
                    .table-container {{
                        box-shadow: none;
                        border: 1px solid var(--gray-200);
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                <!-- Header -->
                <div class="header">
                    <h1>🧁 Test Execution Report</h1>
                    <p class="subtitle">Petite Pâtisserie - Automated Testing Suite</p>
                    <span class="timestamp">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        {timestamp}
                    </span>
                </div>
                
                <!-- Stats Cards -->
                <div class="stats-grid">
                    <div class="stat-card total">
                        <div class="label">Total Tests</div>
                        <div class="value">{total_tests}</div>
                    </div>
                    <div class="stat-card passed">
                        <div class="label">✓ Passed</div>
                        <div class="value">{passed_count}</div>
                    </div>
                    <div class="stat-card failed">
                        <div class="label">✗ Failed</div>
                        <div class="value">{failed_count}</div>
                    </div>
                    <div class="stat-card time">
                        <div class="label">Duration</div>
                        <div class="value">{total_duration:.1f}s</div>
                    </div>
                </div>
                
                <!-- Charts -->
                <div class="charts-section">
                    <!-- Donut Chart -->
                    <div class="chart-card">
                        <h3>Success Rate</h3>
                        <div class="donut-chart">
                            <svg width="200" height="200">
                                <circle class="donut-bg" cx="100" cy="100" r="{radius}"></circle>
                                <circle class="donut-pass" cx="100" cy="100" r="{radius}"></circle>
                            </svg>
                            <div class="donut-center">
                                <div class="percentage">{success_rate:.0f}%</div>
                                <div class="label">Success</div>
                            </div>
                        </div>
                        <div class="chart-legend">
                            <div class="legend-item">
                                <span class="legend-dot pass"></span>
                                <span>Pass ({pass_percentage:.1f}%)</span>
                            </div>
                            <div class="legend-item">
                                <span class="legend-dot fail"></span>
                                <span>Fail ({fail_percentage:.1f}%)</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Bar Charts -->
                    <div class="chart-card">
                        <h3>Test Results Breakdown</h3>
                        <div class="bar-item">
                            <div class="bar-header">
                                <span>Passed Tests</span>
                                <span>{passed_count} / {total_tests}</span>
                            </div>
                            <div class="bar-track">
                                <div class="bar-fill pass" style="width: {pass_percentage}%;">
                                    {pass_text}
                                </div>
                            </div>
                        </div>
                        <div class="bar-item">
                            <div class="bar-header">
                                <span>Failed Tests</span>
                                <span>{failed_count} / {total_tests}</span>
                            </div>
                            <div class="bar-track{' empty' if fail_percentage == 0 else ''}">
                                <div class="bar-fill fail" style="width: {fail_percentage}%;">
                                    {fail_text}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Test Results Table -->
                <div class="results-section">
                    <h2>Test Case Details</h2>
                    <div class="table-container">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th>Test ID</th>
                                    <th>Status</th>
                                    <th>Duration</th>
                                    <th>Error Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table_rows_html}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save the report
        try:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📊 HTML Test Report generated: {REPORT_FILE}")
        except Exception as e:
            print(f"⚠️ Could not write HTML report: {e}")

    # Main Test Execution Method
    def test_all_dessert_orders(self):
        """Run all test cases from CSV and generate a report"""
        test_results_summary = []
        overall_start_time = time.time()
        
        for row in self.test_cases:
            test_id = row['Test_ID']
            test_start_time = time.time()
            
            try:
                self.run_single_test_case(row)
                test_end_time = time.time()
                duration = test_end_time - test_start_time
                test_results_summary.append({
                    'id': test_id, 
                    'status': 'PASS', 
                    'details': 'N/A', 
                    'duration': duration
                })
                
            except (AssertionError, NoSuchElementException, TimeoutException, Exception) as e:
                test_end_time = time.time()
                duration = test_end_time - test_start_time
                full_error = traceback.format_exc()
                
                print(f"❌ Test Case {test_id}: FAIL")
                print(f"⚠️ Error: {e}")
                
                log_error_to_file(test_id, full_error)
                
                timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")
                screenshot_file = os.path.join(SCREENSHOT_DIR, f"{test_id}_FAIL_{timestamp}.png")
                self.driver.save_screenshot(screenshot_file)
                print(f"📸 Screenshot saved to {screenshot_file}")
                print(f"📝 Full error log saved to {ERROR_LOG_FILE}")
                
                error_summary = str(e).splitlines()[0] if str(e).splitlines() else str(e)
                test_results_summary.append({
                    'id': test_id,
                    'status': 'FAIL',
                    'details': error_summary,
                    'duration': duration
                })
        
        # Console Summary
        overall_end_time = time.time()
        total_duration = overall_end_time - overall_start_time
        
        print("\n\n" + "=" * 60)
        print("                 TEST RUN SUMMARY (Console)")
        print("=" * 60)
        print(f"{'Test ID':<10} | {'Status':<10} | {'Duration (s)':<15} | {'Details':<30}")
        print("-" * 60)
        
        failed_count = 0
        for result in test_results_summary:
            test_id = result['id']
            status = result['status']
            details = result['details']
            duration = result['duration']
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"{test_id:<10} | {status_icon} {status:<8} | {duration:<15.2f} | {details:<30}")
            if status == "FAIL":
                failed_count += 1
        
        print("-" * 60)
        total_tests = len(test_results_summary)
        passed_count = total_tests - failed_count
        print(f"Total Tests: {total_tests}, Passed: {passed_count}, Failed: {failed_count}")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print("=" * 60)
        
        # Generate HTML Report
        self.generate_html_report(test_results_summary, total_duration)
        
        self.assertEqual(failed_count, 0, f"{failed_count} test case(s) failed")


# Main execution
if __name__ == "__main__":
    print("🚀 Running tests in GitHub Actions environment...")
    print("=" * 60)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(DessertOrderTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n🎉 Result: All test cases passed! 🎉")
        sys.exit(0)
    else:
        print(f"\n❌ Result: {len(result.failures) + len(result.errors)} test(s) failed.")
        sys.exit(1)
