# ____________________________________GENERAL METADATA DATA____________________________________
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


# _________________________________GENERAL SCRAPING SETTINGS________________________________
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
headers = {'User-Agent': user_agent}


# __________________________________________EREDES_________________________________________

# DATA/METADATA EXTRACTION:
eredes_url = 'https://e-redes.opendatasoft.com/explore/?sort=modified'
eredes_metadata_folder = "app/indicators_data/eredes/eredes_metadata/"
eredes_metadata = "app/indicators_data/eredes/eredes_metadata/metadata.csv"

# DATA/METADATA PROCESSING:
eredes_raw_data = "app/indicators_data/eredes/data/raw/"
eredes_merged = "app/indicators_data/eredes/data/temp_eredes_merged/"
eredes_removed_files = [
    "articles.csv",
    "civil-parishes-portugal.csv",
    "districts-portugal.csv",
    "municipalities-portugal.csv",              #-----------------------------------------------------------#
    "network-scheduling-work.csv",              # List of files removed during the processing - not useful. #
    "news-events.csv",                          #-----------------------------------------------------------#
    "capacidade-rececao-rnd.csv",
    "consumo_horario_codigo_postal_7_digitos.csv",
    "12-continuidade-de-servico-indicadores-gerais-de-continuidade-de-servico.csv",
    "15-ordens-de-servico.csv",
    "20-caracterizacao-pes-contrato-ativo.csv",
    "21-contadores-de-energia.csv",
    "outages-per-geography.csv",
    "postos-transformacao-distribuicao.csv",
    "rede-inteligente.csv"

] 
eredes_final_data = "app/indicators_data/eredes/data/processed/"
eredes_date_cols = ["Date/Time", "Date"]
eredes_year_cols = ["Year", "ANO", "year", "ano"]     #------------------------------------------------------------------#
eredes_month_cols = ["Month", "month", "mes"]         # Naming options for time related columns in the eredes data files #
eredes_semester_cols = ["Semester"]                   #------------------------------------------------------------------#
eredes_quarter_cols = ["Quarter"]


# _________________________________________EUROSTAT________________________________________
# Eurostat TOC (Table of Contents) URL in .xml format
eurostat_toc_url_txt = "https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en"
# Path to TOC folder
eurostat_toc_folder = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/"
# Path to TOC (Eurostat Table of Contents) in .txt
eurostat_toc_txt = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/table_of_contents_en.txt"
# Folder to save Eurostat raw data
eurostat_raw_data = "app/indicators_data/eurostat/eurostat_data/raw"
# Path to eurostat complementary data files
eurostat_comp_files = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files"
# File with definitions for each eurostat dataset code (datacode)
eurostat_dataset_def = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/datasets_definitions.csv"
# Eurostat TOC (Table of Contents) URL in .xml format
eurostat_toc_url_xml = "https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/xml"
# Path to TOC (Eurostat Table of Contents) in .xml
eurostat_toc_xml = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/table_of_contents.xml"
# Path to Eurostat indicators codes list
eurostat_datacodes = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/eurostat_datacodes.csv"
# Abbreviations for all the possible countries to select in the Eurostat db
eurostat_country_codes = [
    "eu", "be", "el", "lt", "pt", "bg", "es", "lu", "ro", "cz", "fr", "hu", "si", 
    "dk", "hr", "mt", "sk", "de", "it", "nl", "fi", "ee", "cy", "at", "se", 
    "ie", "lv", "pl", "is", "no", "li", "ch", "ba", "me", "md", "mk", "ge", 
    "al", "rs", "tr", "ua", "xk", "am", "by", "az", "dz", "lb", "sy", "eg", 
    "ly", "tn", "il", "ma", "jo", "ps", "ar", "au", "br", "ca", "cn_x_hk", 
    "hk", "in", "jp", "mx", "ng", "nz", "ru", "sg", "za", "kr", "tw", "uk", "us"
]
# Filename for saving metadata zip links
eurostat_download_metadata = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/download_metadata.csv"
# Filename for saving manual download links
eurostat_manual_metadata = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/manual_metadata.csv"
# Folder to save Eurostat metadata
eurostat_metadata_folder = "app/indicators_data/eurostat/eurostat_metadata"
# Filename for saving merged codes (datacode,metadatacode)
merged_codes_file = "app/indicators_data/eurostat/eurostat_data/eurostat_comp_files/merged_codes.csv"
# Folder to save Eurostat processed data
eurostat_processed_data = "app/indicators_data/eurostat/eurostat_data/processed"

# ___________________________________________INE___________________________________________
ine_url = "https://www.ine.pt"
ine_catalog_path = "app/indicators_data/ine/ine_data/ine_comp_files/"
ine_catalog_filename = "ine_indicators_catalog.json"
ine_data_path = "app/indicators_data/ine/ine_data/raw/"
ine_metadata_path = "app/indicators_data/ine/ine_metadata/"
ine_processed_data = "app/indicators_data/ine/ine_data/processed/"


# _____________________________________THE WORLD BANK______________________________________
wb_catalog_file = "app/indicators_data/worldbank/wb_data/wb_comp_files/wbindicators.json"
wb_data_path = "app/indicators_data/worldbank/wb_data/raw/wb_data.json"
wb_metadata_path = "app/indicators_data/worldbank/wb_metadata/wb_metadata.json"
wb_complete_file = "app/indicators_data/worldbank/wb_data/processed/wb_final_data.csv"