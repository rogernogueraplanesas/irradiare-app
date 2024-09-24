import csv
import os
from typing import List, Tuple, Dict, Any

def load_data(data_file: str) -> Tuple[List[str], List[List[str]]]:
    """
    Load data from a CSV file, skipping the first two lines and any blank lines.

    Args:
        archivo_datos (str): Path to the CSV data file.

    Returns:
        Tuple[List[str], List[List[str]]]: A tuple containing the headers and the data rows.
    """
    with open(data_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)

        # Skip the first three lines
        for _ in range(3):
            next(reader)  # Omit the first two lines

        # Read until the headers are found, ignoring any blank lines
        headers = []
        while not headers:
            headers = next(reader)  # Read headers (first non-empty row)

        # Read the remaining data
        data = list(reader)

    print("Data loaded.")
    return headers, data


def load_metadata(metadata_file: str) -> Dict[str, Dict[str, str]]:
    """
    Load metadata from a CSV file, skipping the header row.

    Args:
        archivo_metadata (str): Path to the metadata CSV file.

    Returns:
        Dict[str, Dict[str, str]]: A dictionary mapping indicator codes to their metadata.
    """
    with open(metadata_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header
        metadata = {row[0]: {'name': row[1], 'description': row[2], 'source': row[3]} for row in reader}
    
    print("Metadata loaded.")
    return metadata

def create_csv_for_indicator(headers: List[str], datos: List[List[str]], 
                              metadatos: Dict[str, Dict[str, str]], output_dir: str) -> None:
    """
    Generate CSV files for each indicator based on the provided headers and data.

    Args:
        headers (List[str]): List of headers from the data file.
        datos (List[List[str]]): List of data rows from the data file.
        metadatos (Dict[str, Dict[str, str]]): Dictionary of metadata for indicators.
        output_dir (str): Directory where the generated CSV files will be saved.

    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over each data row
    for row in datos:
        indicator_name = row[2]
        indicator_code = row[3]

        # Skip if there is no indicator code
        if not indicator_code:
            continue

        # Look up the indicator code in the metadata
        if indicator_code not in metadatos:
            print(f"Metadata not found for indicator: {indicator_code}")
            continue
        
        # Get the description and source from the metadata
        metadata = metadatos[indicator_code]
        indicator_description = metadata['description']
        indicator_source = metadata['source']

        # Create the CSV file for the indicator
        csv_filename = f"{indicator_code}.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)
        
        with open(csv_filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['timecode', 'source_code', 'name', 'description', 'value', 'source'])
            
            # Write data for each year (1960-2023)
            for i, year in enumerate(headers[4:], start=4):
                year_value = row[i]  # Get the value for the year
                if year_value:  # If there is a value for that year
                    writer.writerow([headers[i], indicator_code, indicator_name, indicator_description, year_value, indicator_source])
        
        print(f"File generated for {indicator_code}: {csv_filepath}")


def main() -> None:
    """
    Main function to load data, load metadata, and generate CSV files for indicators.
    
    Returns:
        None
    """
headers, datos = load_data("app/indicators_data/worldbank/wb_data/raw/API_PRT_DS2_en_csv_v2_3412148.csv")
metadatos = load_metadata("app/indicators_data/worldbank/wb_metadata/Metadata_Indicator_API_PRT_DS2_en_csv_v2_3412148.csv")
create_csv_for_indicator(headers=headers, datos=datos, metadatos=metadatos, output_dir="app/indicators_data/worldbank/wb_data/processed")

if __name__ == "__main__":
    main()