import json
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


def final_data(wb_data_path, wb_metadata_path, wb_final_path):
    # Leer archivos JSON
    with open(wb_data_path, 'r') as f:
        datos = json.load(f)

    with open(wb_metadata_path, 'r') as f:
        metadatos = json.load(f)

    # Función para extraer metadatos de un código indicador específico
    def obtener_metadatos(metadatos, source_id, series_id):
        key = f"('{source_id}', '{series_id}')"
        return metadatos.get(key, None)

    # Combinar datos y metadatos
    resultados = []
    for dato in datos:
        for entry in dato["source"]["data"]:
            row = {}
            source_id = dato["source"]["id"]
            series_id = None
            country = None
            version = None
            timecode = None
            name = None

            for variable in entry["variable"]:
                if variable["concept"] == "Series":
                    series_id = variable["id"]
                    name = variable["value"]
                elif variable["concept"] == "Country":
                    country = variable["value"]
                elif variable["concept"] == "Version":
                    version = variable["value"]
                elif variable["concept"] == "Time":
                    timecode = variable["value"].replace('YR', '')

            row["timecode"] = timecode
            row["source_code"] = series_id
            row["name"] = name
            row["value"] = entry["value"]

            metadato = obtener_metadatos(metadatos, source_id, series_id)
            if metadato:
                for source in metadato["source"]:
                    for concept in source["concept"]:
                        for variable in concept["variable"]:
                            if variable["id"] == "PRT":
                                for metatype in variable["metatype"]:
                                    if metatype["id"] == "CurrencyUnit":
                                        row["units"] = metatype["value"]
                                    elif metatype["id"] == "SpecialNotes":
                                        row["units_description"] = metatype["value"]
                                row["source"] = source["name"]
            else:
                row["units"] = "unknown"
                row["units_description"] = "NA"
                row["source"] = "unknown"

            resultados.append(row)

    # Definir el nombre de las columnas para el CSV
    columns = ["timecode", "source_code", "name", "value", "units", "units_description", "source"]

    # Escribir el CSV
    with open(wb_final_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for row in resultados:
            writer.writerow(row)

        print("CSV successfully generated.")
