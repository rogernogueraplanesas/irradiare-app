from eurostatapiclient import EurostatAPIClient

import csv
import json
import sys
import os

import logging
import requests


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

def download_toc(url: str, save_path: str) -> None:
    """
    Download the TOC (Table of Contents) for the Eurostat database through a given URL and save it to a specified directory.

    Args:
    - url (str): The URL to download the file from.
    - save_path (str): The file path where the downloaded TOC will be saved.

    Returns:
    - None
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


def get_eurostat_data(data_save_path: str, labels_save_path: str, eurostat_toc_txt: str, labels_file: str) -> None:
    """
    Fetch and save Eurostat data for specified codes using EurostatAPIClient.

    The data is filtered based on predefined parameters (for Portugal) and saved as JSON files. 
    Additionally, a CSV file with the dataset codes and labels is created.

    Args:
    - data_save_path (str): The directory where the JSON files with the datasets will be saved.
    - labels_save_path (str): The directory where the CSV file with the dataset labels will be saved.
    - eurostat_toc_txt (str): Path to the file containing the Eurostat Table of Contents (TOC) with the codes.
    - labels_file (str): Path where the CSV file with the dataset codes and labels will be saved.

    Returns:
    - None
    """
    # Version 1.0 is the only available
    version = '1.0'
    # The only possible format is JSON
    data_format = 'json'
    # Specify language: 'en', 'fr', 'de'
    language = 'en'

    client = EurostatAPIClient(version, data_format, language)

    # Required query parameters (Filter only for Portugal data)
    params = {
        'geo': 'PT',
    }
    
    # Ensure the directory where data will be saved exists
    os.makedirs(data_save_path, exist_ok=True)
    # Ensure the directory where data will be saved exists
    os.makedirs(labels_save_path, exist_ok=True)

    # Initialize a list to store code and label information
    code_label_list = []

    # Read the Eurostat indicators Table of contents (TOC) file
    with open(eurostat_toc_txt, 'r', encoding='utf-8') as codes_file:
        reader = csv.reader(codes_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        for row in reader:
            code = row[1].strip('"')  # Extract the code for the indicator in each row
            print(code)
            path = os.path.join(data_save_path, f"{code}.json")  # Define a code adjustable path to save the JSON datasets
            print(path)
            try:
                # Get data from the server for the code + query parameters specified
                filtered_dataset = client.get_dataset(code, params=params)
                # Get the label for the dataset
                label = filtered_dataset.label
                print(label)
                # Append the code and label to the list
                code_label_list.append((code, label))
                # Convert the dataset into a pandas dataframe
                filtered_dataframe = filtered_dataset.to_dataframe()
                # Convert the dataframe into JSON. orient='records': each row from the df is converted into a dict. The result is a list of dictionaries. 
                filtered_dataframe_json = filtered_dataframe.to_json(orient='records')
                print("DataFrame converted to JSON.")
                # Create/open the code adjustable path in 'write' mode
                with open(path, 'w', encoding='utf-8') as dataset:
                    json.dump(filtered_dataframe_json, dataset, indent=4, ensure_ascii=False)  # Dump the JSON data into the file
                    print(f"Data for {code} saved.")

            except requests.exceptions.RequestException as e:
                print(f"An exception occurred for code {code}: {e}")
                continue

    # Write the code and label information to a CSV file
    with open(labels_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Code', 'Label'])
        writer.writerows(code_label_list)

def main() -> None:
    """
    Main function to download the TOC and fetch Eurostat data.
    """
    # Download the Eurostat TOC file
    download_toc(url=s.eurostat_toc_url_txt, save_path=s.eurostat_toc_txt)
    
    # Fetch and save the Eurostat data
    get_eurostat_data(
        data_save_path=s.eurostat_raw_data,
        labels_save_path=s.eurostat_comp_files,
        eurostat_toc_txt=s.eurostat_toc_txt,
        labels_file=s.eurostat_dataset_def
    )

# Call main() within the if statement
if __name__ == "__main__":
    main()
