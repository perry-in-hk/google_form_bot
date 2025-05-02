# Google Form Bot

A Python-based automation tool for filling out Google Forms with randomized yet realistic responses that mimic human behavior.

## Overview

This project provides a flexible framework for automating Google Form submissions with intelligent response patterns. It uses Selenium WebDriver to interact with form elements and implements various strategies to handle different question types commonly found in Google Forms.

## Features

- **Multi-question support**: Handles radio buttons, checkboxes, linear scales, text inputs, and grid questions
- **Human-like responses**: Implements weighted randomization to create realistic response patterns
- **Resilient form navigation**: Multiple fallback mechanisms to ensure reliable form completion
- **Headless operation**: Can run in background without UI for better performance
- **Configurable response patterns**: Easy to customize for different forms and use cases

## Key Files

- `google_form_bot.py`: Core class-based implementation for general Google Forms
- `google_form.py`: Specialized implementation for the Mannings consumer survey example

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/google-form-bot.git
cd google-form-bot
```

2. Install required dependencies:
```bash
pip install selenium webdriver-manager
```

3. Ensure you have Chrome browser installed on your system.

## Usage

### Basic Usage

```python
from google_form_bot import GoogleFormBot

# Replace with your target form URL
form_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"

# Create bot instance and start form submission
bot = GoogleFormBot(form_url)
bot.start()
```

### Batch Submissions

```python
# For multiple submissions
for i in range(10):
    print(f"Starting submission {i+1}/10")
    bot = GoogleFormBot(form_url)
    bot.start()
```

## Bot Implementations Tutorial

This project includes two different bot implementations to help you understand how to approach Google Form automation:

### 1. Function-Based Bot (`google_form.py`)

The `google_form.py` file demonstrates a function-based approach focused on a specific survey (Mannings consumer survey). This approach is ideal when:
- You need to handle a specific form with fixed structure
- You want to create highly correlated responses
- Complex answer logic depends on previous selections

Key aspects:
```python
# Helper functions to locate different question types
def find_question_elements(driver, question_index):
    # Finds a specific question by its index
    
def find_radio_options(question_element):
    # Locates radio button options within a question element
    
def find_checkbox_options(question_element):
    # Finds checkbox options for a question
```

Main function structure:
```python
def fill_mannings_survey():
    # Initialize driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open form
    driver.get("https://forms.gle/pokY573SrLfa5XLR7")
    
    # Cache all questions
    all_questions = get_all_questions()
    
    # Question-by-question logic with weighted randomization
    # Q1: Age group
    # Q2: Online purchase frequency
    # etc.
    
    # Submission
    submit_button.click()
```

**How to adapt**:
1. Replace the form URL with your target form
2. Modify the question-finding functions to match your form's structure
3. Update the weights and choices for each question
4. Add or remove questions based on your form's content
5. Customize the correlation logic between answers

### 2. Class-Based Bot (`google_form_bot.py`)

The `google_form_bot.py` file implements a more flexible, object-oriented approach suitable for adapting to different forms. This is recommended when:
- You need to automate multiple different forms
- You want a reusable framework
- You prefer a more structured, maintainable codebase

Key components:
```python
class GoogleFormBot:
    def __init__(self, form_url):
        self.form_url = form_url
        self.driver = self.setup_driver()
    
    def setup_driver(self):
        # Configure and return the WebDriver
    
    def start(self):
        # Main entry point that begins the form-filling process
        
    def fill_page_1(self):
        # Page-specific form filling logic
        
    # Methods for different input types
    def select_radio_option(self, option_text):
        # Select a radio button by text
        
    def select_checkbox_option(self, option_text):
        # Select a checkbox by text
        
    def select_linear_scale_by_id(self, scale_id, value):
        # Select a value on a linear scale
```

**How to adapt**:
1. Create a subclass of `GoogleFormBot` for your specific form
2. Override the `fill_page_X` methods with your form's structure
3. Add custom methods for special question types if needed
4. Implement form-specific logic in your page methods
5. For complex forms, use JavaScript execution for reliable element selection:
```python
js_result = self.driver.execute_script("""
    // Find elements and interact with them directly
    var elements = document.querySelectorAll('span, div, label');
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].textContent.includes('Option Text')) {
            elements[i].click();
            return true;
        }
    }
    return false;
""")
```

## Creating Human-like Responses

The key techniques used in this project to create more natural responses:

1. **Weighted randomization**: Instead of uniform random selection, options are weighted based on realistic distributions
   ```python
   # Example from google_form.py
   age_weights = [0.05, 0.25, 0.25, 0.25, 0.10, 0.05, 0.05]
   age_choice = random.choices(age_options, weights=age_weights, k=1)[0]
   ```

2. **Response correlation**: Answers to later questions depend on previous answers
   ```python
   # Example: Only answer app satisfaction if user responded they used the app
   if user_choices.get('used_app', False):
       # Answer satisfaction questions
   ```

3. **Varied text inputs**: For free-text fields, using a diverse pool of realistic answers
   ```python
   meaningful_suggestions = [
       "App could be faster.",
       "More promotions needed.",
       # ... more varied responses
   ]
   ```

4. **Natural timing**: Adding small delays between actions to mimic human interaction patterns

## Adapting to Different Forms

To adapt this bot for your own Google Form:

1. Study the form structure using browser developer tools
2. Identify question types and their selectors
3. Customize the selection methods or create new page-specific methods
4. Adjust randomization weights to match expected response distributions
5. Test with headless=False to visually verify correct selection

### Key Selector Patterns

The bot uses these CSS/XPath patterns to identify form elements:

- Radio buttons: `div.nWQGrd.zwllIb` or `[role="radio"]`
- Checkboxes: `div.eBFwI` or `[role="checkbox"]`
- Text inputs: `textarea.KHxj8b` or `input[type="text"]`
- Linear scales: `[role="radiogroup"]`

## Troubleshooting

If the bot fails to interact with certain elements:

1. Run in non-headless mode by removing the `--headless` option
2. Add `time.sleep()` calls to debug timing issues
3. Check if the form structure has changed and update selectors
4. Try alternative selection methods (direct XPath, JavaScript execution)

## Ethical Considerations

This tool is intended for legitimate testing, research, and automation purposes only. Please use responsibly:

- Always obtain permission before submitting to forms you don't own
- Don't use for spam, manipulation of surveys, or circumventing rate limits
- Consider the impact on form owners' data quality and server resources


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 