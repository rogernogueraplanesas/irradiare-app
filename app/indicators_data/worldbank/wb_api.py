import settings as s
import requests
import json
import time
import os


def get_catalog(format: str) -> list:
    """
    Retrieve the catalog data from the World Bank API and return it as a list.

    Args:
    - format (str): The format of the data ('json' or 'xml').

    Returns:
    - list: A list containing the catalog data.
    """
    catalog_data = [] # Create an empty list
    page_number = 1 # Page counter
    max_pages = 489 # Set max. page number

    while page_number <= max_pages:
        url = f"https://api.worldbank.org/v2/indicator?page={page_number}&format={format}" # Custom url increasing page number
        response = requests.get(url=url)

        if response.status_code == 200:
            data = response.json() # Response converted to json
            catalog_data.extend(data) # Response added to the list
            print(f"Page {page_number} imported.")
            time.sleep(1)
        else:
            print(f"Error importing page {page_number}.")
        
        page_number += 1 # Increase page number by 1

    return catalog_data


def save_catalog(save_path: str, filename: str, catalog_data: list) -> None:
    """
    Save the catalog data to a JSON file.

    Args:
    - catalog_path (str): The path where the catalog file will be saved.
    - catalog_data (list): The catalog data to save.
    """
    os.makedirs(save_path, exist_ok=True) 
    with open(os.path.join(save_path, filename), "w", encoding="utf-8") as data_file:
        json.dump(catalog_data, data_file, indent=4, ensure_ascii=False)
    print("Indicators saved")


def get_source_id(catalog_path: str) -> list:
    """
    Extract source IDs from the catalog data.

    Args:
    - catalog_path (str): The path to the catalog file.

    Returns:
    - list: A list of source IDs.
    """
    list_source_id = []

    with open(catalog_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file) # Load its content into data
        except json.decoder.JSONDecodeError as e:
            print(f"Error loading data from {file}: {e}")
            return []
# From each page list, skips the first dict (w/ page info) and takes the 2nd element (indicators info))
        for index in range(1, len(data), 2):
            indicators = data[index] # Load list of indicators per page into a variable
            for indicator in indicators:
                source_id = indicator.get("source", {}).get("id") # Take source and extract id for each indicator
                if source_id:
                    list_source_id.append(source_id) # Append the id to the list

    return list_source_id


def get_id(catalog_path: str) -> list:
    """
    Extract indicator IDs from the catalog data.

    Args:
    - catalog_path (str): The path to the catalog file.

    Returns:
    - list: A list of indicator IDs.
    """
    llista_id = []

    with open(catalog_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError as e:
            print(f"Error loading data from {file}: {e}")
            return []

        for index in range(1, len(data), 2):
            indicators = data[index]
            for indicator in indicators:
                id = indicator.get("id")
                if id:
                    llista_id.append(id)

    return llista_id


def get_data(source_id: str, indicator_id: str) -> dict:
    """
    Retrieve data for a specific indicator from the World Bank API.

    Args:
    - source_id (str): The source ID.
    - indicator_id (str): The indicator ID.

    Returns:
    - dict: The retrieved data, or None if there was an error.
    """
    url = f"https://api.worldbank.org/v2/sources/{source_id}/country/PRT/series/{indicator_id}/time/all/version/199704/data?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data for indicator {indicator_id} and source {source_id}: {e}")
        return None


def get_indicator_data(source_id_list: list, indicator_id_list: list) -> list:
    """
    Retrieve data for a list of indicators.

    Args:
    - source_id_list (list): A list of source IDs.
    - indicator_id_list (list): A list of indicator IDs.

    Returns:
    - list: A list of dictionaries containing the indicator data.
    """
    indicators_data_dict = []

    for source_id, indicator_id in zip(source_id_list, indicator_id_list): # 'zip' to iterate over both lists
        indicator_data = get_data(source_id, indicator_id)
        indicator_data = get_data(source_id, indicator_id)
        if indicator_data:
            print(f"Data for indicator {indicator_id} and source {source_id}: {indicator_data}")
            indicators_data_dict.append(indicator_data)
        else:
            print(f"No data available for indicator {indicator_id} and source {source_id}")

    return indicators_data_dict


def get_metadata_source_id(data_file: str) -> list:
    """
    Retrieve source IDs from the metadata file.

    Returns:
    - list: A list of source IDs.
    """
    llista_source_id = []
    with open(data_file, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError as e:
            print(f"Error loading data from {file}: {e}")
            return []
        
        # Iterate through each element in the "data" list
        for indicator in data:
            source_id = indicator["source"]["id"]
            llista_source_id.append(source_id)

    return llista_source_id


def get_metadata_id(data_file: str) -> list:
    """
    Retrieve indicator IDs from the metadata file.

    Returns:
    - list: A list of indicator IDs.
    """
    llista_ids = []
    with open(data_file, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError as e:
            print(f"Error loading data from {file}: {e}")
            return []

        for indicator in data:
            id = indicator["source"]["data"][0]["variable"][2]["id"]
            llista_ids.append(id)

    return llista_ids


def get_metadata(source_id: str, indicator_id: str) -> dict:
    """
    Retrieve metadata for a specific indicator from the World Bank API.

    Args:
    - source_id (str): The source ID.
    - indicator_id (str): The indicator ID.

    Returns:
    - dict: The retrieved metadata, or None if there was an error.
    """
    url = f"https://api.worldbank.org/v2/sources/{source_id}/country/PRT/series/{indicator_id}/metadata?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve metadata for indicator {indicator_id} and source {source_id}: {e}")
        return None


def get_indicator_metadata(source_id_list: list, indicator_id_list: list) -> dict:
    """
    Retrieve metadata for a list of indicators.

    Args:
    - source_id_list (list): A list of source IDs.
    - indicator_id_list (list): A list of indicator IDs.

    Returns:
    - dict: A dictionary containing the indicator metadata.
    """
    indicators_metadata_dict = {}

    for source_id, indicator_id in zip(source_id_list, indicator_id_list): # 'zip' to iterate over both lists
        metadata = get_metadata(source_id, indicator_id)
        metadata = get_metadata(source_id, indicator_id)
        if metadata:
            print(f"Metadata for indicator {indicator_id} and source {source_id}: {metadata}")
            indicators_metadata_dict[(source_id, indicator_id)] = metadata
        else:
            print(f"No metadata available for indicator {indicator_id} and source {source_id}")

    return indicators_metadata_dict


def save_json_file(path: str, data_dict: dict) -> None:
    """
    Save a dictionary to a JSON file.

    Args:
    - path (str): The path where the JSON file will be saved.
    - data_dict (dict): The data to save.
    """
    converted_dict = {str(k): v for k, v in data_dict.items()} # Convert tuple keys to strings
    os.makedirs(path, exist_ok=True)
    with open(path, "w", encoding="utf-8") as data_file:
        json.dump(converted_dict, data_file, indent=4, ensure_ascii=False)
    print("Indicators saved")


def main() -> None:
    """
    Main function to execute the script.
    """
    format = 'json'
    data = get_catalog(format=format)
    save_catalog(catalog_path=s.wb_catalog_path, filename=s.wb_catalog_filename, catalog_data=data)

    source_id = get_source_id(catalog_path=s.wb_catalog_path)
    indicator_id = get_id(catalog_path=s.wb_catalog_path)

    indicator_data_dict = get_indicator_data(source_id_list=source_id, indicator_id_list=indicator_id)
    save_json_file(path=s.wb_data_path, data_dict=indicator_data_dict)

    metadata_source_id = get_metadata_source_id(s.wb_data_path)
    metadata_id = get_metadata_id(s.wb_data_path)

    indicator_metadata_dict = get_indicator_metadata(source_id_list=metadata_source_id, indicator_id_list=metadata_id)
    save_json_file(path=s.wb_metadata_path, data_dict=indicator_metadata_dict)


if __name__ == "__main__":
    main()

