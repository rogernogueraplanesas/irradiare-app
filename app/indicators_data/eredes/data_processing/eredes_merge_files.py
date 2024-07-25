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


def eliminar_archivos_csv(raw_data, files_to_delete):
    for filename in files_to_delete:
        file_path = os.path.join(raw_data, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Archivo {filename} eliminado.")
        else:
            print(f"Archivo {filename} no encontrado.")

def load_metadata(metadata):
    metadata_dict = {}
    with open(metadata, "r", encoding='utf-8') as metadata_file:
        reader = csv.reader(metadata_file, delimiter=',')
        metadata_headers = next(reader)  # Skip the header row
        for row in reader:
            src_code = row[2]
            metadata_dict[src_code] = row
    return metadata_headers, metadata_dict

def combine_data_and_metadata(raw_data, metadata_headers, metadata_dict, merged_files_path):
    for filename in os.listdir(raw_data):
        if filename.endswith(".csv"):
            src_code = filename.replace('.csv', '')
            if src_code in metadata_dict:
                metadata_row = metadata_dict[src_code]
                file_path = os.path.join(raw_data, filename)
                with open(file_path, "r", encoding='utf-8') as data_file:
                    reader = csv.reader(data_file, delimiter=';')
                    headers = next(reader)
                    combined_rows = [headers + metadata_headers]  # Combined header row
                    for row in reader:
                        combined_row = row + metadata_row
                        combined_rows.append(combined_row)
                # Write the combined rows to a new CSV file
                os.makedirs(merged_files_path, exist_ok=True)
                output_file_path = os.path.join(merged_files_path, f"temp_merged_{filename}")
                with open(output_file_path, "w", encoding='utf-8', newline='') as output_file:
                    writer = csv.writer(output_file, delimiter=';')
                    writer.writerows(combined_rows)
                print(f"Combined data written to {output_file_path}")

# Eliminar archivos especificados
eliminar_archivos_csv(s.eredes_raw_data, files_to_delete=s.eredes_removed_files)

# Load the metadata
metadata_headers, metadata_dict = load_metadata(s.eredes_metadata)

# Combine data and metadata
combine_data_and_metadata(s.eredes_raw_data, metadata_headers, metadata_dict, merged_files_path=s.eredes_merged)
