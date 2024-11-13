STORAGE_DATAYPES = [
    "string",
    "int"
    "double", 
    "float",
    "tinyint",
    "smallint"
    "bigint",
    "boolean",
    "date",
    "geopoint",
    "geometry",
    "array",
    "object",
    "map"
    ]

NUMERICAL_STORAGE_DATATYPES = [
    "int",
    "double", 
    "float",
    "tinyint",
    "smallint",
    "bigint"
]

# MEANING_DATATYPES keys correpsonds to the meanings we see in the UI, 
# while values correspond to their labels in dataset settings.
MEANING_DATATYPES = { 
    "Text": "Text",
    "Decimal": "DoubleMeaning",
    "Integer": "LongMeaning",
    "Boolean": "Boolean",
    "Date": "Date",
    "Object": "JSONObjectMeaning",
    "Array": "JSONArrayMeaning",
    "Natural lang.": "FreeText",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "GeoPoint": "GeoPoint",
    "Geometry": "GeometryMeaning",
    "Country": "CountryMeaning",
    "US State": "USStateMeaning",
    "IP Address": "IPAddress",
    "HTTP Query string": "QueryString",
    "URL": "URL",
    "User-Agent": "UserAgent",
    "E-mail address": "Email",
    "Temperature": "Temperature",
    "Bag of words": "BagOfWordsMeaning",
    "Gender": "Gender",
    "Size/Weight": "Measure",
    "Currency code": "CurrencyMeaning",
    "Money amount": "CurrencyAmountMeaning",
    "Date (unparsed)": "DateSource",
    "Decimal (comma)": "FrenchDoubleMeaning"
    }