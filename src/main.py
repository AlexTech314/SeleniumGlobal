import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from tempfile import mkdtemp

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def handler(event, context):
    logger.debug("Handler invoked. Event: %s", json.dumps(event))
    
    try:
        # Parse the incoming event body
        body = json.loads(event.get('body', '{}'))
        state = body.get('state')
        license_type = body.get('licenseType')
        license_number = body.get('licenseNumber')
        first_name = body.get('firstName')
        last_name = body.get('lastName')

        # Check if all required fields are present
        if not all([state, license_type, license_number, first_name, last_name]):
            logger.error("Missing one or more required fields.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields in the body.'})
            }

        driver = initialise_driver()
        logger.debug("Webdriver initialized successfully.")

        # Open the webpage
        driver.get("https://search.dca.ca.gov/")
        logger.debug("Opened URL: https://search.dca.ca.gov/")

        # Locate and select "License Type" dropdown
        license_type_select = Select(driver.find_element(By.ID, 'licenseType'))
        logger.debug("License Type dropdown located.")
        license_type_select.select_by_visible_text(license_type)
        logger.debug(f"Selected '{license_type}' from License Type dropdown.")

        # Fill in the First Name
        first_name_input = driver.find_element(By.ID, 'firstName')
        logger.debug("First Name input field located.")
        first_name_input.send_keys(first_name)
        logger.debug(f"Entered '{first_name}' into First Name input.")

        # Fill in the Last Name
        last_name_input = driver.find_element(By.ID, 'lastName')
        logger.debug("Last Name input field located.")
        last_name_input.send_keys(last_name)
        logger.debug(f"Entered '{last_name}' into Last Name input.")

        # Click the Search button
        search_button = driver.find_element(By.XPATH, '//input[@value="SEARCH"]')
        logger.debug("Search button located.")
        search_button.click()
        logger.debug("Search button clicked.")

        # Extract the resultsx
        results = driver.find_elements(By.CLASS_NAME, 'post.yes')
        logger.debug("Results located: %d results found.", len(results))

        # Loop through each result and extract the key data
        res_body = []
        for index, result in enumerate(results):
            try:
                name = result.find_element(By.XPATH, './/strong').text
                license_number_result = result.find_element(By.XPATH, './/a').text
                details = result.text.split("\n")
                
                res_body.append({
                    "name": name,
                    "license_number_result": license_number_result,
                    "details": details
                })
                logger.debug("Extracted result #%d: %s", index + 1, result)
            except Exception as e:
                logger.exception("Error extracting data from result #%d: %s", index + 1, str(e))
        
        driver.quit()
        logger.debug("Webdriver closed.")

        return {
            'statusCode': 200,
            'body': json.dumps(res_body)
        }

    except Exception as e:
        logger.exception("Error in handler: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def initialise_driver():
    logger.debug("Initializing webdriver.")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--window-size=2560x1440")  # Set a default window size
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

        driver = webdriver.Chrome(options=chrome_options)
        logger.debug("Webdriver initialized.")
        return driver

    except Exception as e:
        logger.exception("Error initializing webdriver: %s", str(e))
        raise
