import os
import re
import time
import requests
import zipfile
import csv
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

import logging
import sys

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

def read_metadata_links_from_csv(csv_file: str) -> List[str]:
    """
    Read and save a list of metadata download links with no repeated elements.

    Args:
        csv_file (str): CSV file path

    Returns:
        List[str]: List of unique metadata download links
    """
    links = set()  # Utilizar un set para almacenar enlaces únicos
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar la fila del encabezado
        for row in reader:
            if len(row) > 1:
                links.add(row[1])  # Añadir el segundo elemento (enlace de metadatos) al set
            else:
                # Log or handle the case where there's no link
                print(f"No link found in row: {row}")
    return list(links)  # Convertir el set a una lista

def any_country_condition(link: str, eurostat_country_codes) -> bool:
    """
    Determine if a link corresponds to any specific country condition.

    Args:
        link (str): The link to check.

    Returns:
        bool: True if the link corresponds to any country code.
    """
    return any(f"{code}.htm" in link.lower() for code in eurostat_country_codes)

def process_metadata_links(links: List[str], headers: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Process the metadata links to extract the download links.

    Args:
        links (List[str]): The list of metadata links.
        headers (Dict[str, str]): Headers to use for the HTTP requests.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the links.
    """
    download_links = []
    manual_download_links = []

    for metadata_link in links:
        try:
            response = requests.get(metadata_link, headers=headers)
            time.sleep(1)  # Add a 1-second delay

            if response.status_code == 200:
                metadata_soup = BeautifulSoup(response.content, "html.parser")
                url = response.url

                if any_country_condition(metadata_link, s.eurostat_country_codes):
                    download_link = metadata_soup.find("a", string=re.compile(r"Download\s*"))
                    if download_link:
                        complete_download_link = urljoin(url, download_link["href"])
                        if complete_download_link == "http://www.adobe.com/products/acrobat/readstep.html":
                            manual_download_links.append({
                                "htm_link": metadata_link,
                                "download_link": f"Manually download from {metadata_link}"
                            })
                        else:
                            download_links.append({
                                "htm_link": metadata_link,
                                "download_link": complete_download_link
                            })
                            print(f"Download link added: {download_link['href']}")
                    else:
                        print(f"No 'Download' link found on metadata page: {metadata_link}")
                else:
                    portugal_links = metadata_soup.find_all("a", string=re.compile(r"Portugal"))
                    portugal_download_found = False

                    if portugal_links:
                        for portugal_link in portugal_links:
                            portugal_href = urljoin(url, portugal_link.get('href'))
                            print(f"Processing Portugal link: {portugal_href}")
                            try:
                                portugal_response = requests.get(portugal_href, headers=headers)
                                time.sleep(1)  # Add a 1-second delay
                                if portugal_response.status_code == 200:
                                    portugal_soup = BeautifulSoup(portugal_response.content, "html.parser")
                                    download_link = portugal_soup.find("a", string=re.compile(r"Download\s*"))
                                    if download_link:
                                        complete_download_link = urljoin(url, download_link["href"])
                                        if complete_download_link == "http://www.adobe.com/products/acrobat/readstep.html":
                                            manual_download_links.append({
                                                "htm_link": metadata_link,
                                                "download_link": f"Manually download from {metadata_link}"
                                            })
                                        else:
                                            download_links.append({
                                                "htm_link": metadata_link,
                                                "download_link": complete_download_link
                                            })
                                        portugal_download_found = True
                                        print(f"Download link added: {download_link['href']}")
                                        break
                                    else:
                                        print(f"No 'Download' link found on Portugal page: {portugal_href}")
                            except requests.exceptions.RequestException as e:
                                print(f"HTTP request error for Portugal page: {e}")

                    if not portugal_download_found:
                        download_link = metadata_soup.find("a", string=re.compile(r"Download\s*"))
                        if download_link:
                            complete_download_link = urljoin(url, download_link["href"])
                            if complete_download_link == "http://www.adobe.com/products/acrobat/readstep.html":
                                manual_download_links.append({
                                    "htm_link": metadata_link,
                                    "download_link": f"Manually download from {metadata_link}"
                                })
                            else:
                                download_links.append({
                                    "htm_link": metadata_link,
                                    "download_link": complete_download_link
                                })
                            print(f"Download link added: {download_link['href']}")
                        else:
                            print(f"No 'Download' link found on metadata page: {metadata_link}")

            else:
                print(f"Error in main webpage request: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error for metadata page: {e}")

    print(f"Final download links: {download_links}")
    print(f"Manual download links: {manual_download_links}")
    return download_links, manual_download_links

def save_links_to_csv(links: List[Dict[str, str]], save_path: str) -> None:
    """
    Save the list of links to a CSV file.

    Args:
        links (List[Dict[str, str]]): The list of dictionaries containing links to save.
        save_folder (str): The folder where the CSV file will be saved.
        filename (str): The name of the CSV file.
    """

    with open(save_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["htm_link", "download_link"])
        writer.writeheader()
        for link in links:
            writer.writerow(link)
    print(f"Links saved to {save_path}")

def download_metadata(save_path: str, link: str, download_link: str, headers: Dict[str, str]) -> None:
    """
    Download and extract a metadata file from the given link.

    Args:
        link (str): The htm link for reference.
        download_link (str): The download link.
        headers (dict): Headers to use for the HTTP request.
    """
    print(f"Downloading from: {download_link}")

    os.makedirs(save_path, exist_ok=True)
    save_dir = os.path.join(save_path, os.path.basename(link).split('.')[0])
    try:
        response = requests.get(download_link, headers=headers)
        time.sleep(1)  # Add a 1-second delay
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
        return

    if response.status_code == 200:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Directory created: {save_dir}")

        file_name = os.path.basename(download_link)
        file_path = os.path.join(save_dir, file_name)

        with open(file_path, "wb") as file:
            file.write(response.content)
            print(f"File saved as: {file_name}")

        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(save_dir)
            os.remove(file_path)
            print(f"File extracted and .zip deleted: {file_name}")
        else:
            print(f"The file is not a valid ZIP file: {file_name}")

    else:
        print(f"Could not download the file: {download_link}")

def main() -> None:
    """
    Main function to read metadata links, process them, and download the metadata files.
    """
    # Read metadata links from a CSV file
    metadata_links = read_metadata_links_from_csv(csv_file=s.eurostat_datacodes)

    # Process metadata links to get download and manual download links
    download_links, manual_download_links = process_metadata_links(links=metadata_links, headers=s.headers)

    # Save download and manual download links to CSV files
    save_links_to_csv(links=download_links, save_path=s.eurostat_download_metadata)
    save_links_to_csv(links=manual_download_links, save_path=s.eurostat_manual_metadata)

    # Initialize a set to keep track of processed download links
    processed_links = set()  # Set to track processed download links

    # Iterate over the download links and download the metadata files
    for link_info in download_links:
        if link_info["download_link"] not in processed_links:
            download_metadata(
                s.eurostat_metadata_folder,
                link=link_info["htm_link"],
                download_link=link_info["download_link"],
                headers=s.headers
            )
            # Add the processed link to the set to avoid reprocessing
            processed_links.add(link_info["download_link"])

if __name__ == "__main__":
    main()