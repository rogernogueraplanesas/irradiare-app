CREATE_STAGGING_TABLE = """
CREATE TABLE IF NOT EXISTS stg_table(
    nuts1 TEXT,
    nuts2 TEXT,
    nuts3 TEXT,
    geocode TEXT,
    type TEXT,
    distrito TEXT,
    concelho TEXT,
    freguesia TEXT,
    timecode TEXT,
    data_value TEXT,
    name_indicator TEXT,
    description TEXT,
    units TEXT,
    units_desc TEXT,
    calculation TEXT,
    source TEXT,
    source_code TEXT,
    attributes TEXT,
    name_attribute TEXT,
    value_attribute TEXT,
    value_tag TEXT
);
"""

CREATE_NUTS_TABLE = """
CREATE TABLE IF NOT EXISTS nuts(
    id_nuts INTEGER PRIMARY KEY AUTOINCREMENT,
    nuts1 TEXT,
    nuts2 TEXT,
    nuts3 TEXT,
    UNIQUE (nuts1, nuts2, nuts3)
);
"""

CREATE_GEODATA_TABLE = """
CREATE TABLE IF NOT EXISTS geodata(
    id_geodata INTEGER PRIMARY KEY AUTOINCREMENT,
    id_nuts INTEGER,
    id_geolevel INTEGER,
    geocode TEXT,
    type TEXT,
    FOREIGN KEY (id_nuts) REFERENCES nuts(id_nuts),
    FOREIGN KEY (id_geolevel) REFERENCES geolevel(id_geolevel)
    UNIQUE (id_nuts, id_geolevel, geocode, type)
);
"""

CREATE_GEOLEVEL_TABLE = """
CREATE TABLE IF NOT EXISTS geolevel(
    id_geolevel INTEGER PRIMARY KEY AUTOINCREMENT,
    distrito TEXT,
    concelho TEXT,
    freguesia TEXT,
    UNIQUE (distrito, concelho, freguesia)
);
"""

CREATE_DATA_VALUES_TABLE = """
CREATE TABLE IF NOT EXISTS data_values(
    id_value INTEGER PRIMARY KEY AUTOINCREMENT,
    id_geodata INTEGER,
    id_indicator INTEGER,
    timecode REAL,
    value NUMERIC,
    attributes TEXT,
    FOREIGN KEY (id_geodata) REFERENCES geodata(id_geodata),
    FOREIGN KEY (id_indicator) REFERENCES indicator(id_indicator)
);
"""


CREATE_VAL_ATTR_TABLE = """
CREATE TABLE IF NOT EXISTS val_attr(
    id_value INTEGER,
    id_attribute INTEGER,
    PRIMARY KEY (id_value, id_attribute),
    FOREIGN KEY(id_value) REFERENCES data_values(id_value),
    FOREIGN KEY(id_attribute) REFERENCES attributes(id_attribute)
);
"""

CREATE_ATTRIBUTES_TABLE = """
CREATE TABLE IF NOT EXISTS attributes(
    id_attribute INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    value TEXT,
    UNIQUE (name, value)
);
"""

CREATE_INDICATOR_TABLE = """
CREATE TABLE IF NOT EXISTS indicator(
    id_indicator INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    units TEXT,
    units_desc TEXT,
    calculation TEXT,
    source TEXT,
    source_code TEXT,
    attributes TEXT,
    UNIQUE(name, source_code)
);
"""

CREATE_TYPE_TABLE = """
CREATE TABLE IF NOT EXISTS type(
    id_indicator INTEGER,
    id_tag INTEGER,
    PRIMARY KEY (id_indicator, id_tag),
    FOREIGN KEY(id_indicator) REFERENCES indicator(id_indicator),
    FOREIGN KEY(id_tag) REFERENCES tags(id_tag)
);
"""

CREATE_TAGS_TABLE = """
CREATE TABLE IF NOT EXISTS tags(
    id_tag INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT,
    UNIQUE (value)
);
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE (email)
);
"""