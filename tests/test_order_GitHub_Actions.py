import time
import csv
import os  
import sys
import argparse
import traceback
import unittest
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

# --- Global Settings for GitHub Actions ---
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/index.php")
SCREENSHOT_DIR = os.path.join("test_screenshots")
ERROR_LOG_FILE = os.path.join("test_screenshots", "error_log.txt")

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
        """Set up test class - runs once before all tests. Configured for GitHub Actions."""
        print("Setting up the browser for GitHub Actions (headless mode)...")
        options = Options()
        
        # Chrome arguments for stability and GitHub Actions compatibility
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
        
        # Let Selenium automatically manage the driver
        cls.driver = webdriver.Chrome(options=options)
        
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
        
        # Navigate to the order page
        self.driver.get(BASE_URL)
        
        # Use explicit wait instead of time.sleep()
        wait = WebDriverWait(self.driver, 10)
        
        # Wait for the calculate button to be present (indicates page is ready)
        wait.until(EC.presence_of_element_located((By.ID, 'calculateBtn')))

        # Fill in quantities for all dessert items
        for csv_key, input_id in ITEM_MAPPING.items():
            quantity = row[csv_key]
            if int(quantity) >= 0:
                # Wait for the input to be present before interacting
                qty_input = wait.until(EC.presence_of_element_located((By.ID, input_id)))
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", qty_input)
                # Using JavaScript to set value is more reliable than .send_keys()
                self.driver.execute_script("arguments[0].value = arguments[1];", qty_input, quantity)
        
        # Display total items in this test case
        total_items = 0
        for csv_key in ITEM_MAPPING.keys():
            total_items += int(row[csv_key])
        print(f"🛒 Total items in order: {total_items}")
        
        # Handle the discount toggle with stronger validation
        discount_needed = row['Discount_Enabled']
        discount_checkbox = wait.until(EC.presence_of_element_located((By.ID, 'discountToggle')))
        discount_slider = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.discount-toggle .slider')))
        is_checked = discount_checkbox.is_selected()

        if discount_needed == 'Yes' and not is_checked:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", discount_slider)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.discount-toggle .slider')))
            self.driver.execute_script("arguments[0].click();", discount_slider)
            # Verify the toggle state changed
            time.sleep(0.3)  # Brief pause for animation
            self.assertTrue(discount_checkbox.is_selected(), "Discount toggle failed to enable")
        elif discount_needed == 'No' and is_checked:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", discount_slider)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.discount-toggle .slider')))
            self.driver.execute_script("arguments[0].click();", discount_slider)
            # Verify the toggle state changed
            time.sleep(0.3)  # Brief pause for animation
            self.assertFalse(discount_checkbox.is_selected(), "Discount toggle failed to disable")
        
        # Show final discount status
        print(f"💰 Discount: {'Enabled' if discount_needed == 'Yes' else 'Disabled'} ✓")
            
        # Validate discount toggle final state
        final_state = discount_checkbox.is_selected()
        expected_state = (discount_needed == 'Yes')
        self.assertEqual(final_state, expected_state, 
                        f"Discount toggle state mismatch: Expected {expected_state}, got {final_state}")

        # Click the "Calculate Bill" button
        calculate_button = wait.until(EC.element_to_be_clickable((By.ID, 'calculateBtn')))
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", calculate_button)
        self.driver.execute_script("arguments[0].click();", calculate_button)
        
        # Wait for the receipt page to load using explicit wait
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".receipt-row.subtotal .receipt-value")))
        
        # Extract actual values from the receipt page
        subtotal_spans = self.driver.find_elements(By.CSS_SELECTOR, ".receipt-row.subtotal .receipt-value")
        self.assertTrue(len(subtotal_spans) > 0, "Could not find subtotal on receipt page.")

        # When discount is enabled, use the last subtotal value (after discount)
        if discount_needed == 'Yes' and len(subtotal_spans) > 1:
            subtotal_text = subtotal_spans[-1].text
        else:
            subtotal_text = subtotal_spans[0].text

        actual_subtotal = subtotal_text.replace('RM', '').strip()
        actual_sst = self.driver.find_element(By.CSS_SELECTOR, ".receipt-row.sst .receipt-value").text.replace('RM', '').strip()
        actual_grand_total = self.driver.find_element(By.CSS_SELECTOR, ".receipt-row.grand-total .receipt-value").text.replace('RM', '').strip()

        # Get expected values from CSV
        expected_subtotal = row['Expected_Subtotal']
        expected_sst = row['Expected_SST']
        expected_grand_total = row['Expected_Grand_Total']

        # Verify that actual values match expected values using Decimal for precision
        self.assertEqual(d(expected_subtotal), d(actual_subtotal), 
                        f"Subtotal mismatch: Expected '{expected_subtotal}' but got '{actual_subtotal}'")
        self.assertEqual(d(expected_sst), d(actual_sst), 
                        f"SST mismatch: Expected '{expected_sst}' but got '{actual_sst}'")
        self.assertEqual(d(expected_grand_total), d(actual_grand_total), 
                        f"Grand Total mismatch: Expected '{expected_grand_total}' but got '{actual_grand_total}'")
        
        print(f"✅ Subtotal: RM{actual_subtotal} | SST: RM{actual_sst} | Grand Total: RM{actual_grand_total}")

        # Test passed - save screenshot
        print(f"✅ Test Case {test_id}: PASS")
        screenshot_file = os.path.join(SCREENSHOT_DIR, f"{test_id}_PASS.png")
        self.driver.save_screenshot(screenshot_file)
        print(f"📸 Screenshot saved to {screenshot_file}")
    
    def test_all_dessert_orders(self):
        """Run all test cases from CSV"""
        test_results_summary = []
        
        for row in self.test_cases:
            test_id = row['Test_ID']
            
            try:
                self.run_single_test_case(row)
                test_results_summary.append((test_id, "PASS", "N/A"))
                
            except (AssertionError, NoSuchElementException, TimeoutException, Exception) as e:
                # Test failed - save screenshot and log full error
                full_error = traceback.format_exc()
                
                print(f"❌ Test Case {test_id}: FAIL")
                print(f"⚠️ Error: {e}")
                
                # Log full error details to file for debugging
                log_error_to_file(test_id, full_error)
                
                screenshot_file = os.path.join(SCREENSHOT_DIR, f"{test_id}_FAIL.png")
                self.driver.save_screenshot(screenshot_file)
                print(f"📸 Screenshot saved to {screenshot_file}")
                print(f"📝 Full error log saved to {ERROR_LOG_FILE}")
                
                # Store first line of error for summary
                error_summary = str(e).splitlines()[0] if str(e).splitlines() else str(e)
                test_results_summary.append((test_id, "FAIL", error_summary))
        
        # Print summary report
        print("\n\n" + "=" * 60)
        print("                 TEST RUN SUMMARY")
        print("=" * 60)
        print(f"{'Test ID':<10} | {'Status':<10} | {'Details':<30}")
        print("-" * 60)
        
        failed_count = 0
        for result in test_results_summary:
            test_id, status, details = result
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"{test_id:<10} | {status_icon} {status:<8} | {details:<30}")
            if status == "FAIL":
                failed_count += 1
        
        print("-" * 60)
        total_tests = len(test_results_summary)
        passed_count = total_tests - failed_count
        print(f"Total Tests: {total_tests}, Passed: {passed_count}, Failed: {failed_count}")
        print("=" * 60)
        
        # Assert that all tests passed
        self.assertEqual(failed_count, 0, f"{failed_count} test case(s) failed")


# Main execution
if __name__ == "__main__":
    print("🚀 Running tests in GitHub Actions environment...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(DessertOrderTestCase)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\n🎉 Result: All test cases passed! 🎉")
        sys.exit(0)
    else:
        print(f"\n❌ Result: {len(result.failures) + len(result.errors)} test(s) failed.")
        sys.exit(1)