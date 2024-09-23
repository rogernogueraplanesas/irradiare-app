import os
import xml.etree.ElementTree as ET
import csv
import requests
from typing import Dict, List, Optional

import sys
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

import app.utils.settings as s


def download_toc(url: str, save_path: str) -> None:
    """
    Download the TOC (Table of Contents) for the Eurostat database through a given URL and save it to a specified directory.

    Args:
        url (str): The URL to download the file from.
        save_path (str): The path where the downloaded file will be saved.

    Returns:
        None
    """
    try:
        # Send a HTTP GET request to the URL
        response = requests.get(url)
        # Raise an error if the request was unsuccessful
        response.raise_for_status()
        
        # Write the content of the response to a file
        with open(save_path, 'wb') as file:
            print("Correct saving path. Download in progress...")
            file.write(response.content)
        
        print(f"File downloaded successfully and saved to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the file: {e}")

def get_data_names(path: str, output_file: str) -> None:
    """
    Write the names of JSON files in a directory to a text file.

    Args:
        path (str): The directory containing JSON files.
        output_file (str): The file where the names of the JSON files will be saved.

    Returns:
        None
    """
    with open(output_file, 'w') as f:
        for archivo in os.listdir(path):
            if archivo.endswith('.json'):
                f.write(os.path.splitext(archivo)[0] + '\n')
    print(f"Filenames CSV saved in: {output_file}")

def find_link(code: str, file_xml: str) -> Optional[str]:
    """
    Find the metadata link for a given code in an XML file.

    Args:
        codigo (str): The code to search for in the XML.
        archivo_xml (str): The XML file to search in.

    Returns:
        Optional[str]: The metadata link if found, otherwise None.
    """
    tree = ET.parse(file_xml)
    root = tree.getroot()
    # Namespace of the XML file
    ns = {'nt': 'urn:eu.europa.ec.eurostat.navtree'}

    for leaf in root.findall(".//nt:leaf", ns):
        code_element = leaf.find("nt:code", ns)
        if code_element is not None and code_element.text == code:
            metadata_element = leaf.find("nt:metadata[@format='html']", ns)
            if metadata_element is not None:
                print(f"Found {metadata_element.text} for {code}")
                return metadata_element.text
    return None

def fill_metadata_list(names_json: List[str], file_xml: str, metadata_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Fill the metadata dictionary with links found in an XML file.

    Args:
        names_json (List[str]): The list of JSON file names to search for.
        file_xml (str): The XML file to search in.
        metadata_dict (Dict[str, str]): The dictionary to fill with metadata links.

    Returns:
        Dict[str, str]: The updated metadata dictionary.
    """
    # Fill the dictionary with the metadata links
    for name in names_json:
        link = find_link(name, file_xml)
        if link:
            metadata_dict[name] = link
    return metadata_dict

def merge_datacode_metadata_link(csv_file: str, metadata_dict: Dict[str, str], updated_csv_file: str) -> None:
    """
    Merge metadata links into an existing CSV file based on a metadata dictionary.

    Args:
        csv_file (str): The CSV file to read and update.
        metadata_dict (Dict[str, str]): The dictionary of metadata links.
        updated_csv_file (str): The path to the updated CSV file.

    Returns:
        None
    """
    with open(csv_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    for row in rows:
        codigo = row[0]
        row.append(metadata_dict.get(codigo, ''))

    with open(updated_csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

    print("CSV updated with metadata links.")

def main() -> None:
    """
    Main function to execute the workflow of downloading TOC, extracting JSON file names,
    filling metadata links, and merging them into a CSV file.

    This function performs the following tasks:
    1. Downloads the TOC (Table of Contents) XML file.
    2. Extracts JSON file names and saves them to a CSV file.
    3. Fills a metadata dictionary with links from the XML file.
    4. Merges the metadata links into the CSV file.

    Args:
        None

    Returns:
        None
    """
    download_toc(url=s.eurostat_toc_url_xml, save_path=s.eurostat_toc_xml)
    get_data_names(path=s.eurostat_raw_data, output_file=s.eurostat_datacodes)
    
    # Get JSON filenames without extension
    nombres_json = [f.split('.')[0] for f in os.listdir(s.eurostat_raw_data) if f.endswith('.json')]
    
    # Create a dict to save metadata links
    metadata_links: Dict[str, str] = {}
    
    # Fill the dict
    metadata_dict = fill_metadata_list(nombres_json=nombres_json, archivo_xml=s.eurostat_toc_xml, metadata_dict=metadata_links)
    
    # Update the CSV with the metadata dict info
    merge_datacode_metadata_link(archivo_csv=s.eurostat_datacodes, metadata_dict=metadata_dict, archivo_csv_actualizado=s.eurostat_datacodes)

if __name__ == "__main__":
    main()