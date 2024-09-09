<br>
<div align="center">
  <img src="images/eurostat-logo.png" width="30%" height="30% alt="E-Redes"">
</div>

# Eurostat Data Pathway


This document is a guide that describes how data for indicators is obtained from the Eurostat Database, as well as the processes for completing and cleaning this data. Although the data insertion scripts may be located in the same common folder as the extraction and transformation scripts, the insertion process will be executed separately from the other steps.

---
## Isolated execution
To execute the data **extraction and transformation scripts** in order to obtain a set of data files ready to be inserted into the database, input the following commands in the terminal:

Set the current directory to the eurostat folder:
```
cd /path/to/irradiare_app/app/indicators_data/eurostat
```

Execute the main script:
```
python eurostat_main.py
```

The steps in *eurostat_main.py* can also be executed individually through their respective scripts.

---

## Process sequence
Brief description of E-REDES data lifecycle:

  1. The *Table of Contents (TOC)* is downloaded. It provides a textual representation of Eurostat navigation tree and information on datasets and tables available on the Eurostat website and via the API. The TOC is obtained in **.txt format** via API from [API - Detailed guidelines - Catalogue API - TOC](https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en).
     
  2. After the source code (uniquely identifier code) is extracted for all the indicators listed in the TOC, the data files can be retrieved using the **EurostatAPIClient**. This client efficiently fetches JSON data from the Eurostat REST service and converts it into a pandas DataFrame. For more information, visit [here](https://github.com/opus-42/eurostat-api-client).

  3. During the data retrieval process, while the datasets are still in pandas format, the **label** (descriptive name) for each dataset is extracted. In each iteration, the source code and its corresponding label are appended to a list, which will be saved as a complementary file (***datasets_definitions.csv***) for later steps. **The datasets are saved in JSON format**.

  4. Before retrieving any metadata file, it is essential to match each indicator with its corresponding metadata. To facilitate this process, the **TOC is downloaded again, but in XML format**. 

  5. By scraping data from the XML TOC file, it becomes easier to locate the metadata site link (in HTML format) for each indicator based on the source code. **A new CSV file is generated** containing two columns: one with all the source codes and the other with their respective metadata links found along the TOC file (***eurostat_datacodes.csv***).

  6. A request is made to each metadata HTML link to scrape the site using **BeautifulSoup**. Once the content is retrieved, the goal is to extract the final metadata download link.<br> The first step is to check whether there is any link redirecting to metadata specific to Portuguese indicators. If such a link exists, a request is made to it. In both cases (whether or not there is a Portugal-specific link), the final step is to locate and extract the <ins>**Download**</ins> link for the metadata.

<br>
(Imatges on es troba el download link)
<br>

  7. This link is then added to a **new CSV file** containing two columns: one for the original metadata HTML link and another for the final metadata download link (***download_metadata.csv***).

<br>
(recorte amb el download_metadata.csv)
<br>

  8. **In case of an error**, a separate CSV file is generated (***manual_metadata.csv***), listing the original metadata HTML links that need to be manually processed to download the final metadata files. Typically, **only 4 or 5** indicators encounter errors.
  <br>
  (recorte amb manual_metadata.csv)
  <br>
  
  9. The metadata links listed in *download_metadata.csv* are automatically executed, and the metadata is downloaded and stored in a specified folder. Meanwhile, the user can manually download the links from manual_metadata.csv and **save them in the same folder**.

  10. All metadata files are in .zip format. The next step is to unzip them and extract only the **.xml metadata files**.


  11.  With all the CSV data files in one folder and the XML metadata files in another, a new complementary file (***merged_codes.csv***) is created based on the information from *eurostat_datacodes.csv*, *download_metadata.csv*, and *manual_metadata.csv*. As mentioned earlier, the eurostat_datacodes file contains the source code for each data file (which matches the data filenames) along with their corresponding preeliminary HTML metadata link. Similarly, the download_metadata file lists the preeliminary HTML metadata links and the final metadata links, from which the metadata filenames can be extracted using regular expressions (re). A similar situation applies to the manual_metadata file. Obviously, **the connecting factor will be the preliminary HTML metadata link**, which is present in all the CSV files. The new file will have two columns: one for the source code (data filenames) and another for the corresponding metadata code (metadata filenames). This auxiliary file enables the association of each data file (.json) with its corresponding metadata file (.xml).
  <br>
  (recorte amb merged_codes.csv)
  <br>
  12.  The final step involves **iterating** over the rows present in *merged_codes.csv*, opening the corresponding files for each of them as well as the *datasets_definitions.csv* file, and **extracting the relevant data and metadata** needed to create a set of 'processed' data files, which will be ready for insertion into the database.

The complementary files generated during the program's execution—such as *datasets_definitions.csv*, *download_metadata.csv*, *eurostat_datacodes.csv*, *manual_metadata.csv*, and *merged_codes.csv*—are saved in a folder named **eurostat_comp_files/**, located within **eurostat_data/**.

The purpose of these files is to **store and reuse key information** needed throughout the process, such as the relationships between dataset source codes and metadata codes/links. This information is used to merge files or in some cases to add data (e.g., dataset definitions) to complete the final data files.


  <div align="center">
    <img src="images/card_metadata.jpg" width="40%" height="40%" alt="Card Metadata">
    <br>
    <sub>Indicator's card metadata (example)</sub>
  </div>
  
  <br>
  
---

## Eurostat Folder Structure:
The folder structure **before executing** the program is as follows:

```
eurostat
    |
    +- data_extraction ............. --> Code to retrieve data and metadata
    |   |
    |   +- eurostat_client_data.py ... --> Code to retrieve Eurostat datasets and definitions
    |   |
    |   +- eurostat_get_metadata.py .. --> Code to retrieve complete metadata folders
    |
    +- data_processing ............. --> Code to merge, clean, and complete the raw data files
    |   |
    |   +- eurostat_datacodes.py ... --> Code to match each dataset source code with a metadata HTML link
    |   |    
    |   +- eurostat_final_data.py .. --> Code to merge data and metadata files completing the final CSV files
    |   |
    |   +- eurostat_join_codes.py .. --> Code to merge metadata HTML links and final metadata download links
    |   |    
    |   +- extract_xml_files ....... --> Code to to unzip the downloaded metadata folders and extract the .xml files
    |
    +- data_load ................... --> Code to select and load the desired data to the database(s)
    |   |
    |   +- sqlite_load.py .......... --> Code to insert eredes indicators' data to the SQLite database
    |   |    
    |   +- sqlite_queries.py ....... --> Reusable SQL queries for the SQLite data insertion
    |
    +- eurostat_main.py ............ --> Main script to execute the full E-REDES data process
```

<br>

**After running** the program, the resulting directory structure, is as follows:

<br>

```
eurostat
    |
    +- data_extraction ............. --> Code to retrieve data and metadata
    |   |
    |   +- eurostat_client_data.py ... --> Code to retrieve Eurostat datasets and definitions
    |   |
    |   +- eurostat_get_metadata.py .. --> Code to retrieve complete metadata folders
    |
    +- data_processing ............. --> Code to merge, clean, and complete the raw data files
    |   |
    |   +- eurostat_datacodes.py ... --> Code to match each dataset source code with a metadata HTML link
    |   |    
    |   +- eurostat_final_data.py .. --> Code to merge data and metadata files completing the final CSV files
    |   |
    |   +- eurostat_join_codes.py .. --> Code to merge metadata HTML links and final metadata download links
    |   |    
    |   +- extract_xml_files ....... --> Code to to unzip the downloaded metadata folders and extract the .xml files
    |
    +- data_load ................... --> Code to select and load the desired data to the database(s)
    |   |
    |   +- sqlite_load.py .......... --> Code to insert eredes indicators' data to the SQLite database
    |   |    
    |   +- sqlite_queries.py ....... --> Reusable SQL queries for the SQLite data insertion
    |
    +- eurostat_main.py ............ --> Main script to execute the full E-REDES data process
    |
    +- eurostat_data ............... --> Holds processed, unprocessed data files and complementary files
    |   |
    |   +- eurostat_comp_files  .... --> Contains complementary files generated along the execution
    |   |
    |   +- processed  .............. --> Contains the final processed data files.
    |   |
    |   +- raw  .................... --> Contains the downloaded/unprocessed data files.
    |
    +- eurostat_metadata  .......... --> Contains the extracted metadata XML files
```

<br>

[![My Skills](https://skillicons.dev/icons?i=sqlite&theme=light)](https://skillicons.dev)  As explained at the beginning, the `processed` data is selected and inserted into the **SQLite database**.<br>
The source code can be found 'here', while its execution is performed 'here', separately from the extraction and transformation logic.
