from dku_utils.type_checking import DSSProject, check_object_is_project


def get_flow_graph(project: DSSProject):
    """
    Retrieves the graph associated with a project's flow. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: flow_graph: dataikuapi.dss.flow.DSSProjectFlowGraph: The flow graph.
    """
    check_object_is_project(project)
    flow = project.get_flow()
    flow_graph = flow.get_graph()
    return flow_graph


def get_flow_input_dataset_names(project: DSSProject, include_shared_datasets: bool=False):
    """
    Retrieves all project input dataset names. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param include_shared_datasets: bool: To retrieve datasets shared from other projects.
        DISCLAIMERS :
        - 1: If set to 'True', this parameter can lead to have datasets with the pattern:
            `REMOTE_PROJECT_KEY`.`REMOTE_PROJECT_DATASET_NAME` where: 
            - `REMOTE_PROJECT_KEY` is the key of the project that shares a dataset with `project`.
            - `REMOTE_PROJECT_DATASET_NAME` is the name of the dataset, in `REMOTE_PROJECT_KEY`, shared in `project`
        - 2: Datasets are not considered as `project` inputs if they are not the inputs of some recipes in `project`.

    :returns: project_input_dataset_names: list: List of all project input dataset names.
    """
    check_object_is_project(project)
    flow_graph = get_flow_graph(project)
    flow_inputs = flow_graph.get_source_datasets()
    if include_shared_datasets:
        project_input_dataset_names = [dataiku_dataset.name for dataiku_dataset in flow_inputs]
    else:
        project_input_dataset_names = [dataiku_dataset.name for dataiku_dataset in flow_inputs if '.' not in dataiku_dataset.name]
    
    return project_input_dataset_names


def get_flow_element_successors_names_and_types(project: DSSProject, flow_element: str):
    """
    Retrieves a 'flow element' SUCCESSORS names and types
        A 'flow element' can be 'dataset_name', 'recipe_name', 'folder_id', 'deployed_model_id', etc...
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param flow_element: str: Name or ID of the element.

    :returns: element_successors_names: list: List of all the flow element successor names.
    :returns: element_successors_types: list: List of all the flow element successor types.
    """
    check_object_is_project(project)
    flow_graph = get_flow_graph(project)
    flow_nodes = flow_graph.data["nodes"]
    element_successors_names = flow_nodes[flow_element].get("successors")
    element_successors_types = []
    for successor_name in element_successors_names:
        element_successors_types.append(flow_nodes[successor_name]["type"])
    return element_successors_names, element_successors_types


def get_flow_element_predecessors_names_and_types(project: DSSProject, flow_element: str):
    """
    Retrieves a 'flow element' PREDECESSORS names and types
        A 'flow element' can be 'dataset_name', 'recipe_name', 'folder_id', 'deployed_model_id', etc...
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param flow_element: str: Name or ID of the element.

    :returns: element_predecessors_names: list: List of all the flow element predecessor names.
    :returns: element_predecessors_types: list: List of all the flow element predecessor types.
    """
    check_object_is_project(project)
    flow_graph = get_flow_graph(project)
    flow_nodes = flow_graph.data["nodes"]
    element_predecessors_names = flow_nodes[flow_element].get("predecessors")
    element_predecessors_types = []
    for successor_name in element_predecessors_names:
        element_predecessors_types.append(flow_nodes[successor_name]["type"])
    return element_predecessors_names, element_predecessors_types