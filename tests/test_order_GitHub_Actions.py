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
        """Generates a report from the test results."""
        print(f"\nGenerating HTML test report...")
    
        # Calculate stats
        passed_count = sum(1 for r in results if r['status'] == 'PASS')
        failed_count = sum(1 for r in results if r['status'] == 'FAIL')
        total_tests = len(results)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate percentages for visual elements
        pass_percentage = (passed_count / total_tests * 100) if total_tests > 0 else 0
        fail_percentage = (failed_count / total_tests * 100) if total_tests > 0 else 0
    
        # Build Table Rows
        table_rows_html = ""
        for r in results:
            status_class = "status-pass" if r['status'] == 'PASS' else "status-fail"
            row_class = "row-fail" if r['status'] == 'FAIL' else ""
            icon = "✅" if r['status'] == 'PASS' else "❌"
            details_html = (
                f"<pre class='error-details'>{html.escape(r['details'])}</pre>" 
                if r['status'] == 'FAIL' 
                else 'N/A'
            )
            
            table_rows_html += f"""
                <tr class='{row_class}'>
                    <td>{html.escape(r['id'])}</td>
                    <td class='{status_class}'>{icon} {r['status']}</td>
                    <td>{r['duration']:.2f} s</td>
                    <td>{details_html}</td>
                </tr>
            """
    
        # HTML & CSS Content with Visual Elements
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Run Report - Petite Pâtisserie</title>
            <style>
                :root {{
                    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    --color-pass: #28a745;
                    --color-fail: #dc3545;
                    --color-total: #007bff;
                    --color-time: #6c757d;
                    --color-bg: #f4f7f6;
                    --color-bg-light: #ffffff;
                    --color-bg-fail-light: #fbeeee;
                    --color-border: #e0e0e0;
                    --color-text: #212529;
                    --color-text-muted: #6c757d;
                    --shadow: 0 4px 8px rgba(0,0,0,0.05);
                    --radius: 8px;
                }}
                body {{
                    font-family: var(--font-sans);
                    background-color: var(--color-bg);
                    color: var(--color-text);
                    margin: 0;
                    padding: 24px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1 {{
                    font-size: 2.25rem;
                    color: var(--color-text);
                    border-bottom: 2px solid var(--color-border);
                    padding-bottom: 10px;
                    margin-bottom: 16px;
                }}
                .report-meta {{
                    font-size: 0.9rem;
                    color: var(--color-text-muted);
                    margin-bottom: 24px;
                }}
                h2 {{
                    font-size: 1.75rem;
                    margin-bottom: 16px;
                    margin-top: 32px;
                }}
                
                /* Summary Cards */
                .summary-container {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 32px;
                }}
                .summary-card {{
                    background: var(--color-bg-light);
                    border-radius: var(--radius);
                    box-shadow: var(--shadow);
                    padding: 24px;
                    flex: 1;
                    min-width: 220px;
                    border-top: 4px solid;
                }}
                .summary-card h3 {{
                    margin: 0 0 8px 0;
                    font-size: 1.1rem;
                    color: var(--color-text-muted);
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                .summary-card .count {{
                    font-size: 2.5rem;
                    font-weight: 700;
                }}
                .summary-card.total {{
                    border-color: var(--color-total);
                }}
                .summary-card.total .count {{
                    color: var(--color-total);
                }}
                .summary-card.passed {{
                    border-color: var(--color-pass);
                }}
                .summary-card.passed .count {{
                    color: var(--color-pass);
                }}
                .summary-card.failed {{
                    border-color: var(--color-fail);
                }}
                .summary-card.failed .count {{
                    color: var(--color-fail);
                }}
                .summary-card.duration {{
                    border-color: var(--color-time);
                }}
                .summary-card.duration .count {{
                    color: var(--color-time);
                }}
    
                /* Visual Chart Section */
                .visual-section {{
                    display: flex;
                    gap: 30px;
                    margin-bottom: 32px;
                    flex-wrap: wrap;
                }}
                
                /* Pie Chart */
                .chart-container {{
                    background: var(--color-bg-light);
                    border-radius: var(--radius);
                    box-shadow: var(--shadow);
                    padding: 24px;
                    flex: 1;
                    min-width: 300px;
                    text-align: center;
                }}
                .chart-container h3 {{
                    margin-top: 0;
                    color: var(--color-text);
                }}
                .pie-chart {{
                    width: 200px;
                    height: 200px;
                    border-radius: 50%;
                    background: conic-gradient(
                        var(--color-pass) 0deg {pass_percentage * 3.6}deg,
                        var(--color-fail) {pass_percentage * 3.6}deg 360deg
                    );
                    margin: 20px auto;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .chart-legend {{
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin-top: 16px;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .legend-color {{
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                }}
                .legend-color.pass {{
                    background-color: var(--color-pass);
                }}
                .legend-color.fail {{
                    background-color: var(--color-fail);
                }}
                
                /* Progress Bars */
                .progress-container {{
                    background: var(--color-bg-light);
                    border-radius: var(--radius);
                    box-shadow: var(--shadow);
                    padding: 24px;
                    flex: 1;
                    min-width: 300px;
                }}
                .progress-container h3 {{
                    margin-top: 0;
                    color: var(--color-text);
                }}
                .progress-item {{
                    margin-bottom: 20px;
                }}
                .progress-label {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                    font-size: 0.9rem;
                    font-weight: 600;
                }}
                .progress-bar-bg {{
                    background-color: #e9ecef;
                    border-radius: 10px;
                    height: 24px;
                    overflow: hidden;
                }}
                .progress-bar {{
                    height: 100%;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 0.85rem;
                    font-weight: 700;
                    transition: width 0.5s ease;
                }}
                .progress-bar.pass {{
                    background-color: var(--color-pass);
                }}
                .progress-bar.fail {{
                    background-color: var(--color-fail);
                }}
    
                /* Table Styles */
                .details-table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: var(--color-bg-light);
                    box-shadow: var(--shadow);
                    border-radius: var(--radius);
                    overflow: hidden;
                }}
                .details-table th,
                .details-table td {{
                    border: 1px solid var(--color-border);
                    padding: 12px 16px;
                    text-align: left;
                    vertical-align: top;
                }}
                .details-table thead {{
                    background-color: #f8f9fa;
                }}
                .details-table th {{
                    font-weight: 600;
                }}
                .details-table tr:hover {{
                    background-color: #f1f1f1;
                }}
                .status-pass {{
                    color: var(--color-pass);
                    font-weight: 700;
                }}
                .status-fail {{
                    color: var(--color-fail);
                    font-weight: 700;
                }}
                .row-fail {{
                    background-color: var(--color-bg-fail-light);
                }}
                .error-details {{
                    background: #fff0f0;
                    border: 1px solid var(--color-fail);
                    color: var(--color-fail);
                    padding: 10px;
                    border-radius: 4px;
                    font-family: monospace;
                    font-size: 0.85rem;
                    white-space: pre-wrap;
                    word-break: break-all;
                    margin: 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Test Run Report</h1>
                <p class="report-meta">
                    <strong>Project:</strong> Petite Pâtisserie<br>
                    <strong>Generated on:</strong> {timestamp}
                </p>
    
                <h2>Run Summary</h2>
                <div class="summary-container">
                    <div class="summary-card total">
                        <h3>📦 Total Tests</h3>
                        <p class="count">{total_tests}</p>
                    </div>
                    <div class="summary-card passed">
                        <h3>✅ Passed</h3>
                        <p class="count">{passed_count}</p>
                    </div>
                    <div class="summary-card failed">
                        <h3>❌ Failed</h3>
                        <p class="count">{failed_count}</p>
                    </div>
                    <div class="summary-card duration">
                        <h3>⏱️ Total Duration</h3>
                        <p class="count">{total_duration:.2f} s</p>
                    </div>
                </div>
    
                <h2>Visual Test Results</h2>
                <div class="visual-section">
                    <!-- Pie Chart -->
                    <div class="chart-container">
                        <h3>📊 Test Results Distribution</h3>
                        <div class="pie-chart"></div>
                        <div class="chart-legend">
                            <div class="legend-item">
                                <div class="legend-color pass"></div>
                                <span>Passed ({pass_percentage:.1f}%)</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-color fail"></div>
                                <span>Failed ({fail_percentage:.1f}%)</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Progress Bars -->
                    <div class="progress-container">
                        <h3>📈 Test Statistics</h3>
                        <div class="progress-item">
                            <div class="progress-label">
                                <span>Passed Tests</span>
                                <span>{passed_count} of {total_tests}</span>
                            </div>
                            <div class="progress-bar-bg">
                                <div class="progress-bar pass" style="width: {pass_percentage}%;">
                                    {pass_percentage:.1f}%
                                </div>
                            </div>
                        </div>
                        <div class="progress-item">
                            <div class="progress-label">
                                <span>Failed Tests</span>
                                <span>{failed_count} of {total_tests}</span>
                            </div>
                            <div class="progress-bar-bg">
                                <div class="progress-bar fail" style="width: {fail_percentage}%;">
                                    {fail_percentage:.1f}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
    
                <h2>Test Details</h2>
                <table class="details-table">
                    <thead>
                        <tr>
                            <th>Test ID</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
    
        # Write the content to the report file
        try:
            # REPORT_FILE is now just "test_report.html",
            # saving it in the CWD
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
