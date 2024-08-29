CREATE_STAGGING_TABLE = """
CREATE IF NOT EXISTS stg_table(
nuts1 TEXT,
nuts2 TEXT,
nuts3 TEXT,
geocode TEXT,
type TEXT,
distrito TEXT,
concelho TEXT,
freguesia TEXT,
timecode TEXT,
value_value TEXT,
name_indicator TEXT,
description TEXT,
units TEXT,
units_desc TEXT,
calculation TEXT,
source TEXT,
source_code TEXT,
attributes TEXT,
value_tag TEXT,
name_attribute TEXT,
value_attribute TEXT
);
"""

CREATE_NUTS_TABLE = """
CREATE TABLE IF NOT EXISTS nuts(
id_nuts INTEGER PRIMARY KEY AUTOINCREMENT,
nuts1 TEXT,
nuts2 TEXT,
nuts3 TEXT
);
"""

CREATE_GEODATA_TABLE = """
CREATE TABLE IF NOT EXISTS geodata(
id_geodata INTEGER PRIMARY KEY AUTOINCREMENT,
geocode TEXT,
type TEXT
);
"""

CREATE_GEOLEVEL_TABLE = """
CREATE TABLE IF NOT EXISTS geolevel(
id_geolevel INTEGER PRIMARY KEY AUTOINCREMENT,
distrito TEXT,
concelho TEXT,
freguesia TEXT
);
"""

CREATE_VALUES_TABLE = """
CREATE TABLE IF NOT EXISTS values(
id_value INTEGER PRIMARY KEY AUTOINCREMENT,
timecode REAL,
value REAL
);
"""

CREATE_INDICATORS_TABLE = """
CREATE TABLE IF NOT EXISTS indicators(
id_indicator INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
description TEXT,
units TEXT,
units_desc TEXT,
calculation TEXT,
source TEXT,
source_code TEXT,
attributes TEXT
);
"""

CREATE_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS tags(
id_tag INTEGER PRIMARY KEY AUTOINCREMENT,
value TEXT
);
"""

CREATE_ATTRIBUTES_TABLE = """
CREATE TABLE IF NOT EXISTS attributes(
id_attribute INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
value TEXT
);
"""