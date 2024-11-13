DATASET_TYPES = {
    "upload_your_files": [
        "UploadedFiles"
        ],
    "filesystem": [
        "Filesystem"
    ],
    "network": [
        "FTP",
        "SFTP",
        "SCP",
        "HTTP"
    ],
    "hdfs": [
        "HDFS"
    ],
    "sql_databases": [
        "Snowflake", # Snowflake
        "Redshift", # Amazon Redshift
        "Synapse", # Azure Synapse
        "BigQuery", # Google BigQuery
        "PostgreSQL", # PostgreSQL
        "MySQL", # MySQL
        "SQLServer", # MS SQL Server
        "Oracle", # Oracle
        "Teradata", # Teradata
        "Greenplum", # Greenplum
        "AlloyDB", # Google AlloyDB
        "Athena", # Athena
        "Vertica", # Vertica
        "SAPHANA", # SAP HANA
        "Netezza", # IBM Netezza
        "Databricks", # Databricks
        "JDBC" # Other SQL Databases
    ],
    "cloud_storages_&_social": [
        "S3", # Amazon S3
        "Azure", # Azure Blob Storage
        "GCS", # Google Cloud Storage
        "Twitter" # Twitter
    ],
    "no_sql": [
        "MongoDB", # MongoDB
        "Cassandra", # Cassandra
        "ElasticSearch", # ElasticSearch
    ],
    "folder": [
        "FilesInFolder"
    ],
    "editable": [
        "Inline"
        ],
    "internal": [
        "JobsDB", # Metrics
        "StatsDB", # Internal stats
        "ExperimentsDB", # Experiments
    ]
}