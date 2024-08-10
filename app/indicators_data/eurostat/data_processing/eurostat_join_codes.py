import csv
import logging
import os
import sys

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the path of the root directory (irradiare-app)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Add the path to sys.path
sys.path.append(irradiare_app_path)

import app.utils.settings as s

# Función para leer un archivo CSV y devolver los datos como una lista de listas
def read_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        return list(reader)

# Función para guardar los datos en un archivo CSV
def write_csv(file_path, fieldnames, rows):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def join_datacodes_metadatacodes():
    # Leer los archivos CSV
    csv1 = read_csv(s.eurostat_datacodes)
    csv2 = read_csv(s.eurostat_download_metadata)
    csv3 = read_csv(s.eurostat_manual_metadata)

    # Convertir los CSV 2 y 3 en diccionarios de búsqueda
    link_to_download_link = {row[0]: row[1] for row in csv2}
    link_to_manual_link = {row[0]: row[1] for row in csv3}

    # Procesar los enlaces del primer CSV y generar el CSV final
    final_rows = []
    for row in csv1:
        indicator_name = row[0]
        htm_link = row[1]

        if htm_link in link_to_download_link:
            # Extraer el nombre del archivo del enlace de descarga
            download_link = link_to_download_link[htm_link]
            metadata_name = download_link.split('/')[-1].split('.')[0]
        elif htm_link in link_to_manual_link:
            # Extraer el nombre del archivo del enlace manual
            metadata_name = htm_link.split('/')[-1].split('.')[0]
        else:
            # Si no hay enlace, dejar en blanco
            metadata_name = ''

        final_rows.append({'indicator_name': indicator_name, 'metadata_name': metadata_name})

    # Guardar el archivo CSV final
    write_csv(file_path=s.merged_codes_file, fieldnames=['indicator_name', 'metadata_name'], rows=final_rows)
