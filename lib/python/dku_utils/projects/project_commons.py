import dataiku
import re
from ..type_checking import DSSProject, check_object_is_project, check_project_key_exists
from .recipes.recipe_types import VISUAL_RECIPES
from .recipes.recipe_commons import adapt_recipe_engine_to_priority_and_availability


def get_current_project_and_variables():
    """
    Retrieves current dataiku DSS project and its variables.

    :returns: project: DSSProject: A handle to interact with a project on the DSS instance.
    :returns: variables: dict: Variables of the project
    """
    project = dataiku.api_client().get_project(dataiku.get_custom_variables()["projectKey"])
    variables = project.get_variables()
    return project, variables


def get_project_and_variables(project_key: str):
    """
    Retrieves any dataiku DSS project handler and its variables.

    :param project_key: str: The project key of interest.

    :returns: project: DSSProject: A handle to interact with a project on the DSS instance.
    :returns: variables: dict: Variables of the project
    """
    check_project_key_exists(project_key)
    project = dataiku.api_client().get_project(project_key)
    variables = project.get_variables()
    return project, variables


def get_all_project_dataset_names(project: DSSProject):
    """
    Retrieves all project dataset names. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: project_dataset_names: list: List of all project dataset names.
    """
    check_object_is_project(project)
    flow_datasets = project.list_datasets()
    project_dataset_names = [dataset_information["name"] for dataset_information in flow_datasets]
    return project_dataset_names


def get_all_project_recipe_names(project: DSSProject):
    """
    Retrieves all project recipe names.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :returns: project_recipe_names: list: List of all project recipe names.
    """
    check_object_is_project(project)
    flow_recipes = project.list_recipes()
    project_recipe_names = [recipe_information["name"] for recipe_information in flow_recipes]
    return project_recipe_names


def get_all_project_recipe_names_with_chosen_type(project: DSSProject, type_of_recipes: list):
    """
    Retrieves the list of all the project recipes of a given type. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param type_of_recipes: list: Type of the recipes to look for. A list of the available recipe types, 
        classified by recipe categories can be found in ./recipes/recipe_types.
    
    :returns: flow_recipes_with_chosen_type: list: List of all the project recipes matching with the chosen type.
    """
    check_object_is_project(project)
    flow_recipes_with_chosen_type = [recipe["name"]
                                     for recipe in project.list_recipes()
                                     if recipe["type"] in type_of_recipes]
    return flow_recipes_with_chosen_type


def get_all_project_folder_names(project: DSSProject):
    """
    Retrieves all project folder names. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: project_folder_names: list: List of all project folder names.
    """
    check_object_is_project(project)
    project_folders_data = project.list_managed_folders()
    project_folder_names = [folder_information["name"] for folder_information in project_folders_data]
    return project_folder_names


def get_all_project_scenarios_ids(project: DSSProject):
    """
    Retrieves all the scenarios IDs defined in a project.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: all_project_scenarios_ids: list: List of all scenarios IDs defined in the project.
    """
    check_object_is_project(project)
    print("Retrieving all project '{}' scenario IDs...".format(project.project_key))
    project_scenarios_information = project.list_scenarios()
    all_project_scenarios_ids = [scenario_information["id"] for scenario_information in project_scenarios_information]
    print("All project '{}' scenario IDs successfully retrieved!".format(project.project_key))
    return all_project_scenarios_ids


def switch_all_project_visual_recipes_engines(project: DSSProject, recipe_engines_priority: list=[]):
    """
    Switches the engine of all project visual recipes.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_engines_priority: list: List of the engines to prioritize in the process of imputing an
        engine to the recipe.
        IF 'recipe_engines_priority' is set empty: 
            - The default engines priority will be the one defined in the project settings.
                - If no engines priority has been set in the project settings, the default engine is DSS.
        ELSE: It overrides the engines priority set in the project.
        'recipe_engines_priority' values should be ordered by decreasing priority.
            - Example: ['SQL', 'SPARK', 'DSS'] means that 'SQL' should be prioritized over 
            'SPARK' and 'DSS' if they are available.
    """
    all_visual_recipe_names = get_all_project_recipe_names_with_chosen_type(project, VISUAL_RECIPES)
    for recipe_name in all_visual_recipe_names:
        adapt_recipe_engine_to_priority_and_availability(project, recipe_name, recipe_engines_priority)
    pass


def get_all_project_webapp_names_and_ids(project: DSSProject, webapp_types: list=[]):
    """Retrieves all project webapp names and IDs. 

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param webapp_types: list: the types of webapps to retrieve from the project.
        The native DSS webapp types are: 
         - STANDARD: For standard webapps combining HTML, Javascript, CSS and optionally a python backend.
         - SHINY: For R Shiny webapps.
         - DASH: For python Dash webapps.
         - BOKEH: For python Bokeh webapps.
        For visual webapps, the webapp type syntax is: 'webapp_PLUGIN_ID_WEBAPP_ID' 
            (Example: webapp_document-question-answering_document-intelligence-explorer)

    :returns: project_webapp_names: list: List of all project webapp names.
    :returns: project_webapp_ids: list: List of all project webapp IDs.
    """
    check_object_is_project(project)
    project_webapp_names = []
    project_webapp_ids = []
    flow_webapps = project.list_webapps()
    for webapp_information in flow_webapps:
        webapp_type = webapp_information["type"]
        name_to_add = webapp_information["name"]
        id_to_add = webapp_information["id"]
        if webapp_types:
            if webapp_type not in webapp_types:
                name_to_add = None
                id_to_add = None
        if name_to_add and id_to_add:
            project_webapp_names.append(name_to_add)
            project_webapp_ids.append(id_to_add)
    
    return project_webapp_names, project_webapp_ids


def expand_project_key(dss_object_string: str, project_key_to_expand: str):
    """Expands the '${projectKey}' variable contained in a dataiku DSS object string.

    :param dss_object_string: str: The Dataiku DSS object string.
    :param project_key_to_expand: str: The value of project key to expand.

    Example: expand_project_key('${projectKey}_my_first_table', 'SANDBOX') leads to 'SANDBOX_my_first_table.
    
    :returns: expanded_dss_object_string: str: The expanded dataiku DSS object string.
    """
    expanded_dss_object_string = re.sub(r'\${projectKey}', project_key_to_expand, dss_object_string)
    return expanded_dss_object_string