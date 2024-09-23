import csv
import os
from typing import List, Dict

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

def read_csv(file_path: str) -> List[List[str]]:
    """
    Read a CSV file and return its contents as a list of lists.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        List[List[str]]: The contents of the CSV file, where each inner list represents a row.
    """
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        return list(reader)

def write_csv(file_path: str, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    """
    Save data to a CSV file.

    Args:
        file_path (str): The path to the CSV file.
        fieldnames (List[str]): The list of field names (headers) for the CSV file.
        rows (List[Dict[str, str]]): The rows of data to write, each represented as a dictionary.
    
    Returns:
        None
    """
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main() -> None:
    """
    Join data from different CSV files to generate a merged CSV with indicator names and metadata names.

    This function reads from three CSV files, processes the links, and generates a final CSV file with the joined data.

    Args:
        None

    Returns:
        None
    """
    # Read the csv files
    csv1 = read_csv(s.eurostat_datacodes)
    csv2 = read_csv(s.eurostat_download_metadata)
    csv3 = read_csv(s.eurostat_manual_metadata)

    # Convert csv 2 and 3 into search dicts
    link_to_download_link: Dict[str, str] = {row[0]: row[1] for row in csv2}
    link_to_manual_link: Dict[str, str] = {row[0]: row[1] for row in csv3}

    # Process links from the first csv and generate the final csv
    final_rows: List[Dict[str, str]] = []
    for row in csv1:
        indicator_name = row[0]
        htm_link = row[1]

        if htm_link in link_to_download_link:
            # Extract the filename from the download link
            download_link = link_to_download_link[htm_link]
            metadata_name = download_link.split('/')[-1].split('.')[0]
        elif htm_link in link_to_manual_link:
            # Extract the filename from the manual download link
            metadata_name = htm_link.split('/')[-1].split('.')[0]
        else:
            metadata_name = ''

        final_rows.append({'indicator_name': indicator_name, 'metadata_name': metadata_name})

    write_csv(file_path=s.merged_codes_file, fieldnames=['indicator_name', 'metadata_name'], rows=final_rows)

if __name__ == "__main__":
    main()