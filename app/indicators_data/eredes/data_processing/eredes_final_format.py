from typing import List, Dict, Union, Any, Tuple

import csv
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
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

# Function to clean 'Date' columns
def clean_date(value: str) -> str:
    """
    Cleans the 'Date' column by removing non-numeric characters and converting the string to uppercase.

    Args:
        value (str): The original date string.

    Returns:
        str: The cleaned and formatted date string.
    """
    return re.sub(r'[^SQsq0-9]', '', value).upper()

# Function used to create a timecode combining year+period (month, semester, quarter)
def combine_year_with_period(year: str, period: str) -> str:
    """
    Combines a year and a period (month, semester, quarter) into a timecode.

    Args:
        year (str): The year value as a string.
        period (str): The period value as a string.

    Returns:
        str: A combined string representing the timecode (year + period).
    """
    return year + period

def extract_date(value: str) -> str:
    """
    Extracts a date from a string, and cleans it if necessary.

    Args:
        value (str): The string containing the date.

    Returns:
        str: The cleaned and extracted date in the format YYYYMMDD.
    """
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    return date_match.group(1).replace("-", "") if date_match else clean_date(value)

def get_column_indices(headers: List[str], column_groups: Dict[str, List[str]]) -> Dict[str, Union[int, None]]:
    """
    Maps header column names to their corresponding indices, based on predefined column groups.

    Args:
        headers (List[str]): The list of header names from the CSV file.
        column_groups (Dict[str, List[str]]): A dictionary of column groups with possible column names.

    Returns:
        Dict[str, Union[int, None]]: A dictionary mapping group names to their respective column index or None.
    """
    column_indices = {}
    header_map = {col.lower(): idx for idx, col in enumerate(headers)}

    for group_name, column_names in column_groups.items():
        for col_name in column_names:
            col_name_lower = col_name.lower()
            if col_name_lower in header_map:
                column_indices[group_name] = header_map[col_name_lower]
                break
        else:
            column_indices[group_name] = None

    return column_indices

def process_file(filename: str, merged_files_path: str, final_data_path: str) -> None:
    """
    Processes a CSV file by adding a 'timecode' column and saving the modified file.

    Args:
        filename (str): The name of the CSV file to process.
        merged_files_path (str): The path where the merged files are located.
        final_data_path (str): The path where the processed files will be saved.
    """
    file_path = os.path.join(merged_files_path, filename)
    print(f"Processing file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        headers = next(reader)
        headers = [header.lstrip('\ufeff') for header in headers]

        column_groups = {
            'date': s.eredes_date_cols,
            'year': s.eredes_year_cols,
            'month': s.eredes_month_cols,
            'semester': s.eredes_semester_cols,
            'quarter': s.eredes_quarter_cols
        }

        column_indices = get_column_indices(headers, column_groups)

        date_idx = column_indices.get('date', None)
        year_idx = column_indices.get('year', None)
        month_idx = column_indices.get('month', None)
        semester_idx = column_indices.get('semester', None)
        quarter_idx = column_indices.get('quarter', None)

        headers.insert(0, "timecode")
        new_rows = []

        for row in reader:
            new_row = row.copy()
            timecode = ""
            if date_idx is not None and date_idx < len(row):
                timecode = extract_date(row[date_idx])
            elif year_idx is not None and year_idx < len(row):
                year_value = row[year_idx]
                if month_idx is not None and month_idx < len(row):
                    month_value = row[month_idx].zfill(2)
                    timecode = combine_year_with_period(year_value, month_value)
                elif semester_idx is not None and semester_idx < len(row):
                    semester_value = row[semester_idx].zfill(2)
                    if len(semester_value) == 1:
                        semester_value = 'S' + semester_value
                    timecode = combine_year_with_period(year_value, semester_value)
                elif quarter_idx is not None and quarter_idx < len(row):
                    quarter_value = row[quarter_idx].zfill(2)
                    if len(quarter_value) == 1:
                        quarter_value = 'Q' + quarter_value
                    timecode = combine_year_with_period(year_value, quarter_value)
                else:
                    timecode = year_value
            else:
                if quarter_idx is not None and quarter_idx < len(row):
                    timecode = clean_date(row[quarter_idx])
                elif semester_idx is not None and semester_idx < len(row):
                    timecode = clean_date(row[semester_idx])

            new_row.insert(0, timecode)
            new_rows.append(new_row)

    os.makedirs(final_data_path, exist_ok=True)
    output_file_path = os.path.join(final_data_path, f"temp_timecode_{filename}")
    with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=';')
        writer.writerow(headers)
        writer.writerows(new_rows)

    print(f"File processed and saved at: {output_file_path}")
    os.remove(file_path)
    print(f"Original file deleted: {file_path}")

def add_timecode(merged_files_path: str, final_data_path: str) -> None:
    """
    Adds timecodes to all CSV files in the merged files directory and saves the results.

    Args:
        merged_files_path (str): The directory containing the merged files.
        final_data_path (str): The directory where the processed files will be saved.
    """
    files = [filename for filename in os.listdir(merged_files_path) if filename.endswith(".csv")]
    with ThreadPoolExecutor(max_workers=4) as executor:
        for filename in files:
            executor.submit(process_file, filename, merged_files_path, final_data_path)
    os.rmdir(merged_files_path)


#/////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////     ADDING GEOLOCATION DATA     ////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////

def load_dicofre_data(dicofre_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file and return it as a dictionary.

    Args:
        dicofre_path (str): The file path to the JSON file.

    Returns:
        Dict[str, Any]: The data loaded from the JSON file, represented as a dictionary.
    """
    with open(dicofre_path, 'r', encoding='utf-8') as dicofre_file:
        return json.load(dicofre_file)


def load_zipcode_data(zipcode_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file containing zipcode information and return it as a dictionary.

    Args:
        zipcode_path (str): The file path to the JSON file containing zipcode data.

    Returns:
        Dict[str, Any]: The data loaded from the JSON file, represented as a dictionary.
    """
    with open(zipcode_path, 'r', encoding='utf-8') as zipcode_file:
        return json.load(zipcode_file)


def load_nuts_data(nuts_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file containing NUTS (Nomenclature of Territorial Units for Statistics) information and return it as a dictionary.

    Args:
        nuts_path (str): The file path to the JSON file containing NUTS data.

    Returns:
        Dict[str, Any]: The data loaded from the JSON file, represented as a dictionary.
    """
    with open(nuts_path, 'r', encoding='utf-8') as nuts_file:
        return json.load(nuts_file)


def get_location_data_dicofre(dicofre: Union[int, str], dicofre_dict: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
    """
    Retrieve location data (district, county, parish) from a dicofre code.

    Args:
        dicofre (Union[int, str]): The dicofre code as an integer or string.
        dicofre_dict (Dict[str, Dict[str, str]]): Dictionary with dicofre location data.

    Returns:
        Tuple[str, str, str]: A tuple containing district, county, and parish.
    """
    dicofre_str = str(dicofre)
    location_data = {}
    distrito, concelho, freguesia = 'undefined', 'undefined', 'undefined'

    if len(dicofre_str) >= 6:
        location_data = dicofre_dict.get(dicofre_str, {})
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
        freguesia = location_data.get('freguesia', 'undefined')
    elif len(dicofre_str) >= 4:
        for key, data in dicofre_dict.items():
            if key.startswith(dicofre_str[:4]):
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
    elif len(dicofre_str) >= 2:
        for key, data in dicofre_dict.items():
            if key.startswith(dicofre_str[:2]):
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
        
    return distrito, concelho, freguesia


def get_location_data_zipcode(zipcode: Union[int, str], zipcode_dict: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
    """
    Retrieve location data (district, county, parish) from a zipcode.

    Args:
        zipcode (Union[int, str]): The zipcode as an integer or string.
        zipcode_dict (Dict[str, Dict[str, str]]): Dictionary with zipcode location data.

    Returns:
        Tuple[str, str, str]: A tuple containing district, county, and parish.
    """
    zipcode_clean = re.sub(r'[^0-9]', '', str(zipcode))
    
    if len(zipcode_clean) == 4:
        for key, data in zipcode_dict.items():
            if data['ZipNoFormat'].startswith(zipcode_clean):
                return data['distrito'], data['concelho'], 'undefined'
    
    if len(zipcode_clean) >= 7:
        location_data = zipcode_dict.get(zipcode_clean, {})
        if location_data:
            return location_data['distrito'], location_data['concelho'], location_data['freguesia']
        else:
            for key, data in zipcode_dict.items():
                if data['ZipNoFormat'].startswith(zipcode_clean):
                    return data['distrito'], data['concelho'], data['freguesia']
    
    return 'undefined', 'undefined', 'undefined'


def get_nuts_data(concelho: str, nuts_dict: Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]) -> Tuple[str, str, str]:
    """
    Retrieve NUTS (Nomenclature of Territorial Units for Statistics) data from a county (concelho).

    Args:
        concelho (str): The county name.
        nuts_dict (Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]): Dictionary containing NUTS data.

    Returns:
        Tuple[str, str, str]: A tuple containing NUTS 1, NUTS 2, and NUTS 3 regions.
    """
    nuts1, nuts2, nuts3 = 'undefined', 'undefined', 'undefined'
    
    for nuts1_region, nuts1_info in nuts_dict.items():
        for region_nuts2, nuts2_info in nuts1_info.get("NUTS 2", {}).items():
            for nuts3_region, nuts3_data in nuts2_info.get("NUTS 3", {}).items():
                if concelho in nuts3_data.get("Municipalities", []):
                    return nuts1_region, region_nuts2, nuts3_region
    
    return nuts1, nuts2, nuts3


def add_geodata(final_data_path: str, dicofre_dict: Dict[str, Dict[str, str]], zipcode_dict: Dict[str, Dict[str, str]], nuts_dict: Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]) -> None:
    """
    Add geolocation data to CSV files by retrieving relevant information using dicofre and zipcode data.

    Args:
        final_data_path (str): Path to the folder containing CSV files to process.
        dicofre_dict (Dict[str, Dict[str, str]]): Dictionary containing dicofre data.
        zipcode_dict (Dict[str, Dict[str, str]]): Dictionary containing zipcode data.
        nuts_dict (Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]): Dictionary containing NUTS data.
    """
    for filename in os.listdir(final_data_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(final_data_path, f"final_geodata_{filename}")
            print(f"Processing file: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter=';')
                headers = next(reader)
                headers = [header.lstrip('\ufeff') for header in headers]
                headers.extend(['distrito', 'concelho', 'freguesia', 'nuts1', 'nuts2', 'nuts3','dicofre', 'zipcode'])

                zip_col_idx = next((i for i, h in enumerate(headers) if h in ['Zip Code', 'ZipCode']), None)
                dicofre_col_idx = next((i for i, h in enumerate(headers) if h in ['DistrictMunicipalityParishCode', 'CodDistritoConcelhoFreguesia', 'DistrictMunicipalityCode', 'MinicipalityCode', 'CodConcelho', 'CODIGO_CONCELHO']), None)

                if zip_col_idx is None and dicofre_col_idx is None:
                    print(f"No se encontró la columna de dicofre ni zip code en el archivo: {file_path}")
                    continue

                new_rows = []
                for row in reader:
                    distrito, concelho, freguesia = 'undefined', 'undefined', 'undefined'
                    nuts1, nuts2, nuts3 = 'undefined', 'undefined', 'undefined'
                    dicofre = 'undefined'
                    zipcode = 'undefined'

                    if zip_col_idx is not None:
                        zipcode = re.sub(r'[^0-9]', '', row[zip_col_idx])
                        if zipcode:
                            distrito, concelho, freguesia = get_location_data_zipcode(zipcode, zipcode_dict)
                            if concelho != 'undefined':
                                area = concelho
                                nuts1, nuts2, nuts3 = get_nuts_data(area, nuts_dict)
                                if concelho == 'undefined':
                                    if len(zipcode) >= 2:
                                        partial_zipcode = zipcode[:2]
                                        zipcode = partial_zipcode
                                        if partial_zipcode[0] in s.continental_zipcode:
                                            nuts1 = 'Continental Portugal'
                                        elif partial_zipcode == s.madeira_dicode:
                                            nuts1 = 'Região Autónoma dos Madeira'
                                        elif partial_zipcode == s.açores_dicode:
                                            nuts1 = 'Região Autónoma dos Açores'
                                    elif len(zipcode) == 1:
                                        partial_zipcode = zipcode[0]
                                        zipcode = partial_zipcode
                                        if partial_zipcode in s.continental_zipcode:
                                            nuts1 = 'Continental Portugal'
                                        elif partial_zipcode == '9':
                                            nuts1 = 'Overseas Portugal'

                    elif dicofre_col_idx is not None:
                        dicofre = re.sub(r'[^0-9]', '', row[dicofre_col_idx])
                        if dicofre:
                            distrito, concelho, freguesia = get_location_data_dicofre(dicofre, dicofre_dict)
                            if concelho != 'undefined':
                                area = concelho
                                nuts1, nuts2, nuts3 = get_nuts_data(area, nuts_dict)
                            elif concelho == 'undefined':
                                if dicofre[:2] in s.continental_dicode:
                                    nuts1 = 'Continental Portugal'
                                    dicofre = dicofre[:2]
                                elif dicofre[:2] in s.madeira_dicode:
                                    nuts1 = 'Região Autónoma dos Madeira'
                                    dicofre = dicofre[:2]
                                elif dicofre[:2] in s.açores_dicode:
                                    nuts1 = 'Região Autónoma dos Açores'
                                    dicofre = dicofre[:2]

                    row.extend([distrito, concelho, freguesia, nuts1, nuts2, nuts3, dicofre, zipcode])
                    new_rows.append(row)

            with open(file_path, 'w', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(new_rows)

            print(f"Archivo procesado y guardado en: {final_data_path}")


def main() -> None:
    """
    Main function to process append time and geolocation data in order to obtain the final eredes data files.

    This function performs the following tasks:
    1. Adds time codes to temporary merged files by calling `add_timecode`.
    2. Loads the Dicofre data into a dictionary by calling `load_dicofre_data`.
    3. Loads the Zip Code data into a dictionary by calling `load_zipcode_data`.
    4. Loads the NUTS (Nomenclature of Territorial Units for Statistics) data into a dictionary by calling `load_nuts_data`.
    5. Adds geographic data to the final dataset by calling `add_geodata` using the previous dictionaries as parameters.
    """
    add_timecode(merged_files_path=s.eredes_merged, final_data_path=s.eredes_final_data)
    dicofre_dict = load_dicofre_data(dicofre_path=s.dicofre_data)
    zipcode_dict = load_zipcode_data(zipcode_path=s.zipcode_data)
    nuts_dict = load_nuts_data(nuts_path=s.nuts_data)
    add_geodata(final_data_path=s.eredes_final_data, dicofre_dict=dicofre_dict, zipcode_dict=zipcode_dict, nuts_dict=nuts_dict)

if __name__=="__main__":
    main()