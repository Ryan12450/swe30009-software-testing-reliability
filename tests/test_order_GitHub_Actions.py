import time
import csv
import os
import sys
import traceback
import unittest
import html
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
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

        # --- FIXED DRIVER SETUP ---
        # Let Selenium Manager auto-resolve a compatible ChromeDriver.
        # This avoids version mismatch on GitHub Actions runners.
        print("Using Selenium Manager to resolve a compatible ChromeDriver...")
        cls.driver = webdriver.Chrome(options=options)

        # Create screenshot directory
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
        pass

    def tearDown(self):
        pass

    def run_single_test_case(self, row):
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

        total_items = sum(int(row[k]) for k in ITEM_MAPPING.keys())
        print(f"🛒 Total items in order: {total_items}")

        # Handle discount toggle
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
        self.assertEqual(final_state, expected_state, f"Discount toggle state mismatch: Expected {expected_state}, got {final_state}")

        calculate_button = wait.until(EC.element_to_be_clickable((By.ID, 'calculateBtn')))
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", calculate_button)
        self.driver.execute_script("arguments[0].click();", calculate_button)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".receipt-row.subtotal .receipt-value")))

        subtotal_spans = self.driver.find_elements(By.CSS_SELECTOR, ".receipt-row.subtotal .receipt-value")
        self.assertTrue(len(subtotal_spans) > 0, "Could not find subtotal on receipt page.")

        subtotal_text = subtotal_spans[-1].text if (discount_needed == 'Yes' and len(subtotal_spans) > 1) else subtotal_spans[0].text

        actual_subtotal = subtotal_text.replace('RM', '').strip()
        actual_sst = self.driver.find_element(By.CSS_SELECTOR, ".receipt-row.sst .receipt-value").text.replace('RM', '').strip()
        actual_grand_total = self.driver.find_element(By.CSS_SELECTOR, ".receipt-row.grand-total .receipt-value").text.replace('RM', '').strip()

        expected_subtotal = row['Expected_Subtotal']
        expected_sst = row['Expected_SST']
        expected_grand_total = row['Expected_Grand_Total']

        self.assertEqual(d(expected_subtotal), d(actual_subtotal), f"Subtotal mismatch: Expected '{expected_subtotal}' but got '{actual_subtotal}'")
        self.assertEqual(d(expected_sst), d(actual_sst), f"SST mismatch: Expected '{expected_sst}' but got '{actual_sst}'")
        self.assertEqual(d(expected_grand_total), d(actual_grand_total), f"Grand Total mismatch: Expected '{expected_grand_total}' but got '{actual_grand_total}'")

        print(f"✅ Subtotal: RM{actual_subtotal} | SST: RM{actual_sst} | Grand Total: RM{actual_grand_total}")

        print(f"✅ Test Case {test_id}: PASS")
        timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")
        screenshot_file = os.path.join(SCREENSHOT_DIR, f"{test_id}_PASS_{timestamp}.png")
        self.driver.save_screenshot(screenshot_file)
        print(f"📸 Screenshot saved to {screenshot_file}")

    def generate_html_report(self, results, total_duration):
        passed_count = sum(1 for r in results if r['status'] == 'PASS')
        failed_count = sum(1 for r in results if r['status'] == 'FAIL')
        total_tests = len(results)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        pass_percentage = (passed_count / total_tests * 100) if total_tests > 0 else 0
        fail_percentage = (failed_count / total_tests * 100) if total_tests > 0 else 0
        pass_text = f'{pass_percentage:.1f}%' if pass_percentage >= 5 else ''
        fail_text = f'{fail_percentage:.1f}%' if fail_percentage >= 5 else ''
        success_rate = pass_percentage

        radius = 70
        circumference = 2 * 3.14159 * radius
        pass_offset = circumference - (pass_percentage / 100 * circumference)

        table_rows_html = ""
        for r in results:
            status_badge = "pass-badge" if r['status'] == 'PASS' else "fail-badge"
            row_highlight = "fail-row" if r['status'] == 'FAIL' else ""
            icon = "✓" if r['status'] == 'PASS' else "✗"
            error_display = f"<div class='error-box'>{html.escape(r['details'])}</div>" if r['status'] == 'FAIL' else '<span class="no-error">—</span>'
            table_rows_html += f"""
                <tr class='data-row {row_highlight}'>
                    <td class='test-id'>{html.escape(r['id'])}</td>
                    <td><span class='badge {status_badge}'>{icon} {r['status']}</span></td>
                    <td class='duration-cell'>{r['duration']:.2f}s</td>
                    <td class='details-cell'>{error_display}</td>
                </tr>
            """

        html_content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Test Report</title></head>
<body><h1>Test Report</h1><p>Generated: {timestamp}</p>
<p>Total: {total_tests} | Passed: {passed_count} | Failed: {failed_count} | Duration: {total_duration:.2f}s</p>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>Test ID</th><th>Status</th><th>Duration</th><th>Details</th></tr>
{table_rows_html}
</table></body></html>"""

        try:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📊 HTML Test Report generated: {REPORT_FILE}")
        except Exception as e:
            print(f"⚠️ Could not write HTML report: {e}")

    def test_all_dessert_orders(self):
        test_results_summary = []
        overall_start_time = time.time()

        for row in self.test_cases:
            test_id = row['Test_ID']
            test_start_time = time.time()
            try:
                self.run_single_test_case(row)
                duration = time.time() - test_start_time
                test_results_summary.append({'id': test_id, 'status': 'PASS', 'details': 'N/A', 'duration': duration})
            except (AssertionError, NoSuchElementException, TimeoutException, Exception) as e:
                duration = time.time() - test_start_time
                full_error = traceback.format_exc()
                print(f"❌ Test Case {test_id}: FAIL")
                print(f"⚠️ Error: {e}")
                log_error_to_file(test_id, full_error)
                timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")
                screenshot_file = os.path.join(SCREENSHOT_DIR, f"{test_id}_FAIL_{timestamp}.png")
                self.driver.save_screenshot(screenshot_file)
                error_summary = str(e).splitlines()[0] if str(e).splitlines() else str(e)
                test_results_summary.append({'id': test_id, 'status': 'FAIL', 'details': error_summary, 'duration': duration})

        total_duration = time.time() - overall_start_time
        failed_count = sum(1 for r in test_results_summary if r['status'] == 'FAIL')
        total_tests = len(test_results_summary)
        passed_count = total_tests - failed_count

        print("\n" + "=" * 60)
        print("TEST RUN SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}, Passed: {passed_count}, Failed: {failed_count}")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print("=" * 60)

        self.generate_html_report(test_results_summary, total_duration)
        self.assertEqual(failed_count, 0, f"{failed_count} test case(s) failed")

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
