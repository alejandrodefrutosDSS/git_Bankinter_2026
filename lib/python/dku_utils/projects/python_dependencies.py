import pandas as pd
from .project_commons import get_all_project_scenarios_ids, get_all_project_recipe_names_with_chosen_type
from .scenarios.scenario_commons import get_scenario_library_dependencies_dataframe
from .recipes.python_recipe import get_python_recipe_library_dependencies_dataframe
from ..type_checking import DSSProject, check_object_is_project


def get_all_project_scenarios_library_dependencies_dataframe(project: DSSProject):
    """
    Retrieves a DataFrame containing all python modules dependencies for a all project's scenarios.
        DISCLAIMER: Does not retrieves import done within functions.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: all_flow_scenarios_library_dependencies_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing information about all the imports done in all the scenario python scripts.
    """
    check_object_is_project(project)
    print("Retrieving project '{}' all 'scenarios' python dependencies ...".format(project.project_key))
    LIBRARY_DEPENDENCIES_SCHEMA = ["scenario_id", "scenario_step_index", "imported_from",
                                            "imported", "all_import_information"]
    all_flow_scenarios_ids = get_all_project_scenarios_ids(project)
    all_flow_scenarios_library_dependencies = []
    for scenario_id in all_flow_scenarios_ids:
        scenario_library_dependencies_dataframe = get_scenario_library_dependencies_dataframe(project, scenario_id)
        all_flow_scenarios_library_dependencies.append(scenario_library_dependencies_dataframe)
    
    if len(all_flow_scenarios_library_dependencies) > 0:
        all_flow_scenarios_library_dependencies_dataframe = pd.concat(all_flow_scenarios_library_dependencies).reset_index()
    else:
        all_flow_scenarios_library_dependencies_dataframe = pd.DataFrame(columns=LIBRARY_DEPENDENCIES_SCHEMA)
    print("All project '{}' 'scenarios' python dependencies successfully retrieved!".format(project.project_key))   
    return all_flow_scenarios_library_dependencies_dataframe


def get_all_project_python_recipes_library_dependencies_dataframe(project: DSSProject):
    """
    Retrieves a DataFrame containing all python modules dependencies for a all project recipes.
        DISCLAIMER: Does not retrieves import done within functions.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: all_flow_python_recipes_library_dependencies_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing information about all the imports done in all the recipes python scripts.
    """
    check_object_is_project(project)
    print("Retrieving project '{}' all 'python recipes' python dependencies ...".format(project.project_key))
    LIBRARY_DEPENDENCIES_SCHEMA = ["recipe_name", "imported_from",
                                  "imported", "all_import_information"]
    all_flow_python_recipe_names = get_all_project_recipe_names_with_chosen_type(project, ["python", "pyspark"])
    all_flow_python_recipe_library_dependencies = []
    for recipe_name in all_flow_python_recipe_names:
        recipe_library_dependencies_dataframe = get_python_recipe_library_dependencies_dataframe(project, recipe_name)
        all_flow_python_recipe_library_dependencies.append(recipe_library_dependencies_dataframe)
    
    if len(all_flow_python_recipe_library_dependencies) > 0:
        all_flow_python_recipes_library_dependencies_dataframe = pd.concat(all_flow_python_recipe_library_dependencies).reset_index()
    else:
        all_flow_python_recipes_library_dependencies_dataframe = pd.DataFrame(columns=LIBRARY_DEPENDENCIES_SCHEMA)    
    print("All project '{}' 'python recipes' python dependencies successfully retrieved!".format(project.project_key))   
    return all_flow_python_recipes_library_dependencies_dataframe


def get_all_project_library_dependencies_dataframe(project: DSSProject, feature_scopes: list=["SCENARIOS", "PYTHON_RECIPES"]):
    """
    Retrieves a DataFrame containing all python modules dependencies for scenarios and/or recipes.
        DISCLAIMER: Does not retrieves import done within functions.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param: feature_scopes: list: List of all dataiku features ("SCENARIOS", "PYTHON_RECIPES") where to look python
        modules dependencies.
    
    :returns: all_flow_python_recipes_library_dependencies_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing information about all the library depencencies  in project features covered by 'feature_scopes'.
    """
    ALLOWED_FEATURE_SCOPES = ["SCENARIOS", "PYTHON_RECIPES"]
    LIBRARY_DEPENDENCIES_SCHEMA = ["feature_scope", "imported_from", "imported", "all_import_information"]
    check_object_is_project(project)
    if len(feature_scopes) == 0:
        log_message = f"Not any feature_scope have been provided: please provide at least one\
              feature scope in '{ALLOWED_FEATURE_SCOPES}'!"
        raise ValueError(log_message)
    for feature_scope in feature_scopes:
        if feature_scope not in ALLOWED_FEATURE_SCOPES:
            log_message = f"Feature score '{feature_scope}' is not part of the allowed feature scopes:\
                  please choose feature scopes present in '{ALLOWED_FEATURE_SCOPES}'!"
            raise ValueError(log_message)
    project_library_dependencies_dataframes = []
    if "PYTHON_RECIPES" in feature_scopes:
        all_flow_python_recipes_library_dependencies_dataframe = get_all_project_python_recipes_library_dependencies_dataframe(project)
        all_flow_python_recipes_library_dependencies_dataframe["feature_scope"] = "PYTHON_RECIPE"
        project_library_dependencies_dataframes.append(all_flow_python_recipes_library_dependencies_dataframe)
        LIBRARY_DEPENDENCIES_SCHEMA.append("recipe_name")
    if "SCENARIOS" in feature_scopes:
        all_flow_scenarios_library_dependencies_dataframe = get_all_project_scenarios_library_dependencies_dataframe(project)
        all_flow_scenarios_library_dependencies_dataframe["feature_scope"] = "SCENARIO"
        project_library_dependencies_dataframes.append(all_flow_scenarios_library_dependencies_dataframe)
        for column in ["scenario_id", "scenario_step_index"]:
            LIBRARY_DEPENDENCIES_SCHEMA.append(column)
    all_project_library_dependencies_dataframe = pd.concat(project_library_dependencies_dataframes)
    if "SCENARIOS" in feature_scopes:
        all_project_library_dependencies_dataframe["scenario_step_index"] = all_project_library_dependencies_dataframe["scenario_step_index"].fillna(-1).astype(int)
    all_project_library_dependencies_dataframe = all_project_library_dependencies_dataframe[LIBRARY_DEPENDENCIES_SCHEMA].reset_index()
    return all_project_library_dependencies_dataframe


def get_per_recipe_library_dependencies(project: DSSProject):
    """
    Retrieves a dictionary containing all python modules dependencies for a all project recipes.
        DISCLAIMER: Does not retrieves import done within functions.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: recipe_library_dependencies: dict: Dictionary containing information about all the imports done
        in all the recipes python scripts.
    """
    check_object_is_project(project)
    all_flow_python_recipes_library_dependencies_dataframe = get_all_project_python_recipes_library_dependencies_dataframe(project)
    recipe_names = list(all_flow_python_recipes_library_dependencies_dataframe["recipe_name"].unique())
    recipe_library_dependencies = {}
    for recipe_name in recipe_names:
        tmp_df = all_flow_python_recipes_library_dependencies_dataframe[(all_flow_python_recipes_library_dependencies_dataframe["recipe_name"]==recipe_name)]

        recipe_library_dependencies[recipe_name] = {"imported_python_entities": [], "all_import_informations": []}
        for element, import_information in zip(list(tmp_df["imported"]),
                                                tmp_df["all_import_information"]):
            recipe_library_dependencies[recipe_name]["imported_python_entities"].append(element)
            recipe_library_dependencies[recipe_name]["all_import_informations"].append(import_information)
    return recipe_library_dependencies


def get_per_scenario_library_dependencies(project: DSSProject):
    """
    Retrieves a dictionary containing all python modules dependencies for a all project scenarios.
        DISCLAIMER: Does not retrieves import done within functions.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.

    :returns: scenario_library_dependencies: dict: Dictionary containing information about all the imports done
        in all the scenarios python scripts.
    """
    check_object_is_project(project)
    all_project_scenarios_library_dependencies_dataframe = get_all_project_scenarios_library_dependencies_dataframe(project)
    scenario_ids = list(all_project_scenarios_library_dependencies_dataframe["scenario_id"].unique())
    scenario_library_dependencies = {}
    for scenario_id in scenario_ids:
        scenario_library_dependencies[scenario_id] = {}
        tmp_df = all_project_scenarios_library_dependencies_dataframe[(all_project_scenarios_library_dependencies_dataframe["scenario_id"]==scenario_id)]
        scenario_python_step_indexes = list(tmp_df["scenario_step_index"].unique())
        for scenario_step_index in scenario_python_step_indexes:
            tmp_df_on_step = tmp_df[(tmp_df["scenario_step_index"]==scenario_step_index)]
            step_name = f"{scenario_id}_step_{scenario_step_index}"
            scenario_library_dependencies[scenario_id][step_name] = {"imported_python_entities": [], "all_import_informations": []}
            for element, import_information in zip(list(tmp_df_on_step["imported"]),
                                                    tmp_df_on_step["all_import_information"]):
                scenario_library_dependencies[scenario_id][step_name]["imported_python_entities"].append(element)
                scenario_library_dependencies[scenario_id][step_name]["all_import_informations"].append(import_information)
    return scenario_library_dependencies


def get_per_features_library_dependencies(project: DSSProject, feature_scopes: list=["SCENARIOS", "PYTHON_RECIPES"]):
    """
    Retrieves a dictionary containing all python modules dependencies for scenarios and/or recipes.
        DISCLAIMER: Does not retrieves import done within functions.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param: feature_scopes: list: List of all dataiku features ("SCENARIOS", "PYTHON_RECIPES") where to look python
        modules dependencies.
    
    :returns: per_features_library_dependencies: dict: Dictionary containing information about all the library depencencies 
        in project features covered by 'feature_scopes'.
    """
    check_object_is_project(project)
    ALLOWED_FEATURE_SCOPES = ["SCENARIOS", "PYTHON_RECIPES"]
    if len(feature_scopes) == 0:
        log_message = f"Not any feature_scope have been provided: please provide at least one\
              feature scope in '{ALLOWED_FEATURE_SCOPES}'!"
        raise ValueError(log_message)
    for feature_scope in feature_scopes:
        if feature_scope not in ALLOWED_FEATURE_SCOPES:
            log_message = f"Feature score '{feature_scope}' is not part of the allowed feature scopes:\
                  please choose feature scopes present in '{ALLOWED_FEATURE_SCOPES}'!"
            raise ValueError(log_message)
    per_features_library_dependencies = {}
    if "SCENARIOS" in feature_scopes:
        per_features_library_dependencies["SCENARIOS"] = get_per_scenario_library_dependencies(project)
    if "PYTHON_RECIPES" in feature_scopes:
        per_features_library_dependencies["PYTHON_RECIPES"] = get_per_recipe_library_dependencies(project)
    return per_features_library_dependencies