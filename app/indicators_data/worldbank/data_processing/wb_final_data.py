import json
import csv
import os
import re
import sys
from typing import Dict, Any, Optional, List
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

def final_data(wb_data_path: str, wb_metadata_path: str, wb_final_path: str) -> None:
    """
    Process and combine data from JSON files and generate a final CSV file with the combined results.

    Args:
        wb_data_path (str): The file path to the JSON file containing the data.
        wb_metadata_path (str): The file path to the JSON file containing the metadata.
        wb_final_path (str): The file path where the resulting CSV file will be saved.

    Returns:
        None
    """
    # Leer archivos JSON
    with open(wb_data_path, 'r') as f:
        datos: List[Dict[str, Any]] = json.load(f)

    with open(wb_metadata_path, 'r') as f:
        metadatos: Dict[str, Any] = json.load(f)

    def obtener_metadatos(metadatos: Dict[str, Any], source_id: str, series_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata for a specific indicator code.

        Args:
            metadatos (Dict[str, Any]): The metadata dictionary.
            source_id (str): The source identifier.
            series_id (str): The series identifier.

        Returns:
            Optional[Dict[str, Any]]: The metadata corresponding to the source and series identifiers, or None if not found.
        """
        key = f"('{source_id}', '{series_id}')"
        return metadatos.get(key, None)

    # Combinar datos y metadatos
    resultados = []
    for dato in datos:
        for entry in dato["source"]["data"]:
            row = {}
            source_id = dato["source"]["id"]
            series_id = 'Undefined'
            country = 'Undefined'
            timecode = 'Undefined'
            name = 'Undefined'
            units = 'Undefined'

            for variable in entry["variable"]:
                if variable["concept"] == "Series":
                    series_id = variable["id"]
                    name = variable["value"]
                    
                    # Expresión regular para buscar contenido entre paréntesis
                    match = re.search(r'\((.*?)\)', name)
                    if match:
                        # Extrae el contenido entre paréntesis
                        units = match.group(1)
                        # Elimina el contenido entre paréntesis del name
                        name = re.sub(r'\s*\(.*?\)\s*', '', name).strip()
                        
                elif variable["concept"] == "Country":
                    country = variable["value"]
                elif variable["concept"] == "Time":
                    timecode = variable["value"].replace('YR', '')

            row["timecode"] = timecode
            row["source_code"] = series_id
            row["name"] = name
            row["country"] = country
            row["value"] = entry["value"]
            row["units"] = units
            row["units_description"] = 'Undefined'

            metadato = obtener_metadatos(metadatos, source_id, series_id)
            if metadato:
                for source in metadato["source"]:
                    for concept in source["concept"]:
                        for variable in concept["variable"]:
                            row["source"] = source["name"]
            else:

                row["source"] = "'Undefined'"

            resultados.append(row)

    # Definir el nombre de las columnas para el CSV
    columns = ["timecode", "source_code", "name", "country", "value", "units", "units_description", "source"]

    # Escribir el CSV
    with open(wb_final_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for row in resultados:
            writer.writerow(row)

        print("CSV successfully generated.")


def dividir_csv_por_source_code(wb_final_path: str) -> None:
    """
    Dividir el archivo CSV final en múltiples archivos CSV según el valor de 'source_code'.

    Args:
        wb_final_path (str): La ruta del archivo CSV generado.

    Returns:
        None
    """
    # Crear un diccionario para almacenar las filas agrupadas por 'source_code'
    source_code_data = {}

    # Leer el archivo CSV
    with open(wb_final_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source_code = row['source_code']
            if source_code not in source_code_data:
                source_code_data[source_code] = []
            source_code_data[source_code].append(row)

    # Obtener la carpeta donde se encuentra el archivo final
    base_path = os.path.dirname(wb_final_path)

    # Crear un CSV para cada 'source_code'
    for source_code, rows in source_code_data.items():
        # Definir la ruta del nuevo archivo CSV
        new_csv_path = os.path.join(base_path, f"{source_code}.csv")
        
        # Escribir las filas correspondientes a ese 'source_code' en el nuevo archivo
        with open(new_csv_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Archivo '{new_csv_path}' generado con éxito.")

    try:
        os.remove(wb_final_path)
        print(f"Archivo '{wb_final_path}' eliminado con éxito.")
    except FileNotFoundError:
        print(f"El archivo '{wb_final_path}' no existe o ya ha sido eliminado.")
    except Exception as e:
        print(f"Error al intentar eliminar el archivo '{wb_final_path}': {e}")


def main():
    try:
        final_data(wb_data_path=s.wb_data_path, wb_metadata_path=s.wb_metadata_path,wb_final_path=s.wb_complete_file)
    except Exception as e:
        print("An exception occured: {e}")

    try:
        dividir_csv_por_source_code(wb_final_path=s.wb_complete_file)
    except Exception as e:
        print("An exception occured: {e}")


if __name__=="__main__":
    main()    