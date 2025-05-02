import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

def find_question_elements(driver, question_index):
    """Helper function to find elements within a specific question container"""
    try:
        # Using a more specific selector that targets the main div for each question
        questions = driver.find_elements(By.CSS_SELECTOR, "div.Qr7Oae")
        if question_index < len(questions):
            return questions[question_index]
        else:
            print(f"Warning: Question index {question_index} out of range (found {len(questions)} questions).")
    except Exception as e:
        print(f"Error finding question container {question_index}: {e}")
    return None

def find_radio_options(question_element):
    """Find radio button options within a question element"""
    # Target the div that wraps each individual radio option (label + input)
    try:
        return question_element.find_elements(By.CSS_SELECTOR, "div.nWQGrd.zwllIb")
    except Exception as e:
        print(f"Error finding radio options: {e}")
        return []

def find_checkbox_options(question_element):
    """Find checkbox options within a question element"""
    # Target the div that wraps each individual checkbox option
    try:
        return question_element.find_elements(By.CSS_SELECTOR, "div.eBFwI") # Use the specific checkbox wrapper class
    except Exception as e:
        print(f"Error finding checkbox options: {e}")
        return []

def find_scale_options(question_element):
    """Find scale (1-5) options within a question element"""
    # Targeting the labels specifically for the scale type question
    try:
        return question_element.find_elements(By.CSS_SELECTOR, ".T5pZmf")
    except Exception as e:
        print(f"Error finding scale options: {e}")
        return []

def find_text_input(question_element):
    """Find text input area within a question element"""
    try:
        return question_element.find_element(By.CSS_SELECTOR, "textarea.KHxj8b")
    except NoSuchElementException:
        return None

def find_other_text_input(question_element):
    """Find the text input for the 'Other' option in checkboxes/radios"""
    try:
        # Find the 'Other' checkbox container first, then the input within it
        other_option_container = question_element.find_element(By.CSS_SELECTOR, ".RVLOe")
        return other_option_container.find_element(By.CSS_SELECTOR, "input.Hvn9fb[type='text']")
    except NoSuchElementException:
        return None

def fill_mannings_survey():
    """Fill in the Mannings consumer behavior survey with random but logical data"""
    # Set up Chrome options - OPTIMIZED
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3") # Suppress non-critical logs
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false") # Disable image loading
    
    # Set up the WebDriver with optimized service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set page load timeout
    driver.set_page_load_timeout(30)
    
    # Open the Google Form
    driver.get("https://forms.gle/pokY573SrLfa5XLR7")
    
    # Wait for form to load - INCREASED TIMEOUT
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".Qr7Oae")) # Wait for question containers
        )
        print("Form loaded successfully")
    except TimeoutException:
        print("Form loading timed out!")
        driver.quit()
        return {}
    
    # Small delay to ensure the form is fully loaded
    time.sleep(1)
    
    # Function to refresh the questions list
    def get_all_questions():
        try:
            return driver.find_elements(By.CSS_SELECTOR, "div.Qr7Oae")
        except Exception as e:
            print(f"Error getting all questions: {e}")
            return []
    
    # Cache all questions at once to reduce DOM queries
    all_questions = get_all_questions()
    
    user_choices = {}

    # --- Question Answering Logic --- 
    
    # Q1: Age group (index 0)
    print("\nAnswering Q1: Age group")
    q1_element = all_questions[0] if len(all_questions) > 0 else None
    if q1_element:
        try:
            age_options = find_radio_options(q1_element)
            if len(age_options) == 7:
                age_weights = [0.05, 0.25, 0.25, 0.25, 0.10, 0.05, 0.05]
                age_choice = random.choices(age_options, weights=age_weights, k=1)[0]
                age_text = age_choice.text.split('\n')[0] # Get text before newline if any
                age_choice.click()
                user_choices['age_group'] = age_text
                print(f"Selected age group: {age_text}")
            else:
                 print(f"Found {len(age_options)} options for Q1, expected 7.")
        except Exception as e:
            print(f"Error answering Q1: {e}")
    
    # Small delay between questions
    time.sleep(0.5)

    # Q2: Online purchase frequency (index 1)
    print("\nAnswering Q2: Online purchase frequency")
    # Refresh questions list
    all_questions = get_all_questions()
    q2_element = all_questions[1] if len(all_questions) > 1 else None
    if q2_element:
        try:
            purchase_options = find_radio_options(q2_element)
            if len(purchase_options) == 5:
                purchase_weights = [0.10, 0.30, 0.30, 0.20, 0.10] 
                purchase_choice = random.choices(purchase_options, weights=purchase_weights, k=1)[0]
                purchase_text = purchase_choice.text.split('\n')[0]
                purchase_choice.click()
                user_choices['purchase_frequency'] = purchase_text
                print(f"Selected purchase frequency: {purchase_text}")
            else:
                 print(f"Found {len(purchase_options)} options for Q2, expected 5.")
        except Exception as e:
            print(f"Error answering Q2: {e}")
    
    # Small delay between questions
    time.sleep(0.5)

    # Q3: Used Mannings app? (index 2)
    print("\nAnswering Q3: Used Mannings app?")
    # Refresh questions list
    all_questions = get_all_questions()
    q3_element = all_questions[2] if len(all_questions) > 2 else None
    has_used_app = False # Default
    if q3_element:
        try:
            app_options = find_radio_options(q3_element)
            if len(app_options) == 2:
                app_yes_prob = 0.6
                has_used_app = random.choices([True, False], weights=[app_yes_prob, 1-app_yes_prob], k=1)[0]
                app_choice = app_options[0] if has_used_app else app_options[1]
                app_text = app_choice.text.split('\n')[0]
                app_choice.click()
                user_choices['used_app'] = has_used_app
                print(f"Used Mannings app: {app_text}")
            else:
                 print(f"Found {len(app_options)} options for Q3, expected 2.")
        except Exception as e:
            print(f"Error answering Q3: {e}")
    
    # Small delay between questions
    time.sleep(0.5)

    # Refresh questions again after answering Q3
    all_questions = get_all_questions()

    # Q4: App satisfaction (index 3, only if Q3 was Yes)
    if user_choices.get('used_app', False):
        print("\nAnswering Q4: App satisfaction")
        q4_element = all_questions[3] if len(all_questions) > 3 else None
        if q4_element:
            try:
                # Use the specific selector for scale options
                satisfaction_options = find_scale_options(q4_element)
                if len(satisfaction_options) == 5:
                    print(f"Found {len(satisfaction_options)} scale rating options")
                    satisfaction_weights = [0.1, 0.4, 0.30, 0.15, 0.05]
                    satisfaction_choice = random.choices(satisfaction_options, weights=satisfaction_weights, k=1)[0]
                    # Get the rating number (e.g., '1', '2') from the first div inside the label
                    rating_text = satisfaction_choice.find_element(By.CSS_SELECTOR, "div.Zki2Ve").text.strip()
                    satisfaction_choice.click()
                    print(f"Selected satisfaction rating: {rating_text}")
                else:
                    print(f"Found {len(satisfaction_options)} scale options for Q4, expected 5.")
            except Exception as e:
                print(f"Error answering Q4: {e}")
        
        # Small delay between questions
        time.sleep(0.5)
    else:
        print("\nSkipping Q4 (User did not use app)")

    # Refresh questions list again
    all_questions = get_all_questions()

    # Q5: App Confusion (index 4, only if Q3 was Yes)
    if user_choices.get('used_app', False):
        print("\nAnswering Q5: App confusion")
        q5_element = all_questions[4] if len(all_questions) > 4 else None
        if q5_element:
            try:
                confusion_options = find_radio_options(q5_element)
                if len(confusion_options) == 4:
                    confusion_weights = [0.3, 0.3, 0.2, 0.2] # Often, Sometimes, Rarely, Never
                    confusion_choice = random.choices(confusion_options, weights=confusion_weights, k=1)[0]
                    confusion_text = confusion_choice.text.split('\n')[0]
                    confusion_choice.click()
                    print(f"App confusion level: {confusion_text}")
                else:
                    print(f"Found {len(confusion_options)} options for Q5, expected 4.")
            except Exception as e:
                print(f"Error answering Q5: {e}")
        
        # Small delay between questions
        time.sleep(0.5)
    else:
        print("\nSkipping Q5 (User did not use app)")

    # Refresh questions again
    all_questions = get_all_questions()

    # Q6: AI Willingness (index 5 or 3 depending on app usage)
    print("\nAnswering Q6: AI Willingness")
    q6_index = 5 if user_choices.get('used_app', False) else 3
    q6_element = all_questions[q6_index] if len(all_questions) > q6_index else None
    if q6_element:
        try:
            ai_options = find_scale_options(q6_element)
            if len(ai_options) == 5:
                ai_weights = [0.10, 0.10, 0.20, 0.30, 0.30] # Weighted towards neutral/positive
                ai_choice = random.choices(ai_options, weights=ai_weights, k=1)[0]
                ai_rating_text = ai_choice.find_element(By.CSS_SELECTOR, "div.Zki2Ve").text.strip()
                ai_choice.click()
                print(f"AI willingness rating: {ai_rating_text}")
            else:
                print(f"Found {len(ai_options)} scale options for Q6, expected 5.")
        except Exception as e:
            print(f"Error answering Q6: {e}")
    
    # Small delay between questions
    time.sleep(1)  # Longer delay after scale question

    # Refresh questions list again
    all_questions = get_all_questions()

    # Q7: Helpful Features
    print("\nAnswering Q7: Helpful Features")
    q7_index = 6 if user_choices.get('used_app', False) else 4
    q7_element = all_questions[q7_index] if len(all_questions) > q7_index else None
    if q7_element:
        try:
            # Wait for the checkbox options to be visible
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.eBFwI"))
            )
            feature_options = find_checkbox_options(q7_element)
            # Checkbox options are wrapped differently, use the specific helper
            if len(feature_options) == 6: # 5 features + Other
                num_features_to_select = random.randint(1, 3)
                # Exclude 'Other' option initially when sampling
                selected_features = random.sample(feature_options[:-1], num_features_to_select)
                
                # Decide whether to select 'Other'
                select_other = random.random() < 0.1 # 10% chance
                
                # Click selected features
                for feature in selected_features:
                    feature.click()
                    # Find the text span within the label
                    feature_text = feature.find_element(By.CSS_SELECTOR, ".aDTYNe").text
                    print(f"Selected feature: {feature_text}")
                
                # Handle 'Other' option if selected
                if select_other:
                    other_option = feature_options[-1] # The last one is 'Other'
                    other_option.click()
                    other_input = find_other_text_input(q7_element)
                    if other_input:
                        other_text = random.choice(["Better search", "More detailed product info", "Easier checkout"])
                        other_input.send_keys(other_text)
                        print(f"Selected feature: Other: {other_text}")
                    else:
                        print("Could not find input for Other option")
            else:
                 print(f"Found {len(feature_options)} options for Q7, expected 6.")
        except TimeoutException:
            print("Timed out waiting for checkbox options in Q7")
        except Exception as e:
            print(f"Error answering Q7: {e}")
    
    # Small delay between questions
    time.sleep(1)

    # Refresh questions again
    all_questions = get_all_questions()

    # Q8: Sustainability
    print("\nAnswering Q8: Sustainability")
    q8_index = 7 if user_choices.get('used_app', False) else 5
    q8_element = all_questions[q8_index] if len(all_questions) > q8_index else None
    if q8_element:
        try:
            # Wait for radio options to be visible
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.nWQGrd.zwllIb"))
            )
            sustainability_options = find_radio_options(q8_element)
            if len(sustainability_options) == 2:
                sustainability_choice = random.choices(sustainability_options, weights=[0.7, 0.3], k=1)[0] # More likely Yes
                sustainability_text = sustainability_choice.text.split('\n')[0]
                sustainability_choice.click()
                print(f"Sustainability considered: {sustainability_text}")
            else:
                 print(f"Found {len(sustainability_options)} options for Q8, expected 2.")
        except TimeoutException:
            print("Timed out waiting for radio options in Q8")
        except Exception as e:
            print(f"Error answering Q8: {e}")
    
    # Small delay between questions
    time.sleep(1)

    # Refresh questions again
    all_questions = get_all_questions()

    # Q9: Live Shopping
    print("\nAnswering Q9: Live Shopping")
    q9_index = 8 if user_choices.get('used_app', False) else 6
    q9_element = all_questions[q9_index] if len(all_questions) > q9_index else None
    if q9_element:
        try:
            # Wait for radio options to be visible
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.nWQGrd.zwllIb"))
            )
            live_options = find_radio_options(q9_element)
            if len(live_options) == 3:
                live_weights = [0.5, 0.4, 0.1] # Frequently, Occasionally, Never
                live_choice = random.choices(live_options, weights=live_weights, k=1)[0]
                live_text = live_choice.text.split('\n')[0]
                live_choice.click()
                print(f"Participate in live shopping: {live_text}")
            else:
                 print(f"Found {len(live_options)} options for Q9, expected 3.")
        except TimeoutException:
            print("Timed out waiting for radio options in Q9") 
        except Exception as e:
            print(f"Error answering Q9: {e}")
    
    # Small delay between questions
    time.sleep(1)

    # Refresh questions again
    all_questions = get_all_questions()

    # Q10: Suggestions
    print("\nAnswering Q10: Suggestions")
    q10_index = 9 if user_choices.get('used_app', False) else 7
    q10_element = all_questions[q10_index] if len(all_questions) > q10_index else None
    if q10_element:
        try:
            # Wait for text area to be visible
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.KHxj8b"))
            )
            suggestion_input = find_text_input(q10_element)
            if suggestion_input:
                # 50% chance of giving a meaningful suggestion, 50% chance of N/A
                if random.random() < 0.5:
                    # List of meaningful suggestions (expand this list)
                    meaningful_suggestions = [
                        "App could be faster.", 
                        "More promotions needed.", 
                        "Easier navigation would be good.",
                        "Add more product details.",
                        "Improve search functionality.",
                        "Offer loyalty points for app usage.",
                        "Better integration with physical store experience.",
                        "Wishlist feature is needed.",
                        "Include video reviews for products.",
                        "More payment options (e.g., Apple Pay).",
                        "App crashes occasionally on my device.",
                        "Provide nutritional information more clearly.",
                        "Filter options could be more extensive.",
                        "Notifications are sometimes irrelevant.",
                        "Offer in-app exclusive deals.",
                        "The UI feels a bit dated.",
                        "Better customer support chat within the app.",
                        "Show stock availability in nearby stores.",
                        "Allow saving multiple delivery addresses.",
                        "Improve the product comparison feature.",
                        "Make it easier to reorder past purchases.",
                        "Add barcode scanner for in-store price checks.",
                        "Provide personalized health recommendations.",
                        "The app uses too much battery.",
                        "Offer guest checkout option.",
                        "Simpler returns process through the app.",
                        "More language options would be helpful.",
                        "Loading times for product images are slow.",
                        "Better explanation of loyalty program tiers.",
                        "Integrate with health tracking apps."
                    ]
                    suggestion_text = random.choice(meaningful_suggestions)
                else:
                    # List of N/A or no comment responses
                    no_comment_responses = [
                        "N/A",
                        "No comment",
                        "None",
                        "No suggestions at this time.",
                        "Nothing to add.",
                        "-",
                        "Keep up the good work.", # Neutral positive
                        "Satisfied with current services."
                    ]
                    suggestion_text = random.choice(no_comment_responses)
                
                suggestion_input.send_keys(suggestion_text)
                print(f"Suggestion provided: {suggestion_text}")
            else:
                 print(f"Could not find suggestion input box for Q10.")
        except TimeoutException:
            print("Timed out waiting for textarea in Q10")
        except Exception as e:
            print(f"Error answering Q10: {e}")
    
    # Give the page time to process all answers before submission
    time.sleep(2)

    # --- Find and Click Submit --- 
    try:
        # Wait for submit button to be visible and enabled
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button'][jsname='M2UYVd']"))
        )
        
        # Optimized submit button search - directly try the most reliable selector first
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, "div[role='button'][jsname='M2UYVd']")
            if submit_button.is_displayed() and submit_button.is_enabled():
                print("\nFound submit button")
                submit_button.click()
                print("Form submitted!")
                # Short wait to ensure submission completes
                time.sleep(2)
            else:
                raise NoSuchElementException("Button not clickable")
        except NoSuchElementException:
            # Fallback to other selectors
            selectors = [
                ".freebirdFormviewerViewNavigationSubmitButton",
                "//span[contains(text(), 'Submit') or contains(text(), '提交')]/ancestor::div[@role='button'][1]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        submit_elements = driver.find_elements(By.XPATH, selector)
                    else:
                        submit_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for el in submit_elements:
                        if el.is_displayed() and el.is_enabled():
                            el.click()
                            print("Form submitted with fallback selector!")
                            time.sleep(2)
                            break
                except Exception:
                    continue
    except TimeoutException:
        print("Timed out waiting for submit button")
    except Exception as e:
        print(f"Error submitting form: {e}")
    
    # Close the browser
    driver.quit()
    return user_choices

def run_multiple_submissions(count=3):
    """Run multiple form submissions with random data"""
    all_responses = []
    start_time = time.time()
    
    for i in range(count):
        print(f"\n{'='*50}")
        print(f"Starting submission {i+1} of {count}")
        print(f"{'='*50}")
        
        user_choices = fill_mannings_survey()
        if user_choices: # Only append if the survey function didn't fail early
            all_responses.append(user_choices)
    
    total_time = time.time() - start_time
    print(f"\nCompleted {len(all_responses)} submissions in {total_time:.2f} seconds")
    print(f"Average time per submission: {total_time/len(all_responses):.2f} seconds")

if __name__ == "__main__":
    # Change the number to control how many submissions to make
    run_multiple_submissions(500)
