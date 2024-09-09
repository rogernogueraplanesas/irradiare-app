<br>
<div align="center">
  <img src="images/eurostat-logo.png" width="30%" height="30% alt="E-Redes"">
</div>

# Eurostat Data Pathway


This document is a guide that describes how data for indicators is obtained from the Eurostat Database, as well as the processes for completing and cleaning this data. Although the data insertion scripts may be located in the same common folder as the extraction and transformation scripts, the insertion process will be executed separately from the other steps.

---
## Isolated execution
To execute the data **extraction and transformation scripts** in order to obtain a set of data files ready to be inserted into the database, input the following commands in the terminal:

Set the current directory to the eredes folder:
```
cd /path/to/irradiare_app/app/indicators_data/eurostat
```

Execute the main script:
```
python eurostat_main.py
```

The steps in the *eurostat_main* script can also be executed individually from their respective paths.

---

## Process sequence
Brief description of E-REDES data lifecycle:

  1. The *Table of Contents* is downloaded. The "table of contents" (TOC) provides a textual representation of Eurostat navigation tree and information on datasets and tables available on the Eurostat website and via the API. The TOC is downloaded in .txt format via API from [API - Detailed guidelines - Catalogue API - TOC](https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en).
     
  2. After the source code (uniquely identifier code) is extracted for the indicators listed in the TOC, all data files can be retrieved using the EurostatAPIClient. This client efficiently fetches JSON data from the Eurostat REST service and converts it into a pandas DataFrame. For more information, visit [here](https://github.com/opus-42/eurostat-api-client).

  3. During the data retrieval process, while the datasets are still in pandas format, the label (descriptive name) for each dataset is extracted. In each iteration, the source code and its corresponding label are appended to a list, which will be saved as a complementary file (datasets_definitions.csv) for later steps.

  4. Before retrieving any metadata file, it is essential to match each indicator with its corresponding metadata. To facilitate this process, the TOC is downloaded again, but in XML format. 

  5. By scraping data from the XML TOC file, it becomes easier to locate the metadata site link (in .htm format) for each indicator based on the source code. A new CSV file is generated containing two columns: one with all the source codes and the other with their respective metadata links found along the TOC file (eurostat_datacodes.csv).

  6. A request is made to each metadata HTML link to scrape the site using BeautifulSoup. Once the content is retrieved, the goal is to extract the final metadata download link. The first step is to check whether there is any link redirecting to metadata specific to Portuguese indicators. If such a link exists, a request is made to it. In both cases (whether or not there is a Portugal-specific link), the final step is to locate and extract the *Download* link for the metadata. This link is then added to a new CSV file containing two columns: one for the original metadata HTML link and another for the final metadata download link (download_metadata.csv). In case of an error, a separate CSV file is generated (manual_metadata.csv), listing the original metadata HTML links that need to be manually processed to download the final metadata files. Typically, only 4 or 5 indicators encounter errors.

  7.The metadata links listed in 'download_metadata.csv' are automatically executed, and the metadata is downloaded and stored in a specified folder. Meanwhile, the user can manually download the links from manual_metadata.csv and save them in the same folder.

  8. All metadata files are in .zip format. The next step is to unzip them and extract only the .xml metadata files.

  9. With all the CSV data files in one folder and the XML metadata files in another, a new complementary file is created based on the information from eurostat_datacodes.csv, download_metadata.csv, and manual_metadata.csv. As mentioned earlier, the eurostat_datacodes file contains the source code for each data file (which matches the data filenames) along with their corresponding preeliminary HTML metadata link. Similarly, the download_metadata file lists the preeliminary HTML metadata links and the final metadata links, from which the metadata filenames can be extracted using regular expressions (re). A similar situation applies to the manual_metadata file. Obviously, the connecting factor will be the preliminary HTML metadata link, which is present in all the CSV files. The new file will have two columns: one for the source code (data filenames) and another for the corresponding metadata code (metadata filenames). This auxiliary file enables the association of each data file (.json) with its corresponding metadata file (.xml).

  10. The final step involves opening both files to extract the relevant data and metadata needed to create a set of 'processed' data files, which will be ready for insertion into the database.


  <div align="center">
    <img src="images/card_metadata.jpg" width="40%" height="40%" alt="Card Metadata">
    <br>
    <sub>Indicator's card metadata (example)</sub>
  </div>
  
  <br>
  
  3. The indicator data files are **merged** with their corresponding metadata from the previously generated metadata file, creating a **temporary** file for each indicator. The matching process is based on the source code name (src_code).


  4. The data in the temporary merged files is completed by adding time and geolocation information. After this enhancement, a final data file is generated for each indicator, and the corresponding temporary files are **deleted**. <br>
     - A **timecode** is added based solely on the data from the file itself (columns such as date, year, month, etc.). <br><br>
     **The timecode structure follows a logical sequence:**
       
       + YYYY: Year only (4 digits)
       + YYYYMM: Year + Month (6 digits)
       + YYYYMMDD: Year + Month + Day (8 digits)
       + *Any previous combination* + S*X*: S followed by a digit shows the semester of the year
       + *Any previous combination* + Q*X*: Q followed by a digit shows the quarter of the year

      <br>
 
     - **Geolocation data (distrito, concelho, freguesia, and NUTS I, II, III)** is extracted from the `dicofre.json`, `zipcodes.json`, and `NUTS.json` files. <br>
     For each record in the data file, there is a column with either a dicofre or zipcode number (normally, one is present while the other is not).
     Each value in this column is matched totally or partially with the corresponding entry in the dicofre or zipcode files, this match provides information about the distrito, concelho, and freguesia. <br>
     Using the concelho, it is possible to determine the NUTS I, II, and III regions. If the concelho is not available because the zipcode or dicofre is too short, a partial match is performed to extract at least the NUTS I and II levels, or just the NUTS I level.

  
  6. The raw data files are **never deleted** but are replaced each time the data extraction script is executed.

---

## E-REDES Folder Structure:
The folder structure **before executing** the program is as follows:

```
eredes
    |
    +- data_extraction ............. --> Code to retrieve data and metadata
    |   |
    |   +- eredes_data.py .......... --> Code to retrieve data from E-REDES data source
    |   |
    |   +- eredes_metadata.py ...... --> Code to retrieve metadata related to each data file
    |
    +- data_processing ............. --> Code to merge, clean, and complete the raw data files
    |   |
    |   +- eredes_final_format.py .. --> Code to clean and complete data files
    |   |    
    |   +- eredes_merge_files.py ... --> Code to merge each data file with its corresponding metadata
    |
    +- data_load ................... --> Code to select and load the desired data to the database(s)
    |   |
    |   +- sqlite_load.py .......... --> Code to insert eredes indicators' data to the SQLite database
    |   |    
    |   +- sqlite_queries.py ....... --> Reusable SQL queries for the SQLite data insertion
    |
    +- main.py ..................... --> Main script to execute the full E-REDES data process
```

<br>

**After running** the program, the resulting directory structure, is as follows:

<br>

```
eredes
    |
    +- data ........................ --> Holds processed and unprocessed data files
    |   |
    |   +- processed  .............. --> Contains the processed data files.
    |   |
    |   +- raw  .................... --> Contains the downloaded/unprocessed data files.
    |
    +- data_extraction ............. --> Code to retrieve data and metadata
    |   |
    |   +- eredes_data.py .......... --> Code to retrieve data from E-REDES data source
    |   |
    |   +- eredes_metadata.py ...... --> Code to retrieve metadata related to each data file
    |
    +- data_processing ............. --> Code to merge, clean, and complete the raw data files
    |   |
    |   +- eredes_final_format.py .. --> Code to clean and complete data files
    |   |    
    |   +- eredes_merge_files.py ... --> Code to merge each data file with its corresponding metadata
    |
    +- data_load ................... --> Code to select and load the desired data to the database(s)
    |   |
    |   +- sqlite_load.py .......... --> Code to insert eredes indicators' data to the SQLite database
    |   |    
    |   +- sqlite_queries.py ....... --> Reusable SQL queries for the SQLite data insertion
    |
    +- main.py ..................... --> Main script to execute the full E-REDES data process
    |
    +- metadata  ................... --> Contains the extracted metadata file
```

<br>

[![My Skills](https://skillicons.dev/icons?i=sqlite&theme=light)](https://skillicons.dev)  As explained at the beginning, the `processed` data is selected and inserted into the **SQLite database**.<br>
The source code can be found 'here', while its execution is performed 'here', separately from the extraction and transformation logic.
