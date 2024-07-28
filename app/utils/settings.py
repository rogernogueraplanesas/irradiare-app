
# ____________________________________COMMON METADATA FILES____________________________________
original_dicofre_data = "app/utils/loc_codes/original_dicofre.json"
original_zipcode_data = "app/utils/loc_codes/original_zipcodes.csv"
dicofre_data = "app/utils/loc_codes/dicofre.json"
zipcode_data = "app/utils/loc_codes/zipcodes.json"
nuts_data = "app/utils/nuts_levels/NUTS.json"
continental_dicode = {'01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18'}
madeira_dicode = {'31', '32'}
açores_dicode = {'41', '42', '43', '44', '45', '46', '47', '48', '49'}
continental_zipcode = {'1', '2', '3', '4', '5', '6', '7', '8'}
madeira_zipcode = {'90', '91', '92', '93', '94'}
açores_zipcode = {'95', '96', '97', '98', '99'}


# _________________________________COMMON SCRAPING SETTINGS________________________________
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
headers = {'User-Agent': user_agent}


# __________________________________________EREDES_________________________________________

# DATA/METADATA EXTRACTION:
eredes_url = 'https://e-redes.opendatasoft.com/explore/?sort=modified'
eredes_files_folder = "app/indicators_data/eredes/data/raw/"
eredes_metadata = "app/indicators_data/eredes/metadata/metadata.csv"

# DATA/METADATA PROCESSING:
eredes_raw_data = "app/indicators_data/eredes/data/raw/"
eredes_metadata = "app/indicators_data/eredes/metadata/metadata.csv"
eredes_merged = "app/indicators_data/eredes/data/temp_eredes_merged/"
eredes_removed_files = [
    "articles.csv",
    "civil-parishes-portugal.csv",
    "districts-portugal.csv",
    "municipalities-portugal.csv",              #-----------------------------------------------------------#
    "network-scheduling-work.csv",              # List of files removed during the processing - not useful. #
    "news-events.csv",                          #-----------------------------------------------------------#
    "capacidade-rececao-rnd.csv",
    "consumo_horario_codigo_postal_7_digitos.csv"
] 
eredes_final_data = "app/indicators_data/eredes/data/processed/"
eredes_date_cols = ["Date"]
eredes_year_cols = ["Year", "ANO", "year", "ano"]     #------------------------------------------------------------------#
eredes_month_cols = ["Month", "month", "mes"]         # Naming options for time related columns in the eredes data files #
eredes_semester_cols = ["Semester"]                   #------------------------------------------------------------------#
eredes_quarter_cols = ["Quarter"]


# _________________________________________EUROSTAT________________________________________
# When interested in working with from Eurostat navigation tree , a classification of Eurostat datasets into hierarchical categories, it is possible to retrieve a TXT or XML representation named "table of contents" (TOC)
# Path to the table of contents file
eurostat_table_contents = "app/indicators_data/eurostat/table_of_contents_en.txt" # Obtained from https://wikis.ec.europa.eu/display/EUROSTATHELP/API+-+Getting+started+with+catalogue+API
# Base URL for Eurostat metadata
eurostat_metadata_url = "https://ec.europa.eu/eurostat/cache/metadata/en/"
# Eurostat base folder
eurostat_folder = "app/indicators_data/eurostat/"
# Folder to save Eurostat data
eurostat_data_folder = "app/indicators_data/eurostat/eurostat_data"
# Folder to save Eurostat metadata
eurostat_metadata_folder = "app/indicators_data/eurostat/eurostat_metadata"
# Filename for saving metadata zip links
eurostat_metadata_filename = "metadata_zip_links.csv"
# Filename for saving manual download links
eurostat_metadata_manual_filename = "metadata_manual_download.csv"


# ___________________________________________INE___________________________________________
ine_url = "https://www.ine.pt"
ine_catalog_path = "app/indicators_data/ine/ine_files/"
ine_catalog_filename = "indicators_catalog.json"
ine_data_path = "app/indicators_data/ine/ine_files/ine_data/"
ine_metadata_path = "app/indicators_data/ine/ine_files/ine_metadata/"


# _____________________________________THE WORLD BANK______________________________________
wb_catalog_path = "app/indicators_data/worldbank/wb_files/"
wb_catalog_filename = "wbindicators.json"
wb_data_path = "app/indicators_data/worldbank/wb_files/wb_data.json"
wb_metadata_path= "app/indicators_data/worldbank/wb_files/wb_metadata.json"