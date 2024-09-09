import os
import shutil
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

# Ruta de la carpeta principal
root_dir = "app/indicators_data/eurostat/eurostat_metadata"

def move_smdx_files_and_cleanup(root_dir):
    # Recorre los subdirectorios de primer nivel en root_dir
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            for subentry in os.scandir(entry.path):
                if subentry.is_file() and subentry.name.endswith('.sdmx.xml'):
                    xml_file_path = subentry.path
                    new_path = os.path.join(root_dir, subentry.name)
                    
                    # Asegúrate de que el nombre del archivo no sobrescriba a otros
                    if os.path.exists(new_path):
                        base, extension = os.path.splitext(subentry.name)
                        counter = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(root_dir, f"{base}_{counter}{extension}")
                            counter += 1

                    shutil.move(xml_file_path, new_path)
                    print(f'Moved: {xml_file_path} to {new_path}')

def remove_all_dirs(root_dir):
    # Recorre los subdirectorios y archivos en el directorio dado
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            # Elimina subdirectorios recursivamente
            remove_all_dirs(entry.path)
            
            # Intenta eliminar el directorio actual y todo su contenido
            try:
                shutil.rmtree(entry.path)  # Elimina el directorio y todo su contenido
                print(f'Removed directory and its contents: {entry.path}')
            except OSError as e:
                print(f'Could not remove directory: {entry.path}. Error: {e}')


# Ejecutar la función
move_smdx_files_and_cleanup(root_dir=s.eurostat_metadata_folder)
remove_all_dirs(root_dir=s.eurostat_metadata_folder)