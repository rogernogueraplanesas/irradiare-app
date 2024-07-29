from typing import List, Dict, Union, Any, Tuple

import csv
import json
import os
import re
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


#/////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////       ADDING TIMECODES       //////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////

# Function to clean 'Date' columns
def clean_date(value: str) -> str:
    """
    Cleans the input date string by removing all characters except for digits, 'S' and 'Q'.
    'S' refers to semester, while 'Q' refers to quarter.
    
    Args:
    value (str): The input string to be cleaned.

    Returns:
    str: Cleaned uppercase string.
    """
    return re.sub(r'[^SQsq0-9]', '', value).upper() # Letters must be uppercase


# Function used to create a timecode combining year+period (month, semester, quarter)
def combine_year_with_period(year: str, period: str) -> str:
    """
    Combines the input year string with the period string.

    Args:
        year (str): The year string.
        period (str): The period string (e.g., 'S1', 'Q2').

    Returns:
        str: The concatenated string of the year and period.
    """
    return year + period


def extract_date(value:str) -> str:
    """
    Returns a date from the input string in the format YYYYMMDD.
    If no valid date to extract is found (format different than YYYY-MM-DD), it cleans the input string using the clean_date function.

    Args:
        value (str): The input string from which to extract the date.

    Returns:
        str: The extracted date in YYYYMMDD format, or a cleaned version of the input string.
    """
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", value) # The value's format is compared to a YYYY-MM-DD date format
    return date_match.group(1).replace("-", "") if date_match else clean_date(value) # If the format is different, execute 'clean_date()


def get_column_indices(headers: List[str], column_groups: Dict[str, List[str]]) -> Dict[str, Union[int, None]]:
    """
    Returns a dictionary with the column group names and their corresponding indices if present in headers.

    Args:
        headers (List[str]): A list of column header names.
        column_groups (Dict[str, List[str]]): A dictionary where the keys are group names and the values are lists of column names.

    Returns:
        Dict[str, Union[int, None]]: A dictionary where the keys are group names and the values are indices of the first matching column name in headers. If no match is found, the value is None.
    """
    column_indices = {}
    header_map = {col.lower(): idx for idx, col in enumerate(headers)} # Dictionary that maps each header (in lowercase) to its index in the list.

    for group_name, column_names in column_groups.items():
    # For each time column there is a general name (such as 'year', 'month', etc.)
    # In this dataset, it is possible to find variations (such as ANO, ano, Year, etc.)
    # Split the general accepted name (group_name) and the list of possible variations (column_names)
        for col_name in column_names: # Iterate over the possible alias
            col_name_lower = col_name.lower()
            if col_name_lower in header_map: # Compare the lowercase alias with the input headers list
                column_indices[group_name] = header_map[col_name_lower] # Save the 'formal' group name related to the alias 
                break                                                   # with the position of the column in the input headers list where it matched
        else:
            column_indices[group_name] = None  # No alias match in header_map

    return column_indices


def add_timecode(merged_files_path: str, final_data_path: str) -> None:
    """
    Processes CSV files in the specified directory, adding a 'timecode' column to each file based on various date-related columns.

    For each CSV file in `merged_files_path`, this function:
    1. Reads the file and cleans any BOM (Byte Order Mark) characters from the headers.
    2. Identifies the indices of date-related columns (date, year, month, semester, quarter) based on predefined column groups.
    3. Generates a 'timecode' value for each row based on the available date-related columns.
    4. Adds the 'timecode' column to the CSV data and writes the updated data to a new file in `final_data_path`.
    5. Deletes the original (merged) CSV file and removes the directory for merged files if it is empty. The raw data files are not removed

    Args:
        merged_files_path (str): Path to the directory containing the CSV files to process.
        final_data_path (str): Path to the directory where the processed files will be saved.
    """
    for filename in os.listdir(merged_files_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(merged_files_path, filename)
            print(f"Processing file: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter=';')
                headers = next(reader)
                
                # Clean BOM from headers
                headers = [header.lstrip('\ufeff') for header in headers]

                # Create the column groups dictionary
                column_groups = {
                    'date': s.eredes_date_cols,
                    'year': s.eredes_year_cols,
                    'month': s.eredes_month_cols,
                    'semester': s.eredes_semester_cols,
                    'quarter': s.eredes_quarter_cols
                }

                # With the file headers and the column groups dict, get the index for each group  (if possible)
                column_indices = get_column_indices(headers, column_groups)

                date_idx = column_indices.get('date', None)
                year_idx = column_indices.get('year', None)
                month_idx = column_indices.get('month', None)
                semester_idx = column_indices.get('semester', None)
                quarter_idx = column_indices.get('quarter', None)

                # Add a new 'timecode' column at the beggining of the headers row
                headers.insert(0, "timecode")
                new_rows = []

                for row in reader:
                    new_row = row.copy() # Create a copy from each row of the data file

                    timecode = ""
                    # Timecode is generated based in the index found previously
                    if date_idx is not None and date_idx < len(row):
                        timecode = extract_date(row[date_idx]) # If date column found, extract with YYYYMMDD format
                    elif year_idx is not None and year_idx < len(row):
                        year_value = row[year_idx] # If year found, check the possibility of merging it with month, sem. or quarter values
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
                            timecode = year_value # If there is no month, quarter or semester, timecode = year
                    else:
                        if quarter_idx is not None and quarter_idx < len(row):
                            timecode = clean_date(row[quarter_idx])
                        elif semester_idx is not None and semester_idx < len(row):
                            timecode = clean_date(row[semester_idx])

                    new_row.insert(0, timecode)
                    new_rows.append(new_row)
            # Ensure that the path for the final data files exists
            os.makedirs(s.eredes_final_data, exist_ok=True)

            # Save the new files with timecodes added
            output_file_path = os.path.join(final_data_path, f"temp_timecode_{filename}")
            with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
                writer = csv.writer(output_file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(new_rows)

            print(f"Archivo procesado y guardado en: {output_file_path}")

            # Remove the files used as a source ( temp_merged files)
            os.remove(file_path)
            print(f"Archivo original eliminado: {file_path}")

    # Delete the empty directory for the temp_merged files
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


# Obtener datos de localización
def get_location_data_dicofre(dicofre: Union[int, str], dicofre_dict: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
    """
    Given a dicofre code number, retrieve up to three levels of administrative divisions (distrito, concelho, and freguesia) in Portugal by means of a dicofre dictionary with metadata.

    Args:
        dicofre (Union[int, str]): The dicofre code for which location data is to be retrieved. It can be an integer or a string.
        dicofre_dict (Dict[str, Dict[str, str]]): A dictionary where keys are dicofre codes (as strings) and values are dictionaries
                                              containing location data with keys 'distrito', 'concelho', and 'freguesia'.

    Returns:
        Tuple[str, str, str]: A tuple containing three strings:
            - 'distrito': The district corresponding to the zip code, or 'undefined' if not found.
            - 'concelho': The municipality corresponding to the zip code, or 'undefined' if not found.
            - 'freguesia': The parish corresponding to the zip code, or 'undefined' if not found.
    """
    dicofre_str = str(dicofre)
    location_data = {} # Dictionary where geolocation data is saved
    distrito = 'undefined'
    concelho = 'undefined'
    freguesia = 'undefined'
    if len(dicofre_str) >= 6: # If the dicofre has 6 or + digits
        location_data = dicofre_dict.get(dicofre_str, {}) # Match the dicofre with the key of the dicofre_dict and get the data
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined') # From the data, get the values for distrito, concelho and freguesia
        freguesia = location_data.get('freguesia', 'undefined')
    elif len(dicofre_str) >= 4:
        for key, data in dicofre_dict.items():
            if key.startswith(dicofre_str[:4]): # For a dicofre of 4 digits, freguesia is not considered
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
    elif len(dicofre_str) >= 2 and not location_data:
        for key, data in dicofre_dict.items():
            if key.startswith(dicofre_str[:2]): # For a dicofre of 4 digits, concelho and freguesia are not considered
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
    return distrito, concelho, freguesia


def get_location_data_zipcode(zipcode: Union[int, str], zipcode_dict: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
    """
    Retrieve up to three levels of administrative divisions based on the provided zip code. A zip code dictironary with metadata is used.

    The function handles zip codes with 4 or 7 or more digits, returning:
    - The district ('distrito')
    - The municipality ('concelho')
    - The parish ('freguesia')

    Args:
        zipcode (Union[int, str]): The zip code for which location data is to be retrieved. It can be an integer or a string.
        zipcode_dict (Dict[str, Dict[str, str]]): A dictionary where keys are zip codes (as strings) and values are dictionaries
                                                  containing 'ZipNoFormat', 'distrito', 'concelho', and 'freguesia'.
                                                  ZipNoFormat presents the digits of a zipcode with no symbols.

    Returns:
        Tuple[str, str, str]: A tuple containing:
            - 'distrito': The district corresponding to the zip code, or 'undefined' if not found.
            - 'concelho': The municipality corresponding to the zip code, or 'undefined' if not found.
            - 'freguesia': The parish corresponding to the zip code, or 'undefined' if not found.
    """
    # The zip code is 'cleaned' leaving only digits, for comparison purposes
    zipcode_clean = re.sub(r'[^0-9]', '', zipcode)

    # For a zip code of 4 digits
    if len(zipcode_clean) == 4:
        # A partial coincidence is searched in the zip code dict.
        for key, data in zipcode_dict.items():
            if data['ZipNoFormat'].startswith(zipcode_clean):
                return data['distrito'], data['concelho'], 'undefined'
    
    # For a zip code of 7 digits, an exact coincidence is searched
    if len(zipcode_clean) >= 7:
        location_data = zipcode_dict.get(zipcode_clean, {})
        if location_data:
            return location_data['distrito'], location_data['concelho'], location_data['freguesia']
        else:
            # If there is no coincidence, partial matches are searched (not common)
            for key, data in zipcode_dict.items():
                if data['ZipNoFormat'].startswith(zipcode_clean):
                    return data['distrito'], data['concelho'], data['freguesia']
    
    # If there are no matches, 'undefined' is the default value
    return 'undefined', 'undefined', 'undefined'


def get_nuts_data(concelho: str, nuts_dict: Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]) -> Tuple[str, str, str]:
    """
    Retrieves the NUTS (Nomenclature of Territorial Units for Statistics) levels based on the provided area. From NUTSI down to NUTSIII.

    Args:
    - area (str): The name or identifier of the area to search for in the NUTS hierarchy. The area will be always a concelho/municipality.
                  Distritos and Freguesías are not included in the NUTS dictionary but for all of them, a respective concelho or distrito value is present.
                  In case of not having a concelho name (f.e. dicofre=distrito code with only 2 digits) the NUTS level will only cover NUTS III.
    - nuts_dict (Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]): A dictionary containing NUTS levels.
      The structure is assumed to be:
      {
          NUTS 1 (Name): {
              "NUTS 2": {
                  NUTS 2 (Name): {
                      "NUTS 3": {
                          NUTS 3 (Name): {
                              "Municipalities": [
                                  Concelho (name 1),
                                  Concelho (name 2)...
                                  ]
                                }
                            }
                        }
                    }
                }
            }
            
    Returns:
    - Tuple[str, str, str]: A tuple containing the NUTS 1, NUTS 2, and NUTS 3 regions. If not found, returns 'undefined' for each level.
    """
    nuts1 = 'undefined'
    nuts2 = 'undefined'
    nuts3 = 'undefined'
    # Split the keys and the values contained in the nuts dictionary
    for nuts1_region, nuts1_info in nuts_dict.items():
        for region_nuts2, nuts2_info in nuts1_info.get("NUTS 2", {}).items():
            for nuts3_region, nuts3_data in nuts2_info.get("NUTS 3", {}).items():
                if concelho in nuts3_data.get("Municipalities", []): # If concelho matches any municipality
                    return nuts1_region, region_nuts2, nuts3_region # Returns all the NUTS levels
    return nuts1, nuts2, nuts3


def add_geodata(final_data_path, dicofre_dict, zipcode_dict, nuts_dict):
    for filename in os.listdir(final_data_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(final_data_path, filename)
            print(f"Processing file: {file_path}") # Iterate and process all CSV files from the given path

            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter=';')
                headers = next(reader)
                headers = [header.lstrip('\ufeff') for header in headers] # Clears 'BOM' in any header
                headers.extend(['distrito', 'concelho', 'freguesia', 'nuts1', 'nuts2', 'nuts3']) # Complete the headers with the six new parameters

                zip_col_idx = next((i for i, h in enumerate(headers) if h in ['Zip Code', 'ZipCode']), None) # Given diferent namings for the zip code columns, takes just the index for the first coincidence. Same process for dicofre.
                dicofre_col_idx = next((i for i, h in enumerate(headers) if h in ['DistrictMunicipalityParishCode', 'CodDistritoConcelhoFreguesia', 'DistrictMunicipalityCode', 'MinicipalityCode', 'CodConcelho', 'CODIGO_CONCELHO']), None)

                if zip_col_idx is None and dicofre_col_idx is None:
                    print(f"No se encontró la columna de dicofre ni zip code en el archivo: {file_path}")
                    continue

                new_rows = []
                for row in reader: # The default values for the new rows are: 'undefined'
                    distrito, concelho, freguesia = 'undefined', 'undefined', 'undefined'
                    nuts1, nuts2, nuts3 = 'undefined', 'undefined', 'undefined'
                    
                    if zip_col_idx is not None: # If there is a zip code column in the file
                        zipcode = re.sub(r'[^0-9]', '', row[zip_col_idx]) # For every row in the file, clears any value placed in the same index as the zip code header
                        if zipcode:
                            distrito, concelho, freguesia = get_location_data_zipcode(zipcode, zipcode_dict) # Use the zip code value and the zip code dictionary to get the location data
                            if concelho != 'undefined':
                                area = concelho
                                nuts1, nuts2, nuts3 = get_nuts_data(area, nuts_dict)
                                if concelho == 'undefined':
                                    if len(zipcode) >= 2:
                                        partial_zipcode = zipcode[:2]
                                        if partial_zipcode[0] in s.continental_zipcode: # Continental Portugal first digit from the zipcode
                                            nuts1 = 'Continental Portugal'
                                        elif partial_zipcode == s.madeira_dicode: # Madeira first 2 zip code digits
                                            nuts1 = 'Região Autónoma dos Madeira'
                                        elif partial_zipcode == s.açores_dicode: # Azores first 2 zip code digits
                                            nuts1 = 'Região Autónoma dos Açores'
                                    elif len(zipcode) == 1:
                                        partial_zipcode = zipcode[0]
                                        if partial_zipcode in s.continental_zipcode: # Continental Portugal starting digit
                                            nuts1 = 'Continental Portugal'
                                        elif partial_zipcode == '9': # Overseas (both Madeira and Açores) starting digits
                                            nuts1 = 'Overseas Portugal'

                    elif dicofre_col_idx is not None: # If there is a dicofre column in the file
                        dicofre = re.sub(r'[^0-9]', '', row[dicofre_col_idx]) # For every row in the file, clears any value placed in the same index as the dicofre header
                        if dicofre:
                            distrito, concelho, freguesia = get_location_data_dicofre(dicofre, dicofre_dict) # Use the dicofre value and the dicofre dictionary to get the location data
                            if concelho != 'undefined':
                                area = concelho
                                nuts1, nuts2, nuts3 = get_nuts_data(area, nuts_dict)
                            elif concelho == 'undefined':
                                if dicofre[:2] in s.continental_dicode: # Continental Portugal first 2 distrito digits
                                    nuts1 = 'Continental Portugal'
                                elif dicofre[:2] in s.madeira_dicode: # Madeira first 2 distrito digits
                                    nuts1 = 'Região Autónoma dos Madeira'
                                elif dicofre[:2] in s.açores_dicode: # Açores first 2 distrito digits
                                    nuts1 = 'Região Autónoma dos Açores'

                    row.extend([distrito, concelho, freguesia, nuts1, nuts2, nuts3])
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