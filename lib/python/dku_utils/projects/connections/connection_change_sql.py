import hashlib
import re
from dku_utils.projects.project_commons import expand_project_key
from dku_utils.projects.datasets.dataset_commons import (get_dataset_schema,
                                         get_dataset_settings_and_dictionary,
                                         get_dataset_in_connection_settings)
from dku_utils.type_checking import DSSProject, check_object_is_project


def change_sql_dataset_table(project: DSSProject, dataset_name: str, table_name: str):
    """
    Changes the table associated with a SQL project dataset.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param table_name: str: Name of the table associated with the dataset.
    """
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_settings.settings["params"]["table"] = table_name
    dataset_settings.save()
    pass


def get_sql_dataset_table(project: DSSProject, dataset_name: str, expand_the_project_key: bool=False):
    """
    Retrieves the name of a table associated with a SQL project dataset.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :returns: table_name: str: Name of the table associated with the SQL project dataset.
    """
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    table_name = dataset_settings.settings["params"]["table"]
    if expand_the_project_key:
        table_name = expand_project_key(table_name, project.project_key)
    return table_name


def switch_managed_dataset_connection_to_sql(project: DSSProject, dataset_name: str,
                                             connection_name: str,
                                             bool_use_project_key_for_table_naming: bool,
                                             table_naming_letter_case: str="dataiku_case"
                                             ):
    """
    Changes the connection of a managed DSS dataset toward a SQL connection.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param connection_name: str: Name of the SQL connection.
    :param bool_use_project_key_for_table_naming: bool: Precises if we want to use the current project key for naming the
        table associated with the dataset.
    :param table_naming_letter_case: str: Letter case used to name the table in the connection. Possible values are:
        - 'dataiku_case' [default value]: If this letter case is selected, the name of the table will be:
            --> if 'bool_use_project_key_for_table_naming' equals True: the result from the function 
                'compute_sql_table_name':
                    ---> "${project_key}_{dataset_name}" if this concatenation is not hashed, 
                        with '${project_key}' in uppercase and 'dataset_name' in the same case.
                    ---> result of 'sha256' hashing applied on "${project_key}_dataset_name" if it is hashed due to 
                        a table name too long for the used connection.
            --> else: the value of 'dataset_name', with the same case.
        - 'uppercase': If this letter case is selected, the name of the table will be in uppercase.
            In that case, the project key will be hard coded in uppercase instead of using the variable '${projectKey}'.
        - 'lowercase': If this letter case is selected, the name of the table will be in lowercase.
            In that case, the project key will be hard coded in lowercase instead of using the variable '${projectKey}'
    """
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_connection_settings = get_dataset_in_connection_settings(project, connection_name)
    connection_type = dataset_connection_settings["type"]
    if bool_use_project_key_for_table_naming:
        sql_table_name = compute_sql_table_name(project, connection_type, dataset_name)
    else:
        sql_table_name = dataset_name
    
    if table_naming_letter_case in ["uppercase", "lowercase"]:
        sql_table_name = re.sub("\${projectKey}", project.project_key, sql_table_name)
        if table_naming_letter_case == 'uppercase':
            sql_table_name = sql_table_name.upper()
        elif table_naming_letter_case == 'lowercase':
            sql_table_name = sql_table_name.lower()
    
    dataset_connection_settings["params"]["table"] = sql_table_name
    dataset_connection_settings["name"] = dataset_name
    dataset_connection_settings["schema"]["columns"] = get_dataset_schema(project, dataset_name)
    dataset_connection_settings["metrics"] = dataset_settings.settings["metrics"]
    dataset_settings.settings = dataset_connection_settings
    dataset_settings.save()
    pass


def compute_sql_table_name(project: DSSProject, connection_type: str, dataset_name: str, default_characters_limit: int=None):
    """
    Computes the name of the table associated with a project managed dataset in a SQL connection.
        Default name is the concatenation of the current 'project_key' and the 'dataset_name'. 
        When this name exceeds the database name length limits, it is hashed and then shortened.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param connection_type: str: Type of the dataset's connection.
    :param dataset_name: str: Name of the project managed dataset associated with the SQL table.
    :param default_characters_limit: int: The default characters limit to use to name tables.
        Its default value is 'None': only define it when the 'connection_type' is not part of the 
        constant 'CONNECTIONS_TABLE_NAMES_LIMIT'. 
        DISCLAIMER: Once defined, this parameter takes the priority over the 'connection_type' in the code execution. 
    """    
    CONNECTIONS_TABLE_NAMES_LIMIT = {
        "Redshift": 127,
        "BigQuery": 1024,
        "PostgreSQL": 63,
        "SQLServer": 128,
        "Snowflake": 255,
        "Databricks": 255
    }
    check_object_is_project(project)
    if default_characters_limit:
        if not isinstance(default_characters_limit, int):
            raise ValueError(f"The parameter 'default_characters_limit' must be an integer. "\
                             f"The current value is '{default_characters_limit}' of type {type(default_characters_limit)}.")
    project_key = project.project_key
    sql_table_name = "{}_{}".format("${projectKey}", dataset_name)
    sql_table_name_expanded = f"{project_key}_{dataset_name}"
    if connection_type in CONNECTIONS_TABLE_NAMES_LIMIT.keys() or default_characters_limit:
        if default_characters_limit:
            connection_table_names_limit = default_characters_limit
        else:
            connection_table_names_limit = CONNECTIONS_TABLE_NAMES_LIMIT[connection_type]
        if len(sql_table_name_expanded) > connection_table_names_limit:
            h = hashlib.new('sha256')
            h.update(dataset_name.encode('utf-8'))
            hashed_dataset_name = h.hexdigest()
            sql_table_name = f"{project_key}_{hashed_dataset_name}"
            sql_table_name = sql_table_name[0: connection_table_names_limit-1]
            sql_table_name = re.sub(f"^{project_key}", "${projectKey}", sql_table_name)
    else:
        log_message = "connection_type '{}' is not usable in this function ."\
            "Allowed connection types are: {}. You can bypass them by passing an integer "\
            "value to the parameter 'default_characters_limit'.".format(connection_type, list(CONNECTIONS_TABLE_NAMES_LIMIT.keys()))
        raise ValueError(log_message)
    return sql_table_name


def autodetect_sql_dataset_schema(project: DSSProject, dataset_name: str):
    """
    Detects the schema of a project SQL dataset.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the project dataset to detect the schema from.
    """
    check_object_is_project(project)
    print("Trying to detect dataset '{}' schema ...".format(dataset_name))
    dataset = project.get_dataset(dataset_name)
    dataset_settings = dataset.get_settings()
    
    dataset_detected_settings = dataset.test_and_detect()
    dataset_detected_schema = dataset_detected_settings["schemaDetection"]["detectedSchema"]["columns"]
    dataset_settings.get_raw()["schema"]["columns"] = dataset_detected_schema
    dataset_settings.save()
    print("Dataset '{}' schema detected and replaced !".format(dataset_name))
    pass