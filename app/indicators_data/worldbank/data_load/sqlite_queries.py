INSERT_DATA_STAGGING = """
INSERT INTO stg_table (
    nuts1, nuts2, nuts3, geocode, type, distrito, 
    concelho, freguesia, timecode, data_value, 
    name_indicator, description, units, units_desc, 
    calculation, source, source_code, attributes, 
    name_attribute, value_attribute, value_tag
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
