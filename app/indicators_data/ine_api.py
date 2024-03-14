import requests
import xml.etree.ElementTree as ET
import json
import time


def extract_catalog(lang):
    host_url = "https://www.ine.pt"
    url = f"{host_url}/ine/xml_indic.jsp?opc=3&lang={lang}"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    catalog_data = {}
    indicators = []
    for indicator in root.findall('.//indicator'):
        indicator_data = {}
        for child in indicator:
            indicator_data[child.tag] = child.text
        indicators.append(indicator_data)
    catalog_data["indicators"] = indicators
    return catalog_data




def extract_data(varcd_cod, lang):
    host_url = "https://www.ine.pt"
    url = f"{host_url}/ine/json_indicador/pindica.jsp?op=2&varcd={varcd_cod}&lang={lang}"
    response = requests.get(url)
    data = response.json()
    return data




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
    # Recorrer todos los indicadores para sacar la data asociada a ellos
    for indicator in catalog_data["indicators"]:
        varcd_cod = indicator["varcd"]
        data = extract_data(varcd_cod, lang)
        data_path = f"app/indicators_data/ine_files/data_{varcd_cod}.json"

        with open(data_path, "w", encoding="utf-8") as data_file:
            json.dump(data, data_file, indent=4, ensure_ascii=False)
        print(f"Datos del Indicador {varcd_cod} guardados en {data_path}")

        # Agregar un pequeño retardo de 1 segundo
        time.sleep(1)



# Recorrer los indicadores en el catálogo y obtener su metainformación
def get_save_metadata(catalog_data):
    for indicator in catalog_data["indicators"]:
        varcd_cod = indicator["varcd"]
        metadata = extract_metadata(varcd_cod, lang)
        metadata_path = f"app/indicators_data/ine_files/metadata_{varcd_cod}.json"

        with open(metadata_path, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=4, ensure_ascii=False)
        print(f"Metainformación del Indicador {varcd_cod} guardada en metadata_{varcd_cod}.json")

        # Agregar un pequeño retardo de 1 segundo
        time.sleep(1)




if __name__ == "__main__":
    lang = "PT"
    
    # Extraer el catálogo de indicadores
    catalog_data = extract_catalog(lang)

    #get_save_catalog(catalog_data=catalog_data)
    get_save_data(catalog_data=catalog_data)
    #get_save_metadata(catalog_data=catalog_data)



    






