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
    return re.sub(r'\W+', '', value)

def combine_year_with_period(year, period):
    return year + period



#### PROBLEMA!!!! SEMBLA QUE LLEGEIX ELS HEADERS I AGAFA POSICIONS INCORRECTES JA QUE ESCRIU DADES D'ALTRES COLUMNES


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
                        date_idx = idx
                        break

                # Si hay columna 'Date', procesar solo esa columna
                if date_idx is not None:
                    for row in rows:
                        new_row = row.copy()
                        timecode = clean_date(row[date_idx])
                        new_row.insert(0, timecode)
                        new_rows.append(new_row)

                else:
                    # Buscar columnas 'Year', 'Month', 'Semester', 'Quarter'
                    for idx, col in enumerate(headers):
                        col_lower = col.lower()
                        if date_idx is None and any(dc.lower() in col_lower for dc in date_cols):
                            date_idx = idx
                        elif year_idx is None and any(yc.lower() in col_lower for yc in year_cols):
                            year_idx = idx
                        elif month_idx is None and any(mc.lower() in col_lower for mc in month_cols):
                            month_idx = idx
                        elif semester_idx is None and any(sc.lower() in col_lower for sc in semester_cols):
                            semester_idx = idx
                        elif quarter_idx is None and any(qc.lower() in col_lower for qc in quarter_cols):
                            quarter_idx = idx

                    # Procesar combinación de 'Year' con 'Month', 'Semester' o 'Quarter'
                    for row in rows:
                        new_row = row.copy()
                        timecode = ""

                        if year_idx is not None:
                            year_value = row[year_idx] if year_idx < len(row) else ""
                            if month_idx is not None and month_idx < len(row) and len(row[month_idx]) <= 2:
                                month_value = row[month_idx]
                                timecode = combine_year_with_period(year_value, month_value)
                            elif semester_idx is not None and semester_idx < len(row) and len(row[semester_idx]) <= 2:
                                semester_value = row[semester_idx]
                                timecode = combine_year_with_period(year_value, semester_value)
                            elif quarter_idx is not None and quarter_idx < len(row) and len(row[quarter_idx]) <= 2:
                                quarter_value = row[quarter_idx]
                                timecode = combine_year_with_period(year_value, quarter_value)
                            elif quarter_idx is not None:
                                timecode = clean_date(row[quarter_idx])

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
    with open(nuts_path, 'r', encoding = 'utf-8') as nuts_file:
        nuts_dict = json.load(nuts_file)
    return nuts_dict


def get_location_data(zipcode, zip_dict):
    zipcode_str = str(zipcode)
    location_data = {}
    distrito = 'undefined'
    concelho = 'undefined'
    freguesia = 'undefined'

    if len(zipcode_str) == 6:
        # Buscar en el diccionario de zipcodes para zipcode completo de 6 cifras
        location_data = zip_dict.get(zipcode_str, {})
        # Extraer 'distrito', 'concelho' y 'freguesia' si están disponibles
        distrito = location_data.get('distrito', 'undefined')
        concelho = location_data.get('concelho', 'undefined')
        freguesia = location_data.get('freguesia', 'undefined')

    elif len(zipcode_str) == 4:
            for key, data in zip_dict.items():
                if key.startswith(zipcode_str):
                    location_data = data
                    break
            # Extraer 'distrito' y 'concelho' si están disponibles
            distrito = location_data.get('distrito', 'undefined')
            concelho = location_data.get('concelho', 'undefined')

    elif len(zipcode_str) == 2:
            for key, data in zip_dict.items():
                if key.startswith(zipcode_str):
                    location_data = data
                    break
            # Extraer solo 'distrito' si está disponible
            distrito = location_data.get('distrito', 'undefined')
    else:
        # Código postal con longitud incorrecta
        return distrito, concelho, freguesia
    
    print(distrito, concelho, freguesia)
    return distrito, concelho, freguesia


def get_nuts_data(area, nuts_dict):
    nuts1 = 'PT'
    nuts2 = 'undefined'
    nuts3 = 'undefined'

    # Iterar a través de todas las regiones principales
    for region, nuts_info in nuts_dict.items():
        # Iterar a través de las regiones NUTS 2
        for region_nuts2, nuts2_info in nuts_info.get("NUTS 2", {}).items():
            # Verificar si el área está en los municipios de NUTS 2
            for nuts3_region, nuts3_data in nuts2_info.get("NUTS 3", {}).items():
                if area in nuts3_data.get("Municipalities", []):
                    nuts2 = region_nuts2
                    nuts3 = nuts3_region
                    print(nuts1, nuts2, nuts3)
                    return nuts1, nuts2, nuts3

            # Si no se encuentra en los municipios, verificar las regiones NUTS 3
            for nuts3_region in nuts2_info.get("NUTS 3", {}).keys():
                if area == nuts3_region:
                    nuts2 = region_nuts2
                    nuts3 = nuts3_region
                    print(nuts1, nuts2, nuts3)
                    return nuts1, nuts2, nuts3

            # Si no se encuentra en las regiones NUTS 3, verificar NUTS 2
            if area == region_nuts2:
                nuts2 = region_nuts2
                print(nuts1, nuts2, nuts3)
                return nuts1, nuts2, nuts3
    return nuts1, nuts2, nuts3




add_timecode(temp_merged=temp_merged, output_path=output_path)




    # Cargar los diccionarios
    #zipcode_dict = format_zipcode_dict()
    #nuts_dict = load_nuts_data()

    # Obtener los datos de ubicación (distrito y concelho)
    #distrito, concelho, freguesia = get_location_data("010109", zip_dict=zipcode_dict)

    # Determinar la ubicación a usar para get_nuts_data
    #area = concelho if concelho != 'undefined' else distrito

    # Obtener los datos de NUTS basados en la ubicación determinada
    #nuts1, nuts2, nuts3 = get_nuts_data(area=area, nuts_dict=nuts_dict)

    # Verificar si el área es igual al distrito para ajustar nuts3
    #if nuts2 != 'undefined' and nuts3 != 'undefined' and area == distrito:
        #nuts3 = 'undefined'

    # Mostrar los resultados
    #print(f"Distrito: {distrito}, Concelho: {concelho}, Freguesia: {freguesia}")
    #print(f"NUTS1: {nuts1}, NUTS2: {nuts2}, NUTS3: {nuts3}")





