import requests
import zipfile
import os

# URL de la API donde se descargará el archivo
url = "https://api.worldbank.org/v2/en/country/PRT?downloadformat=csv&_gl=1*d5zsxg*_gcl_au*MTA2OTI2MTU1My4xNzI1NzE5Mzgy"


# Ruta donde quieres guardar el archivo ZIP descargado

complementary_path = "app/indicators_data/worldbank/wb_data/wb_comp_files"

ruta_zip = "app/indicators_data/worldbank/wb_data/wb_comp_files/files.zip"

ruta_data = "app/indicators_data/worldbank/wb_data/raw"

ruta_metadata = "app/indicators_data/worldbank/wb_metadata"

os.makedirs(complementary_path, exist_ok=True)
os.makedirs(ruta_data, exist_ok=True)
os.makedirs(ruta_metadata, exist_ok=True)

# Descargar el archivo ZIP
response = requests.get(url)
with open(ruta_zip, 'wb') as f:
    f.write(response.content)


with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
    # Extraer un archivo en específico
    zip_ref.extract('API_PRT_DS2_en_csv_v2_3412148.csv', ruta_data)
    zip_ref.extract('Metadata_Indicator_API_PRT_DS2_en_csv_v2_3412148.csv', ruta_metadata)


print("Proceso completado.")
