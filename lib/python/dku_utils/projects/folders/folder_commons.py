from dku_utils.type_checking import DSSProject, check_object_is_project


def get_managed_folder_settings_and_dictionary(project: DSSProject, managed_folder_id: str, bool_get_settings_dictionary: bool=True):
    """Retrieves the settings of a project folder.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    :param bool_get_settings_dictionary: bool: Precise if you to rerieve the folder settings dictionary.
    
    :returns: 
        - folder_settings: dataikuapi.dss.managedfolder.DSSManagedFolderSettings: Settings for a managed folder. 
        - folder_settings_dict: dict: Dictionary containing managed folder settings.
    """
    check_object_is_project(project)
    managed_folder_settings = project.get_managed_folder(managed_folder_id).get_settings()
    if bool_get_settings_dictionary:
        managed_folder_settings_dict = managed_folder_settings.settings
    else:
        managed_folder_settings_dict = None
    return managed_folder_settings, managed_folder_settings_dict


def get_managed_folder_metadata(project: DSSProject, managed_folder_name: str):
    """
    Retrieves the information associated with a project folder. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_name: str: Name of the project managed folder.

    :returns: managed_folder_metadata: dict: The associated with 'managed_folder_name'.
    """
    check_object_is_project(project)
    all_managed_folders_information = project.list_managed_folders()
    managed_folder_metadata = None
    for managed_folder_information in all_managed_folders_information:
        if managed_folder_information['name'] == managed_folder_name:
            managed_folder_metadata = managed_folder_information
            pass
        pass
    if managed_folder_metadata is None:
        log_message = "The managed folder named '{}' does not exist! "\
            "Please use the computed 'all_managed_folders_information' to use a valid folder name."\
            "all_managed_folders_information = '{}'".format(managed_folder_name, all_managed_folders_information)
        raise ValueError(log_message)
    return managed_folder_metadata


def get_managed_folder_id(project: DSSProject, managed_folder_name: str, fail_if_several_matching: bool=False, fail_if_not_exists: bool=True):
    """
    Retrieves the ID of a project managed folder, given its name. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_name: str: Name of the project managed folder.
    :param fail_if_several_matching: bool: Precises if the function should fail if several folders 
        have the name 'managed_folder_name'.
    :param fail_if_not_exists: bool: Precises if the function should fail if the folder
        is not found

    :returns: managed_folder_id: str: The ID associated with 'managed_folder_name'.
    """
    check_object_is_project(project)
    managed_folder_name_exists = check_if_managed_folder_name_exists(project, managed_folder_name, fail_if_not_exists=fail_if_not_exists,
                                                                     fail_if_several_matching=fail_if_several_matching)
    if managed_folder_name_exists:
        managed_folder_metadata = get_managed_folder_metadata(project, managed_folder_name)
        managed_folder_id = managed_folder_metadata["id"]
    else:
        managed_folder_id = ""
        if fail_if_not_exists:
            log_message = f"The folder named '{managed_folder_name}' does not exist!"
            raise Exception(log_message)
    return managed_folder_id


def get_managed_folder_name(project: DSSProject, managed_folder_id: str, fail_if_not_exists: bool=True):
    """
    Retrieves the name of a project managed folder, given its ID. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    :param fail_if_not_exists: bool: Precises if the function should fail if the folder
        is not found.

    :returns: managed_folder_name: str: The name associated with 'managed_folder_id'.
    """
    check_object_is_project(project)
    managed_folder_id_exists = check_if_managed_folder_id_exists(project, managed_folder_id, fail_if_not_exists=fail_if_not_exists)
    if managed_folder_id_exists:
        _, managed_folder_settings_dict = get_managed_folder_settings_and_dictionary(project, managed_folder_id)
        managed_folder_name = managed_folder_settings_dict["name"]
    else:
        managed_folder_name = ""
        if fail_if_not_exists:
            log_message = f"The folder with the ID '{managed_folder_id}' does not exist!"
            raise Exception(log_message)
    return managed_folder_name


def create_managed_folder_in_connection(project: DSSProject, managed_folder_name: str, connection_name:str):
    """
    Creates a managed folder in a given connection.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_name: str: Name of the project managed folder.
    :param connection_name: str: Name of the connection.

    :returns: managed_folder: dataikuapi.dss.managedfolder.DSSManagedFolder: A handle to interact with the newly created managed folder.
    :returns: managed_folder_id: str: The ID associated with the newly created 'managed_folder_id'.
    """
    check_object_is_project(project)
    managed_folder = project.create_managed_folder(managed_folder_name, connection_name=connection_name)
    managed_folder_id = managed_folder.id
    print(f"A managed folder named '{managed_folder_name}' has been successfully created in the connection '{connection_name}' "\
          f"with the ID '{managed_folder_id}'")
    return managed_folder, managed_folder_id


def check_if_managed_folder_name_exists(project: DSSProject, managed_folder_name: str, fail_if_not_exists: bool=False,
                                        fail_if_several_matching=False):
    """
    Checks whether a managed folder name exists or not. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_name: string: Name of the managed folder.
    :param fail_if_not_exists: bool: Precises if the function should fail if the manage folder name
        does not exist.
    :param fail_if_several_matching: bool: Precises if the function should fail if several folders 
        have the name 'managed_folder_name'.

    :returns: managed_folder_exists: bool: Boolean indicating if the managed folder name exists or not.
    """
    check_object_is_project(project)
    print("Checking if managed folder named '{}' exists ...".format(managed_folder_name))
    managed_folder_exists = False
    matching_project_folders = [folder_data for folder_data in project.list_managed_folders() if folder_data["name"] == managed_folder_name]
    if matching_project_folders:
        managed_folder_exists = True
        if len(matching_project_folders) > 1:
            log_message = f"Warning: More than one folder matched with the name '{managed_folder_name}'!\n"\
                f"The folders nammatching with the name '{managed_folder_name}' are : '{matching_project_folders}'"
            if fail_if_several_matching:
                raise Exception(log_message)
            else:
                print(log_message)
        log_message = f"The managed folder named '{managed_folder_name}' exists"
    else:
        log_message = f"The managed folder named '{managed_folder_name}' does not exist"
    trigger_failure = ((not managed_folder_exists) and (fail_if_not_exists))
    if trigger_failure:
        raise Exception(log_message)
    else:
        print(log_message)
    return managed_folder_exists


def check_if_managed_folder_id_exists(project: DSSProject, managed_folder_id: str, fail_if_not_exists: bool=False):
    """
    Checks whether a managed folder ID exists or not. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    :param fail_if_not_exists: bool: Precises if the function should fail if the manage folder ID
        does not exist.

    :returns: managed_folder_exists: bool: Boolean indicating if the managed folder ID exists or not.
    """
    check_object_is_project(project)
    print(f"Checking if managed folder ID '{managed_folder_id}' exists ...")
    managed_folder_exists = False
    project_folder_ids = [folder_data["id"] for folder_data in project.list_managed_folders()]
    if managed_folder_id in project_folder_ids:
        managed_folder_exists = True
        log_message = f"The managed folder ID '{managed_folder_id}' exists"
    else:
        log_message = f"The managed folder ID '{managed_folder_id}' does not exist"
    trigger_failure = ((not managed_folder_exists) and (fail_if_not_exists))
    if trigger_failure:
        raise Exception(log_message)
    else:
        print(log_message)
    return managed_folder_exists


def get_managed_folder_connection_type(project: DSSProject, managed_folder_id: str):
    """Retrieves the connection type of a project managed folder.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    
    :returns: managed_folder_connection_type: str: The managed folder connection type.
    """
    check_object_is_project(project)
    check_if_managed_folder_id_exists(project, managed_folder_id, fail_if_not_exists=True)
    __, managed_folder_settings_dict = get_managed_folder_settings_and_dictionary(project, managed_folder_id)
    managed_folder_connection_type = managed_folder_settings_dict["type"]
    return managed_folder_connection_type


def get_managed_folder_connection_name(project: DSSProject, managed_folder_id: str):
    """Retrieves the connection name of a project managed folder.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    
    :returns: managed_folder_connection_name: str: The managed folder connection name.
    """
    check_object_is_project(project)
    check_if_managed_folder_id_exists(project, managed_folder_id, fail_if_not_exists=True)
    __, managed_folder_settings_dict = get_managed_folder_settings_and_dictionary(project, managed_folder_id)
    managed_folder_connection_name = managed_folder_settings_dict["params"]["connection"]
    return managed_folder_connection_name


def get_managed_folder_description(project: DSSProject, managed_folder_id: str, description_type: str="short_description"):
    """Retrieves the description of a project folder.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    :param description_type: str: The type of description to modify.
        The available options are:
            - 'short_description': To enrich the folder short description.
            - 'long_description': To enrich the folder long description.
    :returns: folder_description: str: Description of the project folder.
    """
    check_object_is_project(project)
    folder_settings, _ = get_managed_folder_settings_and_dictionary(project, managed_folder_id)
    if description_type == "short_description":
        folder_description = folder_settings.short_description 
    else:
        folder_description = folder_settings.description
    if folder_description is None:
        folder_description = ""
    return folder_description


def modify_managed_folder_description(project: DSSProject, managed_folder_id: str, description_modification: str,
                                      description_type: str="short_description", type_of_modification: str="replace_all",
                                      descriptions_separator: str="\n\n"):
    """Modifies the description of a project folder.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    :param description_modification: str: The description to modify the folder with.
    :param description_type: str: The type of description to modify.
        The available options are:
            - 'short_description': To enrich the folder short description.
            - 'long_description': To enrich the folder long description.
    :param type_of_modification: str: The type of description modification to apply.
        The available options are:
            - 'replace_all': If you want to replace the existing description.
            - 'add_before': If you want to add your description before the existing description.
            - 'add_after': If you want to add your description after the existing description.
    :param descriptions_separator: str: The separator to use between each description.
        This only applies when 'type_of_modification' equals to 'add_before' or 'add_after'.
    """
    check_object_is_project(project)
    folder_settings, _ = get_managed_folder_settings_and_dictionary(project, managed_folder_id)
    existing_description = get_managed_folder_description(project, managed_folder_id, description_type)
    if not existing_description:
        existing_description = ""
        
    if type_of_modification == "replace_all":
        new_description = description_modification
    
    elif type_of_modification == "add_before":
        new_description = f"{description_modification}{descriptions_separator}{existing_description}"
    
    elif type_of_modification == "add_after":
        new_description = f"{existing_description}{descriptions_separator}{description_modification}"
        
    
    if description_type == "short_description":
        folder_settings.short_description = new_description
    else:
        folder_settings.description = new_description
    folder_settings.save()