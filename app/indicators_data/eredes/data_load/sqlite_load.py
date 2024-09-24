import os
import csv
import sqlite3
from typing import Dict, List, Optional
import sqlite_queries as sq


def extract_and_save_row(input_csv: str, output_csv: str, row_number: int) -> Optional[List[str]]:
    """
    Extracts the last row from a CSV file and saves it to another CSV file with 'savepoint' functionality.

    Args:
        input_csv (str): The path to the input CSV file.
        output_csv (str): The path to the output CSV file where the row will be saved.
        row_number (int): The row number to extract (1-based index).

    Returns:
        Optional[List[str]]: The extracted row data as a list of strings,
                             or None if the row could not be extracted.
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



def find_header_index(headers: list[str], possible_headers: list[str]) -> int:
    """
    Find the index from the first header from a list of possible headers

    Args:
        headers (list[str]): Available headers.
        possible_headers (list[str]): "Possible" headers list.

    Returns:
        int: Index from the found header or -1 if not found.
    """
    for possible_header in possible_headers:
        try:
            return headers.index(possible_header)
        except ValueError:
            continue
    return -1

def assign_units(header_value: str, known_units: Dict[str, str]) -> str:
    """
    Assigns a unit based on the corresponding header.

    Args:
        header_value (str): The value of the header being evaluated.
        known_units (Dict[str, str]): Dictionary of known units.

    Returns:
        str: The assigned unit or 'Undefined' if not found.
    """
    for unit_key, unit_desc in known_units.items():
        if unit_key in header_value:
            return unit_desc
    return 'Undefined'


def insert_into_stagging(database: sqlite3.Connection, csv_folder: str) -> None:
    """
    Inserts data from CSV files into a staging table in the database.

    Args:
        database (sqlite3.Connection): Connection to the SQLite database.
        csv_folder (str): Path to the folder containing the CSV files.

    Returns:
        None
    """
    possible_value_value = {'Active Energy (kWh)', 'Executed Network Connection Requests', 'Number of installations',
                            "Number of CPE's with collected DC", "Number of delivery points with readings",
                            "completed processes", "total installed power (W)", "potencia instalada total (W)",
                            "Connection points for electric vehicles charging stations"}
    known_units = {
        'kWh': 'kilowatt-hour',
        'Requests': 'number of requests',
        'Number' : 'number of installations or locations',
        'completed' : 'completed processes',
        'W' : 'watts',
        'Connection points' : 'connection points'
    }

    try:
        for filename in os.listdir(csv_folder):
            if filename.endswith('.csv'):
                file_path = os.path.join(csv_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as data_file:
                    # Get the last data saved for the filename in savepoint.csv and update it with info from input file
                    last_row = extract_and_save_row(
                        input_csv=file_path,
                        output_csv="app/indicators_data/eredes/data/savepoint.csv",
                        row_number=2
                    )
                    reader = csv.reader(data_file, delimiter=';')
                    headers = next(reader)

                    # Identify the columns
                    nuts1_idx = headers.index('nuts1')
                    nuts2_idx = headers.index('nuts2')
                    nuts3_idx = headers.index('nuts3')
                    dicofre_idx = find_header_index(headers, ['dicofre'])
                    zipcode_idx = find_header_index(headers, ['zipcode'])
                    distrito_idx = headers.index('distrito')
                    concelho_idx = headers.index('concelho')
                    freguesia_idx = headers.index('freguesia')
                    timecode_idx = headers.index('timecode')
                    data_value_idx = find_header_index(headers, possible_value_value)
                    name_indicator_idx = headers.index('title')
                    description_idx = headers.index('description')
                    source_idx = headers.index('Publisher')
                    source_code_idx = headers.index('src_code')

                    cursor = database.cursor()

                    # Process each row of the file
                    for row in reader:
                        # Check for the `last_row`inside the new file
                        if row == last_row:
                            print(f"Reached last row: {last_row}. Stopping the row insertion process..")
                            break  # If the last row is found in the input file, the insertion process ends

                        nuts1 = row[nuts1_idx] if nuts1_idx is not None else 'Undefined'
                        nuts2 = row[nuts2_idx] if nuts2_idx is not None else 'Undefined'
                        nuts3 = row[nuts3_idx] if nuts3_idx is not None else 'Undefined'

                        geocode = 'Undefined'
                        type = 'Undefined'
                        if dicofre_idx != -1 and row[dicofre_idx].lower() != 'undefined':
                            geocode = row[dicofre_idx]
                            type = 'dicofre'
                        elif zipcode_idx != -1 and row[zipcode_idx].lower() != 'undefined':
                            geocode = row[zipcode_idx]
                            type = 'zipcode'

                        distrito = row[distrito_idx] if distrito_idx is not None else 'Undefined'
                        concelho = row[concelho_idx] if concelho_idx is not None else 'Undefined'
                        freguesia = row[freguesia_idx] if freguesia_idx is not None else 'Undefined'
                        timecode = row[timecode_idx] if timecode_idx is not None else 'Undefined'
                        data_value = row[data_value_idx] if data_value_idx is not None else 'Undefined'
                        name_indicator = row[name_indicator_idx] if name_indicator_idx is not None else 'Undefined'
                        description = row[description_idx] if description_idx is not None else 'Undefined'
                        data_value_header = headers[data_value_idx] if data_value_idx != -1 else 'Undefined'
                        units = assign_units(data_value_header, known_units)
                        units_desc = 'Undefined'
                        calculation = 'Undefined'
                        source = row[source_idx] if source_idx is not None else 'Undefined'
                        source_code = row[source_code_idx] if source_code_idx is not None else 'Undefined'
                        attributes = 'Undefined'
                        name_attribute = 'Undefined'
                        value_attribute = 'Undefined'
                        value_tag = 'Undefined'

                        # INSERT into the db
                        cursor.execute(sq.INSERT_DATA_STAGGING, (
                            nuts1, nuts2, nuts3, geocode, type, distrito, concelho, freguesia, timecode, data_value, 
                            name_indicator, description, units, units_desc, calculation, source, source_code, 
                            attributes, name_attribute, value_attribute, value_tag
                        ))

        # Changes commited to the db
        database.commit()
        print("Stagging completed.")

    except Exception as e:
        database.rollback()
        print(f"Error processing the file {filename}: {e}")

    finally:
        cursor.close()


def stg_to_datawarehouse(database: sqlite3.Connection) -> None:
    """
    Processes the data from the staging table and inserts it into the destination tables.

    Args:
        database (sqlite3.Connection): Connection to the SQLite database.

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
                value = float(row_dict['data_value']) if row_dict['data_value'].strip() else None
                if value is None:
                    raise ValueError(f"Valor de data_value inválido: {row_dict['data_value']}")
            except ValueError:
                print(f"data_value value not valid, skipping: {row_dict['data_value']}")
                continue

            # Insert data into `data_values` table
            try:
                cursor.execute('INSERT INTO data_values (id_geodata, id_indicator, timecode, value, attributes) VALUES (?, ?, ?, ?, ?)', 
                               (id_geodata, id_indicator, row_dict['timecode'], value, row_dict['attributes']))
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
        tables = ['stg_table', 'nuts', 'geolevel', 'geodata', 'indicator', 'data_values']
        
        for table in tables:
            cursor.execute(f'DELETE FROM {table}')
            cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}";')  # Autoincrement reset

        database.commit()
        print("All tables empty.")
    except sqlite3.Error as e:
        database.rollback()
        print(f"Error emptying the tables: {e}")
    finally:
        cursor.close()


def truncate_stagging(database: sqlite3.Connection) -> None:
    """
    Empties the staging table in the database.

    Args:
        database (sqlite3.Connection): Connection to the SQLite database.

    Returns:
        None
    """
    cursor = database.cursor()

    try:
        tables = ['stg_table']
        
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
    Main function that manages the database connection, inserts data from CSV into staging,
    moves data from staging to the data warehouse, truncates the staging table, and closes the connection.
    """
    try:
        # Connect to the SQLite database
        database = sqlite3.connect('sqlite_db.db')
        print("Connected to the database (SQLITE).")
        
        # Insert data into the staging table from CSVs
        insert_into_stagging(database=database, csv_folder="app/indicators_data/eredes/data/processed/")
        print("Stagging table completed")

        # Move data from staging to the data warehouse
        stg_to_datawarehouse(database)
        
        # Uncomment this if you want to truncate the stg_table after processing
        #truncate_stagging(database=database)

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