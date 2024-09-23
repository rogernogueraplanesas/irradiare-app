import sqlite3
import create_tables as ct
import indexes as i

def create_tables(database: sqlite3.Connection) -> None:
    """
    Create SQLite DB tables

    Args:
        database (sqlite3.Connection): Connection to the SQLite DB.
    """
    try:
        cursor = database.cursor()
        
        cursor.execute(ct.CREATE_STAGGING_TABLE)
        cursor.execute(ct.CREATE_NUTS_TABLE)
        cursor.execute(ct.CREATE_GEOLEVEL_TABLE)
        cursor.execute(ct.CREATE_ATTRIBUTES_TABLE)
        cursor.execute(ct.CREATE_INDICATOR_TABLE)
        cursor.execute(ct.CREATE_TAGS_TABLE)
        cursor.execute(ct.CREATE_GEODATA_TABLE)
        cursor.execute(ct.CREATE_DATA_VALUES_TABLE)
        cursor.execute(ct.CREATE_VAL_ATTR_TABLE)
        cursor.execute(ct.CREATE_TYPE_TABLE)
        cursor.execute(ct.CREATE_USERS_TABLE)
        cursor.execute(i.GEOCODE_IDX)
        cursor.execute(i.TIMECODE_IDX)
        cursor.execute(i.INDICATOR_NAME_IDX)
        cursor.execute(i.ID_GEODATA_IDX)
        cursor.execute(i.ID_INDICATOR_IDX)
        
        database.commit()
        
        print("All tables created.")
    
    except sqlite3.Error as e:
        print(f"Error creating the tables: {e}")
        # Rollback to revert in case of error
        database.rollback()


def main() -> None:
    """
    Main function to create tables in the DB
    """
    DB_PATH = 'sqlite_db.db'  # Relativa path to the db
    try:
        database = sqlite3.connect(DB_PATH)
        create_tables(database=database)

    except sqlite3.Error as error:
        print(f"Error connecting with the database: {error}")

    finally:
        if database:
            database.close()


if __name__ == "__main__":
    main()