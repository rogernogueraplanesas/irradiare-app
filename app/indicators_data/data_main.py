from app.indicators_data.eredes.eredes_main import eredes_main
from app.indicators_data.eurostat.eurostat_main import eurostat_main
from app.indicators_data.ine.ine_main import ine_main
from app.indicators_data.worldbank.wb_main import wb_main


def data_main():
    """Runs the main data retrieval and transformation processes for each data source."""
    
    # Process E-REDES data
    print("Starting E-REDES data process...")
    try:
        eredes_main()
    except Exception as e:
        print(f"Error during E-REDES data process: {e}")
    
    # Process Eurostat data
    print("Starting Eurostat data process...")
    try:
        eurostat_main()
    except Exception as e:
        print(f"Error during Eurostat data process: {e}")
    
    # Process INE data
    print("Starting INE data process...")
    try:
        ine_main()
    except Exception as e:
        print(f"Error during INE data process: {e}")
    
    # Process World Bank data
    print("Starting World Bank data process...")
    try:
        wb_main()
    except Exception as e:
        print(f"Error during World Bank data process: {e}")
    
    print("Data retrieval and transformation completed for all sources.")


if __name__ == "__main__":
    data_main()
