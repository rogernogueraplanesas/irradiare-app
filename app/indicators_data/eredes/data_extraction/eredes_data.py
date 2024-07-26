from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import sys
import os
import time

import requests
import logging


# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the path of the root directory (irradiare-app)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Add the path to sys.path
sys.path.append(irradiare_app_path)

# Import settings
import app.utils.settings as s

def set_driver(url: str) -> webdriver.Edge:
    options = webdriver.EdgeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Edge(options=options, service=Service(EdgeChromiumDriverManager().install()))
    driver.get(url)
    logging.info(f"Opened URL: {driver.title}")
    return driver

def scroll_page(driver: webdriver.Edge) -> None:
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
    os.makedirs(save_folder, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_csv_file, url, save_folder) for url in urls]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading CSV files"): # The tqdm library adds very basic download information such a progress bar, download speed, etc.
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error: {e}")

def main():
    print("This process may take about 1 to 2 hours to complete, depending on your computer.")
    driver = set_driver(s.eredes_url)
    indicators_url = get_urls(driver)
    final_urls = []
    for url in indicators_url:
        get_datasets_url(url, final_urls)
        logging.info(f"Collected URLs: {final_urls}")
    download_csv_files_parallel(final_urls, s.eredes_files_folder)
    print("PROCESS COMPLETED. DATA EXTRACTED.")

if __name__ == "__main__":
    main()
