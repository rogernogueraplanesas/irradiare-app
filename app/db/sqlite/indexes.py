TIMECODE_IDX = """
CREATE INDEX idx_dataval_timecode
ON data_values(timecode);
"""

GEOCODE_IDX = """
CREATE INDEX idx_geodata_geocode
ON geodata(geocode);
"""

INDICATOR_NAME_IDX = """
CREATE INDEX idx_indicator_name
ON indicator(name);
"""


ID_GEODATA_IDX = """
CREATE INDEX idx_dataval_id_geodata
ON data_values(id_geodata);
"""

ID_INDICATOR_IDX = """
CREATE INDEX idx_dataval_id_indicator 
ON data_values(id_indicator);
"""

