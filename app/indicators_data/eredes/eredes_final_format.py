import os
import json
import csv
import re

temp_merged = "app/indicators_data/eredes/temp_eredes_merged/"
zip_path = "app/indicators_data/eredes/zip_codes/freguesias-metadata.json"
nuts_path = "app/indicators_data/eredes/NUTS_info/NUTS.json"
output_path = "app/indicators_data/eredes/eredes_final"

os.makedirs(output_path, exist_ok=True)

date_cols = ["Date"]
year_cols = ["Year", "ANO", "year", "ano"]
month_cols = ["Month", "month", "mes"]
semester_cols = ["Semester"]
quarter_cols = ["Quarter"]


#....................TIMECODE.....................

def clean_date(value):
    # Eliminar cualquier símbolo y cualquier letra que no sea S o Q
    value = re.sub(r'[^SQsq0-9]', '', value)
    return value.upper()

def combine_year_with_period(year, period):
    return year + period

def extract_date(value):
    # Extraer solo la parte de año, mes y día, ignorando la hora
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    if date_match:
        return date_match.group(1).replace("-", "")
    return clean_date(value)

def add_timecode(temp_merged, output_path):
    for filename in os.listdir(temp_merged):
        if filename.endswith(".csv"):
            file_path = os.path.join(temp_merged, filename)
            print(f"Procesando archivo: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as temp_file:
                # Leer el contenido del archivo y eliminar el BOM si está presente
                content = temp_file.read()
                content = content.lstrip('\ufeff')
                temp_file.seek(0)  # Volver al inicio del archivo después de leerlo

                # Dividir la primera línea del contenido para obtener los encabezados correctamente
                headers = content.splitlines()[0].split(';')

                # Leer el resto del contenido como filas de datos
                rows = [line.split(';') for line in content.splitlines()[1:]]

                # Agregar una nueva columna para 'timecode' al principio
                headers.insert(0, "timecode")

                # Nueva lista de filas con datos procesados
                new_rows = []

                # Buscar los índices de las columnas de interés
                date_idx = None
                year_idx = None
                month_idx = None
                semester_idx = None
                quarter_idx = None

                # Buscar la columna 'Date'
                for idx, col in enumerate(headers):
                    if any(dc.lower() in col.lower() for dc in date_cols):
                        date_idx = idx - 1
                        break

                # Si hay columna 'Date', procesar solo esa columna
                if date_idx is not None:
                    for row in rows:
                        new_row = row.copy()
                        timecode = extract_date(row[date_idx])
                        new_row.insert(0, timecode)
                        new_rows.append(new_row)
                else:
                    # Buscar columnas 'Year', 'Month', 'Semester', 'Quarter'
                    for idx, col in enumerate(headers):
                        col_lower = col.lower()
                        if year_idx is None and any(yc.lower() in col_lower for yc in year_cols):
                            year_idx = idx - 1
                        elif month_idx is None and any(mc.lower() in col_lower for mc in month_cols):
                            month_idx = idx - 1
                        elif semester_idx is None and any(sc.lower() in col_lower for sc in semester_cols):
                            semester_idx = idx - 1
                        elif quarter_idx is None and any(qc.lower() in col_lower for qc in quarter_cols):
                            quarter_idx = idx - 1

                    # Procesar combinación de 'Year' con 'Month', 'Semester' o 'Quarter'
                    for row in rows:
                        new_row = row.copy()
                        timecode = ""

                        if year_idx is not None:
                            year_value = row[year_idx] if year_idx < len(row) else ""
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
                        elif quarter_idx is not None and quarter_idx < len(row):
                            timecode = clean_date(row[quarter_idx])
                        elif semester_idx is not None and semester_idx < len(row):
                            timecode = clean_date(row[semester_idx])

                        new_row.insert(0, timecode)
                        new_rows.append(new_row)

                # Escribir los datos procesados en un nuevo archivo CSV
                output_file_path = os.path.join(output_path, f"temp_timecode_{filename}")
                with open(output_file_path, 'w', encoding='utf-8', newline='') as output_file:
                    writer = csv.writer(output_file, delimiter=';')
                    writer.writerow(headers)
                    writer.writerows(new_rows)

                print(f"Archivo procesado y guardado en: {output_file_path}")

            # Eliminar el archivo original después de haber cerrado su contexto de lectura
            os.remove(file_path)
            print(f"Archivo original eliminado: {file_path}")

#..................GEOCODE/DICOFRE/NUTSIII.....................

def format_zipcode_dict():
    with open(zip_path, 'r', encoding='utf-8') as zip_file:
        zip_data = json.load(zip_file)
        zip_dict = {item['dicofre']: {
            'distrito': item['distrito'],
            'concelho': item['concelho'],
            'freguesia': item['freguesia']
        } for item in zip_data['data']}
    return zip_dict

def load_nuts_data():
    with open(nuts_path, 'r', encoding='utf-8') as nuts_file:
        nuts_dict = json.load(nuts_file)
    return nuts_dict

def get_location_data(zipcode, zip_dict):
    zipcode_str = str(zipcode)
    location_data = {}
    distrito = 'undefined'
    concelho = 'undefined'
    freguesia = 'undefined'

    if len(zipcode_str) == 6:
        location_data = zip_dict.get(zipcode_str, {})
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
        freguesia = location_data.get('freguesia', 'undefined')
    elif len(zipcode_str) == 4:
        for key, data in zip_dict.items():
            if key.startswith(zipcode_str):
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
    elif len(zipcode_str) == 2:
        for key, data in zip_dict.items():
            if key.startswith(zipcode_str):
                location_data = data
                break
        distrito = location_data.get('distrito', 'undefined')
    return distrito, concelho, freguesia

def get_nuts_data(area, nuts_dict):
    nuts1 = 'PT'
    nuts2 = 'undefined'
    nuts3 = 'undefined'

    for region, nuts_info in nuts_dict.items():
        for region_nuts2, nuts2_info in nuts_info.get("NUTS 2", {}).items():
            for nuts3_region, nuts3_data in nuts2_info.get("NUTS 3", {}).items():
                if area in nuts3_data.get("Municipalities", []):
                    nuts2 = region_nuts2
                    nuts3 = nuts3_region
                    return nuts1, nuts2, nuts3
            for nuts3_region in nuts2_info.get("NUTS 3", {}).keys():
                if area == nuts3_region:
                    nuts2 = region_nuts2
                    nuts3 = nuts3_region
                    return nuts1, nuts2, nuts3
            if area == region_nuts2:
                nuts2 = region_nuts2
                return nuts1, nuts2, nuts3
    return nuts1, nuts2, nuts3

def add_geodata():
    zipcode_dict = format_zipcode_dict()
    nuts_dict = load_nuts_data()

    for filename in os.listdir(output_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(output_path, filename)
            print(f"Procesando archivo: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as csv_file:
                content = csv_file.read().lstrip('\ufeff')
                csv_file.seek(0)
                headers = content.splitlines()[0].split(';')
                rows = [line.split(';') for line in content.splitlines()[1:]]

                headers += ['distrito', 'concelho', 'freguesia', 'nuts1', 'nuts2', 'nuts3']

                new_rows = []

                for row in rows:
                    zipcode = None
                    for col_name in ['Zip Code', 'ZipCode', 'DistrictMunicipalityParishCode', 'CodDistritoConcelhoFreguesia', 'DistrictMunicipalityCode', 'CodConcelho', 'CODIGO_CONCELHO']:
                        if col_name in headers:
                            idx = headers.index(col_name)
                            if row[idx] not in ['OUTROS', '', None]:
                                value = row[idx]
                                value = re.sub(r'[^0-9]', '', value)
                                if len(value) in [2, 4, 6]:
                                    zipcode = value
                                    break

                    if zipcode:
                        distrito, concelho, freguesia = get_location_data(zipcode, zip_dict=zipcode_dict)
                        area = concelho if concelho != 'undefined' else distrito
                        nuts1, nuts2, nuts3 = get_nuts_data(area, nuts_dict=nuts_dict)
                        if nuts2 != 'undefined' and nuts3 != 'undefined' and area == distrito:
                            nuts3 = 'undefined'
                    else:
                        distrito, concelho, freguesia = 'undefined', 'undefined', 'undefined'
                        nuts1, nuts2, nuts3 = 'PT', 'undefined', 'undefined'

                    row += [distrito, concelho, freguesia, nuts1, nuts2, nuts3]
                    new_rows.append(row)

            with open(file_path, 'w', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(headers)
                writer.writerows(new_rows)


# Ejecutar la función
add_timecode(temp_merged=temp_merged, output_path=output_path)
add_geodata()