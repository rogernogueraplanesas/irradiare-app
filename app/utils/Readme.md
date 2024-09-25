# Content

Folder structure and brief explanation of key content

```
utils
    |
    +- loc_codes ................ --> Folder containing the original and modified dicofre and zipcode files and related information
    |
    +- nuts_levels ................ --> Folder containing the Portuguese NUTS organization and related information
    |
    +- format_loc_codes.py ............. --> Code to modify the structure of the dicofre and zipcode data files
    |
    +- settings.py ................... --> File containing the variables used along the project
    |
    +- (Other files) ................... --> Complementary files providing information about the data sources used
```

<br>

The `format_loc_codes.py` file contains the necessary code to transform the original dicofre and zipcode files found in the *loc_codes* folder, which provide geolocation data based on dicofre codes or zip codes, into clean, formatted JSON files saved in the same folder. These JSON files are utilized in various sections of the project.
<br><br>
`settings.py` is a key file for the app operation.

