import os
import time
from datetime import datetime, timedelta
import pytz
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()

# Configuration (stored as environment variables in GitHub Actions)
EMAIL = os.environ.get("COURTRESERVE_EMAIL", "caesarlm0327@gmail.com")
PASSWORD = os.environ.get("COURTRESERVE_PASSWORD", "Caesar823823")
LOGIN_URL = "https://mobileapp.courtreserve.com/Online/Account/Login/7629"
BOOKING_URL = "https://mobileapp.courtreserve.com/Online/Reservations/Bookings/7629?sId=11773"

# Court and time preferences
COURT_PREFERENCES = ["Court 3 (North court)", "Court 2 (Center court)"]
PREFERRED_TIMES = ["20:00", "21:00", "11:00"]  # 8pm, 9pm, 11am in 24-hour format

# Days to book (0=Monday, 1=Tuesday, ..., 6=Sunday)
# 2=Wednesday, 6=Sunday, 4=Friday
PREFERRED_DAYS = [0, 6, 4]  # Wednesday, Sunday, Friday 暂时2改成0

def setup_driver():
    """Set up Chrome driver for testing"""
    chrome_options = Options()
    # Comment out headless mode for testing
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Required for running in some environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Required for running in some environments
    return webdriver.Chrome(options=chrome_options)

def login(driver):
    """Log in to CourtReserve using the actual HTML structure"""
    try:
        logger.info("Navigating to login page")
        driver.get(LOGIN_URL)
        time.sleep(3)  # Add a delay to ensure page loads
        
        # Take screenshot of the login page
        driver.save_screenshot("login_page.png")
        log_page_source(driver, "login_page.html")
        
        logger.info("Attempting to log in")
        
        # Try multiple selectors for email field
        email_selectors = [
            "//input[@placeholder='Enter Your Email']",
            "//input[@type='email']",
            "//input[contains(@id, 'email')]",
            "//input[contains(@class, 'email')]"
        ]
        
        # Enter email
        logger.info("Looking for email field")
        email_field = None
        for selector in email_selectors:
            try:
                logger.info(f"Trying email selector: {selector}")
                email_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if email_field:
                    logger.info(f"Found email field with selector: {selector}")
                    break
            except Exception as e:
                logger.info(f"Selector {selector} failed: {str(e)}")
        
        if not email_field:
            logger.error("Could not find email field with any selector")
            log_page_source(driver, "email_field_error.html")
            raise Exception("Email field not found")
        
        logger.info("Entering email")
        email_field.send_keys(EMAIL)
        
        # Try multiple selectors for password field
        password_selectors = [
            "//input[@placeholder='Enter Your Password']",
            "//input[@type='password']",
            "//input[contains(@id, 'password')]",
            "//input[contains(@class, 'password')]"
        ]
        
        # Enter password
        logger.info("Looking for password field")
        password_field = None
        for selector in password_selectors:
            try:
                logger.info(f"Trying password selector: {selector}")
                password_field = driver.find_element(By.XPATH, selector)
                if password_field:
                    logger.info(f"Found password field with selector: {selector}")
                    break
            except Exception as e:
                logger.info(f"Selector {selector} failed: {str(e)}")
        
        if not password_field:
            logger.error("Could not find password field with any selector")
            log_page_source(driver, "password_field_error.html")
            raise Exception("Password field not found")
        
        logger.info("Entering password")
        password_field.send_keys(PASSWORD)
        
        # Try multiple selectors for login button
        button_selectors = [
            "//button[contains(text(), 'Continue')]",
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign In')]",
            "//button[@type='submit']",
            "//input[@type='submit']"
        ]
        
        # Click the login button
        logger.info("Looking for login button")
        login_button = None
        for selector in button_selectors:
            try:
                logger.info(f"Trying button selector: {selector}")
                login_button = driver.find_element(By.XPATH, selector)
                if login_button:
                    logger.info(f"Found login button with selector: {selector}")
                    break
            except Exception as e:
                logger.info(f"Selector {selector} failed: {str(e)}")
        
        if not login_button:
            logger.error("Could not find login button with any selector")
            log_page_source(driver, "login_button_error.html")
            raise Exception("Login button not found")
        
        logger.info("Clicking login button")
        login_button.click()
        time.sleep(3)  # Wait for login process
        
        # Take screenshot after login attempt
        driver.save_screenshot("after_login_click.png")
        log_page_source(driver, "after_login_click.html")
        
        # Try multiple selectors for verification
        verification_selectors = [
            "//a[contains(text(), 'Arrive Streeterville')]",
            "//a[contains(text(), 'Reservations')]",
            "//a[contains(@href, 'Reservations')]",
            "//div[contains(@class, 'user-profile')]",
            "//div[contains(@class, 'dashboard')]"
        ]
        
        # Wait for login to complete
        logger.info("Waiting for login to complete")
        logged_in = False
        for selector in verification_selectors:
            try:
                logger.info(f"Trying verification selector: {selector}")
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                logger.info(f"Login verified with selector: {selector}")
                logged_in = True
                break
            except Exception as e:
                logger.info(f"Verification selector {selector} failed: {str(e)}")
        
        if not logged_in:
            logger.error("Login verification failed with all selectors")
            driver.save_screenshot("login_verification_error.png")
            log_page_source(driver, "login_verification_error.html")
            raise Exception("Login verification failed")
        
        logger.info("Login successful")
        return True
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return False

def navigate_to_reservations(driver):
    """Navigate to the reservations page"""
    try:
        logger.info("Navigating to reservations page")
        
        # Check if we're already on the booking page
        if "Reservations/Bookings" in driver.current_url:
            logger.info("Already on booking page")
            return True
        
        # Check if we're on the portal page
        if "Portal/Index" in driver.current_url:
            logger.info("On portal page, navigating to booking page")
        else:
            logger.info(f"Not on portal page. Current URL: {driver.current_url}")
            # We can still try to navigate directly to the booking URL
        
        # Take screenshot of the current page
        driver.save_screenshot("before_reservation_navigation.png")
        
        # Go to the bookings page directly
        logger.info(f"Navigating directly to booking URL: {BOOKING_URL}")
        driver.get(BOOKING_URL)
        time.sleep(3)
        
        # Take screenshot of the booking page
        driver.save_screenshot("booking_page.png")
        
        # Check if we're on the booking page
        if "Reservations/Bookings" not in driver.current_url:
            logger.error(f"Failed to navigate to booking page. Current URL: {driver.current_url}")
            log_page_source(driver, "booking_navigation_failed.html")
            return False
        
        logger.info("Successfully navigated to reservations page")
        return True
        
    except Exception as e:
        logger.error(f"Failed to navigate to reservations: {str(e)}")
        driver.save_screenshot("reservation_navigation_error.png")
        log_page_source(driver, "reservation_error.html")
        return False

def navigate_to_specific_date(driver, target_date):
    """Navigate to a specific date in the calendar"""
    try:
        logger.info(f"Navigating to date: {target_date.strftime('%a, %b %d')}")
        
        # First check for and dismiss any dialogs that might be in the way
        dialog_buttons = [
            "//button[text()='OK']",
            "//button[text()='Ok']",
            "//button[text()='Close']",
            "//button[contains(@class, 'swal2-confirm')]",
            "//div[contains(@class, 'swal2-actions')]//button"
        ]
        
        for button_xpath in dialog_buttons:
            try:
                button = driver.find_element(By.XPATH, button_xpath)
                logger.info(f"Found dialog button: {button_xpath}")
                driver.execute_script("arguments[0].click();", button)
                logger.info("Clicked dialog button")
                time.sleep(2)
            except Exception:
                pass
        
        # Now proceed with date navigation
        # Take screenshot before navigation
        driver.save_screenshot("before_date_navigation.png")
        
        # First, check if there's a date picker or calendar navigation
        date_selectors = [
            "//div[contains(@class, 'k-scheduler-toolbar')]//span[contains(@class, 'k-scheduler-date')]",
            "//div[contains(@class, 'date-picker')]",
            "//div[contains(@class, 'calendar')]//button",
            "//button[contains(@class, 'date')]"
        ]
        
        date_element = None
        for selector in date_selectors:
            try:
                date_element = driver.find_element(By.XPATH, selector)
                logger.info(f"Found date element with selector: {selector}")
                break
            except Exception:
                pass
        
        if not date_element:
            logger.info("Could not find date navigation element, looking for navigation buttons")
        
        # Find the navigation buttons
        nav_button_selectors = [
            "//div[contains(@class, 'k-scheduler-toolbar')]//button[contains(@class, 'k-nav-next')]",
            "//button[contains(@class, 'next')]",
            "//button[contains(@aria-label, 'Next')]",
            "//button[contains(@title, 'Next')]"
        ]
        
        right_arrow = None
        for selector in nav_button_selectors:
            try:
                right_arrow = driver.find_element(By.XPATH, selector)
                logger.info(f"Found navigation button with selector: {selector}")
                break
            except Exception:
                pass
        
        if not right_arrow:
            logger.error("Could not find navigation button")
            driver.save_screenshot("nav_button_not_found.png")
            log_page_source(driver, "nav_button_not_found.html")
            return False
        
        # Get the current displayed date
        current_date_text = ""
        if date_element:
            current_date_text = date_element.text
            logger.info(f"Current date text: {current_date_text}")
        
        max_attempts = 10  # Prevent infinite loop
        for attempt in range(max_attempts):
            # Check if we've reached the target date
            if date_element:
                current_date_text = date_element.text
                logger.info(f"Current date text (attempt {attempt+1}): {current_date_text}")
                
                # Try different date formats
                target_formats = [
                    target_date.strftime("%b %d").lower(),  # Apr 27
                    target_date.strftime("%a, %b %d").lower(),  # Sat, Apr 27
                    target_date.strftime("%m/%d/%Y").lower(),  # 04/27/2025
                    target_date.strftime("%Y-%m-%d").lower()   # 2025-04-27
                ]
                
                found_date = False
                for date_format in target_formats:
                    if date_format in current_date_text.lower():
                        found_date = True
                break
                
                if found_date:
                    break
            
            # Take screenshot before clicking
            driver.save_screenshot(f"date_navigation_attempt_{attempt+1}.png")
                
            # Click the right arrow to move to the next day
            logger.info(f"Clicking next button (attempt {attempt+1})")
            right_arrow.click()
            time.sleep(2)  # Wait for the calendar to update
        
        # Take screenshot after navigation
        driver.save_screenshot("after_date_navigation.png")
        
        logger.info("Date navigation completed")
        return True
        
    except Exception as e:
        logger.error(f"Failed to navigate to date: {str(e)}")
        driver.save_screenshot("date_navigation_error.png")
        log_page_source(driver, "date_navigation_error.html")
        return False

def find_available_slot(driver):
    """Find an available time slot based on preferences"""
    try:
        logger.info("Looking for available time slots")
        
        # First, collect all available slots
        available_slots = []
        
        # Look for buttons with "Reserve" text
        reserve_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Reserve')]")
        logger.info(f"Found {len(reserve_buttons)} buttons with 'Reserve' text")
        
        for button in reserve_buttons:
            try:
                button_text = button.text.strip()
                logger.info(f"Examining button with text: '{button_text}'")
                
                if button_text and "Reserve" in button_text:
                    # Skip early morning times (before 11 AM)
                    early_morning = False
                    for hour in range(1, 8):#暂时把11改成8
                        hour_str = f"{hour}:00 AM"
                        if hour_str in button_text and hour != 8: #暂时把11改成8
                            logger.info(f"Skipping early morning time: {hour_str}")
                            early_morning = True
                            break
                    
                    if not early_morning:
                        logger.info(f"Found available slot: {button_text}")
                        # Extract the time from the button text
                        time_text = button_text.replace("Reserve ", "").strip()
                        available_slots.append((button, time_text))
            except Exception as e:
                logger.error(f"Error processing button: {str(e)}")
        
        logger.info(f"Found {len(available_slots)} available slots after filtering")
        
        if not available_slots:
            # Try a different approach - look for any buttons that might be clickable
            logger.info("Trying alternative approach to find available slots")
            all_buttons = driver.find_elements(By.XPATH, "//button")
            
            for button in all_buttons:
                try:
                    button_text = button.text.strip()
                    button_class = button.get_attribute("class")
                    
                    # Check if this might be a reservation button
                    if button_text and "Reserve" in button_text:
                        logger.info(f"Found button with Reserve text: '{button_text}', class: '{button_class}'")
                        
                        # Skip early morning times
                        early_morning = False
                        for hour in range(1, 11):
                            if f"{hour}:00 AM" in button_text and hour != 11:
                                early_morning = True
                                break
                        
                        if not early_morning:
                            logger.info(f"Adding available slot: {button_text}")
                            time_text = button_text.replace("Reserve ", "").strip()
                            available_slots.append((button, time_text))
                except Exception as e:
                    logger.error(f"Error processing button in alternative approach: {str(e)}")
        
        if not available_slots:
            # Try one more approach - look for the 12:00 PM slot specifically
            logger.info("Trying to find 12:00 PM slot specifically")
            try:
                noon_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Reserve 12:00 PM')]")
                logger.info(f"Found 12:00 PM button: {noon_button.text}")
                available_slots.append((noon_button, "12:00 PM"))
            except Exception:
                logger.info("No 12:00 PM slot found")
        
        if not available_slots:
            logger.info("No available slots found with any approach")
            return None
        
        logger.info(f"Found {len(available_slots)} available slots in total")
        
        # Now prioritize based on preferred times
        for preferred_time in PREFERRED_TIMES:
            hour_num = preferred_time.split(':')[0]
            
            # Convert to 12-hour format for display
            hour_12 = int(hour_num) % 12
            if hour_12 == 0:
                hour_12 = 12
            am_pm = "AM" if int(hour_num) < 12 else "PM"
            
            time_str = f"{hour_12}:00 {am_pm}"
            logger.info(f"Looking for preferred time: {time_str}")
            
            for button, time_text in available_slots:
                logger.info(f"Comparing preferred time '{time_str}' with available time '{time_text}'")
                if time_str == time_text:
                    logger.info(f"Found preferred time slot: {time_text}")
                    return button
        
        # If no preferred times are available, use the first available slot
        logger.info(f"No preferred times available. Using first available slot: {available_slots[0][1]}")
        return available_slots[0][0]
        
    except Exception as e:
        logger.error(f"Error finding available slots: {str(e)}")
        return None

def book_slot(driver, slot_element):
    """Book the selected time slot"""
    try:
        logger.info("Attempting to book selected time slot")
        logger.info(f"Element text: {slot_element.text}")
        
        # Take screenshot before clicking
        driver.save_screenshot("before_slot_click.png")
        
        # Click the slot element
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", slot_element)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", slot_element)
            logger.info("Clicked on available slot using JavaScript")
        except Exception as e:
            logger.error(f"JavaScript click failed: {str(e)}")
            try:
                slot_element.click()
                logger.info("Clicked on available slot directly")
            except Exception as e2:
                logger.error(f"Direct click failed: {str(e2)}")
                return False
        
        # Wait for the booking form to appear
        time.sleep(3)
        
        # Take screenshot after clicking
        driver.save_screenshot("after_slot_click.png")
        log_page_source(driver, "booking_form.html")
        
        # Check if we're on a booking form page
        booking_form_indicators = [
            "//div[contains(@class, 'modal')]",
            "//h3[contains(text(), 'Book a reservation')]",
            "//div[contains(text(), 'Reservation Type')]",
            "//div[contains(@class, 'modal-content')]",
            "//form[contains(@action, 'Reservation')]"
        ]
        
        form_found = False
        for indicator in booking_form_indicators:
            try:
                element = driver.find_element(By.XPATH, indicator)
                logger.info(f"Found booking form indicator: {indicator}")
                form_found = True
                break
            except Exception:
                pass
        
        if not form_found:
            logger.error("Could not detect booking form after clicking")
            return False
        
        # Fill in the booking form
        logger.info("Filling in booking form details")
        
        # Select number of guests (2)
        try:
            guest_dropdown = driver.find_element(By.XPATH, "//select[contains(@id, 'Guest')]")
            guest_dropdown.click()
            time.sleep(1)
            option_2 = driver.find_element(By.XPATH, "//option[@value='2']")
            option_2.click()
            logger.info("Selected 2 guests")
        except Exception as e:
            logger.error(f"Failed to select guests: {str(e)}")
            # Continue anyway
        
        # Enter "Amy" in the resident name field
        try:
            # Try multiple selectors for the name field
            name_selectors = [
                "//textarea[contains(@placeholder, 'Playing')]",
                "//textarea[contains(@id, 'Name')]",
                "//input[contains(@id, 'Name')]",
                "//input[contains(@placeholder, 'Name')]",
                "//textarea",
                "//input[contains(@class, 'form-control')]"
            ]
            
            for selector in name_selectors:
                try:
                    resident_field = driver.find_element(By.XPATH, selector)
                    resident_field.clear()
                    resident_field.send_keys("Amy")
                    logger.info(f"Entered 'Amy' as resident name using selector: {selector}")
                    break
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Failed to enter resident name: {str(e)}")
            # Continue anyway
        
        # Look for the Save and Close buttons
        save_button = None
        close_button = None
        
        # First, look for buttons in the modal footer
        try:
            modal_footer = driver.find_element(By.XPATH, "//div[contains(@class, 'modal-footer')]")
            footer_buttons = modal_footer.find_elements(By.XPATH, ".//button")
            
            for button in footer_buttons:
                button_text = button.text.strip().lower()
                button_class = button.get_attribute("class").lower()
                
                if "save" in button_text or "primary" in button_class:
                    save_button = button
                    logger.info(f"Found Save button in modal footer: {button_text}")
                elif "close" in button_text or "cancel" in button_class:
                    close_button = button
                    logger.info(f"Found Close button in modal footer: {button_text}")
        except Exception:
            logger.info("No modal footer found")
        
        # If we didn't find the Save button in the footer, look elsewhere
        if not save_button:
            # Look for buttons with text "Save"
            try:
                save_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Save')]")
                if save_buttons:
                    save_button = save_buttons[0]
                    logger.info("Found Save button by text")
            except Exception:
                pass
        
        # If we still don't have a Save button, look for blue buttons
        if not save_button:
            try:
                blue_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-primary')]")
                if blue_buttons:
                    save_button = blue_buttons[0]
                    logger.info("Found Save button by primary class")
            except Exception:
                pass
        
        # If we still don't have a Save button, look for any button that might be a save button
        if not save_button:
            try:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                logger.info(f"Found {len(all_buttons)} buttons in total")
                
                # Look for buttons that are visible and might be save buttons
                for button in all_buttons:
                    if button.is_displayed():
                        button_text = button.text.strip().lower()
                        button_class = button.get_attribute("class").lower()
                        
                        if "save" in button_text or "primary" in button_class or "submit" in button_class:
                            save_button = button
                            logger.info(f"Found potential save button: {button_text}")
                            break
            except Exception:
                pass
        
        # If we still don't have a Save button, use the Close button (which might actually be Save)
        if not save_button and close_button:
            save_button = close_button
            logger.info("Using Close button as Save button")
        
        # If we still don't have a Save button, look for any visible button
        if not save_button:
            try:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for button in all_buttons:
                    if button.is_displayed():
                        save_button = button
                        logger.info(f"Using visible button as Save button: {button.text}")
                        break
            except Exception:
                pass
        
        if not save_button:
            logger.error("Could not find any button to click")
            return False
        
        # Take screenshot before clicking save
        driver.save_screenshot("before_save_click.png")
        
        # Click the Save button
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", save_button)
            logger.info("Clicked Save button with JavaScript")
        except Exception as e:
            logger.error(f"JavaScript save click failed: {str(e)}")
            try:
                save_button.click()
                logger.info("Clicked Save button directly")
            except Exception as e2:
                logger.error(f"Direct save click failed: {str(e2)}")
                return False
        
        # Wait for confirmation
        time.sleep(5)
        
        # Take screenshot after clicking save
        driver.save_screenshot("after_save_click.png")
        log_page_source(driver, "after_save.html")
        
        # Check for critical error messages first
        critical_error_indicators = [
            "//div[contains(text(), 'no longer available')]",
            "//div[contains(text(), 'Reservation Notice')]",
            "//div[contains(text(), 'Error')]"
        ]
        
        for indicator in critical_error_indicators:
            try:
                error_element = driver.find_element(By.XPATH, indicator)
                error_text = error_element.text.strip()
                logger.error(f"Found critical error message: {error_text}")
                
                # Click OK on the error dialog
                try:
                    ok_button = driver.find_element(By.XPATH, "//button[text()='OK' or text()='Ok']")
                    ok_button.click()
                    logger.info("Clicked OK on error dialog")
                except Exception:
                    pass
                
                return False
            except Exception:
                pass
        
        # Check for success indicators
        success_indicators = [
            "//div[contains(@class, 'swal2-success')]",
            "//div[contains(text(), 'Success')]",
            "//div[contains(text(), 'successfully')]",
            "//div[contains(text(), 'booked')]"
        ]
        
        for indicator in success_indicators:
            try:
                success_element = driver.find_element(By.XPATH, indicator)
                success_text = success_element.text.strip()
                logger.info(f"Found success message: {success_text}")
                
                # Handle any confirmation dialogs
                dialog_buttons = [
                    "//button[text()='OK']",
                    "//button[text()='Ok']",
                    "//button[text()='Close']",
                    "//button[contains(@class, 'swal2-confirm')]",
                    "//div[contains(@class, 'swal2-actions')]//button"
                ]
                
                for button_xpath in dialog_buttons:
                    try:
                        button = driver.find_element(By.XPATH, button_xpath)
                        logger.info(f"Found dialog button: {button_xpath}")
                        driver.execute_script("arguments[0].click();", button)
                        logger.info("Clicked dialog button")
                        time.sleep(2)
                        break
                    except Exception:
                        pass
                
                return True
            except Exception:
                pass
        
        # If we didn't find any explicit success or error messages, check if we're back on the calendar
        try:
            # Check if we're back on the calendar view
            calendar = driver.find_element(By.XPATH, "//div[contains(@class, 'k-scheduler')]")
            
            # Check if there's a dialog with an error message
            try:
                dialog = driver.find_element(By.XPATH, "//div[contains(@class, 'swal2-container')]")
                dialog_text = dialog.text.strip()
                if "no longer available" in dialog_text.lower() or "error" in dialog_text.lower():
                    logger.error(f"Found error dialog: {dialog_text}")
                    return False
            except Exception:
                pass
            
            # If we're back on the calendar with no error dialog, assume success
            logger.info("Back on calendar view with no critical error, assuming booking succeeded")
            return True
            
        except Exception:
            logger.error("Not back on calendar view, booking likely failed")
            return False
        
    except Exception as e:
        logger.error(f"Failed to book the court: {str(e)}")
        return False

def book_multiple_slots(driver):
    """Book up to 3 slots for the week"""
    central_tz = pytz.timezone('US/Central')
    now = datetime.now(central_tz)
    
    # Calculate dates to book
    dates_to_book = []
    
    # Start from tomorrow
    start_date = now + timedelta(days=1)
    
    # First, check the newest available day (8 days from now)
    newest_date = start_date + timedelta(days=8)
    
    # If the newest day is one of our preferred days, add it first
    if newest_date.weekday() in PREFERRED_DAYS:
        dates_to_book.append(newest_date)
        logger.info(f"Added newest available day {newest_date.strftime('%A, %b %d')} to booking list")
    
    # Then check all other days, starting from tomorrow
    for i in range(8):  # Check next 7 days
        check_date = start_date + timedelta(days=i)
        # Skip the newest day if we already added it
        if check_date == newest_date:
            continue
        # If this day's weekday is in our preferred days, add it
        if check_date.weekday() in PREFERRED_DAYS:
            dates_to_book.append(check_date)
    
    logger.info(f"Will attempt to book slots on: {', '.join([date.strftime('%A, %b %d') for date in dates_to_book])}")
    
    # Track successful bookings
    successful_bookings = 0
    max_bookings = 3  # Maximum allowed per week
    
    # Navigate to the reservations page once at the beginning
    if not navigate_to_reservations(driver):
        logger.error("Failed to navigate to reservations, aborting")
        return successful_bookings
    
    # Try to book each date
    for booking_date in dates_to_book:
        if successful_bookings >= max_bookings:
            logger.info(f"Reached maximum of {max_bookings} bookings for the week")
            break
            
        logger.info(f"Attempting to book a slot on {booking_date.strftime('%A, %b %d')}")
        
        # Navigate to the specific date
        if not navigate_to_specific_date(driver, booking_date):
            logger.error(f"Failed to navigate to {booking_date.strftime('%A, %b %d')}, skipping this date")
            continue
        
        # Try up to 3 times to find and book an available slot
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Booking attempt {attempt}/{max_attempts} for {booking_date.strftime('%A, %b %d')}")
            
            # Find an available slot
            available_slot = find_available_slot(driver)
            if not available_slot:
                logger.info(f"No available slots found for {booking_date.strftime('%A, %b %d')}, skipping this date")
                break
            
            # Book the slot
            if book_slot(driver, available_slot):
                successful_bookings += 1
                logger.info(f"Successfully booked slot {successful_bookings}/{max_bookings} for {booking_date.strftime('%A, %b %d')}")
                
                # Navigate back to the reservations page for the next booking
                if not navigate_to_reservations(driver):
                    logger.error("Failed to navigate back to reservations, aborting remaining bookings")
                    return successful_bookings
                break
            else:
                logger.error(f"Failed to book slot on attempt {attempt}")
                
                # If this wasn't the last attempt, refresh the page and try again
                if attempt < max_attempts:
                    logger.info("Refreshing page to try again")
                    driver.refresh()
                    time.sleep(3)
                    
                    # Dismiss any dialogs
                    dialog_buttons = [
                        "//button[text()='OK']",
                        "//button[text()='Ok']",
                        "//button[text()='Close']",
                        "//button[contains(@class, 'swal2-confirm')]",
                        "//div[contains(@class, 'swal2-actions')]//button"
                    ]
                    
                    for button_xpath in dialog_buttons:
                        try:
                            button = driver.find_element(By.XPATH, button_xpath)
                            logger.info(f"Found dialog button: {button_xpath}")
                            driver.execute_script("arguments[0].click();", button)
                            logger.info("Clicked dialog button")
                            time.sleep(2)
                        except Exception:
                            pass
    
    logger.info(f"Booking process completed. Successfully booked {successful_bookings}/{max_bookings} slots")
    return successful_bookings

def wait_until_noon():
    """Wait until exactly 12:00:00 PM Central time"""
    central_tz = pytz.timezone('US/Central')
    now = datetime.now(central_tz)
    target = now.replace(hour=12, minute=0, second=0, microsecond=0)
    
    # If it's already past noon, no need to wait
    if now >= target:
        logger.info("It's already past noon, continuing immediately")
        return
    
    wait_seconds = (target - now).total_seconds()
    logger.info(f"Waiting {wait_seconds:.2f} seconds until 12:00:00 PM Central time")
    
    # If we're close to noon (within 10 seconds), do a more precise wait
    if wait_seconds < 10:
        time.sleep(wait_seconds)
    else:
        # Sleep until 5 seconds before noon, then do a more precise wait
        time.sleep(wait_seconds - 5)
        # Recalculate the remaining time
        now = datetime.now(central_tz)
        target = now.replace(hour=12, minute=0, second=0, microsecond=0)
        remaining_seconds = (target - now).total_seconds()
        if remaining_seconds > 0:
            time.sleep(remaining_seconds)
    
    logger.info("It's noon! Starting booking process")

def main():
    """Main function to run the booking process"""
    logger.info("Starting court booking process")
    
    # Check if we need to wait until noon
    central_tz = pytz.timezone('US/Central')
    now = datetime.now(central_tz)
    
    # If we're running close to noon, wait until exactly 12:00 PM
    if now.hour == 11 and now.minute >= 55:
        wait_until_noon()
    
    driver = setup_driver()
    
    try:
        # Login
        if not login(driver):
            logger.error("Login failed, aborting")
            return
        
        # Book multiple slots
        slots_booked = book_multiple_slots(driver)
        logger.info(f"Booked {slots_booked} slots in total")
            
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        
    finally:
        driver.quit()
        logger.info("Browser closed")

def log_page_source(driver, filename):
    """Save the page source to a file for debugging"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f"Saved page source to {filename}")
    except Exception as e:
        logger.error(f"Failed to save page source: {str(e)}")

if __name__ == "__main__":
    main()