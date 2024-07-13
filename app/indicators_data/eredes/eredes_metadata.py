import sys
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor
import csv
from typing import List, Dict

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the path of the 'irradiare-app' directory (two levels up from eredes_metadata.py)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Add the path to sys.path
sys.path.append(irradiare_app_path)

# Now you can import settings
import app.indicators_data.settings as s

def set_driver(url: str) -> webdriver.Edge:
    """
    Configure the Edge driver and navigate to the provided URL.

    Args:
    - url (str): The URL to navigate to.

    Returns:
    - webdriver.Edge: Initialized instance of the Edge WebDriver.
    """
    options = webdriver.EdgeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Edge(options=options, service=Service(EdgeChromiumDriverManager().install()))
    driver.get(url)
    logging.info(f"Opened URL: {driver.title}")
    return driver

def scroll_page(driver: webdriver.Edge) -> None:
    """
    Scroll the page to load all content.

    Args:
    - driver (webdriver.Edge): Instance of the WebDriver to control the browser.
    """
    body_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(5)
        new_body_height = driver.execute_script("return document.body.scrollHeight")
        if new_body_height == body_height:
            break
        body_height = new_body_height
    logging.info("Scrolling completed")

def get_metadata_items(driver: webdriver.Edge) -> List[Dict[str, str]]:
    """
    Extract all label-value pairs from the page.

    Args:
    - driver (webdriver.Edge): Instance of the WebDriver to control the browser.

    Returns:
    - list: List of dictionaries containing the title, description, and a dictionary of metadata.
    """
    metadata_list = []

    scroll_page(driver)

    try:
        main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main"))
        )
        logging.info("Main element located")

        ods_elements = main.find_elements(By.TAG_NAME, "ods-catalog-card")
        
        for ods in ods_elements:
            try:
                title_element = ods.find_element(By.CLASS_NAME, "ods-catalog-card__title")
                title_text = title_element.text.strip()

                # Skip entries that don't look like indicators
                if '[cms]' in title_text.lower() or title_text == '':
                    continue

                description_element = ods.find_element(By.CLASS_NAME, "ods-catalog-card__description")
                description_text = description_element.text.strip()

                # Find all label and value elements within the ods-catalog-card element
                label_elements = ods.find_elements(By.CLASS_NAME, "ods-catalog-card__metadata-item-label")
                value_elements = ods.find_elements(By.CLASS_NAME, "ods-catalog-card__metadata-item-value")

                # Collect all labels and values in a dictionary
                metadata_items = {}
                for label_element, value_element in zip(label_elements, value_elements):
                    label_text = label_element.text
                    value_text = value_element.text
                    metadata_items[label_text] = value_text

                # Extract src_code from the link
                link_element = ods.find_element(By.CSS_SELECTOR, "a.ods-catalog-card__title-link")
                href = link_element.get_attribute("href")
                src_code = href.split('/')[-2]  # Extract the part between the last two slashes

                # Append the collected data as a dictionary
                metadata_list.append({
                    'title': title_text,
                    'description': description_text,
                    'metadata': metadata_items,
                    'src_code': src_code
                })

            except Exception as e:
                logging.error(f"Error extracting metadata from card: {e}")

    except Exception as e:
        logging.error(f"Error accessing main element: {e}")

    return metadata_list

def save_metadata_to_csv(metadata_list: List[Dict[str, str]], save_folder: str, csv_filename: str) -> None:
    """
    Save the metadata list to a CSV file.

    Args:
    - metadata_list (list): List of dictionaries containing metadata.
    - save_folder (str): The folder where the CSV file will be saved.
    - csv_filename (str): The filename for the CSV file.
    """
    os.makedirs(save_folder, exist_ok=True)

    # Extract headers
    headers = ["title", "description", "src_code"] + sorted({k for d in metadata_list for k in d['metadata'].keys()})

    with open(os.path.join(save_folder, csv_filename), mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        
        writer.writeheader()
        
        for data in metadata_list:
            row = {**data['metadata'], "title": data['title'], "description": data['description'], "src_code": data['src_code']}
            writer.writerow(row)
            
    logging.info(f"CSV file saved as {csv_filename}")

def main() -> None:
    """
    Main entry point of the script.
    """
    driver = None
    try:
        driver = set_driver(s.eredes_url)
        indicators_metadata = get_metadata_items(driver=driver)
        save_metadata_to_csv(indicators_metadata, s.eredes_metadata, 'metadata.csv')
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        
    finally:
        if driver:
            driver.quit()  # Ensure WebDriver is closed at the end
            logging.info("WebDriver closed")

if __name__ == "__main__":
    main()

