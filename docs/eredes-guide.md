# E-REDES Data Pathway


>External files involved along the process:
  >- dicofre.csv (Original source: [freguesias-metadata.json](https://dados.gov.pt/pt/datasets/freguesias-de-portugal/) )
  >- zipcodes.csv (Modified version. Original source: [CP7_Portugal_nov2022.txt](https://github.com/temospena/CP7/tree/master/CP7%20Portugal) )
  >- NUTS.csv (Proprietary file. Created based on the following article: [List of regions and sub-regions of Portugal](https://en.wikipedia.org/wiki/List_of_regions_and_sub-regions_of_Portugal) )



This document is a guide that describes how data for indicators is obtained from the E-REDES Open Data Portal, as well as the processes for completing and cleaning this data.

---

## Process structure
Brief description of E-REDES data lifecycle:

  1. The data is downloaded by means of dynamic web scraping the [E-REDES Open Data Portal](https://e-redes.opendatasoft.com/pages/homepage/). One data file is obtained per indicator.
  2. The required metadata is extracted by web scraping the `Informação` tab for each of the involved indicators. A single file is obtained for all the metadata.
  3. The data files are merged with their corresponding metadata, creating a temporary file for each.
  4. The merged files are completed by adding time and geolocation data. <br> A timecode is added based solely on the data itself, while the geolocation data (distrito, concelho, freguesía, and NUTS I, II, III) is extracted from the `dicofre.json`, `zipcodes.csv`, and `NUTS.json` files by matching the zipcode or dicofre number present in each record.
