import sqlite3
import create_tables as ct
import indexes as i

def create_tables(database: sqlite3.Connection) -> None:
    """
    Crea las tablas en la base de datos SQLite especificada.

    Args:
        database (sqlite3.Connection): Conexión a la base de datos SQLite.
    """
    try:
        cursor = database.cursor()
        
        # Crear las tablas en la base de datos
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
        cursor.execute(i.GEOCODE_IDX)
        cursor.execute(i.TIMECODE_IDX)
        cursor.execute(i.INDICATOR_NAME_IDX)
        cursor.execute(i.ID_GEODATA_IDX)
        cursor.execute(i.ID_INDICATOR_IDX)
        
        # Confirmar los cambios
        database.commit()
        
        print("Todas las tablas se han creado correctamente.")
    
    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")
        # Hacer rollback para revertir cambios en caso de error
        database.rollback()
        # Aquí podrías implementar estrategias adicionales para manejar el error.

if __name__ == "__main__":
    database = None
    try:
        # Conectar a la base de datos SQLite
        database = sqlite3.connect('sqlite_db.db')
        # Crear las tablas
        create_tables(database=database)
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    finally:
        # Asegurarse de cerrar la conexión, incluso si ocurre un error
        if database:
            database.close()
