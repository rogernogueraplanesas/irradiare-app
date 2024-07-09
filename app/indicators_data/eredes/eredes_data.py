import sys
import os
import time
import requests
import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor

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
    Set up the Edge driver and navigate to the given URL.

    Args:
    - url (str): The URL to navigate to.

    Returns:
    - webdriver.Edge: Initialized Edge WebDriver instance.
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
    - driver (webdriver.Edge): The WebDriver instance for controlling the browser.
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

def get_urls(driver: webdriver.Edge) -> list:
    """
    Get the list of URLs redirecting to indicators subpages from the main page.

    Args:
    - driver (webdriver.Edge): The WebDriver instance for controlling the browser.

    Returns:
    - list: List of subpages URLs found on the page.
    """
    filtered_urls = []
    scroll_page(driver)
    try:
        main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main"))
        )
        logging.info("Main element located")
        ods = main.find_elements(By.TAG_NAME, "ods-catalog-card")
        for element in ods:
            datasets_list = element.find_elements(By.CLASS_NAME, "ods-catalog-card__visualization")
            for dataset in datasets_list:
                href = dataset.get_attribute("href")
                if href.endswith("/export/"):
                    filtered_urls.append(href)
    finally:
        driver.quit()
    return filtered_urls

def get_datasets_url(url: str, final_urls: list) -> None:
    """
    Get the new URLs from the export page.

    Args:
    - url (str): The URL of each indicator subpage.
    - final_urls (list): List to store all the dataset export URLs.
    """
    driver = set_driver(url)
    try:
        export_page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main"))
        )
        logging.info("Export page element located")
        new_url_elements = export_page.find_elements(By.CLASS_NAME, "ods-dataset-export-link__link")
        new_urls = [element.get_attribute("href") for element in new_url_elements if "/csv" in element.get_attribute("href")]
        final_urls.extend(new_urls)
    finally:
        driver.quit()

def download_csv_file(url: str, save_folder: str, retries: int = 3) -> None:
    """
    Download a CSV file from the given URL, with retries on failure.

    Args:
    - url (str): The URL to download the CSV file from.
    - save_folder (str): Path to the directory where CSV files will be saved.
    - retries (int): Number of retries in case of download failure.
    """
    for attempt in range(retries):
        try:
            logging.info(f"Starting download for {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            file_name = url.split("/")[-3] + ".csv"
            with open(os.path.join(save_folder, file_name), "wb") as file:
                file.write(response.content)
            logging.info(f"CSV file downloaded: {file_name}")
            break
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {url}: {e}, attempt {attempt + 1} of {retries}")
            if attempt + 1 == retries:
                logging.error(f"Failed to download {url} after {retries} attempts.")
            else:
                time.sleep(5)

def download_csv_files_parallel(urls: list, save_folder: str, max_workers: int = 4) -> None:
    """
    Download multiple CSV files in parallel.

    Args:
    - urls (list): List of URLs to download CSV files from.
    - save_folder (str): Path to the directory where CSV files will be saved.
    - max_workers (int): Maximum number of threads to use for parallel downloads.
    """
    os.makedirs(save_folder, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_csv_file, url, save_folder) for url in urls]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error: {e}")

def main():
    """
    Main entry point of the script.
    """
    driver = set_driver(s.eredes_url)
    indicators_url = get_urls(driver)
    final_urls = []
    for url in indicators_url:
        get_datasets_url(url, final_urls)
        logging.info(f"Collected URLs: {final_urls}")
    download_csv_files_parallel(final_urls, s.eredes_files_folder)

if __name__ == "__main__":
    main()