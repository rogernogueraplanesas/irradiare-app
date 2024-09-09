from typing import Tuple, List, Dict

import csv
import os
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

# Import settings
import app.utils.settings as s


def delete_csv_files(raw_data: str, files_to_delete: List[str]) -> None:
    """
    Delete a set of non-useful files from the indicators' raw data folder.

    Args:
    - raw_data (str): Path to the downloaded raw data folder
    - files_to_delete (List[str]): List of files to be deleted.
    """
    for filename in files_to_delete:
        file_path = os.path.join(raw_data, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Archivo {filename} eliminado.")
        else:
            print(f"Archivo {filename} no encontrado.")

def load_metadata(metadata: str) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Load metadata rearranging it as a dictionary with the source code being the key.
    The source code (src_code) is the unique identifier for each indicator provided by e-redes.

    Args:
    - metadata (str): Path to the metadata CSV file

    Returns:
    - Tuple[List[str], Dict[str, List[str]]]: Tuple including:
        - List of headers present in the metadata file.
        - Dictionary containing a string (src_code) as a key and the rest of elements of each metadata row as values.
    """
    metadata_dict = {}
    with open(metadata, "r", encoding='utf-8') as metadata_file:
        reader = csv.reader(metadata_file, delimiter=',')
        metadata_headers = next(reader)
        for row in reader:
            src_code = row[2]
            metadata_dict[src_code] = row
    return metadata_headers, metadata_dict

def combine_data_and_metadata(raw_data: str, metadata_headers: List[str], metadata_dict: Dict[str, List[str]], merged_files_path: str) -> None:
    """
    Combine each raw data file row with the corresponding metadata based on their src_code value, and save them into a new folder.

    Args:
    - raw_data (str): Path to the raw data files folder.
    - metadata_headers (List[str]): List of headers extracted from the metadata file.
    - metadata_dict (Dict[str, List[str]]): Dictionary containing metadata values foe each src_code (key value).
    - merged_files_path (str): New temporary folder containing the resulting merged files.
    """
    
    os.makedirs(merged_files_path, exist_ok=True)
    
    for filename in os.listdir(raw_data):
        if filename.endswith(".csv"):
            src_code = filename.replace('.csv', '') # The source code for each raw file is extracted from the filename
            if src_code in metadata_dict:
                metadata_row = metadata_dict[src_code]
                file_path = os.path.join(raw_data, filename)
                with open(file_path, "r", encoding='utf-8') as data_file:
                    reader = csv.reader(data_file, delimiter=';')
                    headers = next(reader)
                    combined_rows = [headers + metadata_headers]  # Create a new headers row by combining the raw one and the metadata headers
                    for row in reader:
                        combined_row = row + metadata_row # Combine the raw data values and the corresponding metadata based on the src_code
                        combined_rows.append(combined_row) # Append each new combined row to the already existing list of rows that included the headers

                output_file_path = os.path.join(merged_files_path, f"temp_merged_{filename}")
                with open(output_file_path, "w", encoding='utf-8', newline='') as output_file:
                    writer = csv.writer(output_file, delimiter=';')
                    writer.writerows(combined_rows)
                print(f"Combined data written to {output_file_path}")


def main() -> None:
    """
    Main entry point of the script. This function performs the following tasks:
    1. Deletes specified CSV files from the raw data directory.
    2. Loads metadata from a specified file.
    3. Combines data from raw CSV files with the metadata and saves the results to a specified directory.
    """
    try:
        # Delete specified CSV files
        print("Deleting specified CSV files...")
        delete_csv_files(s.eredes_raw_data, files_to_delete=s.eredes_removed_files)
        print("Files deleted successfully.")

        # Load metadata
        print("Loading metadata...")
        metadata_headers, metadata_dict = load_metadata(s.eredes_metadata)
        print("Metadata loaded successfully.")

        # Combine data and metadata
        print("Combining data with metadata...")
        combine_data_and_metadata(s.eredes_raw_data, metadata_headers, metadata_dict, merged_files_path=s.eredes_merged)
        print("Data combined and saved successfully.")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr) # Catches exceptions caused by non-existing files
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr) # Catches exceptions caused by lack of permissions opening a file
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr) # Catches general exceptions


if __name__=="__main__":
    main()