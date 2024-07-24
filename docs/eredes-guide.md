# E-REDES Data Pathway

This document is a guide that describes how data for indicators is obtained from the E-REDES Open Data Portal, as well as the processes for completing and cleaning this data.

---

## Process structure
Brief description of E-REDES data lifecycle:

  1. The data is downloaded by means of dynamic web scraping the [E-REDES Open Data Portal](https://e-redes.opendatasoft.com/pages/homepage/). One data file is obtained per indicator.
  2. The required metadata is extracted by web scraping the `Informação` tab for each of the involved indicators. A single file is obtained for all the metadata.
  3. The data files are merged with their corresponding metadata, creating a temporary file for each.
  4. The merged files are completed by adding time and geolocation data. <br> A timecode is added based only on the data itself, while the geolocation data (distrito, concelho, freguesía + NUTS I, II, II) is extracted from the `dicofre.json`, `zipcodes.csv` and `NUTS.json` files by matching the zipcode or dicofre number present in each record.
