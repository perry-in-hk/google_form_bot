import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class GoogleFormBot:
    def __init__(self, form_url):
        self.form_url = form_url
        self.driver = self.setup_driver()
        
    def setup_driver(self):
        """Setup and return the WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run headless for speed
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        
        # Add a short implicit wait to reduce explicit wait time
        driver.implicitly_wait(2)
        return driver
    
    def start(self):
        """Start the form filling process"""
        try:
            print("Starting form submission...")
            self.driver.get(self.form_url)
            
            # Fill out all pages
            self.fill_page_1()
            
            print("Form submission completed successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Auto-close browser after 1 second in headless mode
            time.sleep(1)
            self.driver.quit()
    
    def click_next(self):
        """Click the Next button to move to the next page"""
        try:
            # Use a more specific selector for the next button
            next_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ThHDze')]//span[contains(text(), '下一個') or contains(text(), 'Next')]"))
            )
            # Use JavaScript click for speed
            self.driver.execute_script("arguments[0].click();", next_button)
            return True
        except Exception as e:
            print(f"Could not find or click Next button: {e}")
            return False
    
    def fill_page_1(self):
        """Fill out the first page of the form"""
        try:
            # Improved email field detection - try multiple approaches
            try:
                # Try to find by class name and attributes common in Google Forms
                email_fields = self.driver.find_elements(By.CSS_SELECTOR, "input.whsOnd.zHQkBf")
                if email_fields:
                    # First input field is likely email
                    email_fields[0].send_keys("test@example.com")
                    print("Email field filled using class method")
                else:
                    # Try by XPath with partial matching for typical email field attributes
                    email_field = self.driver.find_element(
                        By.XPATH, 
                        "//input[contains(@aria-label, 'mail') or contains(@placeholder, 'mail') or @type='email']"
                    )
                    email_field.send_keys("test@example.com")
                    print("Email field filled using XPath method")
            except NoSuchElementException:
                # Try a more aggressive approach - find all text inputs and fill the first one
                try:
                    text_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                    if text_inputs:
                        text_inputs[0].send_keys("test@example.com")
                        print("Email field filled using fallback method")
                    else:
                        print("No text input fields found, skipping email")
                except:
                    print("Email field not found, skipping")
            
            # Select Gender (Male/Female)
            self.select_radio_option("Male")
            
            # Select Age
            self.select_radio_option("18 - 30")
            
            # Select BMI
            self.select_radio_option("18.5 - 22.9 (Normal)")
            
            # Select Activity Level
            self.select_radio_option("Lightly active")
            
            # Select Health Conditions - Direct targeting using exact IDs and selectors
            self.select_health_condition_direct()
            
            # Select Dietary Preferences
            self.select_checkbox_option("No specific preference")
            
            # Click Next button
            if self.click_next():
                self.fill_page_2()
        except Exception as e:
            print(f"Error filling page 1: {e}")
    
    def select_health_condition_direct(self):
        """Directly target the 'No' option for health conditions using JavaScript"""
        try:
            print("Selecting health condition 'No' using JavaScript...")
            
            js_result = self.driver.execute_script("""
                // Try to find question containing "health condition"
                var healthTexts = ["health condition", "疾病"];
                var found = false;
                
                // Find all heading or question elements
                var questions = document.querySelectorAll('[role="heading"], [jsname="UWxmff"], [jsname="r4nke"]');
                
                for (var i = 0; i < questions.length && !found; i++) {
                    var questionText = questions[i].textContent.toLowerCase();
                    
                    // Check if this is the health condition question
                    for (var j = 0; j < healthTexts.length && !found; j++) {
                        if (questionText.includes(healthTexts[j])) {
                            // Found the question, now find container
                            var container = questions[i];
                            for (var k = 0; k < 5 && !found; k++) {
                                container = container.parentElement;
                                if (!container) break;
                                
                                // Look for "No" option
                                var options = container.querySelectorAll('[role="checkbox"], [jsname="OCpkoe"]');
                                for (var l = 0; l < options.length; l++) {
                                    var optionText = options[l].textContent.toLowerCase();
                                    if (optionText.includes("no") || l === 0) {  // Often "No" is the first option
                                        options[l].click();
                                        found = true;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Fallback - try to find any checkbox with "No" text nearby
                if (!found) {
                    var allOptions = document.querySelectorAll('[role="checkbox"]');
                    for (var i = 0; i < allOptions.length; i++) {
                        var nearText = allOptions[i].textContent.toLowerCase();
                        if (nearText.includes("no")) {
                            allOptions[i].click();
                            found = true;
                            break;
                        }
                    }
                }
                
                return found;
            """)
            
            if js_result:
                print("Health condition 'No' selected successfully")
                return True
            
            # Fallback to the original XPath method if JavaScript fails
            no_option = self.driver.find_element(By.XPATH, "//span[contains(text(), 'No')]/ancestor::label")
            self.driver.execute_script("arguments[0].click();", no_option)
            print("Health condition 'No' selected using XPath fallback")
            return True
            
        except Exception as e:
            print(f"Error in select_health_condition_direct: {e}")
            return False
    
    def find_option_by_question_context(self, question_text, option_text):
        """Find an option by first locating its parent question"""
        # Find the question containing the specified text
        questions = self.driver.find_elements(By.XPATH, f"//div[contains(@role, 'heading') and contains(text(), '{question_text}')]")
        
        if not questions:
            questions = self.driver.find_elements(By.XPATH, f"//div[contains(text(), '{question_text}')]")
        
        if questions:
            # Find the containing listitem
            for question in questions:
                try:
                    # Navigate up to find the form item container
                    container = question
                    for _ in range(5):  # Try up to 5 levels up
                        container = container.find_element(By.XPATH, "./..")
                        if container.get_attribute("role") == "listitem":
                            break
                    
                    # Find the option within this container
                    options = container.find_elements(By.XPATH, f".//span[contains(text(), '{option_text}')]")
                    if options:
                        for option in options:
                            try:
                                # Navigate up to the clickable element
                                clickable = option
                                for _ in range(3):  # Try up to 3 levels up
                                    clickable = clickable.find_element(By.XPATH, "./..")
                                    if clickable.get_attribute("role") == "checkbox":
                                        clickable.click()
                                        return True
                            except:
                                continue
                except:
                    continue
        
        raise Exception("Could not find option by question context")
    
    def fill_page_2(self):
        """Fill out the second page of the form (Nutritional Awareness)"""
        try:
            # Primary health goals
            self.select_checkbox_option("Weight loss")
            self.select_checkbox_option("Improving overall health")
            
            # Rank factors that affect food decisions
            self.rank_grid_options()
            
            # Other factors that may affect food decisions - use fast JavaScript approach
            print("Filling 'Other factors' field...")
            js_result = self.driver.execute_script("""
                // Find text that mentions "Other factors"
                var labels = document.querySelectorAll('div, span, label');
                for (var i = 0; i < labels.length; i++) {
                    if (labels[i].textContent.includes('Other factors')) {
                        // Found the question, now find the input field
                        var container = labels[i];
                        // Go up to find container
                        for (var j = 0; j < 5; j++) {
                            container = container.parentElement;
                            if (!container) break;
                            
                            // Look for input or textarea
                            var input = container.querySelector('textarea, input[type="text"]');
                            if (input) {
                                input.value = 'Price and convenience';
                                // Trigger input event to ensure form registers the change
                                var event = new Event('input', { bubbles: true });
                                input.dispatchEvent(event);
                                return true;
                            }
                        }
                    }
                }
                
                // Fallback approach - try all text inputs and use the last one
                var allInputs = document.querySelectorAll('textarea, input[type="text"]');
                if (allInputs.length > 0) {
                    var lastInput = allInputs[allInputs.length - 1];
                    lastInput.value = 'Price and convenience';
                    var event = new Event('input', { bubbles: true });
                    lastInput.dispatchEvent(event);
                    return true;
                }
                
                return false;
            """)
            
            if js_result:
                print("Successfully filled 'Other factors' field using JavaScript")
            else:
                print("Failed to fill 'Other factors' field with JavaScript")
            
            # Click Next button
            if self.click_next():
                self.fill_page_3()
        except Exception as e:
            print(f"Error filling page 2: {e}")
    
    def fill_page_3(self):
        """Fill out the third page of the form (Frequency question only)"""
        try:
            print("Filling Page 3...")
            # How often do you eat at TamJai SamGor - this is the only question on page 3
            self.select_radio_option("1-2 times a week")
            print("Selected eating frequency.")
            
            # Click Next button
            print("Attempting to click Next on page 3...")
            if self.click_next():
                print("Successfully clicked Next on page 3.")
                self.fill_page_4()
            else:
                print("Failed to click Next on page 3.")
                # Attempt a JS click as a last resort if standard click failed
                try:
                    next_button_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ThHDze')]//span[contains(text(), '下一個') or contains(text(), 'Next')]")
                    self.driver.execute_script("arguments[0].click();", next_button_element)
                    print("Clicked Next on page 3 using JS fallback.")
                    self.fill_page_4()
                except Exception as js_click_error:
                    print(f"JS click for Next button also failed on page 3: {js_click_error}")
        except Exception as e:
            print(f"Error filling page 3: {e}")

    def fill_page_4(self):
        """Fill out the fourth page of the form (Food choices and preferences)"""
        try:
            print("Filling Page 4...")
            # What do you usually get from TamJai SamGor - this is on page 4
            food_options = ["Chicken 雞肉", "Fishball 魚蛋", "Ma La Soup 麻辣湯", "Lettuce 生菜"]
            for option in food_options:
                self.select_checkbox_option(option)
            print(f"Selected {len(food_options)} food options.")
            
            # Now handle the linear scale questions - these are on page 4
            # How important is meal recommendations (first linear scale)
            self.select_linear_scale_by_id("i133", 4)  # ID from HTML
            
            # How willing to try peer recommendations (second linear scale) 
            self.select_linear_scale_by_id("i138", 4)  # ID from HTML
            
            # Would you like to receive meal plans - this is on page 4
            self.select_radio_option("Yes")
            print("Selected preference for meal plans.")
            
            # What features would you like to see in an AI-powered nutritionist?
            features = ["Gamification", "Interactive interface", "Nutritional information"]
            for feature in features:
                self.select_checkbox_option(feature)
            print(f"Selected features for AI-powered nutritionist: {', '.join(features)}")
            
            # Submit the form (since this is the last page)
            self.submit_form()
        except Exception as e:
            print(f"Error filling page 4: {e}")
    
    def select_radio_option(self, option_text):
        """Select a radio button option by its text"""
        try:
            # Try JavaScript first for speed
            js_result = self.driver.execute_script(f"""
                var elements = document.querySelectorAll('span, div, label');
                for (var i = 0; i < elements.length; i++) {{
                    if (elements[i].textContent.includes('{option_text}')) {{
                        var clickable = elements[i];
                        // Find the clickable parent
                        for (var j = 0; j < 5; j++) {{
                            if (clickable.getAttribute('role') === 'radio' || 
                                clickable.getAttribute('role') === 'checkbox' ||
                                clickable.tagName === 'LABEL') {{
                                clickable.click();
                                return true;
                            }}
                            if (clickable.parentElement) {{
                                clickable = clickable.parentElement;
                            }} else {{
                                break;
                            }}
                        }}
                    }}
                }}
                return false;
            """)
            
            if js_result:
                return
            
            # If JS failed, try direct XPath with short wait
            option = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{option_text}')]/ancestor::*[@role='radio' or @role='checkbox' or self::label][1]"))
            )
            self.driver.execute_script("arguments[0].click();", option)
        except Exception as e:
            # Final attempt - find any element with text and try to click it
            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{option_text}')]")
            for element in elements:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return
                except:
                    continue
            print(f"Failed to select option '{option_text}': {e}")
    
    def select_checkbox_option(self, option_text):
        """Select a checkbox option by its text"""
        self.select_radio_option(option_text)
    
    def rank_grid_options(self):
        """Fill out a grid-style ranking question"""
        try:
            # Find all grid rows
            grid_rows = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'lLfZXe fnxRtf EzyPc')]")
            
            if not grid_rows:
                # Try alternative selector for grid rows
                grid_rows = self.driver.find_elements(By.XPATH, "//div[@role='radiogroup']")
            
            # For each row, select a rank
            for i, row in enumerate(grid_rows):
                # Get a rank that hasn't been used yet
                rank = (i % 5) + 1  # Distribute ranks 1-5 evenly
                try:
                    # Find the radio button for this rank
                    radio = row.find_element(By.XPATH, f".//div[@data-value='{rank}']")
                    radio.click()
                except:
                    print(f"Could not select rank {rank} for row {i+1}")
        except Exception as e:
            print(f"Error with grid ranking: {e}")
    
    def select_linear_scale(self, value):
        """Select a value on a linear scale"""
        try:
            # Find all linear scale questions
            scale_rows = self.driver.find_elements(By.XPATH, "//div[contains(@role, 'radiogroup')]")
            
            # For the most recently found scale that hasn't been filled
            filled_count = 0
            for row in scale_rows:
                # Check if this row has already been filled
                if "aria-checked='true'" not in row.get_attribute("innerHTML"):
                    try:
                        # Find the radio button for this value
                        radio = row.find_element(By.XPATH, f".//div[@data-value='{value}']")
                        radio.click()
                        filled_count += 1
                        break
                    except:
                        print(f"Could not select linear scale value {value}")
            
            if filled_count == 0:
                # Try alternative approach - find all radio buttons with the target value
                radios = self.driver.find_elements(By.XPATH, f"//div[@data-value='{value}']")
                if radios:
                    for radio in radios:
                        try:
                            radio.click()
                            filled_count += 1
                            # Only click two (for the two linear scale questions)
                            if filled_count >= 2:
                                break
                        except:
                            continue
        except Exception as e:
            print(f"Error with linear scale: {e}")
    
    def select_linear_scale_fallback(self, value):
        """Fallback: Select a value on a linear scale (original logic)"""
        try:
            # Find all linear scale questions
            scale_rows = self.driver.find_elements(By.XPATH, "//div[contains(@role, 'radiogroup')]")
            
            # For the most recently found scale that hasn't been filled
            for row in reversed(scale_rows): # Iterate backwards to find unfilled ones
                # Check if this row has already been filled
                is_filled = False
                try:
                    checked_option = row.find_element(By.XPATH, ".//div[@aria-checked='true']")
                    is_filled = True
                except NoSuchElementException:
                    pass # Not filled
                    
                if not is_filled:
                    try:
                        # Find the radio button for this value
                        radio = row.find_element(By.XPATH, f".//div[@data-value='{value}']")
                        radio.click()
                        print(f"Fallback: Selected linear scale value {value}")
                        return True
                    except:
                        print(f"Fallback: Could not select linear scale value {value} in this row")
                        continue # Try next row
            
            print(f"Fallback: Could not find an unfilled linear scale to select value {value}")
            return False

        except Exception as e:
            print(f"Error with fallback linear scale: {e}")
            return False
    
    def select_linear_scale_by_id(self, scale_id, value):
        """Select a value on a linear scale identified by its question ID"""
        try:
            print(f"Selecting value {value} for scale...")
            
            # Use JavaScript to find and click any linear scale option with the given value
            js_result = self.driver.execute_script(f"""
                // Try to find all radiogroups
                var radiogroups = document.querySelectorAll('[role="radiogroup"]');
                var clicked = 0;
                
                // Try each radiogroup
                for (var i = 0; i < radiogroups.length; i++) {{
                    // Check if this radiogroup has already been filled
                    var checked = radiogroups[i].querySelector('[aria-checked="true"]');
                    if (checked) continue;
                    
                    // Find the option with the desired value
                    var option = radiogroups[i].querySelector('[data-value="{value}"]');
                    if (option) {{
                        option.click();
                        clicked++;
                        if (clicked >= 2) return true; // We need to click two scales
                    }}
                }}
                
                return clicked > 0;
            """)
            
            if js_result:
                print(f"Successfully selected linear scale values using JavaScript")
                return True
            
            # Fallback to original approach
            try:
                # Direct XPath as fallback
                xpath = f"//div[@role='radiogroup']//div[@data-value='{value}']"
                options = self.driver.find_elements(By.XPATH, xpath)
                if options:
                    for option in options[:2]:  # Get first two (for the two scales)
                        self.driver.execute_script("arguments[0].click();", option)
                    return True
            except Exception as e:
                print(f"Fallback attempt failed: {e}")
                return False
        except Exception as e:
            print(f"Error in select_linear_scale_by_id: {e}")
            return False
    
    def submit_form(self):
        """Submit the form"""
        try:
            print("Submitting form...")
            # Try JavaScript approach first for fastest submission
            js_result = self.driver.execute_script("""
                // Try to find submit button by text content
                var buttons = document.querySelectorAll('span, div');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.includes('Submit') || 
                        buttons[i].textContent.includes('提交')) {
                        // Click the button or its parent
                        var clickable = buttons[i];
                        for (var j = 0; j < 3; j++) {
                            if (clickable.getAttribute('role') === 'button') {
                                clickable.click();
                                return true;
                            }
                            if (clickable.parentElement) {
                                clickable = clickable.parentElement;
                            } else {
                                break;
                            }
                        }
                    }
                }
                
                // Try to find last button in the form
                var allButtons = document.querySelectorAll('[role="button"]');
                if (allButtons.length > 0) {
                    allButtons[allButtons.length-1].click();
                    return true;
                }
                
                return false;
            """)
            
            if js_result:
                print("Form submitted using JavaScript!")
                return
            
            # Fallback to WebDriver approach
            submit_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '提交') or contains(text(), 'Submit')]/../.."))
            )
            self.driver.execute_script("arguments[0].click();", submit_button)
            print("Form submitted!")
        except Exception as e:
            print(f"Error submitting form: {e}")
            # Last resort - try to get all buttons and click the last one
            buttons = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'uArJ5e') or contains(@role, 'button')]")
            if buttons:
                self.driver.execute_script("arguments[0].click();", buttons[-1])
                print("Form submitted using last button fallback!")

if __name__ == "__main__":
    # URL of the Google Form - replace with your actual form URL
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeOAbkl3gjpn4YS89Ie_vHq6PO9faqKRQydsoallHS1r3Vaew/viewform"
    
    successful_submissions = 0
    failed_submissions = 0
    
    print("Starting form submission loop (10 iterations)...")
    
    for i in range(10):
        print(f"\n--- Starting submission {i+1}/10 ---")
        try:
            bot = GoogleFormBot(form_url)
            bot.start()
            successful_submissions += 1
        except Exception as e:
            print(f"Error in submission {i+1}: {e}")
            failed_submissions += 1
    
    print("\n=== Summary ===")
    print(f"Total submissions attempted: 10")
    print(f"Successful submissions: {successful_submissions}")
    print(f"Failed submissions: {failed_submissions}")
    print("=== Done ===")