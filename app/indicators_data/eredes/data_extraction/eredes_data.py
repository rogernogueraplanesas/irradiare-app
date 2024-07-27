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

"""
Logging is used to check the events flux in this script.
Firstly, its basic configuration is set.
    - The minimum logging severity level set is INFO, including WARNING, ERROR, CRITICAL (lower levels).
    - The format of the log messages is: timestamp - severity level - log message
"""

# Get the path of the root directory (irradiare-app)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

"""
In order to import the settings module from the utils folder, it is needed to calculate the abolute path of the project's root.
    - 'os.path.dirname(__file__)' gets the absolute path to the folder containing the current file (not included)
    - 'os.path.join()' allows the combination of path components into a single one.
    - Combining the absolute path with each '..' component, moves up one level in the directory hierachy.
    - It is needed to use 'os.path.abspath' to return the absolute path to the new directory set.
"""

# Add the path to sys.path
sys.path.append(irradiare_app_path)

"""
The previous abolute path is added to the system path 'sys.path'.
'sys.path' collects the paths to the directories where Python searches for modules by means of 'import' statements.
As the root of the project is now in the 'sys.path', it is possible to import the 'settings' script from the 'utils' folder.
"""

# Import settings
import app.utils.settings as s

def set_driver(url: str) -> webdriver.Edge:
    """
    Set an Edge driver with an specific configuration

    Args:
    - url (str): The URL to navigate to.

    Returns:
    - webdriver.Edge: Initialized instance of the Edge WebDriver.
    """
    options = webdriver.EdgeOptions()
    options.add_experimental_option("detach", True) # Avoids the driver to automatically close after ending the session
    driver = webdriver.Edge(options=options, service=Service(EdgeChromiumDriverManager().install())) # The driver is installed in the first execution
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

def get_urls(driver: webdriver.Edge) -> list:
    """
    Find the 'export page' URL for each indicator's card present in the fully loaded main page.

    Args:
    - driver (webdriver.Edge): Instance of the WebDriver to control the browser.

    Returns:
    - list: A list of strings where each string is an URL redirecting to the 'export' page of each indicator.
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
    Extracts CSV export links from the export page of each indicator and appends them to the provided 'final_urls' list.

    Args:
        url (str): The URL of the export page where the CSV export links are located.
        final_urls (list): A list to which the extracted CSV export URLs will be appended.
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
    Download the CSV data file by means of the CSV export URL for each indicator with a max. of 3 possible tried.
    The downloaded CSV file is saved into a new save_folder.

    Args:
    - url (str): CSV data file download URL.
    - save_folder (str): Folder where the downloaded CSV data files are saved.
    - retries  (int): Maximum amount of download retries allowed.
    
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
    Using the 'download_csv_file' function, downloads multiple CSV files in parallel from the specified URLs and saves them to a designated folder.

        - A pool of 4 workers to complete a task is created by means of ThreadPoolExecutor.
        - Tasks are send to the pool by means of 'executor.submit()' indicating the action to execute ad the parameters.
        - Once the tasks are submited, the execution starts with a max. amount of workers at the same time.
        - With the tasks in process, the lib. 'tqdm' is used to check the status of the downloads (the task for this case).
        - 'as_completed()' returns a completed task as an object.
        - Once this object is returned (with no specific order other than the completion time), it is possible to check the result.
        - If the download was successful, the task id officially completed and a new task is processed by the pool (if possible).
        - Any exception is catched and showed.

    Args:
        urls (list): A list of strings, where each string is a URL pointing to a CSV file to be downloaded.
        save_folder (str): The path to the folder where the downloaded CSV files will be saved.
        max_workers (int, optional): The maximum number of threads to use for downloading files concurrently. Defaults to 4.
    """
    os.makedirs(save_folder, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor: # Creates a pool of 4 workers to execute parallel tasks
        futures = [executor.submit(download_csv_file, url, save_folder) for url in urls] # Set the action 'download_csv_file' and the parameters for the action to be executed by the pool of workers
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading CSV files"): # The tqdm library adds very basic download information such a progress bar, download speed, etc.
            try:                                                                                     # as_completed(futures) iterates over the 'future' objects while tasks are completed
                future.result()
            except Exception as e:
                logging.error(f"Error: {e}")

def main() -> None:
    """
    Main entry point of the script. This function performs the following tasks:
    1. Sets up the driver
    2. Scraps and gets the 'export page' URL for each indicator
    3. Gets the CSV data file specific download link for each indicator
    4. Downloads the CSV files in parallel and saves them in a specific folder
    """

    print("This process may take about 1 to 2 hours to complete, depending on your computer.")
    driver = set_driver(s.eredes_url)
    indicators_url = get_urls(driver)
    final_urls = [] # The list with CSV download URLs must be outside the loop to accumulate all URLs across iterations. Otherwise, it would be reset each time.
    for url in indicators_url:
        get_datasets_url(url, final_urls)
        logging.info(f"Collected URLs: {final_urls}")
    download_csv_files_parallel(final_urls, s.eredes_files_folder)
    print("PROCESS COMPLETED. DATA EXTRACTED.")


if __name__ == "__main__":
    main()
