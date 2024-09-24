import os
import json
import csv
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


def merge_data(raw_data_path: str, metadata_path: str, output_folder: str) -> None:
    """
    Merge data from JSON files in raw_data_path and metadata_path, then save the combined data to CSV files.

    This function reads JSON files from the specified directories, processes the data and metadata, 
    and saves the combined data into CSV files in the output_folder.

    Args:
        raw_data_path (str): The directory path where raw data JSON files are located.
        metadata_path (str): The directory path where metadata JSON files are located.
        output_folder (str): The directory path where the output CSV files will be saved.

    Returns:
        None
    """
    # Get the names of the files from each folder
    data_files = [f for f in os.listdir(raw_data_path) if f.endswith('.json')]
    metadata_files = [f for f in os.listdir(metadata_path) if f.endswith('.json')]

    # Extract the numeric identifier codes
    data_ids = {f.split('_')[1].split('.')[0] for f in data_files}
    metadata_ids = {f.split('_')[1].split('.')[0] for f in metadata_files}

    # Find the codes present in both folders
    matching_ids = data_ids.intersection(metadata_ids)

    # Create an empty dict to save metadata
    metadata_dict = {}

    # Read and process metadata files
    for file_id in matching_ids:
        metadata_filename = f"metadata_{file_id}.json"
        with open(os.path.join(metadata_path, metadata_filename), 'r', encoding='utf-8') as metadata_file:
            metadata_json = json.load(metadata_file)
            indicador_cod = metadata_json[0]["IndicadorCod"]
            unidades_medida = metadata_json[0].get("UnidadeMedida", "")
            dimensiones = {dim["dim_num"]: dim["abrv"] for dim in metadata_json[0]["Dimensoes"]["Descricao_Dim"]}
            metadata_dict[indicador_cod] = {"units": unidades_medida, "dimensiones": dimensiones}

    # Read and process data files
    for file_id in matching_ids:
        data_filename = f"data_{file_id}.json"
        combined_data = []
        with open(os.path.join(raw_data_path, data_filename), 'r', encoding='utf-8') as data_file:
            data_json = json.load(data_file)
            indicador_cod = data_json[0].get("IndicadorCod", "")
            indicador_dsg = data_json[0].get("IndicadorDsg", "")
            datos = data_json[0].get("Dados", {})
            
            for timecode, registros in datos.items():
                for registro in registros:
                    area = registro.get("geodsg", "")
                    value = registro.get("valor", "")

                    # Inicializar entrada combinada
                    combined_entry = {
                        "source_cod": indicador_cod,
                        "name": indicador_dsg,
                        "description": "",
                        "area": area,
                        "value": value,
                        "timecode": timecode
                    }

                    # Agregar filtros (dim_3_t, dim_4_t, etc.)
                    filter_values = {f"filter_value{dim_num}": registro.get(f"dim_{dim_num}_t", "")
                                    for dim_num in range(3, 10) if f"dim_{dim_num}_t" in registro}

                    # Combinar los filtros en la entrada
                    combined_entry.update(filter_values)

                    # Obtener unidades y dimensiones desde metadata
                    metadata = metadata_dict.get(indicador_cod, {})
                    combined_entry["units"] = metadata.get("units", "")
                    
                    # Agregar los valores de las dimensiones desde metadata
                    for dim_num in range(3, 10):
                        filter_key = f"filter_value{dim_num}"
                        if filter_key in combined_entry:
                            combined_entry[f"dimension_{dim_num}"] = metadata.get("dimensiones", {}).get(str(dim_num), "")

                    combined_data.append(combined_entry)

        # Determine the headers of the combined csv based on the keys from the first element in combined_data
        fieldnames = list(set().union(*(entry.keys() for entry in combined_data)))

        # Save the combined data
        filename = f'combined_data_{file_id}.csv'
        output_file = os.path.join(output_folder, filename)
        os.makedirs(output_folder, exist_ok=True)
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write the headers
            writer.writeheader()
            
            # Write the combined data rows
            for entry in combined_data:
                writer.writerow(entry)

        print(f'CSV file generated: {filename}')


def main():
    try:
        merge_data(raw_data_path=s.ine_data_path, metadata_path=s.ine_metadata_path, output_folder=s.ine_processed_data)
    except Exception as e:
        print(f"Error: {e}")


if __name__=="__main__":
    main()