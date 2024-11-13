import pandas as pd
from dku_utils.python_utils.python_scripts import get_python_script_libraries_import_dataframe
from dku_utils.type_checking import DSSProject, check_object_is_project


def get_scenario_settings(project: DSSProject, scenario_id: str):
    """
    Retrieves the settings of a project scenario.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.

    :returns: scenario_settings: dataikuapi.dss.scenario.StepBasedScenarioSettings: Settings of a scenario.
    """
    check_object_is_project(project)
    scenario_settings = project.get_scenario(scenario_id).get_settings()
    return scenario_settings


def switch_scenario_auto_trigger_state(project: DSSProject, scenario_id: str, bool_activate_auto_trigger: bool):
    """
    Activates or desactivates a project scenario 'Auto-triggers'.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    :param bool_activate_auto_trigger: bool: Boolean precising if you want to activate the scenario auto trigger.
    """
    check_object_is_project(project)
    scenario_settings = get_scenario_settings(project, scenario_id)
    if bool_activate_auto_trigger:
        scenario_settings.active = True
        auto_trigger_state = "ACTIVATED"
    else:
        scenario_settings.active = False
        auto_trigger_state = "DESACTIVATED"
    scenario_settings.save()
    print("Scenario auto-trigger state successfully switched to '{}'".format(auto_trigger_state))
    pass


def switch_scenario_triggers_state(project: DSSProject, scenario_id: str, list_bool_trigger_activations: list):
    """
    Activates or desactivates a project scenario 'Triggers'.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    :param list_bool_trigger_activations: list: List of booleans precising if you want to activate the scenario triggers.
        This list should have the length equals to the number of triggers existing in the scenario.
    """
    check_object_is_project(project)
    scenario_settings = get_scenario_settings(project, scenario_id)
    triggers_definition = scenario_settings.get_raw()["triggers"]
    new_triggers_definition = []
    triggers_states = {}
    n_triggers = len(triggers_definition)
    n_boolean_instructions = len(list_bool_trigger_activations)
    if n_triggers != n_boolean_instructions:
        log_message = "It seems that scenario '{}' has '{}' defined but you provided '{}' "\
            "boolean instructions in parameter 'list_bool_trigger_activations' ! "\
            "Prease provide as many boolean instructions as there are triggers"\
            .format(scenario_id, n_triggers, n_boolean_instructions)
        raise ValueError(log_message)
    for trigger_definition, bool_trigger_activation in zip(triggers_definition, list_bool_trigger_activations):
        trigger_name = trigger_definition["name"]
        triggers_states[trigger_name] = "ACTIVATED" if bool_trigger_activation else "DESACTIVATED"
        trigger_definition["active"] = bool_trigger_activation
        new_triggers_definition.append(trigger_definition)
    scenario_settings.get_raw()["triggers"] = new_triggers_definition
    scenario_settings.save()
    print("Scenario triggers states successfully switched to : {}".format(triggers_states))
    pass


def get_scenario_steps(project: DSSProject, scenario_id: str):
    """
    Retrieves the steps of a project scenario.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    :returns: scenario_steps: list: Steps of a scenario.
    """
    check_object_is_project(project)
    print("Retrieving scenario '{}' steps ...".format(scenario_id))
    scenario_settings = get_scenario_settings(project, scenario_id)
    scenario_steps = scenario_settings.get_raw()["params"]["steps"]
    return scenario_steps


def set_scenario_steps(project: DSSProject, scenario_id: str, scenario_steps: list):
    """
    Sets the steps of a project scenario.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    :param scenario_steps: list: Steps of the scenario.
    """
    check_object_is_project(project)
    print("Setting scenario '{}' steps ...".format(scenario_id))
    scenario_settings = get_scenario_settings(project, scenario_id)
    scenario_settings.get_raw()["params"]["steps"] = scenario_steps
    scenario_settings.save()
    print("Scenario '{}' steps successfully set!".format(scenario_id))
    pass


def get_scenario_python_step_script(project: DSSProject, scenario_id: str, step_index: int):
    """
    Retrieves the script of a scenario python step.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    :param step_index: int: Index of the python step of concern.

    :returns: scenario_python_step_script: str: Script of the python step of concern.
    """
    check_object_is_project(project)
    scenario_settings = get_scenario_settings(project, scenario_id)
    scenario_python_step_script = scenario_settings.get_raw()\
    ["params"]["steps"][step_index]["params"]["script"]
    return scenario_python_step_script


def get_scenario_library_dependencies_dataframe(project: DSSProject, scenario_id: str):
    """
    Retrieves a DataFrame containing all python modules dependencies for a project's scenario.
        DISCLAIMER: Does not retrieves import done within functions.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.

    :returns: scenario_library_dependencies_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing information about all the imports done in the scenario python scripts.
    """
    check_object_is_project(project)
    print("Retrieving scenario '{}.{}' python dependencies ...".format(project.project_key, scenario_id))
    LIBRARY_DEPENDENCIES_SCHEMA = ["scenario_id", "scenario_step_index", "imported_from",
                                            "imported", "all_import_information"]
    scenario_type = get_scenario_type(project, scenario_id)
    if scenario_type == "step_based":
        scenario_steps = get_scenario_steps(project, scenario_id)
        steps_library_dependencies_dataframes = []
        for scenario_step_index, scenario_step in enumerate(scenario_steps):
            if scenario_step.get("type") == "custom_python":
                step_python_script = scenario_step["params"]["script"]
                step_imports_dataframe = get_python_script_libraries_import_dataframe(step_python_script)
                step_imports_dataframe["scenario_id"] = scenario_id
                step_imports_dataframe["scenario_step_index"] = scenario_step_index
                step_imports_dataframe = step_imports_dataframe[LIBRARY_DEPENDENCIES_SCHEMA]
                steps_library_dependencies_dataframes.append(step_imports_dataframe)
        if len(steps_library_dependencies_dataframes) > 0:
            scenario_library_dependencies_dataframe = pd.concat(steps_library_dependencies_dataframes).reset_index()
        else:
            scenario_library_dependencies_dataframe = pd.DataFrame(columns=LIBRARY_DEPENDENCIES_SCHEMA)
    else:
        scenario_settings = get_scenario_settings(project, scenario_id)
        scenario_script = scenario_settings.code
        scenario_script_imports_dataframe = get_python_script_libraries_import_dataframe(scenario_script)
        scenario_script_imports_dataframe["scenario_id"] = scenario_id
        scenario_script_imports_dataframe["scenario_step_index"] = 0
        scenario_script_imports_dataframe = scenario_script_imports_dataframe[LIBRARY_DEPENDENCIES_SCHEMA]
        scenario_library_dependencies_dataframe = scenario_script_imports_dataframe

    print("Scenario '{}.{}' python dependencies successfully retrieved!".format(project.project_key, scenario_id))
    return scenario_library_dependencies_dataframe


def check_if_scenario_exists(project: DSSProject, scenario_id: str):
    """
    Checks if a scenario exists in a project.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.

    :returns: scenario_exists: bool: Precises whether the scenario exists or not. 
    """
    check_object_is_project(project)
    project_scenarios = project.list_scenarios()
    scenario_ids = [scenario_data["id"] for scenario_data in project_scenarios]
    scenario_exists = (scenario_id in scenario_ids)
    return scenario_exists


def create_scenario_if_not_exists(project: DSSProject, scenario_id: str, scenario_type: str="custom_python"):
    """
    Creates a scenario in a project if it does not exists.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    :param scenario_type: str: Type of the scenario to create. 
        Available choices are: 
            - 'custom_python' [Default value]
            - 'step_based'
    """
    check_object_is_project(project)
    scenario_exists = check_if_scenario_exists(project, scenario_id)
    if scenario_exists:
         print(f"Scenario '{scenario_id}' already exists in project '{project.project_key}'.")
    else:
        print(f"Scenario '{scenario_id}'does not exist in project '{project.project_key}' and will be created.")
        project.create_scenario(scenario_id, scenario_type)
        print(f"Scenario '{scenario_id}' has been successfully created in project '{project.project_key}'!")
    pass


def delete_scenario_if_exists(project: DSSProject, scenario_id: str):
    """
    Removes a scenario from a project if it exists.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    """
    check_object_is_project(project)
    scenario_exists = check_if_scenario_exists(project, scenario_id)
    if scenario_exists:
        print(f"Deleting scenario '{scenario_id}' from project '{project.project_key}' ...")
        project.get_scenario(scenario_id).delete()
        print(f"Scenario '{scenario_id}' has been successfully deleted from project '{project.project_key}'!")
    else:
        print(f"Scenario '{scenario_id}' does not exists in project '{project.project_key}'.")
    pass


def get_scenario_type(project: DSSProject, scenario_id: str):
    """
    Retrieves the type of a scenario.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param scenario_id: str: ID of the scenario.
    
    :returns: scenario_type: str: The scenario's type.
    """
    check_object_is_project(project)
    scenario_settings = get_scenario_settings(project, scenario_id)
    scenario_type = scenario_settings.get_raw()["type"]
    return scenario_type