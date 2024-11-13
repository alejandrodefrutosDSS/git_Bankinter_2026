import pandas as pd 
from dku_utils.type_checking import DSSProject, check_object_is_project


def get_deployed_model_metadata(project: DSSProject, deployed_model_name: str):
    """
    Retrieves the information associated with a project deployed model. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param deployed_model: str: Name of the project deployed model.

    :returns: deployed_model_metadata: dict: The associated with 'flow_zone_name'.
    """
    check_object_is_project(project)
    all_deployed_models_information = project.list_saved_models()
    deployed_model_metadata = None
    for deployed_model_information in all_deployed_models_information:
        if deployed_model_information['name'] == deployed_model_name:
            deployed_model_metadata = deployed_model_information
            pass
        pass
    if deployed_model_metadata == None:
        log_message = "Deployed model '{}' does not exist! "\
            "Please use the computed 'all_deployed_models_information' to use a valid model name."\
            "all_deployed_models_information = '{}'".format(deployed_model_name, all_deployed_models_information)
        raise ValueError(log_message)
    return deployed_model_metadata
    

def get_deployed_model_id(project: DSSProject, deployed_model_name: str):
    """
    Retrieves the ID of a project deployed model. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param deployed_model_name: str: Name of the project deployed model.

    :returns: deployed_model_id: str: The ID associated with 'deployed_model_name'.
    """
    check_object_is_project(project)
    deployed_model_metadata = get_deployed_model_metadata(project, deployed_model_name)
    deployed_model_id = deployed_model_metadata["id"]
    return deployed_model_id


def get_deployed_model(project: DSSProject, deployed_model_name: str):
    """
    Retrieves a Dataiku deployed model object to interact with.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param deployed_model_name: str: Name of the project deployed model.
    
    :returns: deployed_model: dataikuapi.dss.savedmodel.DSSSavedModel: 
    """
    check_object_is_project(project)
    deployed_model_id = get_deployed_model_id(project, deployed_model_name)
    deployed_model = project.get_saved_model(deployed_model_id) 
    return deployed_model


def get_deployed_model_versions_dataframe(project: DSSProject, deployed_model_name: str):
    """
    Retrieves a dataframe containing information about the model versions associated with a deployed model.
        
    :param: project: DSSProject: A handle to interact with a project on the DSS instance..
    :param: deployed_model_name: str: Name of the project deployed model.
    
    :returns: deployed_model_versions_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing deployed model versions informations.
        deployed_model_versions_dataframe values are sorted from the most recent (first rows) to oldest (last rows) dates.
    """
    check_object_is_project(project)
    deployed_model = get_deployed_model(project, deployed_model_name)
    deployed_model_versions_dataframe = pd.DataFrame(deployed_model.list_versions())
    if not deployed_model_versions_dataframe.empty:
        deployed_model_versions_dataframe =\
        deployed_model_versions_dataframe.sort_values(by="trainDate", ascending=False).reset_index(drop=True)
    return deployed_model_versions_dataframe


def get_deployed_model_active_version_id(project: DSSProject, deployed_model_name: str, bool_fail_if_no_active_version: bool=False):
    """
    Retrieves the 'version_id' of a deployed model active version.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param deployed_model_name: str: Name of the project deployed model.
    :param bool_fail_if_no_active_version: bool: Precises if you want the function call to fail if no active version
        has been saved in the deployed model.
    
    :returns: deployed_model_active_version_id: str: The 'version_id' of the deployed model active version.
        If 'bool_fail_if_no_active_version' is set to 'False' and the model has no active version, 
        'deployed_model_active_version_id' value is None.
    """
    check_object_is_project(project)
    deployed_model_id = get_deployed_model_id(project, deployed_model_name)
    deployed_model_versions_dataframe = get_deployed_model_versions_dataframe(project, deployed_model_name)
    if deployed_model_versions_dataframe.empty:
        log_message = f"Model '{deployed_model_name}' (id='{deployed_model_id}') has no active versions: "\
        "please deploy a model from a ml task before using this function."
        print(log_message)
        if bool_fail_if_no_active_version:
            raise Exception(log_message)
        else:
            deployed_model_active_version_id = None
        
    else:
        deployed_model_active_version_id = \
        list(deployed_model_versions_dataframe[deployed_model_versions_dataframe["active"]==True]["id"])[0]
        
    return deployed_model_active_version_id


def get_deployed_model_input_and_rejected_features(project: DSSProject, deployed_model_name: str):
    """
    Retrieves the lists of all the features in a deployed model 'active version' that are inputs and rejected.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param deployed_model_name: str: Name of the project deployed model.
    
    :returns: deployed_model_input_features: list: List of all the features that are deployed model 'active version' inputs.
    :returns: deployed_model_rejected_features: list: List of all the features that are rejected in the deployed model 'active version' .
    """
    check_object_is_project(project)
    deployed_model_input_features = []
    deployed_model_rejected_features = []
    deployed_model = get_deployed_model(project, deployed_model_name)
    deployed_model_active_version_id = get_deployed_model_active_version_id(project, deployed_model_name)
    deployed_model_active_version_details = deployed_model.get_version_details(deployed_model_active_version_id)
    
    features_preprocessing_settings = deployed_model_active_version_details.details["preprocessing"]["per_feature"]
    feature_names = features_preprocessing_settings.keys()
    for feature_name in feature_names:
        feature_preprocessing = features_preprocessing_settings[feature_name]
        if feature_preprocessing["role"] == "INPUT":
            deployed_model_input_features.append(feature_name)
        if feature_preprocessing["role"] == "REJECT":
            deployed_model_rejected_features.append(feature_name)
    return deployed_model_input_features, deployed_model_rejected_features