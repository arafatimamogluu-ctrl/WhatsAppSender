from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
import logging
import tempfile
import shutil

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhatsAppService")

class WhatsAppService:
    def __init__(self, headless=True):
        self.driver = None
        self.wait = None
        self.headless = headless 
        # Use a local directory for better persistence (not temp)
        self.user_data_dir = os.path.join(os.getcwd(), "whatsapp_session")
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
        logger.info(f"WhatsApp Session Dir: {self.user_data_dir}")
        
    def start_browser(self):
        """Starts the browser (Headless or Visible)"""
        if self.driver: return # Already started

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={self.user_data_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-port=9222") # Debugging port
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36") # Anti-detect
        
        if self.headless:
           options.add_argument("--headless=new")
           options.add_argument("--window-size=1920,1080") # Ensure elements render in headless

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 30)
            self.driver.get("https://web.whatsapp.com")
            logger.info("Browser started. Waiting for login...")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    def is_logged_in(self):
        try:
            if not self.driver: return False
            # Check for side panel
            self.driver.find_element(By.XPATH, '//div[@id="pane-side"]')
            return True
        except:
            return False

    def send_message(self, target_identifier: str, message: str, media_path: str = None):
        if not self.driver:
            if not self.start_browser():
                return False, "Browser failed to start"

        try:
            # 1. Search for Target
            # Try different search box selectors
            search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
            try:
                search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
            except:
                # Fallback implementation
                logger.warning("Standard search box not found, trying fallback...")
                return False, "Search box not found"

            search_box.clear()
            search_box.send_keys(target_identifier)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            # 2. Attach Media if exists
            if media_path and os.path.exists(media_path):
                try:
                    attach_btn = self.driver.find_element(By.XPATH, '//div[@title="Attach"] | //span[@data-icon="clip"] | //span[@data-icon="plus"]')
                    attach_btn.click()
                    time.sleep(1)
                    
                    file_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')
                    file_input.send_keys(os.path.abspath(media_path))
                    time.sleep(3)
                    
                    # Click Send in preview
                    send_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
                    send_btn.click()
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"Media send error: {e}")

            # 3. Send Text
            if message:
                message_box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                # Handle newlines
                for line in message.split('\n'):
                    message_box.send_keys(line)
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)
                
                time.sleep(0.5)
                message_box.send_keys(Keys.ENTER)
            
            logger.info(f"Message sent to {target_identifier}")
            return True, "Sent"

        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False, str(e)

    def send_direct_message(self, phone: str, message: str):
        """Sends a message to a specific phone number using deep link"""
        if not self.driver:
            if not self.start_browser():
                return False, "Browser failed to start"

        try:
            # Clean phone number (remove +, spaces)
            phone = ''.join(filter(str.isdigit, phone))
            
            # Navigate to direct send url
            logger.info(f"Navigating to direct chat: {phone}")
            self.driver.execute_script(f"window.open('https://web.whatsapp.com/send?phone={phone}', '_blank');")
            
            # Switch to new tab
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(5) # Wait for load
            
            # Check for invalid number popup
            try:
                invalid_popup = self.driver.find_element(By.XPATH, '//div[text()="Phone number shared via url is invalid."]')
                if invalid_popup:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    return False, "Geçersiz Numara"
            except:
                pass

            # Wait for message box
            try:
                message_box = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
            except:
                 self.driver.close()
                 self.driver.switch_to.window(self.driver.window_handles[0])
                 return False, "Sohbet yüklenemedi"

            # Send Message
            for line in message.split('\n'):
                message_box.send_keys(line)
                message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            time.sleep(0.5)
            message_box.send_keys(Keys.ENTER)
            time.sleep(2)
            
            # Close tab and return
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return True, "Gönderildi"

        except Exception as e:
            logger.error(f"Direct send failed: {e}")
            # Ensure we don't leave extra tabs open
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            return False, str(e)

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_qr_code(self):
        """Returns base64 encoded QR code screenshot"""
        if not self.driver:
            self.start_browser()
            time.sleep(2)

        try:
            # Check if already logged in first
            if self.is_logged_in():
                logger.info("Asked for QR but already logged in.")
                return None 

            # Wait for QR Canvas
            try:
                # Canvas usually contains the QR code
                qr_canvas = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//canvas[@aria-label="Scan this QR code to link a device!"] | //canvas'))
                )
                time.sleep(1) # Wait for render
                return qr_canvas.screenshot_as_base64
            except:
                # Check for reload button if QR expired
                try:
                    reload_btn = self.driver.find_elements(By.XPATH, '//span[@data-icon="refresh-large"] | //div[@role="button"][contains(text(), "Reload")]')
                    if reload_btn:
                        logger.info("QR Code expired. Clicking reload...")
                        reload_btn[0].click()
                        time.sleep(2)
                        # Try getting canvas again
                        qr_canvas = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//canvas'))
                        )
                        return qr_canvas.screenshot_as_base64
                except Exception as e:
                    logger.warning(f"Reload check failed: {e}")
                
                return None

        except Exception as e:
            logger.error(f"Error getting QR: {e}")
            return None

    def get_pairing_code(self, phone_number):
        """Switches to Pairing Code mode and returns the code"""
        if not self.driver:
            self.start_browser()
            time.sleep(3)

        try:
            # 1. Switch to "Link with phone number" if not already there
            try:
                # Try multiple selectors for the link
                link_btn = None
                selectors = [
                    '//span[contains(text(), "Link with phone number")]',
                    '//span[contains(text(), "phone number")]',
                    '//span[contains(text(), "Telefon numarasıyla")]',
                    '//div[@role="button"]//span[contains(text(), "Link")]',
                    '//div[@role="button"]//span[contains(text(), "Telefon")]'
                ]
                for sel in selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, sel)
                        if elements:
                            link_btn = elements[0]
                            break
                    except:
                        continue
                
                if link_btn:
                    logger.info("Clicking Link with Phone Number button...")
                    link_btn.click()
                    time.sleep(2)
                else:
                    logger.info("Link with Phone Number button not found (might assume already on page or different language).")
            except Exception as e:
                logger.warning(f"Error checking link button: {e}")

            # 2. Input Phone Number
            try:
                # Use general input selectors
                phone_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Type your phone number."] | //input[@type="text"]')))
                phone_input.clear()
                
                logger.info(f"Entering phone number: {phone_number}")
                # Send number
                phone_input.send_keys(phone_number)
                time.sleep(1)
                
                # Click Next
                next_btn = self.driver.find_element(By.XPATH, '//div[text()="Next"] | //div[text()="İleri"]')
                next_btn.click()
                time.sleep(5) # Wait for network
                
            except Exception as input_err:
                logger.error(f"Error entering phone: {input_err}")
                self.driver.save_screenshot("pairing_input_error.png")
                return None

            # 3. Get the Code
            try:
                logger.info("Waiting for code to appear...")
                code_text = None
                
                # Retry loop for 20 seconds
                for i in range(20):
                    try:
                        # Strategy 1: The aria-details container (Structure based)
                        elements = self.driver.find_elements(By.XPATH, '//div[@aria-details="link-device-phone-number-code-screen-instruction"]')
                        if elements:
                            code_text = elements[0].text
                            if code_text and len(code_text) >= 8:
                                break

                        # Strategy 2: Look for the specific data-animate-modal-body
                        elements = self.driver.find_elements(By.XPATH, '//div[@data-animate-modal-body="true"]')
                        for el in elements:
                            text = el.text
                            # Simple heuristic: Code is usually 4 chars space 4 chars (ABCD 1234) or 8 chars
                            clean_text = text.replace("\n", "").replace(" ", "")
                            if len(clean_text) == 8 and clean_text.isalnum():
                                code_text = text
                                break
                        
                        if code_text:
                            break

                        # Strategy 3: Look for 8 distinct spans (if they use that structure)
                        # Sometimes WA uses a div for each char.
                        
                        time.sleep(1)
                    except:
                        pass
                
                if code_text:
                    logger.info(f"Extracted text: {code_text}")
                    return code_text
                else:
                    logger.error("Code not found after 20 seconds.")
                    self.driver.save_screenshot("pairing_timeout.png")
                    return None

            except Exception as code_err:
                logger.error(f"Error extracting code: {code_err}")
                self.driver.save_screenshot("pairing_code_error.png")
                return None

        except Exception as e:
            logger.error(f"Pairing flow failed: {e}")
            self.driver.save_screenshot("pairing_general_error.png")
            return None

    def get_chats(self):
        """Returns list of chats/groups from the side pane with aggressive scrolling"""
        if not self.driver: return []
        
        try:
            # Ensure pane-side is loaded
            try:
                pane_side = self.wait.until(EC.presence_of_element_located((By.ID, "pane-side")))
            except:
                logger.error("Pane side not found")
                return []
            
            # Aggressive Scroll down to load ALL chats
            logger.info("Starting aggressive scroll for groups...")
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", pane_side)
            
            # Scroll up to 20 times or until end
            for i in range(20):
                self.driver.execute_script("arguments[0].scrollTop += 800;", pane_side)
                time.sleep(0.5) # Short wait for DOM update
                
                # Check if we hit bottom (optional optimization, but reliable strictly by count is safer for lazy loading)
                # new_height = self.driver.execute_script("return arguments[0].scrollHeight", pane_side)
                # if new_height == last_height and i > 5:
                #     break
                # last_height = new_height

            time.sleep(1) # Final wait for rendering

            # Strategy 1: Standard role="listitem"
            chat_elements = self.driver.find_elements(By.XPATH, '//div[@id="pane-side"]//div[@role="listitem"]')
            
            # Strategy 2: If detected count is low, try broader selector
            if len(chat_elements) < 3:
                chat_elements = self.driver.find_elements(By.XPATH, '//div[@id="pane-side"]//div[starts-with(@style, "z-index")]')

            logger.info(f"Raw elements found: {len(chat_elements)}")
            
            chats = []
            seen_names = set()

            for el in chat_elements:
                try:
                    # Try multiple ways to get the title
                    name = ""
                    
                    # Method A: Title attribute on span (Most reliable usually)
                    try:
                        title_el = el.find_element(By.XPATH, './/span[@title]')
                        name = title_el.get_attribute("title")
                    except:
                        pass
                        
                    # Method B: Text content of specific classes (Fallback)
                    if not name:
                        try:
                           # Look for the large text element
                           text_el = el.find_element(By.CSS_SELECTOR, 'span[dir="auto"]')
                           name = text_el.text
                        except:
                            pass

                    # ID / Type Detection via InnerHTML (Robust)
                    import re
                    data_id = ""
                    try:
                        inner_html = el.get_attribute("innerHTML")
                        # Look for data-id format inside the element
                        id_match = re.search(r'data-id="([^"]+)"', inner_html)
                        if id_match:
                            data_id = id_match.group(1)
                    except:
                        pass
                    
                    if not data_id:
                        # Fallback: check raw attribute
                        data_id = el.get_attribute("data-id")

                    if data_id:
                        if "@g.us" in data_id:
                            chat_type = "group"
                        elif "@c.us" in data_id:
                            chat_type = "contact"
                        # Use Name as the functional ID for search-based sending, but log the real ID
                        # If we really want to track by ID, we need to map ID -> Name, but for this simple app, Name is key.
                    
                    if name and name not in seen_names:
                        # Fallback Heuristics if simple detection failed
                        if chat_type == "unknown":
                             clean_name = ''.join(filter(str.isdigit, name))
                             if len(clean_name) > 6 and (name.startswith("+") or name[0].isdigit()):
                                  chat_type = "contact"
                             else:
                                  # Default to group if valid name and not a phone number
                                  chat_type = "group"

                        chats.append({
                            "name": name, 
                            "id": name, # functional_id (used for search)
                            "jid": data_id, # real_id (metadata)
                            "type": chat_type,
                            "participants": "Bilinmiyor"
                        })

                        seen_names.add(name)
                except:
                    continue
                    
            logger.info(f"Final unique chats processed: {len(chats)}")
            return chats
        except Exception as e:
            logger.error(f"Error getting chats: {e}")
            return []

    def logout(self):
        if self.driver:
            try:
                # Click menu (3 dots)
                menu_btn = self.driver.find_element(By.XPATH, '//div[@aria-label="Menu"] | //span[@data-icon="menu"]')
                menu_btn.click()
                time.sleep(1)
                # Click Logout
                logout_btn = self.driver.find_element(By.XPATH, '//div[@aria-label="Log out"]')
                logout_btn.click()
                time.sleep(1)
                # Confirm Logout
                confirm_btn = self.driver.find_element(By.XPATH, '//div[text()="Log out"]')
                confirm_btn.click()
            except Exception as e:
                logger.error(f"Logout failed: {e}")

whatsapp_service = WhatsAppService(headless=False) # Run in Visible Mode (Reliable)
