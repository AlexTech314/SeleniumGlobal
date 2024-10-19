import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from tempfile import mkdtemp
from bs4 import BeautifulSoup

import random
import requests

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
        if not all([state, license_number, first_name, last_name]):
            logger.error("Missing one or more required fields.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields in the body.'})
            }
            
        if license_type is None:
            logger.error("Missing one or more required fields.")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields in the body.'})
            }
            
        max_retries = 3  # Maximum number of retries
        attempt = 0

        while attempt < max_retries:
            driver = initialise_driver()
            try:
                # Increment attempt counter
                attempt += 1
                logger.debug(f"Attempt {attempt} of {max_retries}")

                # Open the webpage
                driver.get("https://search.dca.ca.gov/")
                logger.debug("Opened URL: https://search.dca.ca.gov/")

                # Wait for the licenseType element
                license_type_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'licenseType'))
                )
                license_type_select = Select(license_type_element)
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

                # Fill in the License Number
                license_number_input = driver.find_element(By.ID, 'licenseNumber')
                license_number_input.send_keys(license_number)
                logger.debug(f"Entered '{license_number}' into License Number input.")

                # Fill in the First Name
                first_name_input = driver.find_element(By.ID, 'firstName')
                first_name_input.send_keys(first_name)
                logger.debug(f"Entered '{first_name}' into First Name input.")

                # Fill in the Last Name
                last_name_input = driver.find_element(By.ID, 'lastName')
                last_name_input.send_keys(last_name)
                logger.debug(f"Entered '{last_name}' into Last Name input.")

                # Click the Search button
                search_button = driver.find_element(By.XPATH, '//input[@value="SEARCH"]')
                search_button.click()
                logger.debug("Search button clicked.")

                # Wait for the results to be present
                results = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.post.yes'))
                )
                logger.debug("Results located: %d results found.", len(results))
                
                if len(results) == 0:
                    logger.debug("No results found.")
                    return {
                        'statusCode': 404,
                        'body': json.dumps({
                            'message': 'No results found for the provided information.'
                        })
                    }
                
                # Wait until the text 'LICENSE NUMBER' is present in the first result
                WebDriverWait(driver, 10).until(
                    EC.text_to_be_present_in_element(
                        (By.CSS_SELECTOR, '.post.yes'),
                        'LICENSE NUMBER'
                    )
                )

                # Now proceed to extract details
                details = results[0].text.split("\n")
                extracted_info = extract_details(details)

                logger.debug("Extracted information: %s", extracted_info)

                return {
                    'statusCode': 200,
                    'body': json.dumps(extracted_info)
                }
            except TimeoutException:
                logger.debug("TimeoutException occurred.")
                # Optionally, you can add a short delay before retrying
                # time.sleep(2)
                continue  # Retry the operation
            except Exception as e:
                logger.exception("An error occurred: %s", str(e))
                return {
                    'statusCode': 500,
                    'body': json.dumps({'Server error': str(e)})
                }
            finally:
                if driver:
                    driver.quit()
                    logger.debug("Webdriver closed.")
        
        # If we reach here, all retries have failed
        return {
            'statusCode': 500,
            'body': json.dumps({'Server error': 'All retries failed due to TimeoutException.'})
        }
        
    except Exception as e:
        logger.exception("Error in handler: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'Server error': str(e)})
        }

def initialise_driver():
    logger.debug("Initializing webdriver.")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"user-agent={fetch_user_agent()}")
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
        chrome_options.add_argument("--window-size=2560x1440")
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

def fetch_user_agent():
    url = "https://www.useragentlist.net/"
    request = requests.get(url)
    user_agents = []
    soup = BeautifulSoup(request.text, "html.parser")
    for user_agent in soup.select("pre.wp-block-code"):
        user_agents.append(user_agent.text)

    user_agent = random.choice(user_agents)
    print(f'Using user-agent: {user_agent}')
    return user_agent
