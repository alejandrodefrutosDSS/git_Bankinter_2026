from dku_utils.type_checking import DSSProject, check_object_is_project

# --------------- Flow zone functions ---------------
def check_if_flow_zone_exists(project: DSSProject, flow_zone_name: str):
    """
    Checks whether a flow zone exists or not. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param flow_zone_name: string: Name of the flow zone.

    :returns: flow_zone_exists: bool: Boolean indicating if the flow zone exists or not.
    """
    check_object_is_project(project)
    flow = project.get_flow()
    print("Checking if flow zone '{}' exists ...".format(flow_zone_name))
    try:
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        flow.get_zone(flow_zone_id)
        flow_zone_exists = True
        print("Flow zone '{}' exists".format(flow_zone_name))
        pass
    except:
        print("Flow zone '{}' does not exist".format(flow_zone_name))
        flow_zone_exists = False
        pass
    return flow_zone_exists


def drop_flow_zone_if_exists(project: DSSProject, flow_zone_name: str):
    """
    Drops a project flow zone if it exists. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param flow_zone_name: string: Name of the flow zone.
    """
    check_object_is_project(project)
    flow_zone_exists = check_if_flow_zone_exists(project, flow_zone_name)
    if flow_zone_exists:
        flow = project.get_flow()
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        flow_zone = flow.get_zone(flow_zone_id)
        print("Dropping flow zone '{}'...".format(flow_zone_name))
        flow_zone.delete()
        print("Flow zone '{}' Deleted !".format(flow_zone_name))
        pass
    pass


def create_flow_zone_if_not_exists(project: DSSProject, flow_zone_name: str, flow_zone_color: str):
    """
    Creates a project flow zone if it does not exists. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param flow_zone_name: string: Name of the flow zone.
    :param flow_zone_color: string: Flow zone hexadecimal color code.
    """
    check_object_is_project(project)
    if flow_zone_color in ["", None]:
        flow_zone_color = "#C82423"
        pass
    flow_zone_exists = check_if_flow_zone_exists(project, flow_zone_name)
    if not flow_zone_exists:
        flow = project.get_flow()
        print("Creating flow zone '{}'...".format(flow_zone_name))
        flow.create_zone(flow_zone_name, color=flow_zone_color)
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        print("Flow zone '{}' created with id '{}' !".format(flow_zone_name, flow_zone_id))
        pass
    pass


def get_flow_zone_id(project: DSSProject, flow_zone_name: str):
    """
    Retrieves the id associated with a project flow zone . 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param flow_zone_name: str: Name of the flow zone.

    :returns: flow_zone_id: str: The ID associated with 'flow_zone_name'.
    """
    check_object_is_project(project)
    flow = project.get_flow()
    flow_zones_data = flow.list_zones()
    flow_zone_id = None
    for flow_zone_data in flow_zones_data:
        if flow_zone_data.name == flow_zone_name:
            flow_zone_id = flow_zone_data.id
            pass
        pass
    if flow_zone_id is None:
        log_message = "Flow zone '{}' does not exist! "\
            "Valid flow zone names are: '{}'".format(flow_zone_name, flow_zones_data)
        raise ValueError(log_message)
    return flow_zone_id


# --------------- Flow zone functions for datasets ---------------
def move_dataset_in_flow_zone(project: DSSProject, dataset_name: str, flow_zone_name: str):
    """
    Moves a project dataset in a flow zone. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: string: Name of the dataset.
    :param flow_zone_name: string: Name of the flow zone.
    """
    check_object_is_project(project)
    flow_zone_exists = check_if_flow_zone_exists(project, flow_zone_name)
    if flow_zone_exists:
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        project_dataset = project.get_dataset(dataset_name)
        project_dataset.move_to_zone(flow_zone_id)
        print("Dataset '{}' successfully moved in flow zone '{}'!".format(dataset_name, flow_zone_name))
        pass
    pass


def share_dataset_in_flow_zone(project: DSSProject, dataset_name: str, flow_zone_name: str):
    """
    Shares a project dataset in a flow zone. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: string: Name of the dataset.
    :param flow_zone_name: string: Name of the flow zone.
    """
    check_object_is_project(project)
    flow_zone_exists = check_if_flow_zone_exists(project, flow_zone_name)
    if flow_zone_exists:
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        project_dataset = project.get_dataset(dataset_name)
        project_dataset.share_to_zone(flow_zone_id)
        print("Dataset '{}' successfully shared with flow zone '{}'!".format(dataset_name, flow_zone_name))
        pass
    pass


def unshare_dataset_from_flow_zone(project: DSSProject, dataset_name: str, flow_zone_name: str):
    """
    Unshares a project dataset from a flow zone. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: string: Name of the dataset.
    :param flow_zone_name: string: Name of the flow zone.
    """
    check_object_is_project(project)
    flow_zone_exists = check_if_flow_zone_exists(project, flow_zone_name)
    if flow_zone_exists:
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        project_dataset = project.get_dataset(dataset_name)
        project_dataset.unshare_from_zone(flow_zone_id)
        print("Dataset '{}' successfully unshared from flow zone '{}'!".format(dataset_name, flow_zone_name))
        pass
    pass


# --------------- Flow zone functions for recipes ---------------
def move_recipe_in_flow_zone(project: DSSProject, recipe_name: str, flow_zone_name: str):
    """
    Moves a project recipe in a flow zone.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: string: Name of the recipe.
    :param flow_zone_name: string: Name of the flow zone.
    """
    check_object_is_project(project)
    flow_zone_exists = check_if_flow_zone_exists(project, flow_zone_name)
    if flow_zone_exists:
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        project_recipe = project.get_recipe(recipe_name)
        project_recipe.move_to_zone(flow_zone_id)
        print("Recipe '{}' successfully moved in flow zone '{}'!".format(recipe_name, flow_zone_name))
        pass
    pass


# --------------- Flow zone functions for managed folders ---------------
def move_managed_folder_in_flow_zone(project: DSSProject, managed_folder_id: str, flow_zone_name: str):
    """
    Moves a project managed folder in a flow zone. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param managed_folder_id: string: ID of the managed folder.
    :param flow_zone_name: string: Name of the flow zone.
    """
    check_object_is_project(project)
    flow_zone_exists = check_if_flow_zone_exists(project, flow_zone_name)
    if flow_zone_exists:
        flow_zone_id = get_flow_zone_id(project, flow_zone_name)
        project_folder = project.get_managed_folder(managed_folder_id)
        project_folder.move_to_zone(flow_zone_id)
        print(f"Folder '{managed_folder_id}' successfully moved in flow zone '{flow_zone_name}'!")