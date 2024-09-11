import csv
import os


def cargar_datos(archivo_datos):
    with open(archivo_datos, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Saltar las primeras dos líneas y las líneas en blanco
        for _ in range(3):
            next(reader)  # Omitir las dos primeras líneas
        
        # Leer hasta llegar a los encabezados (eliminando posibles líneas en blanco)
        headers = []
        while not headers:
            headers = next(reader)  # Leer los encabezados (que es la primera fila no vacía)
        
        # Leer el resto de los datos
        datos = list(reader)
    
    print("Data loaded.")
    return headers, datos

# Función para cargar el archivo de metadatos
def cargar_metadatos(archivo_metadata):
    with open(archivo_metadata, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar encabezado
        metadatos = {row[0]: {'name': row[1], 'description': row[2], 'source': row[3]} for row in reader}
    print("Metadata loaded.")
    return metadatos

# Función para generar archivos CSV por indicador
def generar_csv_por_indicador(headers, datos, metadatos, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Iterar sobre cada fila de datos
    for row in datos:
        indicator_name = row[2]
        indicator_code = row[3]

        # Si no tiene un código de indicador, continuar
        if not indicator_code:
            continue

        # Buscar el código de indicador en los metadatos
        if indicator_code not in metadatos:
            print(f"Metadatos no encontrados para el indicador: {indicator_code}")
            continue
        
        # Obtener la descripción y fuente del indicador desde metadatos
        metadata = metadatos[indicator_code]
        indicator_description = metadata['description']
        indicator_source = metadata['source']

        # Crear el archivo CSV para el indicador
        csv_filename = f"{indicator_code}.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)
        
        with open(csv_filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir encabezado
            writer.writerow(['timecode', 'source_code', 'name', 'description', 'value', 'source'])
            
            # Escribir datos por año (1960-2023)
            for i, year in enumerate(headers[4:], start=4):
                year_value = row[i]  # Obtener el valor del año
                if year_value:  # Si hay un valor para ese año
                    writer.writerow([headers[i], indicator_code, indicator_name, indicator_description, year_value, indicator_source])
        
        print(f"Archivo generado para {indicator_code}: {csv_filepath}")


headers, datos = cargar_datos("app/indicators_data/worldbank/wb_data/raw/API_PRT_DS2_en_csv_v2_3412148.csv")
metadatos = cargar_metadatos("app/indicators_data/worldbank/wb_metadata/Metadata_Indicator_API_PRT_DS2_en_csv_v2_3412148.csv")
generar_csv_por_indicador(headers=headers, datos=datos, metadatos=metadatos, output_dir="app/indicators_data/worldbank/wb_data/processed")
