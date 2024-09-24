import csv
import re
import os
import sys
import json
from typing import Dict, Any, Union, List, Tuple

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

def get_timecode_area(headers: List[str]) -> Tuple[Union[int, None], Union[int, None]]:
    """
    Gets the indices of the 'timecode' and 'area' columns from the list of headers.

    Args:
        headers (List[str]): List of column names.

    Returns:
        Tuple[Union[int, None], Union[int, None]]: Indices of the 'timecode' and 'area' columns.
    """
    timecode_idx = next((i for i, h in enumerate(headers) if h in ['timecode']), None)
    area_idx = next((i for i, h in enumerate(headers) if h in ["area"]), None)
    return timecode_idx, area_idx


def clean_timecode(row: List[str], timecode_idx: int) -> str:
    """
    Cleans the 'timecode' value by removing non-numeric characters.

    Args:
        row (List[str]): List of values from the CSV row.
        timecode_idx (int): Index of the 'timecode' column.

    Returns:
        str: Cleaned 'timecode' value.
    """
    timecode = row[timecode_idx]
    timecode = re.sub(r'[^0-9]', '', timecode)
    return timecode


def load_nuts_data(nuts_path: str) -> Dict[str, Any]:
    """
    Loads NUTS data from a JSON file.

    Args:
        nuts_path (str): Path to the JSON file containing NUTS data.

    Returns:
        Dict[str, Any]: NUTS data loaded from the file.
    """
    with open(nuts_path, 'r', encoding='utf-8') as nuts_file:
        return json.load(nuts_file)


def load_dicofre_data(dicofre_path: str) -> Dict[str, Any]:
    """
    Loads DICOFRE data from a JSON file.

    Args:
        dicofre_path (str): Path to the JSON file containing DICOFRE data.

    Returns:
        Dict[str, Any]: DICOFRE data loaded from the file.
    """
    with open(dicofre_path, 'r', encoding='utf-8') as dicofre_file:
        return json.load(dicofre_file)


def match_location(name: str, dicofre_data: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
    """
    Matches a name with the location in the DICOFRE data.

    Args:
        name (str): Name of the location to match.
        dicofre_data (Dict[str, Dict[str, str]]): DICOFRE data.

    Returns:
        Tuple[str, str, str]: Tuple containing district, municipality, and parish.
    """
    for key, value in dicofre_data.items():
        if name == value["freguesia"]:
            return value["distrito"], value["concelho"], value["freguesia"]
    
    for key, value in dicofre_data.items():
        if name == value["concelho"]:
            return value["distrito"], value["concelho"], "undefined"
    
    for key, value in dicofre_data.items():
        if name == value["distrito"]:
            return value["distrito"], "undefined", "undefined"
    
    return "undefined", "undefined", "undefined"


def match_nuts_location(area: str, dicofre_data: Dict[str, Dict[str, str]], nuts_dict: Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]) -> Tuple[str, str, str, str, str, str]:
    """
    Matches an area with the corresponding NUTS location in the DICOFRE and NUTS data.

    Args:
        area (str): Name of the area to match.
        dicofre_data (Dict[str, Dict[str, str]]): DICOFRE data.
        nuts_dict (Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]): NUTS data.

    Returns:
        Tuple[str, str, str, str, str, str]: Tuple containing district, municipality, parish, and NUTS codes.
    """
    if area == 'Continente':
        area = 'Portugal Continental'
    elif area == 'Norte':
        area = 'Norte Region'
    elif area == 'Centro':
        area = 'Centro Region'

    nuts1 = 'undefined'
    nuts2 = 'undefined'
    nuts3 = 'undefined'

    distrito, concelho, freguesia = match_location(area, dicofre_data)

    if concelho != 'undefined':
        area = concelho

    for nuts1_region, nuts1_info in nuts_dict.items():
        for region_nuts2, nuts2_info in nuts1_info.get("NUTS 2", {}).items():
            for nuts3_region, nuts3_data in nuts2_info.get("NUTS 3", {}).items():
                if area in nuts3_data.get("Municipalities", []):
                    return distrito, concelho, freguesia, nuts1_region, region_nuts2, nuts3_region
                elif area == region_nuts2:
                    return distrito, concelho, freguesia, nuts1_region, region_nuts2, nuts3
                elif area == nuts1_region:
                    return distrito, concelho, freguesia, nuts1_region, nuts2, nuts3

    return distrito, concelho, freguesia, area, nuts2, nuts3


def main(final_data_path: str, dicofre_path: str, nuts_path: str) -> None:
    """
    Processes CSV files in the final_data_path directory, adding location and NUTS information.

    Args:
        final_data_path (str): Path of the directory containing the CSV files to process.
        dicofre_dict (Dict[str, Dict[str, str]]): DICOFRE data.
        nuts_dict (Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]): NUTS data.

    Returns:
        None
    """
    dicofre_dict = load_dicofre_data(dicofre_path)
    nuts_dict = load_nuts_data(nuts_path)

    os.makedirs(final_data_path, exist_ok=True)
    for filename in os.listdir(final_data_path):
        if filename.endswith('.csv'):
            csv_file = os.path.join(final_data_path, filename)
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                try:
                    headers = next(reader)
                except StopIteration:
                    print(f"Empty file: {filename}")
                    continue
                
                timecode_idx, area_idx = get_timecode_area(headers)
                if timecode_idx is None or area_idx is None:
                    print(f"The file does not have the required columns: {filename}")
                    continue

                headers.extend(['distrito', 'concelho', 'freguesia', 'nuts1', 'nuts2', 'nuts3'])
                new_rows = []
                for row in reader:
                    row[timecode_idx] = clean_timecode(row, timecode_idx)
                    area = row[area_idx]
                    distrito, concelho, freguesia, nuts1, nuts2, nuts3 = match_nuts_location(area, dicofre_dict, nuts_dict)
                    row.extend([distrito, concelho, freguesia, nuts1, nuts2, nuts3])
                    new_rows.append(row)

            output_file = os.path.join(final_data_path, filename)
            with open(output_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(new_rows)

            print(f"File processed and saved in: {output_file}")

if __name__ == "__main__":
    main(s.ine_processed_data, s.dicofre_data, s.nuts_data)