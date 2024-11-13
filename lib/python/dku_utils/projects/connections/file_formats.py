FILE_FORMATS = [
    "csv", # CSV
    "parquet", # Parquet
    "avro", # Avro
    "orcfile" # ORC
]

CSV_REGULAR_FILE_FORMAT_PARAMS = {
    'style': 'unix',
    'charset': 'utf8',
    'separator': '\t',
    'quoteChar': '"',
    'escapeChar': '\\',
    'maxRowChars': 100000000,
    'dateSerializationFormat': 'ISO',
    'arrayMapFormat': 'json',
    'hiveSeparators': ['\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08'],
    'skipRowsBeforeHeader': 0,
    'parseHeaderRow': False,
    'skipRowsAfterHeader': 0,
    'probableNumberOfRecords': 0,
    'normalizeBooleans': False,
    'normalizeDoubles': True,
    'readAdditionalColumnsBehavior': 'INSERT_IN_DATA_WARNING',
    'readMissingColumnsBehavior': 'DISCARD_SILENT',
    'readDataTypeMismatchBehavior': 'DISCARD_WARNING',
    'writeDataTypeMismatchBehavior': 'DISCARD_WARNING',
    'fileReadFailureBehavior': 'FAIL',
    'compress': 'gz'
}

CSV_METASTORE_COMPATIBLE_FILE_FORMAT_PARAMS = {
    'style': 'escape_only_no_quote',
    'charset': 'utf8',
    'separator': '\t',
    'quoteChar': '"',
    'escapeChar': '\\',
    'maxRowChars': 100000000,
    'arrayItemSeparator': '\x02',
    'mapKeySeparator': '\x03',
    'dateSerializationFormat': 'HIVE',
    'arrayMapFormat': 'hive',
    'hiveSeparators': ['\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08'],
    'skipRowsBeforeHeader': 0,
    'parseHeaderRow': False,
    'skipRowsAfterHeader': 0,
    'probableNumberOfRecords': 0,
    'normalizeBooleans': False,
    'normalizeDoubles': True,
    'readAdditionalColumnsBehavior': 'INSERT_IN_DATA_WARNING',
    'readMissingColumnsBehavior': 'DISCARD_SILENT',
    'readDataTypeMismatchBehavior': 'DISCARD_WARNING',
    'writeDataTypeMismatchBehavior': 'DISCARD_WARNING',
    'fileReadFailureBehavior': 'FAIL',
    'compress': ''
}

CSV_REDSHIFT_SYNC_COMPATIBLE_FILE_FORMAT_PARAMS = {
    'style': 'excel',
    'charset': 'utf8',
    'separator': '\t',
    'quoteChar': '"',
    'escapeChar': '\\',
    'maxRowChars': 100000000,
    'dateSerializationFormat': 'ISO',
    'arrayMapFormat': 'json',
    'hiveSeparators': ['\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08'],
    'skipRowsBeforeHeader': 0,
    'parseHeaderRow': False,
    'skipRowsAfterHeader': 0,
    'probableNumberOfRecords': 0,
    'normalizeBooleans': False,
    'normalizeDoubles': True,
    'readAdditionalColumnsBehavior': 'INSERT_IN_DATA_WARNING',
    'readMissingColumnsBehavior': 'DISCARD_SILENT',
    'readDataTypeMismatchBehavior': 'DISCARD_WARNING',
    'writeDataTypeMismatchBehavior': 'DISCARD_WARNING',
    'fileReadFailureBehavior': 'FAIL',
    'compress': 'gz'
}

CSV_BIG_QUERY_SYNC_COMPATIBLE_FILE_FORMAT_PARAMS = {
    'arrayMapFormat': 'json',
    'charset': 'utf8',
    'compress': 'gz',
    'dateSerializationFormat': 'ISO_FORCED_UTC',
    'escapeChar': '\\',
    'fileReadFailureBehavior': 'FAIL',
    'hiveSeparators': ['\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08'],
    'normalizeBooleans': False,
    'normalizeDoubles': True,
    'parseHeaderRow': False,
    'probableNumberOfRecords': 0,
    'quoteChar': '"',
    'readAdditionalColumnsBehavior': 'INSERT_IN_DATA_WARNING',
    'readDataTypeMismatchBehavior': 'DISCARD_WARNING',
    'readMissingColumnsBehavior': 'DISCARD_SILENT',
    'separator': '\t',
    'skipRowsAfterHeader': 0,
    'skipRowsBeforeHeader': 0,
    'style': 'excel',
    'writeDataTypeMismatchBehavior': 'DISCARD_WARNING'
}

AVRO_FILE_FORMAT_PARAMS = {
    'representsNullFields': False,
    'avroCompressionMethod': 'SNAPPY',
    'compress': ''
}

ORC_FILE_FORMAT_PARAMS = {
    'compressionMethod': 'SNAPPY',
    'serdeClass': 'org.apache.hadoop.hive.ql.io.orc.OrcSerde',
    'serdeProperties': {},
    'representsNullFields': False
}