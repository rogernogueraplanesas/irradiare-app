# _________________________________COMMON SCRAPING SETTINGS________________________________
user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
headers = {'User-Agent': user_agent}

# __________________________________________EREDES_________________________________________
eredes_url = 'https://e-redes.opendatasoft.com/explore/?sort=modified'
eredes_files_folder = "app/indicators_data/eredes/eredes_data"
eredes_metadata = "app/indicators_data/eredes/eredes_metadata.csv"

# _________________________________________EUROSTAT________________________________________
# When interested in working with from Eurostat navigation tree , a classification of Eurostat datasets into hierarchical categories, it is possible to retrieve a TXT or XML representation named "table of contents" (TOC)
eurostat_table_contents= "app/indicators_data/eurostat/table_of_contents_en.txt" # Obtained from https://wikis.ec.europa.eu/display/EUROSTATHELP/API+-+Getting+started+with+catalogue+API
eurostat_metadata_url= "https://ec.europa.eu/eurostat/cache/metadata/en/"
eurostat_metadata_url_path= "app/indicators_data/eurostat/metadata_zip_links.csv"
eurostat_metadata_manual_urls= "app/indicators_data/eurostat/metadata_manual_download.csv"

# ___________________________________________INE___________________________________________
ine_url = "https://www.ine.pt"
ine_catalog_path = "app/indicators_data/ine/ine_files/catalogo_indicadores.json"

# _____________________________________THE WORLD BANK______________________________________
wb_catalog_path = "app/indicators_data/worldbank/wb_files/wbindicators.json"
wb_data_path = "app/indicators_data/worldbank/wb_files/wb_data.json"
wb_metadata_path= "app/indicators_data/worldbank/wb_files/wb_metadata.json"