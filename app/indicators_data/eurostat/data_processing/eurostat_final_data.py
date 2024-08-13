import csv
import json
import os
import xml.etree.ElementTree as ET
import html
import concurrent.futures
import sys
import logging
from bs4 import BeautifulSoup  # Importa BeautifulSoup

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the path of the root directory (irradiare-app)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Add the path to sys.path
sys.path.append(irradiare_app_path)

import app.utils.settings as s

def extract_text(element, tag, namespaces):
    value = element.find(tag, namespaces)
    if value is not None and value.text:
        # Decodificar entidades HTML y limpiar HTML
        text = html.unescape(value.text)
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text()  # Devuelve solo el texto limpio
    return None

def process_file(data_code, metadata_code, data_folder, metadata_folder, output_folder):
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

def process_data_and_metadata(data_csv, data_folder, metadata_folder, output_folder):
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

def add_definition_to_csv_files(input_folder, reference_csv_path, output_folder):
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

if __name__ == "__main__":
    data_csv = s.merged_codes_file
    data_folder = s.eurostat_raw_data
    metadata_folder = s.eurostat_metadata_folder
    output_folder = s.eurostat_processed_data

    try:
        process_data_and_metadata(data_csv, data_folder, metadata_folder, output_folder)
    except KeyboardInterrupt:
        logging.info("Main process interrupted by user.")
        sys.exit(1)

    add_definition_to_csv_files(s.eurostat_processed_data, s.eurostat_dataset_def, s.eurostat_processed_data)
