import sys
import os

# Obtiene la ruta del directorio 'irradiare-app' (dos niveles hacia arriba desde eredes_metadata.py)
irradiare_app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Añade la ruta al sys.path
sys.path.append(irradiare_app_path)

import app.indicators_data.settings as s
import csv
import json
import requests
from eurostatapiclient import EurostatAPIClient



def get_eurostat_data() -> None:
    """
    Fetch and save Eurostat data for specified codes usin EurostatAPIClient.

    The data is filtered based on predefined parameters and saved as JSON files.

    Args:
    - None

    Returns:
    - None
    """
    # Version 1.0 is the only available
    version = '1.0'
    # The only possible format is JSON
    data_format = 'json'
    # Specify language: 'en', 'fr', 'de'
    language = 'en'

    client = EurostatAPIClient(version, data_format, language)

    # Required query parameters
    params = {
        'geo': 'PT',
    }

# Read the Eurostat indicators TOC file
    with open(s.eurostat_table_contents, 'r', encoding='utf-8') as codes_file:
        reader = csv.reader(codes_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        for row in reader:
            code = row[1].strip('"') # Extract the code for the indicator in each row
            print(code)
            path = f"app/indicators_data/eurostat/eurostat_data/{code}.json" # Define a code adjustable path to save the JSON datasets
            print(path)
            try:
                # Get data from the server for the code+query parameters specified
                filtered_dataset = client.get_dataset(code, params=params)
                # Convert the dataset into a pandas dataframe
                filtered_dataframe = filtered_dataset.to_dataframe()
                print(filtered_dataframe.head())
                # Convert the dataframe into JSON. orient='records': each row from the df is converted into a dict. The result is a list of dictionaries. 
                filtered_dataframe_json = filtered_dataframe.to_json(orient='records')
                print("DataFrame converted to JSON:")
                # Create/open the code adjustable path in 'write' mode
                with open(path, 'w', encoding='utf-8') as dataset:
                    json.dump(filtered_dataframe_json, dataset, indent=4, ensure_ascii=False) # Dump the JSON data into the file
                    print(f"Data for {code} saved")

            except requests.exceptions.RequestException as e:
                print(f"An exception occurred for code {code}: {e}")
                continue


if __name__ == "__main__":
    get_eurostat_data()




