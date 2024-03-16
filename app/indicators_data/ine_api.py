import requests
import xml.etree.ElementTree as ET
import json
import time
import os

# Extracting catalog data for indicators in XML format and returned as JSON data
def extract_catalog(lang):
    host_url = "https://www.ine.pt"
    url = f"{host_url}/ine/xml_indic.jsp?opc=3&lang={lang}"

    response = requests.get(url)

    root = ET.fromstring(response.content) #Takes the XML response as an argument to convert it into a Element Tree (with hierarchies to manipulate the nodes)

    #'catalog_data' will contain the final dictionary with JSON format data, more than 1 list of JSON data can be inside
    catalog_data = {}

    #'indicators' is a list containing all indicator's information, will be accessible through a key in the catalog_data dictionary
    indicators = []

    for indicator in root.findall('.//indicator'): #Find all the indicators in a recursive (all levels) from the root level (upper level)

        indicator_data = {} #Create a dictionary for each indicator found in the root

        for child in indicator:
            indicator_data[child.tag] = child.text # For each indicator, take the child tags as keys and each child text as values. Each indicator has >1 child.
        indicators.append(indicator_data) # Append the JSON formatted data per indicator in the 'indicator_data' dict.

    catalog_data["indicators"] = indicators # 'catalog_data' dict gets assigned the lost 'indicators' with a corresponding key.

    return catalog_data





# Extracting data for indicators
def extract_data(varcd_cod, lang):
    host_url = "https://www.ine.pt"
    url = f"{host_url}/ine/json_indicador/pindica.jsp?op=2&varcd={varcd_cod}&lang={lang}"
    response = requests.get(url)
    data = response.json()
    return data





# Extracting metadata for indicators
def extract_metadata(varcd_cod, lang):
    host_url = "https://www.ine.pt"
    url = f"{host_url}/ine/json_indicador/pindicaMeta.jsp?varcd={varcd_cod}&lang={lang}"
    response = requests.get(url)
    metadata = response.json()
    return metadata





def get_save_catalog(catalog_data):
    with open("app/indicators_data/ine_files/catalogo_indicadores.json", "w", encoding="utf-8") as catalog_file:
        json.dump(catalog_data, catalog_file, indent=4, ensure_ascii=False)
    print("Catálogo de Indicadores guardado en catalogo_indicadores.json")





def get_save_data(catalog_data):
    # Access to the list "indicators" and check for each indicator
    for indicator in catalog_data["indicators"]:
        varcd_cod = indicator["varcd"] # Extract the 'varcd' for each indicator
        data_path = f"app/indicators_data/ine_files/data_{varcd_cod}.json" # Create a path for each indicator based on its 'varcd'

        # Verify if the path already exists
        if os.path.exists(data_path):
            print(f"El archivo para el indicador {varcd_cod} ya existe. Saltando...")
            continue

        # If the path does not exist, JSON format data is extracted
        data = extract_data(varcd_cod, lang)

        # Open the file in the new path and write the JSON data in it
        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(data, data_file, indent=4, ensure_ascii=False)
        print(f"Data from indicator {varcd_cod} saved in {data_path}")

        # Delay of 1 sec. to not overload the server
        time.sleep(1)






# Recorrer los indicadores en el catálogo y obtener su metainformación
def get_save_metadata(catalog_data):
    # Same initial steps for get_save_data
    for indicator in catalog_data["indicators"]:
        varcd_cod = indicator["varcd"]
        metadata_path = f"app/indicators_data/ine_files/metadata_{varcd_cod}.json"
        
        if os.path.exists(metadata_path):
            print(f"El archivo para el indicador {varcd_cod} ya existe. Saltando...")
            continue
        
        # Metadata extracted for the indicator
        metadata = extract_metadata(varcd_cod, lang)

        # Open the file in the new path and write the JSON data in it
        with open(metadata_path, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=4, ensure_ascii=False)
        print(f"Metainformación del Indicador {varcd_cod} guardada en metadata_{varcd_cod}.json")

        # Delay of 1 sec. to not overload the server
        time.sleep(1)





if __name__ == "__main__":
   
# Catalog data is extracted in portuguese (PT)
    lang = "PT"
    catalog_data = extract_catalog(lang)

# Extracted catalog data written into a JSON file
    get_save_catalog(catalog_data=catalog_data)

# Data extracted and saved in JSON format for each indicator in the catalog
    get_save_data(catalog_data=catalog_data)
    get_save_metadata(catalog_data=catalog_data)



    






