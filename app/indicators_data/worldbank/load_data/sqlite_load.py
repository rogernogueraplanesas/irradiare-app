import os
import csv
import sqlite3
import sqlite_queries as sq


def extract_and_save_row(input_csv, output_csv, row_number):
    # Extraer el nombre del archivo sin la extensión
    filename = os.path.basename(input_csv)

    # Inicializamos la variable last_row que devolveremos
    last_row = None

    # Leer el archivo original como texto
    with open(input_csv, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

        # Obtenemos la fila específica basada en el número de fila dado (contando desde 1)
        if row_number < len(lines):
            row = lines[row_number].strip()  # Remover espacios y saltos de línea
            # Dividir la fila en una lista usando el punto y coma como separador
            row_data = row.split(',')

            # Quitar las comillas dobles alrededor de los campos, si las hay
            row_data = [field.strip('"') for field in row_data]
        else:
            row_data = None

    # Comprobar si el archivo output_csv existe
    if not os.path.exists(output_csv):
        # Si no existe, crear el archivo con el filename y la fila de datos
        with open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
            outfile.write(f"{filename}\n")  # Escribir el nombre del archivo
            if row_data:
                outfile.write(f"{','.join(row_data)}\n")  # Escribir la fila de datos
            last_row = []  # La última fila es vacía inicialmente
    else:
        # Si existe, leemos el archivo existente
        with open(output_csv, 'r', encoding='utf-8') as outfile:
            existing_content = outfile.read()

        # Verificamos si ya está el filename
        if filename in existing_content:
            # Actualizamos la fila bajo el nombre del archivo si ya existe
            updated_content = ""
            lines = existing_content.splitlines()
            skip_next_line = False

            for line in lines:
                if line == filename:
                    updated_content += f"{filename}\n"
                    if row_data:
                        updated_content += f"{','.join(row_data)}\n"
                    skip_next_line = True  # Saltamos la línea siguiente (la fila anterior)
                elif skip_next_line:
                    skip_next_line = False  # Saltar la fila previa
                else:
                    updated_content += f"{line}\n"

            last_row = row_data
        else:
            # Si no está, agregamos el filename y la fila de datos al final
            updated_content = existing_content + f"{filename}\n"
            if row_data:
                updated_content += f"{','.join(row_data)}\n"
            last_row = []  # No hay fila anterior

        # Guardamos el contenido actualizado
        with open(output_csv, 'w', encoding='utf-8') as outfile:
            outfile.write(updated_content)

    return last_row

def insert_into_stagging(database, csv_folder):
    try:
        cursor = database.cursor()
        
        for filename in os.listdir(csv_folder):
            if filename.endswith('.csv'):
                file_path = os.path.join(csv_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as data_file:
                    last_row = extract_and_save_row(
                        input_csv=file_path,  # Pasamos la ruta del archivo CSV, no el objeto abierto
                        output_csv="app/indicators_data/worldbank/wb_data/savepoint.csv",
                        row_number=2
                    )
                    reader = csv.reader(data_file, delimiter=',')
                    headers = next(reader)

                    # Identificar índices de las columnas
                    timecode_idx = headers.index('timecode')
                    data_value_idx = headers.index('value')
                    name_indicator_idx = headers.index('name')
                    units_idx = headers.index('units')
                    units_desc_idx = headers.index('units_description')
                    source_idx = headers.index('source')
                    source_code_idx = headers.index('source_code')

                    for row in reader:
                        if row == last_row:
                            print(f"Se alcanzó la última fila: {last_row}. Deteniendo la inserción de más filas.")
                            break  # Salimos del loop para no procesar las filas posteriores
                        # Asignar valores, usar 'Undefined' como valor predeterminado
                        nuts1 = 'Portugal (all)'
                        nuts2 = 'Undefined'
                        nuts3 = 'Undefined'
                        geocode = 'Undefined'
                        type = 'Undefined'
                        distrito = 'Undefined'
                        concelho = 'Undefined'
                        freguesia = 'Undefined'
                        timecode = row[timecode_idx] if timecode_idx is not None else 'Undefined'
                        data_value = row[data_value_idx] if data_value_idx is not None else 'Undefined'
                        name_indicator = row[name_indicator_idx] if name_indicator_idx is not None else 'Undefined'
                        description = 'Undefined'
                        units = row[units_idx]  if units_idx is not None else 'Undefined'
                        units_desc = row[units_desc_idx]  if units_desc_idx is not None else 'Undefined'
                        calculation = 'Undefined'
                        source = row[source_idx] if source_idx is not None else 'Undefined'
                        source_code = row[source_code_idx] if source_code_idx is not None else 'Undefined'
                        attributes = 'Undefined'
                        name_attribute = 'Undefined'
                        value_attribute = 'Undefined'
                        value_tag = 'Undefined'


                        cursor.execute(sq.INSERT_DATA_STAGGING, (
                            nuts1, nuts2, nuts3, geocode, type, distrito, concelho, freguesia, timecode, data_value,
                            name_indicator, description, units, units_desc, calculation, source, source_code,
                            attributes, name_attribute, value_attribute, value_tag
                        ))

        print("Stagging completed.")
        database.commit()

    except Exception as e:
        database.rollback()
        print(f"Error al procesar el archivo {filename}: {e}")

    finally:
        cursor.close()

def stg_to_datawarehouse(database):
    cursor = database.cursor()

    try:
        cursor.execute('BEGIN TRANSACTION')
        cursor.execute('SELECT * FROM stg_table')
        rows = cursor.fetchall()

        for row in rows:
            row_dict = {
                'nuts1': row[0],
                'nuts2': row[1],
                'nuts3': row[2],
                'geocode': row[3],
                'type': row[4],
                'distrito': row[5],
                'concelho': row[6],
                'freguesia': row[7],
                'timecode': row[8],
                'data_value': row[9],
                'name_indicator': row[10],
                'description': row[11],
                'units': row[12],
                'units_desc': row[13],
                'calculation': row[14],
                'source': row[15],
                'source_code': row[16],
                'attributes': row[17],
                'name_attribute': row[18],
                'value_attribute': row[19],
                'value_tag': row[20]
            }

            # Inserción en la tabla `nuts`
            cursor.execute('INSERT OR IGNORE INTO nuts (nuts1, nuts2, nuts3) VALUES (?, ?, ?)', 
                           (row_dict['nuts1'], row_dict['nuts2'], row_dict['nuts3']))
            id_nuts = cursor.execute('SELECT id_nuts FROM nuts WHERE nuts1 = ? AND nuts2 = ? AND nuts3 = ?',
                                     (row_dict['nuts1'], row_dict['nuts2'], row_dict['nuts3'])).fetchone()[0]

            # Inserción en la tabla `geolevel`
            cursor.execute('INSERT OR IGNORE INTO geolevel (distrito, concelho, freguesia) VALUES (?, ?, ?)', 
                           (row_dict['distrito'], row_dict['concelho'], row_dict['freguesia']))
            id_geolevel = cursor.execute('SELECT id_geolevel FROM geolevel WHERE distrito = ? AND concelho = ? AND freguesia = ?',
                                         (row_dict['distrito'], row_dict['concelho'], row_dict['freguesia'])).fetchone()[0]

            # Inserción en la tabla `geodata`
            cursor.execute('INSERT OR IGNORE INTO geodata (id_nuts, id_geolevel, geocode, type) VALUES (?, ?, ?, ?)', 
                           (id_nuts, id_geolevel, row_dict['geocode'], row_dict['type']))
            id_geodata = cursor.execute('SELECT id_geodata FROM geodata WHERE id_nuts = ? AND id_geolevel = ? AND geocode = ? AND type = ?',
                                        (id_nuts, id_geolevel, row_dict['geocode'], row_dict['type'])).fetchone()[0]

            # Inserción en la tabla `indicator`
            cursor.execute('INSERT OR IGNORE INTO indicator (name, description, units, units_desc, calculation, source, source_code) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                           (row_dict['name_indicator'], row_dict['description'], row_dict['units'], row_dict['units_desc'],
                            row_dict['calculation'], row_dict['source'], row_dict['source_code']))
            id_indicator = cursor.execute('SELECT id_indicator FROM indicator WHERE name = ? AND source_code = ?',
                                          (row_dict['name_indicator'], row_dict['source_code'])).fetchone()[0]
            # Manejo del valor de 'data_value'
            data_value = row_dict['data_value']
            if not data_value:  # Verifica si 'data_value' está vacío o es None
                data_value = None  # Puedes usar None, 0.0 o un valor que haga sentido en tu aplicación

            # Inserción en la tabla `data_values`
            try:
                cursor.execute('INSERT INTO data_values (id_geodata, id_indicator, timecode, value, attributes) VALUES (?, ?, ?, ?, ?)', 
                               (id_geodata, id_indicator, row_dict['timecode'], float(data_value) if data_value else None, row_dict['attributes']))
                id_value = cursor.lastrowid
            except sqlite3.IntegrityError:
                print(f"Duplicado encontrado y saltado: {row_dict}")
                continue

            # Inserción en la tabla `attributes`
            if row_dict['name_attribute'] != 'Undefined' and row_dict['value_attribute'] != 'Undefined':
                cursor.execute('INSERT OR IGNORE INTO attributes (name, value) VALUES (?, ?)', 
                               (row_dict['name_attribute'], row_dict['value_attribute']))
                id_attribute = cursor.execute('SELECT id_attribute FROM attributes WHERE name = ? AND value = ?', 
                                              (row_dict['name_attribute'], row_dict['value_attribute'])).fetchone()[0]

                # Inserción en la tabla `val_attr`
                cursor.execute('INSERT OR IGNORE INTO val_attr (id_value, id_attribute) VALUES (?, ?)', 
                               (id_value, id_attribute))

            # Inserción en la tabla `tags`
            if row_dict['value_tag'] != 'Undefined':
                cursor.execute('INSERT OR IGNORE INTO tags (value) VALUES (?)', 
                               (row_dict['value_tag'],))
                id_tag = cursor.execute('SELECT id_tag FROM tags WHERE value = ?', 
                                        (row_dict['value_tag'],)).fetchone()[0]

                # Inserción en la tabla `type`
                cursor.execute('INSERT OR IGNORE INTO type (id_indicator, id_tag) VALUES (?, ?)', 
                               (id_indicator, id_tag))

        database.commit()

    except sqlite3.Error as e:
        print(f"Error al procesar los datos de staging: {e}")
        database.rollback()

    finally:
        cursor.close()

def truncate_all_tables(database):
    cursor = database.cursor()

    try:
        tables = ['stg_table', 'nuts', 'geolevel', 'geodata', 'indicator', 'data_values', 'attributes', 'val_attr', 'tags', 'type']
        
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')
            cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}";')

        database.commit()
        print("Todas las tablas han sido vaciadas.")
    except sqlite3.Error as e:
        database.rollback()
        print(f"Error al vaciar las tablas: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    try:
        database = sqlite3.connect('sqlite_db.db')
        print("Conexión exitosa a la base de datos.")
        
        insert_into_stagging(database=database, csv_folder="app/indicators_data/worldbank/wb_data/processed/")
        stg_to_datawarehouse(database)

        #truncate_all_tables(database=database)
    
    except sqlite3.Error as db_err:
        print(f"Error: {db_err}")

    finally:
        if database:
            database.close()
            print("Conexión a la base de datos cerrada.")
