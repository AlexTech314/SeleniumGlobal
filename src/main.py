import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Import ChromeOptions as Options
from tempfile import mkdtemp

def handler(event, context):
    driver = initialise_driver()
    
    # Open the webpage
    driver.get("https://search.dca.ca.gov/")

    # Locate and select "License Type" dropdown
    license_type_select = Select(driver.find_element(By.ID, 'licenseType'))
    license_type_select.select_by_visible_text('Psychologist')

    # Fill in the First Name
    first_name_input = driver.find_element(By.ID, 'firstName')
    first_name_input.send_keys('Susan')

    # Fill in the Last Name
    last_name_input = driver.find_element(By.ID, 'lastName')
    last_name_input.send_keys('Lok')

    # Optionally: Click the Search button
    search_button = driver.find_element(By.XPATH, '//input[@value="SEARCH"]')
    search_button.click()

    # Extract the results
    results = driver.find_elements(By.CLASS_NAME, 'post.yes')

    # Loop through each result and extract the key data
    res_body = []
    for result in results:
        # Get the name
        name = result.find_element(By.XPATH, './/strong').text

        # Get license number (it's usually a link so we extract the link text)
        license_number = result.find_element(By.XPATH, './/a').text

        # Get the other details
        details = result.text.split("\n")  # Split the result into individual lines
        
        for detail in details:
            res_body.append(detail)
    
    return {
        'statusCode': 200,
        'body': json.dumps(res_body)
    }

def initialise_driver():
    # Initialize ChromeOptions as Options
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

    return driver
