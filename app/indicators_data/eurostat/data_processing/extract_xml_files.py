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


root_dir = "app/indicators_data/eurostat/eurostat_metadata"

def move_smdx_files_and_cleanup(root_dir: str) -> None:
    """
    Moves .sdmx.xml files from subdirectories to the root directory and renames them if necessary to avoid overwrites.

    Args:
        root_dir (str): The root directory where the files should be moved.
    
    Returns:
        None
    """
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            for subentry in os.scandir(entry.path):
                if subentry.is_file() and subentry.name.endswith('.sdmx.xml'):
                    xml_file_path = subentry.path
                    new_path = os.path.join(root_dir, subentry.name)
                    
                    if os.path.exists(new_path):
                        base, extension = os.path.splitext(subentry.name)
                        counter = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(root_dir, f"{base}_{counter}{extension}")
                            counter += 1

                    shutil.move(xml_file_path, new_path)
                    print(f'Moved: {xml_file_path} to {new_path}')


def remove_all_dirs(root_dir: str) -> None:
    """
    Recursively removes all directories and their contents in the specified root directory.

    Args:
        root_dir (str): The root directory from which directories will be deleted.
    
    Returns:
        None
    """
    # Browse through folders and files from the given path
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            # Recursively delete folders
            remove_all_dirs(entry.path)
            
            # Delete current directory and its content
            try:
                shutil.rmtree(entry.path)
                print(f'Removed directory and its contents: {entry.path}')
            except OSError as e:
                print(f'Could not remove directory: {entry.path}. Error: {e}')


def main() -> None:
    """
    Main function that moves .sdmx.xml files and removes directories in the specified root directory.
    
    Returns:
        None
    """
    move_smdx_files_and_cleanup(root_dir=s.eurostat_metadata_folder)
    remove_all_dirs(root_dir=s.eurostat_metadata_folder)


if __name__ == "__main__":
    main()