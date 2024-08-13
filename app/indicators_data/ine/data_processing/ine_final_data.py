import os
import json
import csv

# Rutas de las carpetas
data_folder = "app/indicators_data/ine/ine_data/raw/"
metadata_folder = "app/indicators_data/ine/ine_metadata/"

# Obtener los nombres de los archivos en ambas carpetas
data_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
metadata_files = [f for f in os.listdir(metadata_folder) if f.endswith('.json')]

# Extraer los identificadores numéricos de los nombres de los archivos
data_ids = {f.split('_')[1].split('.')[0] for f in data_files}
metadata_ids = {f.split('_')[1].split('.')[0] for f in metadata_files}

# Encontrar los identificadores que están presentes en ambas carpetas
matching_ids = data_ids.intersection(metadata_ids)

# Diccionario para almacenar metadatos
metadata_dict = {}

# Leer y procesar los archivos de metadata
for file_id in matching_ids:
    metadata_filename = f"metadata_{file_id}.json"
    with open(os.path.join(metadata_folder, metadata_filename), 'r', encoding='utf-8') as metadata_file:
        metadata_json = json.load(metadata_file)
        indicador_cod = metadata_json[0]["IndicadorCod"]
        unidades_medida = metadata_json[0].get("UnidadeMedida", "")
        dimensiones = {dim["dim_num"]: dim["abrv"] for dim in metadata_json[0]["Dimensoes"]["Descricao_Dim"]}
        metadata_dict[indicador_cod] = {"units": unidades_medida, "dimensiones": dimensiones}

# Leer y procesar los archivos de data
for file_id in matching_ids:
    data_filename = f"data_{file_id}.json"
    combined_data = []
    with open(os.path.join(data_folder, data_filename), 'r', encoding='utf-8') as data_file:
        data_json = json.load(data_file)
        indicador_cod = data_json[0].get("IndicadorCod", "")
        indicador_dsg = data_json[0].get("IndicadorDsg", "")
        datos = data_json[0].get("Dados", {})
        
        for timecode, registros in datos.items():
            for registro in registros:
                geocod = registro.get("geocod", "")
                geolevel = registro.get("geodsg", "")
                value = registro.get("valor", "")
                
                # Validar geocod
                if not geocod.isdigit() or len(geocod) < 4:
                    geocod = ""

                # Inicializar entrada combinada
                combined_entry = {
                    "source_cod": indicador_cod,
                    "name": indicador_dsg,
                    "description": "",
                    "geocode": geocod,
                    "geolevel": geolevel,
                    "value": value,
                    "timecode": timecode
                }

                # Agregar filtros (dim_3_t, dim_4_t, etc.)
                filter_values = {f"filter_value{dim_num}": registro.get(f"dim_{dim_num}_t", "")
                                 for dim_num in range(3, 10) if f"dim_{dim_num}_t" in registro}

                # Combinar los filtros en la entrada
                combined_entry.update(filter_values)

                # Obtener unidades y dimensiones desde metadata
                metadata = metadata_dict.get(indicador_cod, {})
                combined_entry["units"] = metadata.get("units", "")
                
                # Agregar los valores de las dimensiones desde metadata
                for dim_num in range(3, 10):
                    filter_key = f"filter_value{dim_num}"
                    if filter_key in combined_entry:
                        combined_entry[f"dimension_{dim_num}"] = metadata.get("dimensiones", {}).get(str(dim_num), "")

                combined_data.append(combined_entry)

    # Determinar los nombres de las columnas del CSV a partir de las claves del primer elemento en combined_data
    fieldnames = list(set().union(*(entry.keys() for entry in combined_data)))

    # Guardar los datos combinados en un archivo CSV separado
    output_filename = f'app/indicators_data/ine/ine_data/processed/combined_data_{file_id}.csv'
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escribir los encabezados
        writer.writeheader()
        
        # Escribir las filas
        for entry in combined_data:
            writer.writerow(entry)

    print(f'Archivo CSV generado: {output_filename}')
