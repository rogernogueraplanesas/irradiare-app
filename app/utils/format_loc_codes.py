import csv
import json
import os

import settings as s

def format_dicofre_dict(dicofre_path):
    # Leer el archivo JSON original
    with open(dicofre_path, 'r', encoding='utf-8') as dicofre_file:
        dicofre_data = json.load(dicofre_file)

    # Formatear los datos
    formatted_data = {
        item['dicofre']: {
            'distrito': item['distrito'],
            'concelho': item['concelho'],
            'freguesia': item['freguesia']
        } for item in dicofre_data['data']
    }

    # Obtener el directorio del archivo original
    dir_path = os.path.dirname(dicofre_path)
    # Crear la ruta para el nuevo archivo JSON
    new_json_path = os.path.join(dir_path, 'dicofre.json')

    # Guardar los datos formateados en el nuevo archivo JSON
    with open(new_json_path, 'w', encoding='utf-8') as new_dicofre_file:
        json.dump(formatted_data, new_dicofre_file, ensure_ascii=False, indent=4)


def clean_header(header):
    # Limpiar encabezado eliminando BOM y espacios no deseados
    return header.strip().lstrip('\ufeff').strip()

def format_zipcode_data(zipcode_path):
    zipcode_dict = {}
    
    with open(zipcode_path, 'r', encoding='utf-8') as zip_file:
        reader = csv.DictReader(zip_file, delimiter=';')
        
        # Clean BOM from headers
        headers = [clean_header(header) for header in reader.fieldnames]

        for row in reader:
            # Clean row values using cleaned headers
            clean_row = {clean_header(header): row.get(header, '').strip() for header in reader.fieldnames}
            # Verify header values
            zip_code = clean_row.get('ZipCode', '')
            zipcode_dict[zip_code] = {
                'distrito': clean_row.get('Distrito', 'undefined'),
                'concelho': clean_row.get('Concelho', 'undefined'),
                'freguesia': clean_row.get('Freguesia', 'undefined'),
                'ZipNoFormat': clean_row.get('ZipNoFormat', '')
            }
    
    # Get the directory of the input CSV file
    dir_path = os.path.dirname(zipcode_path)
    # Create the path for the output JSON file named 'zipcodes.json'
    json_path = os.path.join(dir_path, 'zipcodes.json')
    
    # Save the dictionary as a JSON file
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(zipcode_dict, json_file, ensure_ascii=False, indent=4)



#format_dicofre_dict(dicofre_path = s.original_dicofre_data)

format_zipcode_data(zipcode_path = s.original_zipcode_data)


