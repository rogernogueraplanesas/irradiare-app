# E-REDES Data Pathway


>External files involved along the process (found in /utils):
  >- dicofre.csv (Modified version. Original source: [freguesias-metadata.json](https://dados.gov.pt/pt/datasets/freguesias-de-portugal/) )
  >- zipcodes.csv (Modified version. Original source: [CP7_Portugal_nov2022.txt](https://github.com/temospena/CP7/tree/master/CP7%20Portugal) )
  >- NUTS.csv (Proprietary file. Created based on the following article: [List of regions and sub-regions of Portugal](https://en.wikipedia.org/wiki/List_of_regions_and_sub-regions_of_Portugal) )
> 
>The dicofre and zipcodes original files where formatted by executing the 'format_loc_codes.py' script, found in the same /utils folder.

<br>
This document is a guide that describes how data for indicators is obtained from the E-REDES Open Data Portal, as well as the processes for completing and cleaning this data.

---

## Process sequence
Brief description of E-REDES data lifecycle:

  1. The data is downloaded by means of dynamic web scraping the [E-REDES Open Data Portal](https://e-redes.opendatasoft.com/pages/homepage/) site. One data file is obtained per indicator.
  2. The required metadata is extracted by web scraping the `Informação` tab for each of the involved indicators. A single file is obtained for all the metadata.
  3. The data files are merged with their corresponding metadata, creating a temporary file for each.
  4. The merged files are completed by adding time and geolocation data. <br> A timecode is added based solely on the data from the file itself, while the geolocation data (distrito, concelho, freguesía, and NUTS I, II, III) is extracted from the `dicofre.json`, `zipcodes.csv`, and `NUTS.json` files by matching the zipcode or dicofre number present in each record of the file.

---

## E-REDES Folder Structure:
The  folder structure before executing the program is as it follows:

```
eredes
    |
    +- data_extraction .......... --> Code to retrieve data and metadata
    |   |
    |   +- eredes_data .......... --> Code to retrieve data from E-REDES data source
    |   |
    |   +- eredes_metadata ...... --> Code to retrieve metadata related to each data file
    |
    +- data_processing .......... --> Code to merge, clean and complete the raw data files
        |
        +- eredes_final_format  . --> Code to clean and complete data files
        |    
        +- eredes_merge_files  .. --> Code to merge each data file with its corresponding metadata
```

After running the program, the resulting directory structure, excluding the temporary folder (which is deleted during execution and used to hold files generated from merging raw data files with their metadata), is as follows:

```
eredes
    |
    +- data ..................... --> Holds processed and unprocessed data files
    |   |
    |   +- processed  ........... --> Processed data files.
    |   |
    |   +- raw  ................. --> Unprocessed data files.
    |
    +- data_extraction .......... --> Code to retrieve data and metadata
    |   |
    |   +- eredes_data .......... --> Code to retrieve data from E-REDES data source
    |   |
    |   +- eredes_metadata ...... --> Code to retrieve metadata related to each data file
    |
    +- data_processing .......... --> Code to merge, clean and complete the raw data files
    |   |
    |   +- eredes_final_format  . --> Code to clean and complete data files
    |   |
    |   +- eredes_merge_files  .. --> Code to merge each data file with its corresponding metadata
    |
    +- metadata  ................ --> Contains the extracted metadata file
        |
        +- eredes_final_format  . --> Metadata file
```

<br>

[![My Skills](https://skillicons.dev/icons?i=sqlite&theme=light)](https://skillicons.dev)
The processed data `processed` is selected and inserted into the SQLite database. Source code in /database.

