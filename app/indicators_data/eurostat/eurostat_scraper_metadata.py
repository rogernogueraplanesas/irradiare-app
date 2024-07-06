import sys
import os

# Obtiene la ruta del directorio 'irradiare-app' (dos niveles hacia arriba desde eredes_metadata.py)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Añade la ruta al sys.path
sys.path.append(irradiare_app_path)

import app.indicators_data.settings as s
import requests
from bs4 import BeautifulSoup
import time
import zipfile
from urllib.parse import urljoin
import re
from typing import List, Dict
import csv

# Lista de abreviaturas de países
country_codes = [
    "eu", "be", "el", "lt", "pt", "bg", "es", "lu", "ro", "cz", "fr", "hu", "si", 
    "dk", "hr", "mt", "sk", "de", "it", "nl", "fi", "ee", "cy", "at", "se", 
    "ie", "lv", "pl", "is", "no", "li", "ch", "ba", "me", "md", "mk", "ge", 
    "al", "rs", "tr", "ua", "xk", "am", "by", "az", "dz", "lb", "sy", "eg", 
    "ly", "tn", "il", "ma", "jo", "ps", "ar", "au", "br", "ca", "cn_x_hk", 
    "hk", "in", "jp", "mx", "ng", "nz", "ru", "sg", "za", "kr", "tw", "uk", "us"
]

def any_country_condition(link: str) -> bool:
    """
    Determine if a link corresponds to any specific country condition.

    Args:
        link (str): The link to check.

    Returns:
        bool: True if the link corresponds to any country code.
    """
    return any(f"{code}.htm" in link.lower() for code in country_codes)

def get_metadata_links(url: str, headers: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Obtain PT metadata links from the given URL.

    Args:
        url (str): The URL to scrape for metadata links.
        headers (dict): Headers to use for the HTTP request.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing htm and download links.
    """
    try:
        # Send a GET request to the specified URL with the provided headers
        response = requests.get(url, headers=headers)
        time.sleep(1)  # Add a 1-second delay to avoid hitting the server too frequently
        print("First response successful")
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        print(f"HTTP request error: {e}")
        return []

    if response.status_code == 200:
        # Parse the response content with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        # Find all 'a' tags with 'href' attributes ending with '.htm'
        links = soup.find_all("a", href=lambda href: href and href.endswith(".htm"))
        
        # Extract the href attributes and combine them with the base URL
        metadata_links = [urljoin(url, link["href"]) for link in links]
        print(f"Metadata links found: {metadata_links}")

        download_links = []
        manual_download_links = []

        for metadata_link in metadata_links:
            print(f"Processing metadata link: {metadata_link}")
            try:
                # Send a GET request to each metadata link
                metadata_response = requests.get(metadata_link, headers=headers)
                time.sleep(1)  # Add a 1-second delay
                if metadata_response.status_code == 200:
                    # Parse the metadata page content
                    metadata_soup = BeautifulSoup(metadata_response.content, "html.parser")

                    # Check if the metadata link is for any specific country
                    if any_country_condition(metadata_link):
                        # Directly find the download link on the metadata page
                        download_link = metadata_soup.find("a", string=re.compile(r"Download\s*"))
                        if download_link:
                            complete_download_link = urljoin(url, download_link["href"])
                            if complete_download_link == "http://www.adobe.com/products/acrobat/readstep.html":
                                manual_download_links.append({
                                    "htm_link": metadata_link,
                                    "download_link": f"Manually download from {metadata_link}"
                                })
                            else:
                                # Add the complete download link to the list
                                download_links.append({
                                    "htm_link": metadata_link,
                                    "download_link": complete_download_link
                                })
                                print(f"Download link added: {download_link['href']}")
                        else:
                            print(f"No 'Download' link found on metadata page: {metadata_link}")
                    else:
                        # Check if there are any 'Portugal' links
                        portugal_links = metadata_soup.find_all("a", string=re.compile(r"Portugal"))
                        portugal_download_found = False

                        if portugal_links:
                            for portugal_link in portugal_links:
                                portugal_href = urljoin(url, portugal_link.get('href'))
                                print(f"Processing Portugal link: {portugal_href}")
                                try:
                                    # Send a GET request to each Portugal link
                                    portugal_response = requests.get(portugal_href, headers=headers)
                                    time.sleep(1)  # Add a 1-second delay
                                    if portugal_response.status_code == 200:
                                        # Parse the Portugal page content
                                        portugal_soup = BeautifulSoup(portugal_response.content, "html.parser")
                                        # Find the download link containing the text 'Download'
                                        download_link = portugal_soup.find("a", string=re.compile(r"Download\s*"))
                                        if download_link:
                                            complete_download_link = urljoin(url, download_link["href"])
                                            # Check if there is a common error when extracting the url
                                            if complete_download_link == "http://www.adobe.com/products/acrobat/readstep.html":
                                                manual_download_links.append({
                                                    "htm_link": metadata_link,
                                                    "download_link": f"Manually download from {metadata_link}"
                                                })
                                            else:
                                                # Add the complete download link to the list
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
                            # If no 'Portugal' links or no 'Download' link found in Portugal page, manually find the download link on the metadata page
                            download_link = metadata_soup.find("a", string=re.compile(r"Download\s*"))
                            if download_link:
                                complete_download_link = urljoin(url, download_link["href"])
                                if complete_download_link == "http://www.adobe.com/products/acrobat/readstep.html":
                                    manual_download_links.append({
                                        "htm_link": metadata_link,
                                        "download_link": f"Manually download from {metadata_link}"
                                    })
                                else:
                                    # Add the complete download link to the list
                                    download_links.append({
                                        "htm_link": metadata_link,
                                        "download_link": complete_download_link
                                    })
                                print(f"Download link added: {download_link['href']}")
                            else:
                                print(f"No 'Download' link found on metadata page: {metadata_link}")

            except requests.exceptions.RequestException as e:
                print(f"HTTP request error for metadata page: {e}")

        print(f"Final download links: {download_links}")
        print(f"Manual download links: {manual_download_links}")
        return download_links, manual_download_links

    else:
        print(f"Error in main webpage request: {response.status_code}")
        return [], []

def download_metadata(code: str, link: str, headers: Dict[str, str]) -> None:
    """
    Download and extract a metadata file from the given link.

    Args:
        code (str): The code for the indicator.
        link (str): The download link.
        headers (dict): Headers to use for the HTTP request.
    """
    print(f"Downloading from: {link}")
    save_dir = f"app/indicators_data/eurostat/eurostat_metadata/{code}"

    try:
        # Send a GET request to the download link
        response = requests.get(link, headers=headers)
        time.sleep(1)  # Add a 1-second delay
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions
        print(f"HTTP request error: {e}")
        return

    if response.status_code == 200:
        # Create the directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Directory created: {save_dir}")

        # Get the file name from the link and create the file path
        file_name = os.path.basename(link)
        file_path = os.path.join(save_dir, file_name)

        # Write the response content to a file
        with open(file_path, "wb") as file:
            file.write(response.content)
            print(f"File saved as: {file_name}")

        # Verify if the downloaded file is a valid ZIP file before extracting
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(save_dir)
            os.remove(file_path)
            print(f"File extracted and .zip deleted: {file_name}")
        else:
            print(f"The file is not a valid ZIP file: {file_name}")

    else:
        print(f"Could not download the file: {link}")

def save_links_to_csv(links: List[Dict[str, str]], filename: str) -> None:
    """
    Save the list of links to a CSV file.

    Args:
        links (List[Dict[str, str]]): The list of dictionaries containing links to save.
        filename (str): The name of the CSV file.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["htm_link", "download_link"])
        writer.writeheader()
        for link in links:
            writer.writerow(link)
    print(f"Links saved to {filename}")

def main() -> None:
    """
    Main function to download metadata files from Eurostat.
    """
    # Get metadata links
    download_links, manual_download_links = get_metadata_links(url=s.eurostat_metadata_url, headers=s.headers)
    
    # Save links to CSV
    save_links_to_csv(download_links, s.eurostat_metadata_url_path)
    save_links_to_csv(manual_download_links, s.eurostat_metadata_manual_urls)
    
    if download_links:
        for link in download_links:
            # Extract the code from the link
            code = link["download_link"].split("/")[-1].split(".")[0]
            # Download the metadata for the given code and link
            download_metadata(code=code, link=link["download_link"], headers=s.headers)
    else:
        print("No valid download links found.")

if __name__ == "__main__":
    main()