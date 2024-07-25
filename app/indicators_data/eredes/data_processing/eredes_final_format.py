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


# Asegurarse de que el directorio de salida existe
os.makedirs(s.eredes_final_data, exist_ok=True)

# Definición de las columnas de tiempo
date_cols = ["Date"]
year_cols = ["Year", "ANO", "year", "ano"]
month_cols = ["Month", "month", "mes"]
semester_cols = ["Semester"]
quarter_cols = ["Quarter"]


#/////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////       ADDING TIMECODES       //////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////

# Funciones de manejo de fechas
def clean_date(value):
    return re.sub(r'[^SQsq0-9]', '', value).upper()

def combine_year_with_period(year, period):
    return year + period

def extract_date(value):
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    return date_match.group(1).replace("-", "") if date_match else clean_date(value)

def get_column_indices(headers, column_groups):
    """
    Devuelve un diccionario con los nombres de las columnas y sus índices si están presentes en headers.
    """
    column_indices = {}
    header_map = {col.lower(): idx for idx, col in enumerate(headers)}

    for group_name, column_names in column_groups.items():
        for col_name in column_names:
            col_name_lower = col_name.lower()
            if col_name_lower in header_map:
                column_indices[group_name] = header_map[col_name_lower]
                break  # Encuentra la primera coincidencia y sale del bucle
        else:
            column_indices[group_name] = None  # Si no se encontró ninguna coincidencia

    return column_indices

def add_timecode(merged_files_path, final_data_path):
    for filename in os.listdir(merged_files_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(merged_files_path, filename)
            print(f"Procesando archivo: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file, delimiter=';')
                headers = next(reader)
                
                # Limpiar BOM en los encabezados
                headers = [header.lstrip('\ufeff') for header in headers]

                # Definir grupos de nombres de columnas
                column_groups = {
                    'date': date_cols,
                    'year': year_cols,
                    'month': month_cols,
                    'semester': semester_cols,
                    'quarter': quarter_cols
                }

                # Encontrar los índices de las columnas de interés
                column_indices = get_column_indices(headers, column_groups)

                date_idx = column_indices.get('date', None)
                year_idx = column_indices.get('year', None)
                month_idx = column_indices.get('month', None)
                semester_idx = column_indices.get('semester', None)
                quarter_idx = column_indices.get('quarter', None)

                # Agregar nueva columna para 'timecode'
                headers.insert(0, "timecode")
                new_rows = []

                for row in reader:
                    new_row = row.copy()
                    timecode = ""

                    # Generar timecode basado en los índices encontrados
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

            # Guardar el archivo procesado
            output_file_path = os.path.join(final_data_path, f"temp_timecode_{filename}")
            with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
                writer = csv.writer(output_file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(new_rows)

            print(f"Archivo procesado y guardado en: {output_file_path}")

            # Eliminar el archivo original
            os.remove(file_path)
            print(f"Archivo original eliminado: {file_path}")

    # Delete the empty directory for the merged files
    os.rmdir(merged_files_path)

#/////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////     ADDING GEOLOCATION DATA     ////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////

def load_dicofre_data(dicofre_path):
    with open(dicofre_path, 'r', encoding='utf-8') as dicofre_file:
        return json.load(dicofre_file)
 
def load_zipcode_data(zipcode_path):
    with open(zipcode_path, 'r', encoding='utf-8') as zipcode_file:
        return json.load(zipcode_file)
    
def load_nuts_data(nuts_path):
    with open(nuts_path, 'r', encoding='utf-8') as nuts_file:
        return json.load(nuts_file)

# Obtener datos de localización
def get_location_data_dicofre(zipcode, zip_dict):
    zipcode_str = str(zipcode)
    location_data = {}
    distrito = 'undefined'
    concelho = 'undefined'
    freguesia = 'undefined'
    if len(zipcode_str) >= 6:
        location_data = zip_dict.get(zipcode_str, {})
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
        freguesia = location_data.get('freguesia', 'undefined')
    elif len(zipcode_str) >= 4:
        for key, data in zip_dict.items():
            if key.startswith(zipcode_str[:4]):
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
    elif len(zipcode_str) >= 2 and not location_data:
        for key, data in zip_dict.items():
            if key.startswith(zipcode_str[:2]):
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
    return distrito, concelho, freguesia

def get_location_data_zipcode(zipcode, zipcode_dict):
    # Limpiar el código postal eliminando caracteres no numéricos
    zipcode_clean = re.sub(r'[^0-9]', '', zipcode)

    # Si el código postal tiene 4 dígitos, solo buscamos distrito y concelho
    if len(zipcode_clean) == 4:
        # Buscar coincidencia parcial en ZipNoFormat
        for key, data in zipcode_dict.items():
            if data['ZipNoFormat'].startswith(zipcode_clean):
                return data['distrito'], data['concelho'], 'undefined'
    
    # Si el código postal tiene 7 dígitos o más, buscamos coincidencia exacta
    if len(zipcode_clean) >= 7:
        location_data = zipcode_dict.get(zipcode_clean, {})
        if location_data:
            return location_data['distrito'], location_data['concelho'], location_data['freguesia']
        else:
            # Buscar coincidencia parcial en ZipNoFormat
            for key, data in zipcode_dict.items():
                if data['ZipNoFormat'].startswith(zipcode_clean):
                    return data['distrito'], data['concelho'], data['freguesia']
    
    # Si no se encontró coincidencia, devolver valores predeterminados
    return 'undefined', 'undefined', 'undefined'

def get_nuts_data(area, nuts_dict):
    nuts1 = 'undefined'
    nuts2 = 'undefined'
    nuts3 = 'undefined'
    for nuts1_region, nuts1_info in nuts_dict.items():
        for region_nuts2, nuts2_info in nuts1_info.get("NUTS 2", {}).items():
            for nuts3_region, nuts3_data in nuts2_info.get("NUTS 3", {}).items():
                if area == nuts3_region:
                    return nuts1_region, region_nuts2, nuts3_region
                if area in nuts3_data.get("Municipalities", []):
                    return nuts1_region, region_nuts2, nuts3_region
            if area == region_nuts2:
                return nuts1_region, region_nuts2, nuts3
    return nuts1, nuts2, nuts3

# Añadir datos geográficos a los archivos CSV
def add_geodata(final_data_path, dicofre_dict, zipcode_dict, nuts_dict):
    for filename in os.listdir(final_data_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(final_data_path, filename)
            print(f"Procesando archivo: {file_path}")

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
                            area = concelho if concelho != 'undefined' else distrito
                            nuts1, nuts2, nuts3 = get_nuts_data(area, nuts_dict)
                            if nuts2 != 'undefined' and nuts3 != 'undefined' and area == distrito:
                                nuts3 = 'undefined'
                    elif dicofre_col_idx is not None:
                        dicofre = re.sub(r'[^0-9]', '', row[dicofre_col_idx])
                        if dicofre:
                            distrito, concelho, freguesia = get_location_data_dicofre(dicofre, dicofre_dict)
                            area = concelho if concelho != 'undefined' else distrito
                            nuts1, nuts2, nuts3 = get_nuts_data(area, nuts_dict)
                            if nuts2 != 'undefined' and nuts3 != 'undefined' and area == distrito:
                                nuts3 = 'undefined'

                    row.extend([distrito, concelho, freguesia, nuts1, nuts2, nuts3])
                    new_rows.append(row)

            with open(final_data_path, 'w', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(new_rows)

            print(f"Archivo procesado y guardado en: {final_data_path}")

# Ejecutar las funciones
add_timecode(merged_files_path = s.eredes_merged, final_data_path = s.eredes_final_data)
dicofre_dict = load_dicofre_data(dicofre_path= s.dicofre_data)
zipcode_dict = load_zipcode_data(zipcode_path = s.zipcode_data)
nuts_dict = load_nuts_data(nuts_path = s.nuts_data)
add_geodata(final_data_path = s.eredes_final_data, dicofre_dict = dicofre_dict, zipcode_dict = zipcode_dict, nuts_dict = nuts_dict)
