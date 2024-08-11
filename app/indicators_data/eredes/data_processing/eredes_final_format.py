from typing import List, Dict, Union, Any, Tuple

import csv
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the path of the root directory (irradiare-app)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Add the path to sys.path
sys.path.append(irradiare_app_path)

# Import settings
import app.utils.settings as s

# Function to clean 'Date' columns
def clean_date(value: str) -> str:
    return re.sub(r'[^SQsq0-9]', '', value).upper()

# Function used to create a timecode combining year+period (month, semester, quarter)
def combine_year_with_period(year: str, period: str) -> str:
    return year + period

def extract_date(value: str) -> str:
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    return date_match.group(1).replace("-", "") if date_match else clean_date(value)

def get_column_indices(headers: List[str], column_groups: Dict[str, List[str]]) -> Dict[str, Union[int, None]]:
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

    print(f"Archivo procesado y guardado en: {output_file_path}")
    os.remove(file_path)
    print(f"Archivo original eliminado: {file_path}")

def add_timecode(merged_files_path: str, final_data_path: str) -> None:
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


# Función para obtener datos de localización a partir de un código dicofre
def get_location_data_dicofre(dicofre: Union[int, str], dicofre_dict: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
    dicofre_str = str(dicofre)
    location_data = {}
    distrito = 'undefined'
    concelho = 'undefined'
    freguesia = 'undefined'
    
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

# Función para obtener datos de localización a partir de un código postal
def get_location_data_zipcode(zipcode: Union[int, str], zipcode_dict: Dict[str, Dict[str, str]]) -> Tuple[str, str, str]:
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

# Función para obtener datos NUTS a partir de un concelho
def get_nuts_data(concelho: str, nuts_dict: Dict[str, Dict[str, Dict[str, Union[Dict[str, str], List[str]]]]]) -> Tuple[str, str, str]:
    nuts1 = 'undefined'
    nuts2 = 'undefined'
    nuts3 = 'undefined'
    
    for nuts1_region, nuts1_info in nuts_dict.items():
        for region_nuts2, nuts2_info in nuts1_info.get("NUTS 2", {}).items():
            for nuts3_region, nuts3_data in nuts2_info.get("NUTS 3", {}).items():
                if concelho in nuts3_data.get("Municipalities", []):
                    return nuts1_region, region_nuts2, nuts3_region
    
    return nuts1, nuts2, nuts3

# Función para añadir datos de geolocalización a archivos CSV
def add_geodata(final_data_path, dicofre_dict, zipcode_dict, nuts_dict):
    for filename in os.listdir(final_data_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(final_data_path, filename)
            print(f"Processing file: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter=';')
                headers = next(reader)
                headers = [header.lstrip('\ufeff') for header in headers]
                headers.extend(['distrito', 'concelho', 'freguesia', 'nuts1', 'nuts2', 'nuts3'])

                zip_col_idx = next((i for i, h in enumerate(headers) if h in ['Zip Code', 'ZipCode']), None)
                dicofre_col_idx = next((i for i, h in enumerate(headers) if h in ['DistrictMunicipalityParishCode', 'CodDistritoConcelhoFreguesia', 'DistrictMunicipalityCode', 'MinicipalityCode', 'CodConcelho', 'CODIGO_CONCELHO']), None)

                if zip_col_idx is None and dicofre_col_idx is None:
                    print(f"No se encontró la columna de dicofre ni zip code en el archivo: {file_path}")
                    continue

                new_rows = []
                for row in reader:
                    distrito, concelho, freguesia = 'undefined', 'undefined', 'undefined'
                    nuts1, nuts2, nuts3 = 'undefined', 'undefined', 'undefined'

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
                                        if partial_zipcode[0] in s.continental_zipcode:
                                            nuts1 = 'Continental Portugal'
                                        elif partial_zipcode == s.madeira_dicode:
                                            nuts1 = 'Região Autónoma dos Madeira'
                                        elif partial_zipcode == s.açores_dicode:
                                            nuts1 = 'Região Autónoma dos Açores'
                                    elif len(zipcode) == 1:
                                        partial_zipcode = zipcode[0]
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
                                elif dicofre[:2] in s.madeira_dicode:
                                    nuts1 = 'Região Autónoma dos Madeira'
                                elif dicofre[:2] in s.açores_dicode:
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