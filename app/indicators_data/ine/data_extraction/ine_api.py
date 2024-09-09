import xml.etree.ElementTree as ET
import json
from requests.exceptions import JSONDecodeError
import time
import os
import sys
from typing import Dict, Any

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


def extract_catalog(host_url: str, lang: str) -> Dict[str, Any]:
    """
    Extract catalog data for indicators in XML format and return as JSON data.

    Args:
    - host_url (str): The host URL for the data source.
    - lang (str): The language code for the data.

    Returns:
    - Dict[str, Any]: A dictionary containing the catalog data in JSON format.
    """
    url = f"{host_url}/ine/xml_indic.jsp?opc=3&lang={lang}" # Create the custom download link for indicators catalog
    response = requests.get(url) # Make a request to get the catalog data
    root = ET.fromstring(response.content) # ElementTree module to parse the data put it in a ET element (root is the higher level)
    catalog_data = {} 
    indicators = [] 
# Create a JSON dict with the XML data
    for indicator in root.findall('.//indicator'): # Find all <indicator> elements in the tree
        indicator_data = {}
        for child in indicator:
            indicator_data[child.tag] = child.text # From all childs in each indicator tag=key, text=value in the dict.
        indicators.append(indicator_data) # Append each indicator data dict. in a list
    catalog_data["indicators"] = indicators # Create a dic including the list with indicators dicts.
    return catalog_data


def save_catalog(save_path: str, filename: str, catalog_data: Dict[str, Any]) -> None:
    """
    Save the extracted catalog data to a JSON file.

    Args:
    - save_path (str): Path where indicators catalog is saved.
    - catalog_data (Dict[str, Any]): The catalog data to save. JSON dict.
    """
    os.makedirs(save_path, exist_ok=True) # Create the folder if it doesn't exist
    with open(os.path.join(save_path, filename), "w", encoding="utf-8") as catalog_file:
        json.dump(catalog_data, catalog_file, indent=4, ensure_ascii=False) # Dump content avoiding ascii sequences
    print("Catalog of indicators saved in catalogo_indicadores.json")


def extract_data(host_url: str, varcd_cod: str, lang: str) -> Dict[str, Any]:
    """
    Extract data for a specific indicator.
    """
    url = f"{host_url}/ine/json_indicador/pindica.jsp?op=2&varcd={varcd_cod}&lang={lang}"
    response = requests.get(url)

    if response.status_code != 200:
        logging.error(f"Failed to fetch data for varcd {varcd_cod}. Status code: {response.status_code}")
        return None  # Return None if the response is not successful (i.e., not 200)

    try:
        return response.json()
    except JSONDecodeError as e:
        logging.error(f"Failed to decode JSON for varcd {varcd_cod}: {e}")
        logging.error(f"Response content: {response.text}")
        return None


def extract_metadata(host_url:str, varcd_cod: str, lang: str) -> Dict[str, Any]:
    """
    Extract metadata for a specific indicator.

    Args:
    - host_url (str): The host URL for the data source.
    - varcd_cod (str): The variable code for the indicator.
    - lang (str): The language code for the metadata.

    Returns:
    - Dict[str, Any]: The extracted metadata.
    """
    url = f"{host_url}/ine/json_indicador/pindicaMeta.jsp?varcd={varcd_cod}&lang={lang}" # Complete custom url
    response = requests.get(url)
    return response.json()


def get_save_data(save_path: str, catalog_data: Dict[str, Any], lang: str) -> None:
    """
    Use the function 'extract_data' and save the data for each indicator in the catalog

    Args:
    - catalog_data (Dict[str, Any]): The catalog data containing indicators.
    - lang (str): The language code for the data.
    """
    # Ensure the directory exists
    os.makedirs(save_path, exist_ok=True)
    for indicator in catalog_data["indicators"]:
        varcd_cod = indicator["varcd"]
        data_path = os.path.join(save_path, f"data_{varcd_cod}.json")

        if os.path.exists(data_path):
            logging.info(f"Indicator {varcd_cod} files already exist. Skipping...")
            continue  # Skip to the next indicator if the file already exists

        data = extract_data(s.ine_url, varcd_cod, lang)
        if not data:  # Ensure data was successfully extracted
            logging.warning(f"No data found for indicator {varcd_cod}. Skipping...")
            continue

        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(data, data_file, indent=4, ensure_ascii=False)
        logging.info(f"Data from indicator {varcd_cod} saved in {data_path}")

        time.sleep(1)  # Adding a delay to prevent API rate limits


def get_save_metadata(save_path: str, catalog_data: Dict[str, Any], lang: str) -> None:
    """
    Use the function 'extract_metadata' and save the data for each indicator in the catalog

    Args:
    - catalog_data (Dict[str, Any]): The catalog data containing indicators.
    - lang (str): The language code for the metadata.
    """

    os.makedirs(save_path, exist_ok=True) # Create the folder if it doesn't exist
    for indicator in catalog_data["indicators"]:
        varcd_cod = indicator["varcd"]
        metadata_path = os.path.join(save_path, f"metadata_{varcd_cod}.json") # Create a custom path to store data for each indicator

        if os.path.exists(metadata_path):
            print(f"Indicator {varcd_cod} files already exists. Skipping...")
            continue

        metadata = extract_metadata(s.ine_url, varcd_cod, lang) # Extract data for each indicator

        with open(metadata_path, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=4, ensure_ascii=False) # Store the metadata in the custom indicator's data path
        print(f"Metadata from indicator {varcd_cod} saved in {metadata_path}")

        time.sleep(1)

def main():
    """
    Main entry point of the script.
    """
    # Indicate language: PT or EN
    lang = "PT"
    catalog_data = extract_catalog(host_url=s.ine_url, lang=lang)
    save_catalog(save_path=s.ine_catalog_path, filename=s.ine_catalog_filename, catalog_data=catalog_data)
    get_save_data(save_path=s.ine_data_path, catalog_data=catalog_data, lang=lang)
    get_save_metadata(save_path=s.ine_metadata_path, catalog_data=catalog_data, lang=lang)


if __name__ == "__main__":
    main()




