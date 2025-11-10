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


def take_screenshot(driver, test_id, page_name):
    """Takes a screenshot of the current page and saves it."""
    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")
        filename = f"{test_id}_{page_name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(filepath)
        print(f"📸 Screenshot saved: {filename}")
        return filepath
    except Exception as e:
        print(f"⚠️ Failed to take screenshot: {e}")
        return None


class DessertOrderTestCase(unittest.TestCase):
    """Unit test class for testing dessert ordering system using Selenium in GitHub Actions."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - runs once before all tests."""
        print("Setting up the browser for GitHub Actions (headless mode)...")
        options = Options()
        
        # Chrome arguments
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--no-first-run')
        options.add_argument('--log-level=3')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        cls.driver = webdriver.Chrome(options=options)
        
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

        take_screenshot(self.driver, test_id, "order_page")

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
        
        take_screenshot(self.driver, test_id, "results_page")

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
        
        # HTML template with embedded CSS and JavaScript
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Testing Report - Petite Pâtisserie</title>
            <style>
                /* CSS Variables - Color Palette */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                :root {{
                    --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    --gradient-success: linear-gradient(135deg, #0ba360 0%, #3cba92 100%);
                    --gradient-danger: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    --gradient-info: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    --color-purple: #667eea;
                    --color-teal: #3cba92;
                    --color-pink: #f5576c;
                    --color-blue: #4facfe;
                    --color-dark: #2d3748;
                    --color-light: #f7fafc;
                    --color-white: #ffffff;
                    --color-gray: #718096;
                    --shadow-soft: 0 10px 40px rgba(102, 126, 234, 0.15);
                    --shadow-hover: 0 15px 50px rgba(102, 126, 234, 0.25);
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: var(--color-dark);
                }}
                
                /* Main Report Container */
                .report-container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 24px;
                    padding: 40px;
                    box-shadow: var(--shadow-soft);
                }}
                
                /* Header Section */
                .header {{
                    text-align: center;
                    margin-bottom: 50px;
                    position: relative;
                }}
                
                .header h1 {{
                    font-size: 3rem;
                    font-weight: 800;
                    background: var(--gradient-primary);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 10px;
                    letter-spacing: -1px;
                }}
                
                .header .subtitle {{
                    font-size: 1.1rem;
                    color: var(--color-gray);
                    font-weight: 500;
                }}
                
                .timestamp {{
                    display: inline-block;
                    margin-top: 15px;
                    padding: 8px 20px;
                    background: var(--gradient-info);
                    color: white;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    font-weight: 600;
                }}
                
                /* Stats Grid Layout */
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 25px;
                    margin-bottom: 50px;
                }}
                
                /* Individual Stat Card Styling */
                .stat-card {{
                    padding: 30px;
                    border-radius: 20px;
                    color: white;
                    position: relative;
                    overflow: hidden;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: var(--shadow-hover);
                }}
                
                .stat-card.total {{
                    background: var(--gradient-info);
                }}
                
                .stat-card.passed {{
                    background: var(--gradient-success);
                }}
                
                .stat-card.failed {{
                    background: var(--gradient-danger);
                }}
                
                .stat-card.time {{
                    background: var(--gradient-primary);
                }}
                
                .stat-card .label {{
                    font-size: 0.95rem;
                    opacity: 0.9;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 10px;
                }}
                
                .stat-card .value {{
                    font-size: 3rem;
                    font-weight: 800;
                    line-height: 1;
                }}
                
                /* Charts Section */
                .charts-section {{
                    display: grid;
                    grid-template-columns: 1fr 1.5fr;
                    gap: 30px;
                    margin-bottom: 50px;
                }}
                
                @media (max-width: 968px) {{
                    .charts-section {{
                        grid-template-columns: 1fr;
                    }}
                }}
                
                /* Chart Card */
                .chart-card {{
                    background: white;
                    border-radius: 20px;
                    padding: 35px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                }}
                
                .chart-card h3 {{
                    font-size: 1.4rem;
                    margin-bottom: 25px;
                    color: var(--color-dark);
                    font-weight: 700;
                }}
                
                /* SVG Donut Chart Container */
                .donut-chart {{
                    position: relative;
                    width: 200px;
                    height: 200px;
                    margin: 30px auto;
                }}
                
                .donut-chart svg {{
                    transform: rotate(-90deg);
                }}
                
                .donut-chart circle {{
                    fill: none;
                    stroke-width: 20;
                }}
                
                .donut-bg {{
                    stroke: #e2e8f0;
                }}
                
                .donut-pass {{
                    stroke: url(#passGradient);
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
                    background: var(--gradient-success);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                
                .donut-center .label {{
                    font-size: 0.85rem;
                    color: var(--color-gray);
                    font-weight: 600;
                    margin-top: 5px;
                }}
                
                .chart-legend {{
                    display: flex;
                    justify-content: center;
                    gap: 30px;
                    margin-top: 20px;
                }}
                
                .legend-item {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-weight: 600;
                }}
                
                .legend-dot {{
                    width: 16px;
                    height: 16px;
                    border-radius: 50%;
                }}
                
                .legend-dot.pass {{
                    background: var(--gradient-success);
                }}
                
                .legend-dot.fail {{
                    background: var(--gradient-danger);
                }}
                
                /* Horizontal Bar Charts */
                .bar-item {{
                    margin-bottom: 25px;
                }}
                
                .bar-header {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    font-weight: 600;
                    color: var(--color-dark);
                }}
                
                .bar-track {{
                    height: 35px;
                    background: #e2e8f0;
                    border-radius: 50px;
                    overflow: hidden;
                    position: relative;
                }}
                
                .bar-track.empty::after {{
                    content: '0%';
                    position: absolute;
                    left: 20px;
                    top: 50%;
                    transform: translateY(-50%);
                    color: var(--color-gray);
                    font-size: 0.85rem;
                    font-weight: 600;
                }}
                
                .bar-track.empty .bar-fill {{
                    display: none;
                }}
                
                .bar-fill {{
                    height: 100%;
                    border-radius: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    padding-right: 15px;
                    color: white;
                    font-weight: 700;
                    font-size: 0.9rem;
                    transition: width 1s cubic-bezier(0.65, 0, 0.35, 1);
                }}
                
                .bar-fill.pass {{
                    background: var(--gradient-success);
                }}
                
                .bar-fill.fail {{
                    background: var(--gradient-danger);
                }}
                
                /* Test Results Table */
                .results-section {{
                    margin-top: 50px;
                }}
                
                .results-section h2 {{
                    font-size: 2rem;
                    margin-bottom: 25px;
                    color: var(--color-dark);
                    font-weight: 700;
                }}
                
                .results-table {{
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                }}
                
                .results-table thead {{
                    background: var(--gradient-primary);
                    color: white;
                }}
                
                .results-table th {{
                    padding: 18px 20px;
                    text-align: left;
                    font-weight: 700;
                    font-size: 0.95rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                .results-table td {{
                    padding: 18px 20px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                
                .data-row {{
                    transition: background 0.2s ease;
                }}
                
                .data-row:hover {{
                    background: #f7fafc;
                }}
                
                .data-row.fail-row {{
                    background: #fff5f7;
                }}
                
                .data-row.fail-row:hover {{
                    background: #ffe5e9;
                }}
                
                .test-id {{
                    font-weight: 700;
                    color: var(--color-purple);
                    font-family: 'Courier New', monospace;
                }}
                
                .badge {{
                    display: inline-block;
                    padding: 6px 16px;
                    border-radius: 20px;
                    font-weight: 700;
                    font-size: 0.85rem;
                }}
                
                .pass-badge {{
                    background: var(--gradient-success);
                    color: white;
                }}
                
                .fail-badge {{
                    background: var(--gradient-danger);
                    color: white;
                }}
                
                .duration-cell {{
                    font-family: 'Courier New', monospace;
                    font-weight: 600;
                    color: var(--color-blue);
                }}
                
                .no-error {{
                    color: var(--color-gray);
                    font-size: 1.2rem;
                }}
                
                .error-box {{
                    background: linear-gradient(135deg, #fff5f7 0%, #ffe5e9 100%);
                    border-left: 4px solid var(--color-pink);
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.85rem;
                    color: var(--color-dark);
                    white-space: pre-wrap;
                    word-break: break-word;
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                <!-- Header -->
                <div class="header">
                    <h1>🧁 Test Execution Report</h1>
                    <p class="subtitle">Petite Pâtisserie - Automated Testing Suite</p>
                    <span class="timestamp">🕐 Generated: {timestamp}</span>
                </div>
                
                <!-- Stats Cards Grid -->
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
                
                <!-- Charts Section -->
                <div class="charts-section">
                    <!-- Donut Chart -->
                    <div class="chart-card">
                        <h3>Success Rate</h3>
                        <div class="donut-chart">
                            <svg width="200" height="200">
                                <defs>
                                    <linearGradient id="passGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" style="stop-color:#0ba360;stop-opacity:1" />
                                        <stop offset="100%" style="stop-color:#3cba92;stop-opacity:1" />
                                    </linearGradient>
                                </defs>
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
                    
                    <!-- Horizontal Bar Charts -->
                    <div class="chart-card">
                        <h3>Detailed Breakdown</h3>
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
