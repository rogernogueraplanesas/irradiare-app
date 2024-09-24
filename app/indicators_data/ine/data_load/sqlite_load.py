import os
import csv
import sqlite3
import sqlite_queries as sq


def extract_and_save_row(input_csv: str, output_csv: str, row_number: int) -> list[str] | None:
    """
    Extracts a specific row from the input CSV file and saves it in an output CSV file under the filename.
    If the filename already exists in the output file, the row is updated. Otherwise, the filename and row are appended.
    
    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file where the row will be saved or updated.
        row_number (int): The row number (1-based index) to extract from the input CSV.

    Returns:
        list[str] | None: The extracted row as a list of strings, or None if the row does not exist.
    """
    # Extract the filename without extension
    filename = os.path.basename(input_csv)
    last_row = None

    with open(input_csv, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
        # Obtain the data written in the specified row number
        if row_number < len(lines):
            row = lines[row_number].strip()  # Remove spaces and break lines
            # Divide the row elements by ;
            row_data = row.split(';')
            # Remove double quotes from any element
            row_data = [field.strip('"') for field in row_data]
        else:
            row_data = None

    # If there's no output file, a new one is created inserting the first 2 rows (filename and data)
    if not os.path.exists(output_csv):
        with open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
            outfile.write(f"{filename}\n")
            if row_data:
                outfile.write(f"{';'.join(row_data)}\n")
            last_row = []

    # In case of existing it is read
    else:
            with open(output_csv, 'r', encoding='utf-8') as outfile:
                existing_content = outfile.read()

            # If the content has the filename written in any line
            if filename in existing_content:
                # A new variable will store the content to replace the original file content
                updated_content = ""
                lines = existing_content.splitlines()
                # Do not 'skip' any line automatically
                skip_next_line = False

                for line in lines:
                    # If filename is found in a line
                    if line == filename:
                        # Extract the content from the next row after the match
                        existing_row_data = None
                        for i in range(len(lines) - 1):
                            if lines[i] == filename:
                                existing_row_data = lines[i + 1].strip()
                                break

                        if existing_row_data:
                            # Save the content of the last row to be substituted by row_data (new last row for the same filename)
                            last_row = existing_row_data.split(';')

                        # Filename is added to the update content variable
                        updated_content += f"{filename}\n"
                        # A new last row substitutes the old one
                        if row_data:
                            updated_content += f"{';'.join(row_data)}\n"
                        # Automatically skips the line after the filename coincident line
                        skip_next_line = True 
                    elif skip_next_line:
                        # Reset automatic skipping to False
                        skip_next_line = False
                    else:
                        # Processes a line (non-coincident) adding its content to updated_content
                        updated_content += f"{line}\n"
            
            else:
                # If filename not present, add the new filename and data row to update_content
                updated_content = existing_content + f"{filename}\n"
                if row_data:
                    updated_content += f"{';'.join(row_data)}\n"
                last_row = []  # No hay fila anterior

            # Write and save the content of update_data into the output file
            with open(output_csv, 'w', encoding='utf-8') as outfile:
                outfile.write(updated_content)

            return last_row



def insert_into_stagging(database: sqlite3.Connection, csv_folder: str) -> None:
    """
    Inserts data from CSV files in the specified folder into the staging table of the database.
    
    Args:
        database (sqlite3.Connection): A connection object to the SQLite database.
        csv_folder (str): Path to the folder containing the CSV files to be processed.
    
    Returns:
        None
    """
    try:
        cursor = database.cursor()
        
        for filename in os.listdir(csv_folder):
            if filename.endswith('.csv'):
                file_path = os.path.join(csv_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as data_file:
                    if os.stat(file_path).st_size == 0:  
                        print(f"Empty file: {filename}. Skipping...")
                        continue
                    
                    
                    lines = data_file.readlines()
                    if len(lines) < 2:  # If there is only the headers row
                        print(f"File without data recorded: {filename}. Skipping...")
                        continue

                    data_file.seek(0)

                    last_row = extract_and_save_row(
                        input_csv=file_path,
                        output_csv="app/indicators_data/ine/ine_data/savepoint.csv",
                        row_number=2
                    )
                    reader = csv.reader(data_file, delimiter=';')
                    headers = next(reader)

                    nuts1_idx = headers.index('nuts1')
                    nuts2_idx = headers.index('nuts2')
                    nuts3_idx = headers.index('nuts3')
                    distrito_idx = headers.index('distrito')
                    concelho_idx = headers.index('concelho')
                    freguesia_idx = headers.index('freguesia')
                    timecode_idx = headers.index('timecode')
                    data_value_idx = headers.index('value')
                    name_indicator_idx = headers.index('name')
                    description_idx = headers.index('description')
                    units_idx = headers.index('units')
                    source_code_idx = headers.index('source_cod')

                    # Managing the optional dimensions
                    dimension_3_idx = headers.index('dimension_3') if 'dimension_3' in headers else None
                    filter_value3_idx = headers.index('filter_value3') if 'filter_value3' in headers else None
                    dimension_4_idx = headers.index('dimension_4') if 'dimension_4' in headers else None
                    filter_value4_idx = headers.index('filter_value4') if 'filter_value4' in headers else None

                    for row in reader:
                        if row == last_row:
                            print(f"Reached last row: {last_row}. Stopping row insertion process.")
                            break 

                        nuts1 = row[nuts1_idx] if nuts1_idx is not None else 'Undefined'
                        nuts2 = row[nuts2_idx] if nuts2_idx is not None else 'Undefined'
                        nuts3 = row[nuts3_idx] if nuts3_idx is not None else 'Undefined'
                        geocode = 'Undefined'
                        type = 'Undefined'
                        distrito = row[distrito_idx] if distrito_idx is not None else 'Undefined'
                        concelho = row[concelho_idx] if concelho_idx is not None else 'Undefined'
                        freguesia = row[freguesia_idx] if freguesia_idx is not None else 'Undefined'
                        timecode = row[timecode_idx] if timecode_idx is not None else 'Undefined'
                        data_value = row[data_value_idx] if data_value_idx is not None else 'Undefined'
                        name_indicator = row[name_indicator_idx] if name_indicator_idx is not None else 'Undefined'
                        description = row[description_idx] if description_idx is not None else 'Undefined'
                        units = row[units_idx] if units_idx is not None else 'Undefined'
                        units_desc = 'Undefined'
                        calculation = 'Undefined'
                        source = 'INE (PT)'
                        source_code = row[source_code_idx] if source_code_idx is not None else 'Undefined'

                        # Managing dimensions and attributes
                        attributes_names = []
                        attributes_values = []
                        if dimension_3_idx is not None and row[dimension_3_idx] != 'undefined':
                            attributes_names.append(row[dimension_3_idx])
                            attributes_values.append(row[filter_value3_idx] if filter_value3_idx is not None and row[filter_value3_idx] != 'undefined' else 'Undefined')
                        if dimension_4_idx is not None and row[dimension_4_idx] != 'undefined':
                            attributes_names.append(row[dimension_4_idx])
                            attributes_values.append(row[filter_value4_idx] if filter_value4_idx is not None and row[filter_value4_idx] != 'undefined' else 'Undefined')

                        attributes_str = ', '.join(f"{name}" for name in attributes_names) if attributes_names else 'Undefined'
                        value_tag = 'Undefined'

                        # Insert into stagging for each combination of attributes
                        for name_attr, value_attr in zip(attributes_names, attributes_values):
                            cursor.execute(sq.INSERT_DATA_STAGGING, (
                                nuts1, nuts2, nuts3, geocode, type, 
                                distrito, concelho, freguesia, 
                                timecode, data_value, name_indicator, description, units, 
                                units_desc, calculation, source, source_code, 
                                attributes_str, name_attr, value_attr, value_tag
                            ))

        # Changes commited to the db
        database.commit()
        print("Stagging completed.")

    except Exception as e:
        database.rollback()
        print(f"Error processing file {filename}: {e}")

    finally:
        cursor.close()


def stg_to_datawarehouse(database: sqlite3.Connection) -> None:
    """
    Transfers data from the staging table to the corresponding data warehouse tables.
    
    Args:
        database (sqlite3.Connection): A connection object to the SQLite database.

    Returns:
        None
    """
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

            # Insert data into `nuts` table
            cursor.execute('INSERT OR IGNORE INTO nuts (nuts1, nuts2, nuts3) VALUES (?, ?, ?)', 
                           (row_dict['nuts1'], row_dict['nuts2'], row_dict['nuts3']))
            id_nuts = cursor.execute('SELECT id_nuts FROM nuts WHERE nuts1 = ? AND nuts2 = ? AND nuts3 = ?',
                                     (row_dict['nuts1'], row_dict['nuts2'], row_dict['nuts3'])).fetchone()[0]

            # Insert data into `geolevel` table
            cursor.execute('INSERT OR IGNORE INTO geolevel (distrito, concelho, freguesia) VALUES (?, ?, ?)', 
                           (row_dict['distrito'], row_dict['concelho'], row_dict['freguesia']))
            id_geolevel = cursor.execute('SELECT id_geolevel FROM geolevel WHERE distrito = ? AND concelho = ? AND freguesia = ?',
                                         (row_dict['distrito'], row_dict['concelho'], row_dict['freguesia'])).fetchone()[0]

            # Insert data into `geodata` table
            cursor.execute('INSERT OR IGNORE INTO geodata (id_nuts, id_geolevel, geocode, type) VALUES (?, ?, ?, ?)', 
                           (id_nuts, id_geolevel, row_dict['geocode'], row_dict['type']))
            id_geodata = cursor.execute('SELECT id_geodata FROM geodata WHERE id_nuts = ? AND id_geolevel = ? AND geocode = ? AND type = ?',
                                        (id_nuts, id_geolevel, row_dict['geocode'], row_dict['type'])).fetchone()[0]

            # Insert data into `indicator` table
            cursor.execute('INSERT OR IGNORE INTO indicator (name, description, units, units_desc, calculation, source, source_code) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                           (row_dict['name_indicator'], row_dict['description'], row_dict['units'], row_dict['units_desc'],
                            row_dict['calculation'], row_dict['source'], row_dict['source_code']))
            id_indicator = cursor.execute('SELECT id_indicator FROM indicator WHERE name = ? AND source_code = ?',
                                          (row_dict['name_indicator'], row_dict['source_code'])).fetchone()[0]
            
            # Validating data_value's value
            try:
                data_value = float(row_dict['data_value']) if row_dict['data_value'].strip() != '' else 0.0
            except ValueError:
                data_value = None
            
            # Insert data into `data_values` table
            try:
                cursor.execute('INSERT INTO data_values (id_geodata, id_indicator, timecode, value, attributes) VALUES (?, ?, ?, ?, ?)', 
                               (id_geodata, id_indicator, row_dict['timecode'], data_value, row_dict['attributes']))
                id_value = cursor.lastrowid
            except sqlite3.IntegrityError:
                print(f"Duplicated found and skipped: {row_dict}")
                continue

            # Insert data into `attributes` table
            if row_dict['name_attribute'] != 'Undefined' and row_dict['value_attribute'] != 'Undefined':
                cursor.execute('INSERT OR IGNORE INTO attributes (name, value) VALUES (?, ?)', 
                               (row_dict['name_attribute'], row_dict['value_attribute']))
                id_attribute = cursor.execute('SELECT id_attribute FROM attributes WHERE name = ? AND value = ?', 
                                              (row_dict['name_attribute'], row_dict['value_attribute'])).fetchone()[0]

                # Insert data into `val_attr` table
                cursor.execute('INSERT OR IGNORE INTO val_attr (id_value, id_attribute) VALUES (?, ?)', 
                               (id_value, id_attribute))

            # Insert data into `tags` table
            if row_dict['value_tag'] != 'Undefined':
                cursor.execute('INSERT OR IGNORE INTO tags (value) VALUES (?)', 
                               (row_dict['value_tag'],))
                id_tag = cursor.execute('SELECT id_tag FROM tags WHERE value = ?', 
                                        (row_dict['value_tag'],)).fetchone()[0]

                # Insert data into `type` table
                cursor.execute('INSERT OR IGNORE INTO type (id_indicator, id_tag) VALUES (?, ?)', 
                               (id_indicator, id_tag))

        database.commit()

    except sqlite3.Error as e:
        print(f"Error processing stagging data: {e}")
        database.rollback()

    finally:
        cursor.close()


def truncate_all_tables(database: sqlite3.Connection) -> None:
    """
    Empties all specified tables in the database.

    Args:
        database (sqlite3.Connection): Connection to the SQLite database.

    Returns:
        None
    """
    cursor = database.cursor()

    try:
        # List of tables to empty
        tables = ['stg_table', 'nuts', 'geolevel', 'geodata', 'indicator', 'data_values', 'attributes', 'val_attr', 'tags', 'type']
        
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')
            cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}";')

        database.commit()
        print("All tables empty.")
    except sqlite3.Error as e:
        database.rollback()
        print(f"Error emptying the tables: {e}")
    finally:
        cursor.close()


def main() -> None:
    """
    Main function that handles the database connection, inserts data from CSV to staging,
    moves data from the staging table to the data warehouse, and manages the database connection lifecycle.
    """
    try:
        # Connect to the SQLite database
        database = sqlite3.connect('sqlite_db.db')
        print("Connected to the database (SQLITE).")
        
        # Insert data into the staging table from CSVs
        insert_into_stagging(database=database, csv_folder="app/indicators_data/ine/ine_data/processed/")
        
        # Move data from staging to the data warehouse
        stg_to_datawarehouse(database)

        # Uncomment this if you want to truncate all tables after processing
        # truncate_all_tables(database=database)
    
    except sqlite3.Error as db_err:
        print(f"Error: {db_err}")
    
    finally:
        # Ensure the database connection is closed
        if database:
            database.close()
            print("Database connection closed.")



if __name__ == "__main__":
    main()
