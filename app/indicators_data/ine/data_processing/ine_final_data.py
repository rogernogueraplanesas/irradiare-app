import csv
import re
import os
import json
from typing import Dict, Any

def get_timecode_area(headers):
    timecode_idx = next((i for i, h in enumerate(headers) if h in ['timecode']), None)
    area_idx = next((i for i, h in enumerate(headers) if h in ["area"]), None)
    return timecode_idx, area_idx

def clean_timecode(row, timecode_idx):
    timecode = row[timecode_idx]
    timecode = re.sub(r'[^0-9]', '', timecode)
    return timecode

def load_nuts_data(nuts_path: str) -> Dict[str, Any]:
    with open(nuts_path, 'r', encoding='utf-8') as nuts_file:
        return json.load(nuts_file)
    
def load_dicofre_data(dicofre_path: str) -> Dict[str, Any]:
    with open(dicofre_path, 'r', encoding='utf-8') as dicofre_file:
        return json.load(dicofre_file)

    
def match_location(name, dicofre_data):
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



def match_nuts_location(area, dicofre_data, nuts_dict):
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

folder = "app/indicators_data/ine/ine_data/processed/"
os.makedirs(folder, exist_ok=True)

for filename in os.listdir(folder):
    if filename.endswith('.csv'):
        csv_file = os.path.join(folder, filename)
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                headers = next(reader)
            except StopIteration:
                print(f"Archivo vacío: {filename}")
                continue  # Saltar archivo vacío
            
            # Verificar si las columnas necesarias existen
            timecode_idx, area_idx = get_timecode_area(headers)
            if timecode_idx is None or area_idx is None:
                print(f"Archivo no tiene las columnas necesarias: {filename}")
                continue

            headers.extend(['distrito', 'concelho', 'freguesia', 'nuts1', 'nuts2', 'nuts3'])
            dicofre_file = load_dicofre_data("app/utils/loc_codes/dicofre.json")
            nuts_file = load_nuts_data("app/utils/nuts_levels/NUTS.json")
            new_rows = []
            for row in reader:
                row[timecode_idx] = clean_timecode(row, timecode_idx)
                area = row[area_idx]
                distrito, concelho, freguesia, nuts1, nuts2, nuts3 = match_nuts_location(area, dicofre_file, nuts_file)
                row.extend([distrito, concelho, freguesia, nuts1, nuts2, nuts3])
                new_rows.append(row)

        output_file = os.path.join(folder, filename)
        with open(output_file, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(headers)
            writer.writerows(new_rows)

        print(f"Archivo procesado y guardado en: {output_file}")
