import re
from .file_formats import (FILE_FORMATS,
                           CSV_REGULAR_FILE_FORMAT_PARAMS,
                           CSV_METASTORE_COMPATIBLE_FILE_FORMAT_PARAMS, 
                           CSV_REDSHIFT_SYNC_COMPATIBLE_FILE_FORMAT_PARAMS,
                           CSV_BIG_QUERY_SYNC_COMPATIBLE_FILE_FORMAT_PARAMS,
                           AVRO_FILE_FORMAT_PARAMS,
                           ORC_FILE_FORMAT_PARAMS
                           )
from dku_utils.projects.datasets.dataset_commons import (
    get_dataset_schema,
    get_dataset_settings_and_dictionary,
    get_dataset_in_connection_settings,
)
from dku_utils.projects.folders.folder_commons import get_managed_folder_id
from dku_utils.type_checking import DSSProject, check_object_is_project


def change_filesystem_dataset_path(project: DSSProject, dataset_name: str, path: str):
    """
    Changes the path of a filesystem project dataset

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param path: str: New dataset path.
    """
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_settings.settings["params"]["path"] = path
    dataset_settings.save()
    pass


def change_folder_path(project: DSSProject, folder_name: str, path: str):
    """
    Changes the path of a project folder.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param folder_name: str: Name of the folder.
    :param path: str: New folder path.
    """
    check_object_is_project(project)
    folder_id = get_managed_folder_id(project, folder_name)
    folder = project.get_managed_folder(folder_id)
    folder_definition = folder.get_definition()
    folder_definition["params"]["path"] = path
    folder.set_definition(folder_definition)
    pass


def change_filesystem_dataset_format(project: DSSProject, dataset_name: str, new_dataset_format: str,
                                     change_dataset_format_type: bool=False,
                                     new_dataset_format_type: str=None):
    """
    Changes the files format of a filesystem project dataset.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param new_dataset_format: str: New dataset files format.
        Note: Allowed values are defined in './file_formats.py/FILE_FORMATS'
    :param change_dataset_format_type: bool: Precises whether the dataset format type should be changed or not.
    :param new_dataset_format_type: str: Type of the file format [Only for 'csv' files]. 
        Available options are:
        - 'regular_csv': Set this value for a classic csv file.
        - 'metastore_compatible_csv': Set this value for metastore- ompatible csv file.
        - CSV's compatible with dataiku DSS fast-path:
            - 'redshift_sync_compatible_csv': Set this value for Redshift-sync compatible csv file.
            - 'big_query_sync_compatible_csv': Set this value for BigQuery-sync compatible csv file.
        
    """
    check_object_is_project(project)
    ALLOWED_FILE_FORMAT_TYPES = ["regular_csv", "metastore_compatible_csv", "redshift_sync_compatible_csv", "big_query_sync_compatible_csv"]
    if new_dataset_format not in FILE_FORMATS:
        log_message = "File format '{}' is not supported by this function, please " "choose a format in '{}'".format(
            new_dataset_format, FILE_FORMATS
        )
        raise ValueError(log_message)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    previous_format = dataset_settings.settings["formatType"]
    print(
        "Switching dataset '{}' format from '{}' to '{}' ...".format(dataset_name, previous_format, new_dataset_format)
    )
    dataset_settings.settings["formatType"] = new_dataset_format

    if change_dataset_format_type:
        if new_dataset_format_type is not None:
            if new_dataset_format_type not in ALLOWED_FILE_FORMAT_TYPES:
                log_message = f"File format of type '{new_dataset_format_type}' is not supported by this function, "\
                    "please choose a format in '{ALLOWED_FILE_FORMAT_TYPES}'"
                raise ValueError(log_message)

        if new_dataset_format == "csv":
            if ((new_dataset_format_type is None) or (new_dataset_format_type == "regular_csv")):
                new_file_format_params = CSV_REGULAR_FILE_FORMAT_PARAMS
            elif (new_dataset_format_type == "metastore_compatible_csv"):
                new_file_format_params = CSV_METASTORE_COMPATIBLE_FILE_FORMAT_PARAMS
            elif (new_dataset_format_type == "redshift_sync_compatible_csv"):
                new_file_format_params = CSV_REDSHIFT_SYNC_COMPATIBLE_FILE_FORMAT_PARAMS
            elif (new_dataset_format_type == "big_query_sync_compatible_csv"):
                new_file_format_params = CSV_BIG_QUERY_SYNC_COMPATIBLE_FILE_FORMAT_PARAMS
        
        elif new_dataset_format == "avro":
            new_file_format_params = AVRO_FILE_FORMAT_PARAMS
        
        elif new_dataset_format == "orcfile":
            new_file_format_params = ORC_FILE_FORMAT_PARAMS
        
        dataset_settings.settings["formatParams"] = new_file_format_params
    dataset_settings.save()
    print("Dataset format '{}' switched".format(dataset_name))
    pass


def change_filesystem_dataset_write_bucketing(project: DSSProject,
                                              dataset_name: str,
                                              new_write_bucketing: int=1):
    """
    Changes the 'Write bucketing' settings of a dataset.

    Explanation: When a dataset is written by DSS from a "single-stream" source (like a SQL database), 
        DSS can automatically "redispatch" the rows accross several files to give an opportunity 
        to downstream recipes to better parallelize. 
        Entering more than 1 here will enable this feature and create multiple output files.
        
        Multiple output files may still be created when running a recipe with input datasets 
        that contain multiple files.
        Incompatible with preserving ordering or forcing single output file.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param new_write_bucketing_size: int: New size of the write bucketing.
    """
    check_object_is_project(project)
    if isinstance(new_write_bucketing, int):
        if new_write_bucketing < 1:
            log_message = f"The parameter 'new_write_bucketing' must be above '1'! "\
            f"Current value is '{new_write_bucketing}': please increase it."
            raise Exception(log_message)
    else:
        log_message = f"The parameter 'new_write_bucketing' should have the datatype 'int' while "\
        f" the current datatype is '{type(new_write_bucketing)}'. Please set an appropriate value."
        raise Exception(log_message)
        
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    previous_write_bucketing = dataset_settings.settings["readWriteOptions"]["writeBuckets"]
    print(f"Switching dataset '{dataset_name}' write bucketing from '{previous_write_bucketing}' "\
          f"to '{new_write_bucketing}' ...")
    
    dataset_order_is_preserved = dataset_settings.settings["readWriteOptions"]["preserveOrder"]
    if dataset_order_is_preserved:
        print("Changing the dataset's write bucketing is not compatible with preserving it's order. "\
              "The 'Preserve ordering' parameter will then be disabled.")
        dataset_settings.settings["readWriteOptions"]["preserveOrder"] = False
        print(f"'Preserve ordering' disabled on dataset '{dataset_name}'!")
    
    dataset_settings.settings["readWriteOptions"]["writeBuckets"] = new_write_bucketing
    dataset_settings.save()
    print(f"'Write bucketing' successfully editied on dataset '{dataset_name}'!")
    pass


def switch_not_managed_dataset_connection_to_cloud_storage(
    project: DSSProject, dataset_name: str, connection_name: str, dataset_path_in_connection: str
):
    """
    Changes the connection of a NOT managed DSS dataset toward a clould storage connection.
    Connection must have a type in ['Azure', 'GCS', 'S3'].

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param connection_name: str: Name of the cloud storage connection.
    :param dataset_path_in_connection: str: Dataset path in the cloud storage connection.
    """
    ALLOWED_CLOUD_STORAGES = ["Azure", "GCS", "S3"]
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_is_managed = dataset_settings.settings["managed"]

    if dataset_is_managed:
        log_message = (
            "Dataset '{}' is a DSS managed dataset.\n"
            "You can't use this function to change its connection".format(dataset_name)
        )
        raise Exception(log_message)

    dataset_connection_settings = get_dataset_in_connection_settings(project, connection_name)
    dataset_connection_settings["managed"] = False
    connection_type = dataset_connection_settings["type"]

    if connection_type not in ALLOWED_CLOUD_STORAGES:
        log_message = (
            "Connection '{}' is of type '{}' that is not allowed by this function.\n"
            "Allowed connection types are '{}'".format(connection_name, connection_type, ALLOWED_CLOUD_STORAGES)
        )
        raise ValueError(log_message)

    dataset_connection_settings["params"]["path"] = dataset_path_in_connection
    dataset_connection_settings["name"] = dataset_name
    metastore_synchronization_enabled = dataset_connection_settings["params"]["metastoreSynchronizationEnabled"]
    if metastore_synchronization_enabled:
        dataset_connection_settings["params"]["metastoreTableName"] = dataset_name
    else:
        dataset_connection_settings["params"]["metastoreTableName"] = ""

    dataset_settings.settings = dataset_connection_settings
    dataset_settings.save()
    pass


def switch_managed_dataset_connection_to_cloud_storage(project: DSSProject, dataset_name: str, connection_name: str):
    """
    Changes the connection of a managed DSS dataset toward a clould storage connection.
    Connection must have a type in ['Azure', 'GCS', 'S3'].

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param connection_name: str: Name of the cloud storage connection.
    """
    ALLOWED_CLOUD_STORAGES = ["Azure", "GCS", "S3"]
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_is_managed = dataset_settings.settings["managed"]

    if not dataset_is_managed:
        log_message = (
            "Dataset '{}' is not a DSS managed dataset.\n"
            "You can't use this function to change its connection".format(dataset_name)
        )
        raise Exception(log_message)

    dataset_connection_settings = get_dataset_in_connection_settings(project, connection_name)
    connection_type = dataset_connection_settings["type"]

    if connection_type not in ALLOWED_CLOUD_STORAGES:
        log_message = (
            "Connection '{}' is of type '{}' that is not allowed by this function.\n"
            "Allowed connection types are '{}'".format(connection_name, connection_type, ALLOWED_CLOUD_STORAGES)
        )
        raise ValueError(log_message)

    connection_path = dataset_connection_settings["params"]["path"]
    connection_path = re.sub("dataset_for_connection_settings_extraction", "", connection_path)
    new_connection_path = "{}{}".format(connection_path, dataset_name)
    dataset_connection_settings["params"]["path"] = new_connection_path

    dataset_connection_settings["name"] = dataset_name
    metastore_synchronization_enabled = dataset_connection_settings["params"]["metastoreSynchronizationEnabled"]
    if metastore_synchronization_enabled:
        dataset_connection_settings["params"]["metastoreTableName"] = dataset_name
    else:
        dataset_connection_settings["params"]["metastoreTableName"] = ""

    dataset_connection_settings["schema"]["columns"] = get_dataset_schema(project, dataset_name)
    dataset_connection_settings["metrics"] = dataset_settings.settings["metrics"]
    dataset_settings.settings = dataset_connection_settings
    dataset_settings.save()
    pass


def switch_managed_dataset_connection_to_local_filesytem_storage(project: DSSProject, dataset_name: str, local_filesystem_connection_name: str):
    """
    Changes the connection of a managed DSS dataset toward a a local filesystem storage.
    Connection must have a type equals to "Filesystem".

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param local_filesystem_connection_name: str: Name of the local filesystem connection.
    """
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_is_managed = dataset_settings.settings["managed"]

    if not dataset_is_managed:
        log_message = (
            "Dataset '{}' is not a DSS managed dataset.\n"
            "You can't use this function to change its connection".format(dataset_name)
        )
        raise Exception(log_message)

    dataset_connection_settings = get_dataset_in_connection_settings(project, local_filesystem_connection_name)
    connection_type = dataset_connection_settings["type"]

    if connection_type != "Filesystem":
        log_message = ("Connection '{}' is of type '{}' that is not allowed by this function.\n"
        "Only allowed connection types is 'Filesystem'".format(local_filesystem_connection_name, connection_type)
        )
        raise ValueError(log_message)

    connection_path = dataset_connection_settings["params"]["path"]
    connection_path = re.sub("dataset_for_connection_settings_extraction", "", connection_path)
    new_connection_path = "{}{}".format(connection_path, dataset_name)
    dataset_connection_settings["params"]["path"] = new_connection_path
    dataset_connection_settings["name"] = dataset_name
    dataset_connection_settings["schema"]["columns"] = get_dataset_schema(project, dataset_name)
    dataset_connection_settings["metrics"] = dataset_settings.settings["metrics"]
    dataset_settings.settings = dataset_connection_settings
    dataset_settings.save()
    pass


def switch_managed_folder_connection(project: DSSProject, folder_name: str, connection_name: str):
    """
    Changes the connection of a managed DSS folder toward a clould storage connection.
    Connection must have a type in ['S3', 'Azure', 'GCS', 'Filesystem'].

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param folder_name: str: Name of the folder.
    :param connection_name: str: Name of the cloud storage connection.
    """
    check_object_is_project(project)
    ALLOWED_CLOUD_STORAGES = ["S3", "Azure", "GCS"]
    ALLOWED_STORAGES = ALLOWED_CLOUD_STORAGES + ["Filesystem"]
    
    folder_id = get_managed_folder_id(project, folder_name)
    folder = project.get_managed_folder(folder_id)
    folder_definition = folder.get_definition()

    dataset_connection_settings = get_dataset_in_connection_settings(project, connection_name)
    connection_type = dataset_connection_settings["type"]

    if connection_type not in ALLOWED_STORAGES:
        log_message = (
            "Connection '{}' is of type '{}' that is not allowed by this function.\n"
            "Allowed connection types are '{}'".format(connection_name, connection_type, ALLOWED_STORAGES)
        )
        raise ValueError(log_message)

    folder_definition["type"] = connection_type
    connection_path = dataset_connection_settings["params"]["path"]
    connection_path = re.sub("dataset_for_connection_settings_extraction", "", connection_path)
    new_connection_path = "{}{}".format(connection_path, "${odbId}")
    folder_definition["params"]["path"] = new_connection_path
    folder_definition["params"]["connection"] = connection_name
    
    if connection_type in ALLOWED_CLOUD_STORAGES:
        metastore_synchronization_enabled = dataset_connection_settings["params"]["metastoreSynchronizationEnabled"]
        if metastore_synchronization_enabled:
            folder_definition["params"]["metastoreTableName"] = "${odbId}"
        else:
            folder_definition["params"]["metastoreTableName"] = ""

    folder.set_definition(folder_definition)
    pass