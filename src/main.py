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
        
        try:
            license_type_select.select_by_visible_text(license_type)
            logger.debug(f"Selected '{license_type}' from License Type dropdown.")
        except Exception as e:
            logger.debug(f'Exception while selecting from License Type dropdown: {str(e)} \n Returning available options.')
            
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'License Type is invalid. Please select from the provided License Type options.',
                    'license_type_options': [option.text for option in license_type_select.options]
                })
            }

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
        
        # Extract the results
        details = results[0].text.split("\n")
        extracted_info = extract_details(details)
        
        driver.quit()
        logger.debug("Webdriver closed.")

        return {
            'statusCode': 200,
            'body': json.dumps(extracted_info)
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
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-path=/tmp")
        chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

        service = Service(
            executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
            service_log_path="/tmp/chromedriver.log"
        )

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        logger.debug("Webdriver initialized.")
        return driver

    except Exception as e:
        logger.exception("Error initializing webdriver: %s", str(e))
        raise
    
def extract_details(details):
    # Dictionary to hold the extracted information
    extracted_info = {}

    # Extract the name (always the first item in the list)
    extracted_info['name'] = details[0]

    # Loop through each string in details starting from the second item
    for line in details[1:]:
        if "LICENSE NUMBER" in line and "LICENSE TYPE" in line:
            # Extract license number and type
            parts = line.split(" LICENSE TYPE: ")
            license_number = parts[0].split("LICENSE NUMBER: ")[1]
            license_type = parts[1]
            extracted_info['license_number'] = license_number
            extracted_info['license_type'] = license_type

        elif "LICENSE STATUS" in line:
            # Extract license status
            license_status = line.split("LICENSE STATUS: ")[1]
            extracted_info['license_status'] = license_status

        elif "EXPIRATION DATE" in line:
            # Extract expiration date
            expiration_date = line.split("EXPIRATION DATE: ")[1]
            extracted_info['expiration_date'] = expiration_date

    return extracted_info
