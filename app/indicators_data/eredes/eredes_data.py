import sys
import os

# Obtiene la ruta del directorio 'irradiare-app' (dos niveles hacia arriba desde eredes_metadata.py)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Añade la ruta al sys.path
sys.path.append(irradiare_app_path)

# Ahora puedes importar settings
import app.indicators_data.settings as s
import time
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def set_driver(url: str) -> webdriver.Edge:
    """
    Set up the Edge driver and navigate to the given URL.

    Args:
    - url (str): The URL to navigate to.

    Returns:
    - webdriver.Edge: Initialized Edge WebDriver instance.
    """
    options = webdriver.EdgeOptions() # Enables webdriver settings configuration
    options.add_experimental_option("detach", True) # Webdriver not closed after its session
    driver = webdriver.Edge(options=options, service=Service(EdgeChromiumDriverManager().install())) # Driver instance created with previous settings (1st execution -> Edge driver installed)
    driver.get(url) # Driver loads url
    print(driver.title) # URL title
    return driver

def scroll_page(driver: webdriver.Edge) -> None:
    """
    Scroll the page to load all content.

    Args:
    - driver (webdriver.Edge): The WebDriver instance for controlling the browser.
    """
    body_height = driver.execute_script("return document.body.scrollHeight") # Starting site height
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') # Scroll until the end of the page
        time.sleep(5)  # Pause 5 sec. to allow content to load
        new_body_height = driver.execute_script("return document.body.scrollHeight") # Get new (extended) height
        if new_body_height == body_height: # Compare to the previous height
            break # If there is no scroll, breakes
        body_height = new_body_height # If there was a scroll, the new height is set as the old one
    print("Scrolling completed")

def get_urls(driver: webdriver.Edge) -> list:
    """
    Get the list of URLs redirecting to indicators subpages from the main page.

    Args:
    - driver (webdriver.Edge): The WebDriver instance for controlling the browser.

    Returns:
    - list: List of subpages URLs found on the page.
    """
    filtered_urls = [] # Create an empty list
    scroll_page(driver) # Load the whole page executing the previous function
    try:
        main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main")) # Create an element instance containing the information from the element with an ID = "main"
        )
        print(main.text)
        ods = main.find_elements(By.TAG_NAME, "ods-catalog-card") # Find all "ods-catalog-card" (tag name) from the element 'main'
        for element in ods:
            datasets_list = element.find_elements(By.CLASS_NAME, "ods-catalog-card__visualization") # Find all the elements with a class name "ods-catalog-card__visualization"
            for dataset in datasets_list:
                href = dataset.get_attribute("href") # Get all the links from the elements stored in the previous list
                if href.endswith("/export/"):
                    filtered_urls.append(href) # Filter the links and store only the ones containing /export/
    finally:
        driver.quit() # Close the driver
    return filtered_urls

def get_datasets_url(url: str, final_urls: list) -> None:
    """
    Get the new URLs from the export page.

    Args:
    - url (str): The URL of each indicator subpage.
    - final_urls (list): List to store all the dataset export URLs.
    """
    driver = set_driver(url) # Set a new driver (as there is no active driver)
    try:
        export_page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main")) # Create an element instance containing the information from the element with an ID = "main"
        )
        print(export_page.text)
        new_url_elements = export_page.find_elements(By.CLASS_NAME, "ods-dataset-export-link__link") # From the main element, get the subelements containing info for the download links
        new_urls = [element.get_attribute("href") for element in new_url_elements if "/csv" in element.get_attribute("href")] # Get the /csv link (export link) searchin in each subelement
        final_urls.extend(new_urls) # Store the 'export' links
    finally:
        driver.quit()

def download_csv_files(urls: list, save_folder: str) -> None:
    """
    Download the CSV files from the given URLs.

    Args:
    - urls (list): List of URLs to download CSV files from.
    - save_folder (str): Path to the directory where CSV files will be saved.
    """
    os.makedirs(save_folder, exist_ok=True) # Create a folder providing a name (save_folder), if it already exists it won't throw an error
    for url in urls:
        try:
            response = requests.get(url) # Make a request for each url in the 'export' urls list
            response.raise_for_status() # Give back the status of the response
            file_name = url.split("/")[-3] + ".csv"  # Create filenames based of the url 'requested'
            with open(os.path.join(save_folder, file_name), "wb") as file: # wb -> write binary
                file.write(response.content) # The csv file will get the whole response content without losing information
            print(f"CSV file downloaded: {file_name}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

def main():
    """
    Main entry point of the script.
    """
    driver = set_driver(s.eredes_url)
    indicators_url = get_urls(driver)
    final_urls = []
    for url in indicators_url:
        get_datasets_url(url, final_urls)
        print(final_urls)
    download_csv_files(final_urls, s.eredes_files_folder)


if __name__ == "__main__":
    main()