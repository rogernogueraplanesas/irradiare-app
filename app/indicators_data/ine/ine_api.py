import app.utils.settings as s
import requests
import xml.etree.ElementTree as ET
import json
import time
import os
from typing import Dict, Any


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

    Args:
    - host_url (str): The host URL for the data source.
    - varcd_cod (str): The variable code for the indicator.
    - lang (str): The language code for the data.

    Returns:
    - Dict[str, Any]: The extracted data.
    """
    url = f"{host_url}/ine/json_indicador/pindica.jsp?op=2&varcd={varcd_cod}&lang={lang}" # Complete custom url
    response = requests.get(url)
    return response.json()


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
        data_path = os.path.join(save_path, f"data_{varcd_cod}.json") # Create a custom path to store data for each indicator

        if os.path.exists(data_path):
            print(f"Indicator {varcd_cod} files already exists. Skipping...")
            continue

        data = extract_data(s.ine_url, varcd_cod, lang) # Extract data for each indicator

        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(data, data_file, indent=4, ensure_ascii=False) # Store the data in the custom indicator's data path
        print(f"Data from indicator {varcd_cod} saved in {data_path}")

        time.sleep(1)


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




