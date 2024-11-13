import dataiku
import dataikuapi
import pandas as pd
from dku_utils.type_checking import DSSProject, check_object_is_project


def get_dataset_settings_and_dictionary(project: DSSProject, dataset_name: str, bool_get_settings_dictionary: bool=True):
    """
    Retrieves the settings of a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param bool_get_settings_dictionary: bool: Precise if you to rerieve the dataset settings dictionary.
    
    :returns: 
        - dataset_settings: dataikuapi.dss.dataset.[DatasetType]DatasetSettings: Settings for a dataset. 
        - dataset_settings_dict: dict: Dictionary containing dataset settings.
    """
    check_object_is_project(project)
    dataset_settings = project.get_dataset(dataset_name).get_settings()
    if bool_get_settings_dictionary:
        dataset_settings_dict = dataset_settings.settings
    else:
        dataset_settings_dict = None
    return dataset_settings, dataset_settings_dict
   
    
def get_dataset_schema(project: DSSProject, dataset_name: str):
    """
    Retrieves a project dataset schema. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.

    :returns: dataset_schema: list: The schema of the dataset, with format: 
        [{'name': 'column_1', 'type': 'column_1_datatype'}, 
        {'name': 'column_2', 'type': 'column_2_datatype'}| 
    """
    check_object_is_project(project)
    dataset_schema = project.get_dataset(dataset_name).get_settings().settings["schema"]["columns"]
    return dataset_schema


def set_dataset_schema(project: DSSProject, dataset_name: str, new_dataset_schema: list):
    """
    Updates a dataset's schema.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param new_dataset_schema: list: The new schema the dataset must have, with format: 
        [{'name': 'column_1', 'type': 'column_1_datatype'}, 
        {'name': 'column_2', 'type': 'column_2_datatype'}| 
    """
    check_object_is_project(project)
    dataset_settings, dataset_settings_dict = get_dataset_settings_and_dictionary(project, dataset_name, True)
    dataset_settings_dict["schema"]["columns"] = new_dataset_schema
    dataset_settings.settings = dataset_settings_dict
    dataset_settings.save()
    pass


def extract_dataset_schema_information(dataset_schema: list):
    """
    Extracts all schema information as lists from a 'dataset_schema'.
    
    :param dataset_schema: list: Schema of the dataset, with format: 
            [{'name': 'column_1', 'type': 'column_1_datatype'}, 
             {'name': 'column_2', 'type': 'column_2_datatype'}| 
        'dataset_schema' can be get as the output of :function:`get_dataset_schema`
        
    :returns: dataset_columns: list: List of all dataset column names.
    :returns: dataset_datatypes: list: List of all dataset column datatypes.
    """
    dataset_columns = [parameter["name"] for parameter in dataset_schema]
    dataset_column_datatypes = [parameter["type"] for parameter in dataset_schema]
    return dataset_columns, dataset_column_datatypes


def get_dataset_schema_information(project: DSSProject, dataset_name: str):
    """
    Retrieves both the list of 'columns names' and 'column datatypes' from a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    
    :returns: dataset_columns: list: List of all dataset column names.
    :returns: dataset_datatypes: list: List of all dataset column datatypes.
    """
    check_object_is_project(project)
    dataset_schema = get_dataset_schema(project, dataset_name)
    dataset_columns, dataset_column_datatypes = extract_dataset_schema_information(dataset_schema)
    return dataset_columns, dataset_column_datatypes


def get_dataset_column_datatypes_mapping(project: DSSProject, dataset_name: str):
    """
    Retrieves the information of the mapping between a project dataset columns and their datatype.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    
    :returns: column_datatypes_mapping: dict: Dictionary containing the mapping between the dataset columns and
        their datatype.
    """
    check_object_is_project(project)
    column_datatypes_mapping = {}
    dataset_schema = get_dataset_schema(project, dataset_name)
    for schema_information in dataset_schema:
        column_datatypes_mapping[schema_information["name"]] = schema_information["type"]
    return column_datatypes_mapping


def copy_dataset_schema(dataset_to_copy_project_key: str, dataset_to_copy_name: str, dataset_project_key: str, dataset_name: str):
    """
    Copies the schema from a dataset into another dataset 
    
    :param dataset_to_copy_project_key: str: Project key of the dataset we want to copy the schema from.
    :param dataset_to_copy_name: str: Name of the dataset we want to copy the schema from.
    :param dataset_project_key: str: Project key of the dataset where the schema should be copied.
    :param dataset_name: str: Name of the dataset where the schema should be copied.
    """
    dataset_to_copy_project = dataiku.api_client().get_project(dataset_to_copy_project_key)
    dataset_project = dataiku.api_client().get_project(dataset_project_key)
    dataset_to_copy_schema = get_dataset_schema(dataset_to_copy_project, dataset_to_copy_name)
    dataset_settings, dataset_settings_dict = get_dataset_settings_and_dictionary(dataset_project, dataset_name, True)
    dataset_settings_dict["schema"]["columns"] = dataset_to_copy_schema
    dataset_settings.settings = dataset_settings_dict
    dataset_settings.save()
    pass


def change_dataset_column_datatype(project: DSSProject, dataset_name: str, column_name: str, new_datatype: str, new_meaning: str=""):
    """
    Updates the datatype of one project dataset column, it its settings.
   
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset. 
    :param new_datatype: str: The new datatype for the column.
    :param new_meaning: str, optional: The new meaning for the column.
        Note: Available storages and meaning datatypes are listed in dku_utils/datasets/datatypes
    """
    check_object_is_project(project)
    print("Updating column {} datatype (from dataset {}) to '{}' ...".format(column_name, dataset_name, new_datatype))
    dataset_schema = get_dataset_schema(project, dataset_name)
    dataset_settings, dataset_settings_dict = get_dataset_settings_and_dictionary(project, dataset_name, True)
    new_dataset_schema = []

    for entity in dataset_schema:
        if entity['name']==column_name:
            entity['type']=new_datatype
            if new_meaning:
                entity['meaning'] = new_meaning
        new_dataset_schema.append(entity)
        
    dataset_settings_dict['schema']['columns'] = new_dataset_schema
    dataset_settings.settings = dataset_settings_dict
    dataset_settings.save()
    print("Column {} datataype (from dataset {}) successfully updated !".format(column_name, dataset_name))
    pass


def get_dataset_column_datatype(project: DSSProject, dataset_name: str, column_name: str):
    """
    Retrieves the datatype of one project dataset column.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    
    :returns: column_datatype: str: Resquested dataset column datatype.
    """
    check_object_is_project(project)
    dataset_schema = get_dataset_schema(project, dataset_name)
    dataset_columns, dataset_column_datatypes = extract_dataset_schema_information(dataset_schema)
    
    try:
        column_index = dataset_columns.index(column_name)
        column_datatype = dataset_column_datatypes[column_index]
        return column_datatype
    except ValueError:
        log_message = "Column '{}' does not exist in dataset '{}' !"\
            "\nExisting columns are '{}'"\
            .format(column_name, dataset_name, dataset_columns)
        raise ValueError(log_message)
        pass
    pass
    

def clear_dataset(project: DSSProject, dataset_name: str):
    """
    Clears a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    """
    check_object_is_project(project)
    print("Clearing dataset {}.{}".format(project.project_key, dataset_name))
    project.get_dataset(dataset_name).clear()
    pass


def get_last_dataset_metrics_information(project: DSSProject, dataset_name: str):
    """
    Retrieves all the last metrics information of a project dataset. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.

    :returns: last_metrics_information_df: pandas.core.frame.DataFrame: DataFrame containing all last dataset metrics information.
    """
    check_object_is_project(project)
    dataset = project.get_dataset(dataset_name)
    dataset_metrics = dataset.get_last_metric_values()
    dataset_metrics_ids = dataset_metrics.get_all_ids()
    metrics_information = []
    metric_ids_splitted = []
    for metric_id in dataset_metrics_ids:
        try:
            metric_information = dataset_metrics.get_global_data(metric_id)
            metrics_information.append(metric_information)
            metric_id = str(metric_id)
            metric_id_splitted = metric_id.split(":")
            metric_ids_splitted.append(metric_id_splitted)
        except:
            pass
    last_metrics_information_df = pd.DataFrame(metric_ids_splitted, columns=["metric_category", "metric_name", "metric_column_or_scope"])
    last_metrics_information_df["metric_information"] = metrics_information
    return last_metrics_information_df


def get_dataset_last_metric_value(project: DSSProject, dataset_name: str, metric_name: str, metric_column_name: str=""):
    """
    Retrieves the last value from a project dataset metric. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param metric_name: str: Name of the metric to retrieve.
    :param metric_column_name: str: Name of the column on which the metric has been computed.

    :returns: last_metric_value: str: Last value of the dataset metric.
    """
    check_object_is_project(project)
    last_metrics_df = get_last_dataset_metrics_information(project, dataset_name)
    last_metrics_df = last_metrics_df[last_metrics_df["metric_name"] == metric_name]
    if metric_column_name:
        last_metrics_df = last_metrics_df[last_metrics_df["metric_column_or_scope"] == metric_column_name]
    last_metric_value = list(last_metrics_df["metric_information"])[0]["value"]
    return last_metric_value


def get_dataset_connection_type(project: DSSProject, dataset_name: str):
    """
    Retrieves the connection type of a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    
    :returns: dataset_connection_type: str: Dataset's connection type.
    """
    check_object_is_project(project)
    __, dataset_settings_dict = get_dataset_settings_and_dictionary(project, dataset_name, True)
    dataset_connection_type = dataset_settings_dict["type"]
    return dataset_connection_type


def get_dataset_connection_name(project: DSSProject, dataset_name: str):
    """
    Retrieves the connection name of a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    
    :returns: dataset_connection_name: str: Dataset's connection name.
    """
    check_object_is_project(project)
    __, dataset_settings_dict = get_dataset_settings_and_dictionary(project, dataset_name, True)
    dataset_connection_name = dataset_settings_dict["params"]["connection"]
    return dataset_connection_name


def create_dataset_in_connection(project: DSSProject, dataset_name: str, connection_name: str):
    """
    Creates a dataset in a given connection.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param connection_name: str: Name of the connection.
    """
    check_object_is_project(project)
    builder = dataikuapi.CodeRecipeCreator("TMP_RECIPE", "python", project)
    builder = builder.with_new_output_dataset(dataset_name, connection_name)
    print("Dataset '{}' has been successfully created in connection '{}'.".format(dataset_name, connection_name))
    pass


def get_dataset_in_connection_settings(project: DSSProject, connection_name: str):
    """
    Retrieves the connection settings of a project dataset in connection 'connection_name'.
    This process is done by:
        - Creating a temporary python recipe in the flow.
            - It has no input.
            - Output is a temporary dataset in connection 'connection_name'.
        - Looking at the settings of the temporary dataset outputed by the recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param connection_name: str: Name of the connection.
    
    :returns: dataset_in_connection_settings: dict: Settings of a project dataset in connection 'connection_name'.
    """
    TMP_DATASET_NAME = "dataset_for_connection_settings_extraction"
    TMP_RECIPE_NAME = "compute_{}".format(TMP_DATASET_NAME)
    check_object_is_project(project)
    print("Creating temporary dataset and with 'dataikuapi' recipes builder...")
    builder = dataikuapi.CodeRecipeCreator(TMP_RECIPE_NAME, "python", project)
    builder = builder.with_new_output_dataset(TMP_DATASET_NAME, connection_name)
    #tmp_recipe = builder.build() #fails without "DATA_SCIENTIST" profile
    print("Temporary dataset ! \nExtracting connection settings from temporary dataset...")
    tmp_dataset = project.get_dataset(TMP_DATASET_NAME)
    dataset_in_connection_settings = tmp_dataset.get_settings().settings
    #print("Connection settings extracted from temporary dataset! \nRemoving temporary dataset and recipe...") #fails without "DATA_SCIENTIST" profile
    #tmp_recipe.delete() #fails without "DATA_SCIENTIST" profile
    tmp_dataset.delete()
    print("Temporary dataset removed!")
    return dataset_in_connection_settings

 
def infer_and_update_dataset_schema(project: DSSProject, dataset_name: str, connection_name: str):
    """
    Infer and updates a project dataset's schema. 
    This process is done by:
        - Creating a temporary prepare recipe in the flow.
            - Input is 'dataset_name'
            - Output is a temporary dataset.
        - Looking at the schema of the temporary dataset outputed by the recipe. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param connection_name: str: Name of the connection.
    """
    TMP_DATASET_NAME = "{}_for_schema_inference".format(dataset_name)
    TMP_RECIPE_NAME = "compute_{}".format(TMP_DATASET_NAME)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    check_object_is_project(project)
    print("Creating temporary prepare recipe '{}' and dataset '{}'"\
          " for infering dataset '{}' schema ...".format(TMP_RECIPE_NAME, TMP_DATASET_NAME, dataset_name))
    tmp_dataset = project.get_dataset(TMP_DATASET_NAME)
    tmp_recipe = dataikuapi.dss.recipe.SingleOutputRecipeCreator('shaker', TMP_RECIPE_NAME, project)
    tmp_recipe.with_input(dataset_name)
    tmp_recipe.with_new_output(TMP_DATASET_NAME, connection_name)
    tmp_recipe.build()
    tmp_dataset_infered_schema = get_dataset_schema(project, TMP_DATASET_NAME)
    dataset_settings.settings["schema"]["columns"] = tmp_dataset_infered_schema
    dataset_settings.save()
    print("Dataset '{}' schema successfully inferred!".format(dataset_name))
    print("Removing temporary prepare recipe '{}' and dataset '{}'...".format(TMP_RECIPE_NAME, TMP_DATASET_NAME))
    project.get_recipe(TMP_RECIPE_NAME).delete()
    tmp_dataset.delete()
    print("Temporary prepare recipe '{}' and dataset '{}' removed!".format(TMP_RECIPE_NAME, TMP_DATASET_NAME))
    pass


def update_dataset_varchar_limit(project: DSSProject, dataset_name: str, new_varchar_limit: int):
    """
    Updates a project dataset varchar limit to avoid connection issues while writing data.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param new_varchar_limit: int: New dataset varchar limit.
    """
    check_object_is_project(project)
    new_dataset_schema_information = []
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_schema_information = dataset_settings.settings["schema"]["columns"]
    for schema_information in dataset_schema_information:
        column_datatype = schema_information["type"]
        if column_datatype == "string":
            schema_information["maxLength"] = new_varchar_limit
        new_dataset_schema_information.append(schema_information)
    dataset_settings.settings["schema"]["columns"] = new_dataset_schema_information
    dataset_settings.save()
    pass


def get_dataset_managed_state(project: DSSProject, dataset_name: str):
    """
    Retrieves the information of a dataset 'managed state', between 'managed' or 'not_managed'.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    
    :returns: dataset_managed_state: str: String informing about the dataset 'managed state'.
    """
    check_object_is_project(project)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    if dataset_settings.settings["managed"]:
        dataset_managed_state = "managed"
    else:
        dataset_managed_state = "not_managed"
    return dataset_managed_state


def change_dataset_managed_state(project: DSSProject, dataset_name: str, bool_should_be_managed_state: bool):
    """
    Changes the state a project dataset so that it becomes a 'managed' or a 'not managed' one.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param bool_should_be_managed_state: bool: Precise if you want the dataset to be managed.
    """
    check_object_is_project(project)
    dataset_connection_type = get_dataset_connection_type(project, dataset_name)
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_settings.settings["managed"] = bool_should_be_managed_state
    if bool_should_be_managed_state:
        if dataset_connection_type == "Redshift":
            dataset_settings.settings["params"]["distributionStyle"] = "AUTO" #["AUTO", "EVEN", "ALL"]
            dataset_settings.settings["params"]["sortKey"] = "NONE" #["NONE", "COMPOUND", "INTERLEAVED"]
            dataset_settings.settings["params"]["sortKeyColumns"] = [] #Should be a list of dataset columns if 'sortKey' != None
            
    dataset_settings.save()
    pass


def disable_dataset_metastore_synchronization(project: DSSProject, dataset_name: str):
    """
    Disables the metastore synchronization of a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    """
    check_object_is_project(project)
    dataset_settings, dataset_settings_dict = get_dataset_settings_and_dictionary(project, dataset_name, True)
    dataset_params = dataset_settings_dict["params"]
    if "metastoreSynchronizationEnabled" in dataset_params.keys():
        print("Disabling dataset '{}' metastore synchronization...".format(dataset_name))
        dataset_params["metastoreSynchronizationEnabled"] = False
        dataset_settings_dict["params"] = dataset_params
        print("Dataset '{}' metastore synchronization disabled! Saving settings...".format(dataset_name))

    dataset_settings.settings = dataset_settings_dict
    dataset_settings.save()
    print("Dataset '{}' settings successfully saved! Metastore synchronization have been disabled!".format(dataset_name))
    pass


def get_dataset_description(project: DSSProject, dataset_name: str, description_type: str="short_description"):
    """
    Retrieves the description of a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param description_type: str: The type of description to modify.
        The available options are:
            - 'short_description': To enrich the dataset short description.
            - 'long_description': To enrich the dataset long description.
    :returns: dataset_description: str: Description of the project dataset.
    """
    check_object_is_project(project)
    dataset_settings, _ = get_dataset_settings_and_dictionary(project, dataset_name)
    if description_type == "short_description":
        dataset_description = dataset_settings.short_description 
    else:
        dataset_description = dataset_settings.description
    if dataset_description is None:
        dataset_description = ""
    return dataset_description


def modify_dataset_description(project: DSSProject, dataset_name: str, description_modification: str,
                               description_type: str="short_description", type_of_modification: str="replace_all",
                               descriptions_separator: str="\n\n"):
    """
    Modifies the description of a project dataset.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param description_modification: str: The description to modify the dataset with.
    :param description_type: str: The type of description to modify.
        The available options are:
            - 'short_description': To enrich the dataset short description.
            - 'long_description': To enrich the dataset long description.
    :param type_of_modification: str: The type of description modification to apply.
        The available options are:
            - 'replace_all': If you want to replace the existing description.
            - 'add_before': If you want to add your description before the existing description.
            - 'add_after': If you want to add your description after the existing description.
    :param descriptions_separator: str: The separator to use between each description.
        This only applies when 'type_of_modification' equals to 'add_before' or 'add_after'.
    """
    check_object_is_project(project)
    dataset_settings, _ = get_dataset_settings_and_dictionary(project, dataset_name)
    existing_description = get_dataset_description(project, dataset_name, description_type)
    if not existing_description:
        existing_description = ""
        
    if type_of_modification == "replace_all":
        new_description = description_modification
    
    elif type_of_modification == "add_before":
        new_description = f"{description_modification}{descriptions_separator}{existing_description}"
    
    elif type_of_modification == "add_after":
        new_description = f"{existing_description}{descriptions_separator}{description_modification}"
        
    
    if description_type == "short_description":
        dataset_settings.short_description = new_description
    else:
        dataset_settings.description = new_description
    dataset_settings.save()