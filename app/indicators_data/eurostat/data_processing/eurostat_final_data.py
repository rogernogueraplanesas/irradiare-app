import csv
import json
import os
import xml.etree.ElementTree as ET
import html
import concurrent.futures
from bs4 import BeautifulSoup
from typing import Optional, Dict

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

def extract_text(element: ET.Element, tag: str, namespaces: Dict[str, str]) -> Optional[str]:
    """
    Extract and clean text from an XML element based on the provided tag and namespaces.

    Args:
        element (ET.Element): The XML element to search within.
        tag (str): The tag to search for within the element.
        namespaces (Dict[str, str]): The namespaces to use for XML parsing.

    Returns:
        Optional[str]: The cleaned text if found, otherwise None.
    """
    value = element.find(tag, namespaces)
    if value is not None and value.text:
        # Decodificar entidades HTML y limpiar HTML
        text = html.unescape(value.text)
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text()  # Devuelve solo el texto limpio
    return None

def process_file(
    data_code: str,
    metadata_code: str,
    data_folder: str,
    metadata_folder: str,
    output_folder: str
) -> None:
    """
    Process data and metadata files, and write the results to a CSV file.

    Args:
        data_code (str): The data code used to locate the JSON file.
        metadata_code (str): The metadata code used to locate the XML file.
        data_folder (str): The directory containing the data JSON files.
        metadata_folder (str): The directory containing the metadata XML files.
        output_folder (str): The directory where the output CSV file will be saved.

    Returns:
        None
    """
    # Define los namespaces utilizados en el XML
    namespaces = {
        'genericmetadata': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/genericmetadata',
        'common': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common'
    }

    data_file_path = os.path.join(data_folder, f"{data_code}.json")
    metadata_file_path = os.path.join(metadata_folder, f"{metadata_code}.sdmx.xml")

    if not os.path.exists(data_file_path):
        logging.warning(f"JSON file does not exist: {data_file_path}")
        return

    if not os.path.exists(metadata_file_path):
        logging.warning(f"XML file does not exist: {metadata_file_path}")
        return

    os.makedirs(output_folder, exist_ok=True)
    output_csv = os.path.join(output_folder, f"{data_code}.csv")

    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['data_code', 'metadata_code', 'value', 'unit', 'time', 'description', 'source', 'calculation', 'units_description'])

        with open(data_file_path, 'r', encoding='utf-8') as datafile:
            try:
                json_str = datafile.read().strip()

                if json_str.startswith('"') and json_str.endswith('"'):
                    json_str = json_str[1:-1]

                json_str = json_str.replace('\\"', '"')

                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {data_file_path}: {e}")
                return

            if not isinstance(data, list):
                logging.error(f"Unexpected JSON format in {data_file_path}. Expected a list.")
                return

            for record in data:
                if not isinstance(record, dict):
                    logging.error(f"Unexpected record format in {data_file_path}: {record}")
                    continue

                value = record.get('values', None)
                unit = record.get('unit', None)
                time = record.get('time', None)

                try:
                    # Usar xml.etree.ElementTree para parsear el XML
                    tree = ET.parse(metadata_file_path)
                    root = tree.getroot()

                    # Usar el namespace correcto en las consultas XPath
                    description = extract_text(root, ".//genericmetadata:ReportedAttribute[@conceptID='DATA_DESCR']/genericmetadata:Value", namespaces)
                    source = extract_text(root, ".//genericmetadata:ReportedAttribute[@conceptID='CONTACT_ORGANISATION']/genericmetadata:Value", namespaces)
                    calculation = extract_text(root, ".//genericmetadata:ReportedAttribute[@conceptID='DATA_COMP']/genericmetadata:Value", namespaces)
                    units_description = extract_text(root, ".//genericmetadata:ReportedAttribute[@conceptID='UNIT_MEASURE']/genericmetadata:Value", namespaces)
                except ET.ParseError as e:
                    logging.error(f"Error parsing XML from {metadata_file_path}: {e}")
                    continue

                writer.writerow([data_code, metadata_code, value, unit, time, description, source, calculation, units_description])

def process_data_and_metadata(
    data_csv: str,
    data_folder: str,
    metadata_folder: str,
    output_folder: str
) -> None:
    """
    Process data and metadata files based on the information provided in a CSV file.

    This function reads data codes and metadata codes from a CSV file, then processes each pair of codes by calling 
    the `process_file` function. It utilizes concurrent processing to handle multiple files in parallel.

    Args:
        data_csv (str): Path to the CSV file containing data codes and metadata codes.
        data_folder (str): Path to the folder containing data JSON files.
        metadata_folder (str): Path to the folder containing metadata XML files.
        output_folder (str): Path to the folder where output CSV files will be saved.

    Returns:
        None
    """
    data_codes = []
    with open(data_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  # Skip header row
        for row in reader:
            data_code = row[0]
            metadata_code = row[1] if len(row) > 1 else None

            if data_code and metadata_code and 'BulkDownloadListing' not in metadata_code:
                data_codes.append((data_code, metadata_code))

    # Limit the number of processes to 4 or adjust according to your system
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_file, data_code, metadata_code, data_folder, metadata_folder, output_folder)
                   for data_code, metadata_code in data_codes]
        try:
            for future in concurrent.futures.as_completed(futures):
                future.result()  # To propagate any exceptions that occurred
        except KeyboardInterrupt:
            logging.info("Process interrupted by user.")
            executor.shutdown(wait=False)  # Optionally, you can set wait=True to wait for currently running tasks to finish
            sys.exit(1)

def add_definition_to_csv_files(
    input_folder: str,
    reference_csv_path: str,
    output_folder: str
) -> None:
    """
    Add dataset definitions from a reference CSV file to multiple CSV files in a specified input folder.

    This function reads a reference CSV file to get dataset definitions, then it iterates over all CSV files in the
    input folder, adding a 'dataset_name' column with the corresponding definitions if a match is found.

    Args:
        input_folder (str): Path to the folder containing input CSV files.
        reference_csv_path (str): Path to the CSV file containing dataset definitions.
        output_folder (str): Path to the folder where modified CSV files will be saved.

    Returns:
        None
    """
    # Leer el archivo de referencia
    reference_dict = {}
    with open(reference_csv_path, mode='r', encoding='utf-8') as reference_file:
        reference_reader = csv.reader(reference_file)
        for row in reference_reader:
            if row:  # Asegurarse de que la fila no esté vacía
                reference_dict[row[0]] = row[1]

    # Crear el output_folder si no existe
    os.makedirs(output_folder, exist_ok=True)

    # Recorrer recursivamente la carpeta de entrada
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                file_name = os.path.splitext(file)[0]

                # Leer el archivo CSV
                with open(file_path, mode='r', encoding='utf-8') as input_file:
                    reader = csv.reader(input_file)
                    rows = list(reader)

                # Agregar la nueva columna 'dataset_definition' al encabezado si hay coincidencia
                if file_name in reference_dict:
                    definition = reference_dict[file_name]
                    # Añadir 'dataset_definition' al encabezado
                    if rows:
                        rows[0].append('dataset_name')
                        # Añadir la definición en cada fila
                        for row in rows[1:]:
                            row.append(definition)

                    # Guardar el archivo modificado en la carpeta de salida
                    output_path = os.path.join(output_folder, file)
                    with open(output_path, mode='w', newline='', encoding='utf-8') as output_file:
                        writer = csv.writer(output_file)
                        writer.writerows(rows)
    print("Process completed")    

def main() -> None:
    """
    Main function to process data and metadata, and update CSV files with dataset definitions.

    This function processes data and metadata files by calling `process_data_and_metadata`, 
    then adds dataset definitions to CSV files using `add_definition_to_csv_files`.

    Args:
        None

    Returns:
        None
    """
    data_csv = s.merged_codes_file
    data_folder = s.eurostat_raw_data
    metadata_folder = s.eurostat_metadata_folder
    output_folder = s.eurostat_processed_data

    
    #try:
        #logging.info("Starting merge")
        #process_data_and_metadata(data_csv, data_folder, metadata_folder, output_folder)
    #except KeyboardInterrupt:
        #logging.info("Main process interrupted by user.")
        #sys.exit(1)

    #logging.info("Merge completed.")
    logging.info("Starting data completion.")
    add_definition_to_csv_files(s.eurostat_processed_data, s.eurostat_dataset_def, s.eurostat_processed_data)
    logging.info("Data completion completed.")

if __name__ == "__main__":
    main()
