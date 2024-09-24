# fill_db.py
from app.db.sqlite.main import main as create_sqlite_db
from app.indicators_data.eredes.data_load.sqlite_load import main as eredes_main
from app.indicators_data.eurostat.data_load.sqlite_load import main as eurostat_main
from app.indicators_data.ine.data_load.sqlite_load import main as ine_main
from app.indicators_data.worldbank.data_load.sqlite_load import main as wb_main

def sqlite_db():
    """Executes the main() function for the SQLite DB creation."""
    print("Creating SQLite database...")
    try:
        create_sqlite_db()
        print("SQLite database created successfully.")
    except Exception as e:
        print(f"Error creating SQLite database: {e}")

def fill_database():
    """Executes the main() function for all the sqlite_load files."""
    
    print("Filling E-REDES database...")
    try:
        eredes_main()
        print("E-REDES database filled successfully.")
    except Exception as e:
        print(f"Error filling E-REDES database: {e}")
    
    print("Filling Eurostat database...")
    try:
        eurostat_main()
        print("Eurostat database filled successfully.")
    except Exception as e:
        print(f"Error filling Eurostat database: {e}")
    
    print("Filling INE database...")
    try:
        ine_main()
        print("INE database filled successfully.")
    except Exception as e:
        print(f"Error filling INE database: {e}")
    
    print("Filling World Bank database...")
    try:
        wb_main()
        print("World Bank database filled successfully.")
    except Exception as e:
        print(f"Error filling World Bank database: {e}")
    
    print("Database filling completed.")

def fill_sqlite_db():
    sqlite_db()
    fill_database()

if __name__ == "__main__":
    fill_sqlite_db()
