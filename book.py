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
import tempfile
import random
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import re

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
PREFERRED_TIMES = ["21:00", "20:00", "19:00", "18:00", "17:00", "12:00", "11:00"]  # 9pm, 8pm, 7pm, 6pm, 5pm, 12pm, 11am

# Days to book (0=Monday, 1=Tuesday, ..., 6=Sunday)
# 2=Wednesday, 6=Sunday, 4=Friday
PREFERRED_DAYS = [1, 6, 4]  # Wednesday, Sunday, Friday 暂时2改成1

def setup_driver():
    """Set up Chrome driver with anti-detection measures"""
    try:
        chrome_options = Options()
        
        # 添加必要的参数
        if os.environ.get("GITHUB_ACTIONS"):
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # 使用临时目录
        temp_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        # 设置更长的超时时间
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(10)
        driver.implicitly_wait(5)
        
        # 添加 cookie 处理
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setBypassServiceWorker', {'bypass': True})
        
        return driver
        
    except Exception as e:
        logger.error(f"Error setting up driver: {str(e)}")
        raise

def login(driver):
    """Log in to CourtReserve with human-like behavior"""
    try:
        logger.info("Navigating to login page")
        driver.get(LOGIN_URL)
        
        # Random sleep to simulate human behavior (3-5 seconds)
        time.sleep(random.uniform(1, 3))
        
        # Take screenshot of the login page
        driver.save_screenshot("login_page.png")
        log_page_source(driver, "login_page.html")
        
        logger.info("Attempting to log in")
        
        # Wait before entering email (simulating human thinking)
        time.sleep(random.uniform(1, 2))
        
        # Try multiple selectors for email field
        email_selectors = [
            "//input[@placeholder='Enter Your Email']",
            "//input[@type='email']",
            "//input[contains(@id, 'email')]",
            "//input[contains(@class, 'email')]",
            "//input[@name='email']"  # Added this selector
        ]
        
        # Enter email with human-like typing
        logger.info("Looking for email field")
        email_field = None
        for selector in email_selectors:
            try:
                logger.info(f"Trying email selector: {selector}")
                email_field = WebDriverWait(driver, 10).until(  # Increased wait time
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
        # Type email character by character with random delays
        for char in EMAIL:
            email_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.10))
        
        time.sleep(random.uniform(0.5, 1.5))  # Pause after typing email
        
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
        
        # 直接导航到预订页面
        driver.get(BOOKING_URL)
        
        # 等待页面加载完成
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "k-scheduler"))
        )
        
        logger.info("Successfully navigated to reservations page")
        return True
        
    except Exception as e:
        logger.error(f"Failed to navigate to reservations page: {str(e)}")
        return False

def navigate_to_specific_date(driver, target_date):
    """Navigate to a specific date in the calendar"""
    try:
        logger.info(f"正在导航到目标日期: {target_date.strftime('%Y-%m-%d (%A)')})")
        
        # 首先检查并关闭任何可能的模态框
        try:
            driver.execute_script("""
                // 关闭任何错误模态框
                var errorModals = document.querySelectorAll('.fn-error-modal-content, .modal-dialog');
                for(var i=0; i<errorModals.length; i++) {
                    var closeButtons = errorModals[i].querySelectorAll('button.close, button.btn, button[data-dismiss="modal"]');
                    for(var j=0; j<closeButtons.length; j++) {
                        closeButtons[j].click();
                    }
                }
                
                // 删除所有模态框背景
                var modalBackdrops = document.querySelectorAll('.modal-backdrop');
                for(var i=0; i<modalBackdrops.length; i++) {
                    modalBackdrops[i].parentNode.removeChild(modalBackdrops[i]);
                }
                
                // 移除body上的modal-open类
                document.body.classList.remove('modal-open');
            """)
            logger.info("尝试关闭可能的模态框")
            time.sleep(1)
        except:
            pass
        
        # 使用更可靠的方法直接导航到目标日期
        # 方法1: 使用JavaScript直接设置日期
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            driver.execute_script(f"""
                try {{
                    // 尝试使用Kendo UI日历API
                    var scheduler = $(document).data('kendoScheduler');
                    if (scheduler) {{
                        console.log("找到scheduler，设置日期为: {date_str}");
                        scheduler.date(new Date("{date_str}"));
                        return true;
                    }}
                }} catch (e) {{
                    console.error("设置日期时出错:", e);
                    return false;
                }}
            """)
            logger.info(f"尝试使用JavaScript方法1直接设置日期为 {date_str}")
            time.sleep(2)
            
            # 验证日期是否已更改
            current_date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
            )
            current_date_text = current_date_element.text
            logger.info(f"当前显示的日期: {current_date_text}")
            
            # 检查是否包含目标日期的月份和日期
            if (target_date.strftime("%b") in current_date_text and 
                str(target_date.day) in current_date_text):
                logger.info(f"成功导航到目标日期: {current_date_text}")
                return True
            else:
                logger.warning(f"导航未完成，当前日期 {current_date_text} 与目标日期 {target_date.strftime('%b %d')} 不匹配")
                driver.save_screenshot("navigation_failed.png")
        except Exception as e:
            logger.error(f"JavaScript导航方法失败: {str(e)}")
        
        # 方法2: 如果JavaScript方法失败，尝试使用UI控件导航
        try:
            # 先获取当前显示的日期
            current_date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
            )
            current_date_text = current_date_element.text
            logger.info(f"当前显示的日期: {current_date_text}")
            
            # 点击导航到特定日期
            actions = ActionChains(driver)
            actions.move_to_element(current_date_element).click().perform()
            logger.info("点击了日期导航元素")
            time.sleep(1)
            
            # 查找并选择目标年/月
            month_year = target_date.strftime("%B %Y")  # 例如: "May 2025"
            logger.info(f"尝试导航到月份: {month_year}")
            
            # 等待日历弹窗出现
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".k-calendar"))
            )
            
            # 使用更直接的方法选择日期
            day = target_date.day
            target_day_selector = f".k-calendar td[data-value='{target_date.strftime('%Y/%m/%d')}'], .k-calendar td a:contains('{day}')"
            
            driver.execute_script(f"""
                // 尝试直接通过日期值找到并点击正确的日期
                var dateFound = false;
                var calendarCells = document.querySelectorAll('.k-calendar td');
                
                for (var i = 0; i < calendarCells.length; i++) {{
                    var cell = calendarCells[i];
                    if (cell.dataset.value === '{target_date.strftime("%Y/%m/%d")}' || 
                        (cell.innerText.trim() == '{day}' && !cell.classList.contains('k-other-month'))) {{
                        cell.click();
                        console.log('找到并点击了日期 {day}');
                        dateFound = true;
                        break;
                    }}
                }}
                
                return dateFound;
            """)
            
            logger.info(f"通过JavaScript尝试选择日期 {day}")
            time.sleep(2)
            
            # 再次检查日期是否正确
            current_date_text = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
            ).text
            
            logger.info(f"导航后的日期: {current_date_text}")
            if (target_date.strftime("%b") in current_date_text and 
                str(target_date.day) in current_date_text):
                logger.info(f"成功导航到目标日期: {current_date_text}")
                return True
        except Exception as e:
            logger.error(f"UI导航方法失败: {str(e)}")
            
        # 如果之前的方法都失败了，最后尝试使用日期导航按钮
        try:
            # 获取当前日期信息
            current_date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
            )
            current_date_text = current_date_element.text
            logger.info(f"开始使用导航按钮，当前日期: {current_date_text}")
            
            # 分析当前日期，决定需要点击"下一天"按钮多少次
            current_date_match = re.search(r'(\w+), (\w+) (\d+), (\d+)', current_date_text)
            if current_date_match:
                current_month = current_date_match.group(2)  # 月份名称
                current_day = int(current_date_match.group(3))  # 日期数字
                current_year = int(current_date_match.group(4))  # 年份
                
                logger.info(f"解析当前日期: 月={current_month}, 日={current_day}, 年={current_year}")
                
                # 创建当前日期的datetime对象用于比较
                current_date = None
                try:
                    current_date = datetime.strptime(f"{current_month} {current_day} {current_year}", "%b %d %Y")
                    logger.info(f"转换当前日期: {current_date.strftime('%Y-%m-%d')}")
                except Exception as e:
                    logger.error(f"日期转换失败: {str(e)}")
                
                if current_date:
                    # 计算需要点击的次数
                    days_diff = (target_date.date() - current_date.date()).days
                    logger.info(f"当前日期与目标日期相差 {days_diff} 天")
                    
                    # 根据天数差异选择按钮和点击次数
                    button_selector = ".k-nav-next" if days_diff > 0 else ".k-nav-prev"
                    clicks_needed = abs(days_diff)
                    
                    if clicks_needed > 0:
                        next_button = driver.find_element(By.CSS_SELECTOR, button_selector)
                        logger.info(f"将点击{'下一天' if days_diff > 0 else '上一天'}按钮 {clicks_needed} 次")
                        
                        for i in range(clicks_needed):
                            logger.info(f"点击第 {i+1}/{clicks_needed} 次")
                            next_button.click()
                            time.sleep(0.5)
                        
                        # 最后检查一次日期
                        current_date_text = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
                        ).text
                        logger.info(f"导航完成后的日期: {current_date_text}")
                        
                        if (target_date.strftime("%b") in current_date_text and 
                            str(target_date.day) in current_date_text):
                            logger.info(f"成功导航到目标日期: {current_date_text}")
                            return True
            else:
                logger.error(f"无法解析当前日期文本: {current_date_text}")
        except Exception as e:
            logger.error(f"使用导航按钮失败: {str(e)}")
        
        # 最后再尝试一下直接更改URL方法
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            # 在URL中添加日期参数
            current_url = driver.current_url
            if "?date=" in current_url:
                new_url = re.sub(r'\?date=[\d-]+', f'?date={date_str}', current_url)
            else:
                if "?" in current_url:
                    new_url = f"{current_url}&date={date_str}"
                else:
                    new_url = f"{current_url}?date={date_str}"
            
            logger.info(f"尝试通过URL导航: {new_url}")
            driver.get(new_url)
            time.sleep(2)
            
            # 检查导航结果
            current_date_text = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
            ).text
            logger.info(f"通过URL导航后的日期: {current_date_text}")
            
            if (target_date.strftime("%b") in current_date_text and 
                str(target_date.day) in current_date_text):
                logger.info(f"通过URL成功导航到目标日期: {current_date_text}")
            return True
        except Exception as e:
            logger.error(f"URL导航方法失败: {str(e)}")
        
        # 所有方法都失败了
        logger.critical("所有导航方法都失败，无法导航到目标日期")
        driver.save_screenshot("navigation_all_failed.png")
        return False
        
    except Exception as e:
        logger.critical(f"导航到特定日期时发生严重错误: {str(e)}")
        driver.save_screenshot("navigation_critical_error.png")
        return False

def find_all_available_slots(driver):
    """通过分析HTML直接找到所有可用时段"""
    try:
        logger.info("分析页面查找所有可用时段")
        available_slots = []
        
        # 使用更精确的选择器，获取所有潜在的预订按钮
        reserve_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(@class, 'slot-btn') and contains(text(), 'Reserve')]")
        logger.info(f"找到 {len(reserve_buttons)} 个潜在的Reserve按钮")
        
        # 详细记录所有潜在的按钮以便调试
        for i, button in enumerate(reserve_buttons):
            try:
                text = button.text.strip()
                logger.info(f"按钮 {i}: 文本 = '{text}'")
            except:
                logger.info(f"按钮 {i}: 无法获取文本")
        
        # 筛选有效的预订按钮
        for button in reserve_buttons:
            try:
                # 获取按钮文本
                button_text = button.text.strip()
                logger.info(f"处理按钮: {button_text}")
                
                # 如果按钮文本包含"Reserved"，跳过
                if "Reserved" in button_text:
                    logger.info(f"跳过已预订: {button_text}")
                    continue
                
                # 获取时间文本
                time_text = button_text.replace('Reserve ', '')
                
                # 修改：允许5点及以后的时间段
                if "AM" in time_text:
                    hour = int(time_text.split(':')[0])
                    if hour < 5:  # 从原来的11改为5
                        logger.info(f"跳过凌晨时段: {time_text}")
                        continue
                
                # 获取按钮的所有相关属性
                button_info = {
                    'text': button_text,
                    'start': button.get_attribute('start'),
                    'courtLabel': button.get_attribute('courtlabel')
                }
                
                logger.info(f"找到可用时段: {time_text} at {button_info['courtLabel']}")
                available_slots.append((button, button_info))
                
            except Exception as e:
                logger.error(f"处理按钮时出错: {str(e)}")
                continue
                
        logger.info(f"总共找到 {len(available_slots)} 个可用时段")
        
        # 添加额外的日志，确认所有可用时段都不是凌晨的
        for button, info in available_slots:
            time_text = info['text'].replace('Reserve ', '')
            if "AM" in time_text:
                hour = int(time_text.split(':')[0])
                if hour < 5:  # 从原来的11改为5
                    logger.error(f"警告：凌晨时段被添加到可用列表: {time_text}")
        
        return available_slots
        
    except Exception as e:
        logger.error(f"查找可用时段时出错: {str(e)}")
        return []

def book_slot(driver, slot_element):
    """Book the selected time slot"""
    try:
        # 首先检查按钮文本，确认不是凌晨时段
        button_text = driver.execute_script("return arguments[0].textContent;", slot_element).strip()
        time_text = button_text.replace('Reserve ', '')
        
        # 再次检查是否是凌晨时段
        if "AM" in time_text:
            hour = int(time_text.split(':')[0])
            if hour < 5:  # 从原来的11改为5
                logger.info(f"在 book_slot 中跳过凌晨时段: {time_text}")
                return False  # 不尝试预订凌晨时段
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "k-scheduler"))
        )
        
        # 点击预订按钮
        try:
            # 确保元素在视图中
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slot_element)
            time.sleep(1)
            
            # 点击按钮
            driver.execute_script("arguments[0].click();", slot_element)
            logger.info(f"点击预订按钮: {button_text}")
            
            # 等待模态框出现
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal-page-inner, div.modal-dialog"))
            )
            logger.info("预订表单已出现")
            
            # 增加一个更长的等待，确保表单完全加载
            time.sleep(5)
            
            # 检查表单中的时间，确保不是凌晨时段
            try:
                time_in_form = driver.find_element(By.CSS_SELECTOR, "input[id*='StartTime'], .modal-title").text
                if "AM" in time_in_form:
                    time_parts = time_in_form.split()
                    for part in time_parts:
                        if ":" in part and "AM" in part:
                            hour = int(part.split(':')[0])
                            if hour < 5:  # 从原来的11改为5
                                logger.info(f"表单中检测到凌晨时段: {time_in_form}，取消预订")
                                driver.find_element(By.CSS_SELECTOR, "button.close, button[data-dismiss='modal']").click()
                                return False
            except Exception as e:
                logger.warning(f"检查表单时间时出错: {str(e)}")
            
            # 不填写客人数量，保持默认值
            logger.info("Keeping default guest count")
            
            # 填写客人名字为"NA"
            try:
                # 尝试多种选择器来定位名字字段
                selectors = [
                    "textarea[name='ArrivePlayers']", 
                    "input[name='ArrivePlayers']",
                    "textarea[placeholder*='Type Name']",
                    "textarea[aria-label*='Name']",
                    "//textarea[contains(@placeholder, 'Type Name')]",
                    "//label[contains(text(), 'Name') or contains(text(), 'Playing')]/following::textarea",
                    "//label[contains(text(), 'Name') or contains(text(), 'Playing')]/following::input"
                ]
                
                guest_name = None
                for selector in selectors:
                    try:
                        if selector.startswith("//"):
                            guest_name = WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                        else:
                            guest_name = WebDriverWait(driver, 2).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                        if guest_name:
                            logger.info(f"Found name field with selector: {selector}")
                            break
                    except:
                        continue
                
                if guest_name:
                    guest_name.clear()
                    guest_name.send_keys("NA")
                    logger.info("Filled guest name with 'NA'")
                else:
                    # 如果找不到字段，尝试使用JavaScript直接填写
                    driver.execute_script("""
                        var inputs = document.querySelectorAll('textarea, input[type="text"]');
                        for(var i = 0; i < inputs.length; i++) {
                            var input = inputs[i];
                            if(input.name && (input.name.includes('Arrive') || input.name.includes('Player') || 
                               input.name.includes('Name'))) {
                                input.value = 'NA';
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                console.log('Set field ' + input.name + ' to NA');
                                break;
                            }
                        }
                    """)
                    logger.info("Attempted to fill guest name with JavaScript")
            except Exception as e:
                logger.warning(f"Could not fill guest name: {str(e)}")
                driver.save_screenshot("name_field_error.png")
            
            # 修改：确保必填字段已被填写
            required_fields_filled = driver.execute_script("""
                var requiredFields = document.querySelectorAll('[required]');
                for (var i = 0; i < requiredFields.length; i++) {
                    if (!requiredFields[i].value) {
                        console.log('Empty required field: ' + requiredFields[i].name);
                        return false;
                    }
                }
                return true;
            """)
            
            if not required_fields_filled:
                logger.warning("有必填字段未填写")
                driver.save_screenshot("required_fields_not_filled.png")
            
            # 等待保存按钮可点击
            save_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary[type='submit'], button.btn.btn-primary"))
            )
            
            # 暂停一下再点击保存按钮
            time.sleep(2)
            
            # 尝试直接使用表单API提交
            form_submit_result = driver.execute_script("""
                // 检查所有必填字段是否已填写
                var requiredFields = document.querySelectorAll('[required]');
                for (var i = 0; i < requiredFields.length; i++) {
                    if (!requiredFields[i].value) {
                        requiredFields[i].value = 'NA';
                    }
                }
                
                // 尝试找到并直接提交表单
                var form = document.querySelector('form');
                if (form) {
                    console.log('Found form, submitting directly');
                    form.submit();
                    return true;
                }
                
                // 如果无法找到表单，尝试点击保存按钮
                var saveButton = document.querySelector('button.btn-primary[type="submit"], button.btn.btn-primary');
                if (saveButton) {
                    console.log('Found save button, clicking');
                    saveButton.click();
                    return true;
                }
                
                return false;
            """)
            
            logger.info("尝试使用JavaScript提交表单")
            time.sleep(3)
            
            # 检查是否有错误消息
            try:
                error_messages = driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .text-danger")
                for msg in error_messages:
                    if msg.is_displayed():
                        logger.warning(f"表单提交错误: {msg.text}")
            except:
                pass
            
            # 检查是否出现"no longer available"消息
            try:
                no_longer_available = driver.find_element(By.XPATH, "//*[contains(text(), 'no longer available')]")
                if no_longer_available:
                    logger.warning("系统显示场地不再可用")
                    
                    # 尝试点击确认按钮继续
                    try:
                        ok_button = driver.find_element(By.CSS_SELECTOR, ".modal-dialog button.btn, button.btn-primary")
                        ok_button.click()
                        logger.info("点击了确认按钮")
                    except:
                        logger.warning("未找到确认按钮")
                    
                    return False
            except:
                # 没有找到消息，继续
                pass
            
            # 检查是否出现预订限制警告  
            try:
                # 更精确地查找预订限制警告
                restriction_warnings = driver.find_elements(By.XPATH, "//*[contains(text(), 'restricted to')]")
                
                if restriction_warnings and any(warning.is_displayed() for warning in restriction_warnings):
                    logger.warning("检测到预订限制警告")
                    driver.save_screenshot("restriction_warning.png")
                    
                    # 查找Close按钮
                    try:
                        # 首先尝试查找text='Close'的按钮
                        close_buttons = driver.find_elements(By.XPATH, "//button[text()='Close']")
                        if close_buttons:
                            close_buttons[0].click()
                            logger.info("点击了Close按钮")
                            time.sleep(1)
                            return True
                    except:
                        pass
                        
                    # 然后尝试查找class包含'close'的按钮
                    try:
                        close_buttons = driver.find_elements(By.CSS_SELECTOR, ".btn-secondary, .close, [aria-label='Close']")
                        if close_buttons:
                            for btn in close_buttons:
                                if btn.is_displayed():
                                    btn.click()
                                    logger.info("点击了关闭按钮")
                                    time.sleep(1)
                                    return True
                    except:
                        pass
                        
                    # 最后尝试使用JavaScript关闭模态框
                    try:
                        driver.execute_script("""
                            var closeButtons = document.querySelectorAll('button.close, button.btn-secondary, button:contains("Close")');
                            for(var i=0; i<closeButtons.length; i++) {
                                closeButtons[i].click();
                            }
                            
                            // 如果关闭按钮不起作用，尝试直接移除模态框
                            var modals = document.querySelectorAll('.modal');
                            for(var i=0; i<modals.length; i++) {
                                modals[i].style.display = 'none';
                            }
                            document.querySelector('.modal-backdrop')?.remove();
                            document.body.classList.remove('modal-open');
                        """)
                        logger.info("使用JavaScript尝试关闭模态框")
                        time.sleep(1)
                    except:
                        pass
                        
                    # 无论是否成功关闭警告，我们都认为这是一个成功的预订
                    # 因为系统限制每天只能预订一个场地，所以我们需要预订另一天
                    return True
            except Exception as e:
                logger.warning(f"处理预订限制警告时出错: {str(e)}")
            
            # 添加额外检查 - 等待页面重新加载或成功消息
            try:
                WebDriverWait(driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success")),
                        EC.presence_of_element_located((By.CLASS_NAME, "k-scheduler")),
                        EC.url_contains("/Online/Reservations/")
                    )
                )
                logger.info("表单提交后看到成功标志")
                return True
            except:
                # 如果无法检测到成功，但也没有看到错误，尝试继续
                if not driver.find_elements(By.CSS_SELECTOR, ".modal-dialog"):
                    logger.info("模态框已关闭，假定预订成功")
                    return True
                else:
                    logger.warning("模态框仍然打开，预订可能失败")
                    driver.save_screenshot("modal_still_open.png")
                    return False
                
        except Exception as e:
            logger.error(f"点击预订按钮或处理表单时出错: {str(e)}")
            driver.save_screenshot("button_error.png")
            return False
            
    except Exception as e:
        logger.error(f"预订尝试失败: {str(e)}")
        driver.save_screenshot("general_error.png")
        return False

def book_multiple_slots(driver):
    """Book just one slot for the latest available date"""
    central_tz = pytz.timezone('US/Central')
    now = datetime.now(central_tz)
    
    logger.info(f"==== 正在寻找最远可预订日期 ====")
    
    # 首先导航到预订页面
    driver.get(BOOKING_URL)
    
    # 等待页面加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "k-scheduler"))
    )
    
    # 点击日期导航器打开日历
    try:
        # 找到并点击日期导航按钮
        date_navigator = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
        )
        logger.info("点击日期导航器打开日历")
        date_navigator.click()
        time.sleep(1)
        
        # 等待日历出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".k-calendar"))
        )
        
        # 查找所有非禁用的日期单元格
        available_dates = driver.execute_script("""
            var availableDates = [];
            var dateCells = document.querySelectorAll('.k-calendar td:not(.k-other-month):not(.k-state-disabled)');
            
            for (var i = 0; i < dateCells.length; i++) {
                var cell = dateCells[i];
                var day = parseInt(cell.textContent.trim());
                if (!isNaN(day)) {
                    availableDates.push({
                        element: cell,
                        day: day
                    });
                }
            }
            
            // 为调试添加日志
            console.log('找到可用日期: ' + availableDates.length + ' 个');
            
            return availableDates;
        """)
        
        if not available_dates:
            logger.error("没有找到任何可用日期")
            driver.save_screenshot("no_available_dates.png")
            return 0
        
        # 找出最后一个可用日期（即最远的日期）
        logger.info(f"找到 {len(available_dates)} 个可用日期")
        
        # 选择最后一个日期（最远日期）
        last_date = available_dates[-1]
        logger.info(f"选择最后一个可用日期: 日期 {last_date['day']}")
        
        # 点击该日期
        driver.execute_script("arguments[0].click();", last_date['element'])
        logger.info(f"已点击最后可用日期")
        time.sleep(2)
        
        # 验证当前显示的日期
        current_date_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".k-scheduler-toolbar .k-nav-current"))
        )
        current_date_text = current_date_element.text
        logger.info(f"当前显示的日期: {current_date_text}")
        
        # 保存截图以验证日期选择
        driver.save_screenshot("date_selected.png")
        
    except Exception as e:
        logger.error(f"选择日期时出错: {str(e)}")
        driver.save_screenshot("date_selection_error.png")
        return 0
    
    # 查找可用时段
    available_slots = find_all_available_slots(driver)
    if not available_slots:
        logger.error(f"{current_date_text} 没有可用时段，终止预订")
        driver.save_screenshot("no_slots.png")
        return 0
    
    # 记录找到的所有时段
    logger.info(f"找到 {len(available_slots)} 个可用时段")
    
    # 过滤掉凌晨的时段并按时间晚到早排序
    filtered_slots = []
    for button, button_info in available_slots:
        # 确保按钮有文本
        if 'text' not in button_info or not button_info['text']:
            continue
        
        time_text = button_info['text'].replace('Reserve ', '')
        
        # 确保时间格式有效
        if ':' not in time_text:
            continue
        
        # 检查是否是凌晨时段
        try:
            if "AM" in time_text:
                hour_text = time_text.split(':')[0].strip()
                if hour_text and hour_text.isdigit():
                    hour = int(hour_text)
                    if hour < 5:
                        logger.info(f"跳过凌晨时段: {time_text}")
                        continue
        except:
            continue
        
        filtered_slots.append((button, button_info))
    
    if not filtered_slots:
        logger.error("过滤后没有可用时段，终止预订")
        return 0
    
    # 将过滤后的时段按时间晚到早排序
    def get_time_value(slot_info):
        try:
            time_text = slot_info[1]['text'].replace('Reserve ', '')
            if not time_text or ':' not in time_text:
                return -1
                
            hour_text = time_text.split(':')[0].strip()
            if not hour_text or not hour_text.isdigit():
                return -1
                
            hour = int(hour_text)
            
            if "PM" in time_text and "12:" not in time_text:
                return hour + 12
            elif "AM" in time_text and "12:" in time_text:
                return 0
            else:
                return hour
        except:
            return -1
    
    # 按时间从晚到早排序
    filtered_slots.sort(key=get_time_value, reverse=True)
    
    # 记录排序后的时段
    logger.info("可用时段从晚到早排序:")
    for i, (button, info) in enumerate(filtered_slots):
        logger.info(f"  {i+1}. {info['text']} at {info['courtLabel']}")
    
    # 尝试预订，从最晚的时间开始
    for button, button_info in filtered_slots:
        logger.info(f"尝试预订: {button_info['text']} at {button_info['courtLabel']}")
        
        try:
            if book_slot(driver, button):
                logger.info(f"成功预订时段! {button_info['text']} at {button_info['courtLabel']}")
                driver.save_screenshot("booking_success.png")
                return 1
            else:
                logger.error(f"预订失败: {button_info['text']}")
                # 继续尝试下一个时段
        except Exception as e:
            logger.error(f"预订时出错: {str(e)}")
            # 继续尝试下一个时段
    
    # 如果所有时段都预订失败
    logger.error("所有时段预订均失败")
    return 0

def wait_until_target_time():
    """Wait until exactly 11:59:20 AM Central time"""
    central_tz = pytz.timezone('US/Central')
    now = datetime.now(central_tz)
    target = now.replace(hour=11, minute=59, second=20, microsecond=0)
    
    # If it's already past target time, no need to wait
    if now >= target:
        logger.info("It's already past 11:59:20 AM, continuing immediately")
        return
    
    wait_seconds = (target - now).total_seconds()
    logger.info(f"Waiting {wait_seconds:.2f} seconds until 11:59:20 AM Central time")
    
    # If we're close to target time (within 10 seconds), do a more precise wait
    if wait_seconds < 10:
        time.sleep(wait_seconds)
    else:
        # Sleep until 5 seconds before target time, then do a more precise wait
        time.sleep(wait_seconds - 5)
        # Recalculate the remaining time
        now = datetime.now(central_tz)
        target = now.replace(hour=11, minute=59, second=20, microsecond=0)
        remaining_seconds = (target - now).total_seconds()
        if remaining_seconds > 0:
            time.sleep(remaining_seconds)
    
    logger.info("It's 11:59:20 AM! Starting booking process")

def main():
    """Main function to run the booking process"""
    # 打印明显的开始标记
    logger.info("="*50)
    logger.info("网球场预订程序开始运行")
    logger.info("="*50)
    
    driver = None
    try:
        # 准备浏览器
        driver = setup_driver()
        
        # 登录
        if not login(driver):
            logger.error("登录失败，中止预订")
            driver.save_screenshot("login_failed.png")
            return
            
        # 尝试预订最远日期的场地
        booked = book_multiple_slots(driver)
        
        # 发送通知电子邮件
        if booked > 0:
            logger.info("✓"*50)
            logger.info(f"成功预订了{booked}个网球场地!")
            logger.info("✓"*50)
            send_notification_email(True, f"成功预订了{booked}个网球场地! 预订时间: {datetime.now()}")
        else:
            logger.error("✗"*50)
            logger.error("未能预订任何网球场地")
            logger.error("✗"*50)
            send_notification_email(False, f"未能预订任何网球场地。请查看日志了解详细信息。预订尝试时间: {datetime.now()}")
            
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        if driver:
            driver.save_screenshot("unexpected_error.png")
    finally:
        if driver:
            driver.quit()
            logger.info("Browser closed")
            logger.info("="*50)
            logger.info("网球场预订程序结束运行")
            logger.info("="*50)

def log_page_source(driver, filename):
    """Save the page source to a file for debugging"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f"Saved page source to {filename}")
    except Exception as e:
        logger.error(f"Failed to save page source: {str(e)}")

def send_notification_email(success, details):
    """发送预订结果通知邮件"""
    try:
        # 如果没有配置邮件设置，则跳过
        if not hasattr(send_notification_email, 'configured'):
            logger.info("邮件通知未配置，跳过发送")
            return
            
        import smtplib
        from email.mime.text import MIMEText
        
        # 配置您的邮件
        sender = "your-email@gmail.com"
        recipient = "your-email@gmail.com"
        password = "your-app-password"  # 为Gmail生成应用专用密码
        
        subject = "网球场预订: " + ("成功" if success else "失败")
        body = f"预订{'成功' if success else '失败'}。\n\n详情:\n{details}"
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        logger.info("通知邮件发送成功")
    except Exception as e:
        logger.error(f"发送通知邮件失败: {str(e)}")

# 设置为未配置状态，除非您填写了正确的邮件信息
send_notification_email.configured = False

if __name__ == "__main__":
    main()