import os
import xml.etree.ElementTree as ET
import csv
import requests

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
    - url: The URL to download the file from.
    - save_dir: The directory to save the downloaded file.
    - filename: The name to save the downloaded file as.

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

def get_data_names(path, output_file):
    with open(output_file, 'w') as f:
        # Recorrer todos los archivos en el directorio
        for archivo in os.listdir(path):
            # Verificar si el archivo tiene la extensión .json
            if archivo.endswith('.json'):
                # Escribir el nombre del archivo sin la extensión en el archivo de salida
                f.write(os.path.splitext(archivo)[0] + '\n')
    print(f"Filenames CSV saved in: {output_file}")


# Función para buscar en el XML y extraer el enlace de metadatos en HTML
def encontrar_link(codigo, archivo_xml):
    # Parsear el archivo XML
    tree = ET.parse(archivo_xml)
    root = tree.getroot()
    # Namespace del archivo XML
    ns = {'nt': 'urn:eu.europa.ec.eurostat.navtree'}

    for leaf in root.findall(".//nt:leaf", ns):
        code_element = leaf.find("nt:code", ns)
        if code_element is not None and code_element.text == codigo:
            metadata_element = leaf.find("nt:metadata[@format='html']", ns)
            if metadata_element is not None:
                print(f"Found {metadata_element.text} for {codigo}")
                return metadata_element.text
    return None


def fill_metadata_list(nombres_json, archivo_xml, metadata_dict):
    # Llenar el diccionario con los enlaces de metadatos
    for nombre in nombres_json:
        link = encontrar_link(nombre, archivo_xml)
        if link:
            metadata_dict[nombre] = link
    return metadata_dict


def merge_datacode_metadata_link(archivo_csv, metadata_dict, archivo_csv_actualizado):
    # Leer el archivo CSV y agregar enlaces de metadatos
    with open(archivo_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Agregar enlaces de metadatos
    for row in rows:
        codigo = row[0]
        row.append(metadata_dict.get(codigo, ''))

    # Escribir el archivo CSV actualizado
    with open(archivo_csv_actualizado, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

    print("Archivo CSV actualizado con enlaces de metadatos.")


if __name__ == "__main__":
    download_toc(url=s.eurostat_toc_url_xml, save_path=s.eurostat_toc_xml)
    # Llamar a la función con los parámetros adecuados
    get_data_names(path=s.eurostat_raw_data, output_file=s.eurostat_datacodes)
    # Obtener nombres de archivos JSON sin la extensión
    nombres_json = [f.split('.')[0] for f in os.listdir(s.eurostat_raw_data) if f.endswith('.json')]
    # Crear un diccionario para almacenar los enlaces de metadatos
    metadata_links = {}
    metadata_dict = fill_metadata_list(nombres_json=nombres_json,archivo_xml=s.eurostat_toc_xml ,metadata_dict=metadata_links)
    merge_datacode_metadata_link(archivo_csv=s.eurostat_datacodes, metadata_dict=metadata_dict, archivo_csv_actualizado=s.eurostat_datacodes)