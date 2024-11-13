from dku_utils.projects.settings.engines import get_project_engines_priority
from dku_utils.type_checking import DSSProject, check_object_is_project


def get_recipe_settings_and_dictionary(project: DSSProject, recipe_name: str, bool_get_settings_dictionary: bool=True):
    """
    Retrieves the settings of a project recipe

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param bool_get_settings_dictionary: bool: Precise if you to rerieve the recipe settings dictionary.

    :returns: recipe_settings: dataikuapi.dss.recipe.[RecipeType]Settings: Settings for a recipe. 
    :returns: recipe_settings_dict: dict: Dictionary containing recipe settings.
    """
    check_object_is_project(project)
    recipe = project.get_recipe(recipe_name)
    recipe_settings = recipe.get_settings()

    if bool_get_settings_dictionary:
        recipe_settings_dict = recipe_settings.recipe_settings
    else:
        recipe_settings_dict = None

    return recipe_settings, recipe_settings_dict


def switch_recipe_engine(project: DSSProject, recipe_name: str, new_engine: str):
    """
    Switches the engine of a project recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param new_engine: str: Name of the recipe engine.
    """
    check_object_is_project(project)
    recipe = project.get_recipe(recipe_name)
    recipe_settings = recipe.get_settings()
    recipe_type = recipe_settings.type
    print("Switching recipe '{}' engine (recipe_type : '{}') ...".format(recipe_name, recipe_type))
    
    if recipe_type in ["prepare", "shaker", "sampling", "sync"]:
        recipe_settings.get_recipe_params()["engineType"] = new_engine
        
    elif recipe_type == "split":
        recipe_settings.obj_payload["engineType"] = new_engine
   
    else:
        recipe_settings.get_json_payload()["engineType"] = new_engine
    recipe_settings.save()
    print("Recipe '{}' engine successfully switched toward '{}'!".format(recipe_name, new_engine))
    pass


def adapt_recipe_engine_to_priority_and_availability(project: DSSProject, recipe_name: str, project_engines_priority_overrides: list=[]):
    """
    Set the recipe's engine to its optimal engine based on:
        - The engines priority set in the project settings OR an overriden engines priority...
        - ...AND The engines available in the recipe.
    The default engine is set to DSS is no match is found.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param project_engines_priority_overrides: list: List of the engines to prioritize in the process of imputing an
        engine to the recipe.  
        IF 'project_engines_priority_overrides' is set empty: 
            - The default engines priority will be the one defined in the project settings.
                - If no engines priority has been set in the project settings, the default engine is DSS.
        ELSE: It overrides the engines priority set in the project.
        'project_engines_priority_overrides' values should be ordered by decreasing priority.
            - Example: ['SQL', 'SPARK', 'DSS'] means that 'SQL' should be prioritized over 
            'SPARK' and 'DSS' if they are available.
    """
    check_object_is_project(project)
    engines_priority = get_project_engines_priority(project)
    if len(project_engines_priority_overrides) > 0:
        engines_priority = project_engines_priority_overrides
    available_engines = get_recipe_available_engines(project, recipe_name)
    if len(set(engines_priority).intersection(available_engines)) > 0:
        for engine in engines_priority:
            if engine in available_engines:
                switch_recipe_engine(project, recipe_name, new_engine=engine)
                break
    else:
        # if no engine from the priority list is an available engine, defaults to DSS
        switch_recipe_engine(project, recipe_name, new_engine="DSS")
    pass


def update_recipe_ouput_schema(project: DSSProject, recipe_name: str):
    """
    Updates the recipe's output dataset schema based on its settings and payload.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    """
    check_object_is_project(project)
    recipe = project.get_recipe(recipe_name)
    required_updates = recipe.compute_schema_updates()
    if required_updates.any_action_required():
        required_updates.apply()
        pass
    pass


def get_recipe_available_engines(project: DSSProject, recipe_name: str):
    """
    Retrieves the recipe's available engines.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.

    :returns: available_engines: list: List of the recipe's available engines.
    """
    check_object_is_project(project)
    available_engines = []
    recipe = project.get_recipe(recipe_name)
    recipe_status = recipe.get_status()
    recipe_engine_details = recipe_status.get_engines_details()
    available_engines = [entity["type"] for entity in recipe_engine_details if ((entity["isSelectable"])
                                                                                and
                                                                                (entity["statusWarnLevel"] == "OK"))]
    if len(available_engines) == 0:
        available_engines.append("DSS")
    return available_engines


def get_recipe_output_datasets(project: DSSProject, recipe_name: str):
    """
    Retrieves the recipe's outout datasets.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.

    :returns: recipe_output_datasets: list: List of the recipe's output datasets.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_output_items = recipe_settings.get_recipe_outputs()["main"]["items"]
    recipe_output_datasets = [item["ref"] for item in recipe_output_items]
    return recipe_output_datasets


def get_recipe_input_datasets(project: DSSProject, recipe_name: str):
    """
    Retrieves the recipe's input datasets.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.

    :returns: recipe_input_datasets: list: List of the recipe's input datasets.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_input_items = recipe_settings.get_recipe_inputs()["main"]["items"]
    recipe_input_datasets = [item["ref"] for item in recipe_input_items]
    return recipe_input_datasets


def set_recipe_input_datasets(project: DSSProject, recipe_name: str, new_input_dataset_names: list):
    """
    Sets new input datasets for a visual recipe.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param new_input_dataset_names: list: List of all dataset names that should be the new recipe inputs.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_settings.get_recipe_inputs()["main"]["items"] = []
    recipe_settings.save()
    for dataset_name in new_input_dataset_names:
        recipe_settings.add_input(role="main", ref=dataset_name)
    recipe_settings.save()
    pass


def override_aggregation_recipe_output_column_names(project: DSSProject, recipe_name: str, output_column_name_overrides: dict):
    """
    Overrides the output column names from recipes aggregating data.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param output_column_name_overrides: dict: Dictionary containing the mapping between the output columns coming
        from the recipe and the names they should have after column names overriding.
        Example: {'column_1_min': 'minimum_value_from_column_1',
                  'column_2_max': 'maximum_value_from_column_2'}
    """
    check_object_is_project(project)
    ALLOWED_RECIPE_TYPES = ["grouping", "window", "distinct", "topn"]
    print("Overriding recipe '{}' output column names with dictionary: '{}'"\
          .format(recipe_name, output_column_name_overrides))
    recipe_settings, recipe_settings_dict = get_recipe_settings_and_dictionary(project, recipe_name, True)
    recipe_type = recipe_settings_dict["type"]
    if recipe_type not in ALLOWED_RECIPE_TYPES:
        log_message = "Recipe '{}' is of type '{}', which is not allowed in this funtion. "\
            "Allowed recipe types are: '{}'".format(recipe_name, recipe_type, ALLOWED_RECIPE_TYPES)
        raise ValueError(log_message)
    recipe_payload = recipe_settings.get_json_payload()
    recipe_payload["outputColumnNameOverrides"] = output_column_name_overrides
    recipe_settings.set_json_payload(recipe_payload)
    recipe_settings.save()
    print("Recipe '{}' column names successfully overrided!".format(recipe_name))
    pass


def switch_visual_recipe_input(project: DSSProject, recipe_name: str, current_input_dataset_name: str, new_input_dataset_name: str):
    """
    Changes the input of a VISUAL recipe (this function has not been tried on plugin recipes).

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param current_input_dataset_name: str: Name of the dataset that is currently the recipe input.
    :param new_input_dataset_name: str: Name of the dataset that should be the new recipe input.
    """
    check_object_is_project(project)
    print("Changing recipe '{}' current input dataset '{}'  with dataset '{}'...".format(recipe_name,
                                                                                      current_input_dataset_name,
                                                                                      new_input_dataset_name))
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_settings.replace_input(current_input_dataset_name, new_input_dataset_name)
    recipe_settings.save()
    print("Recipe '{}' input dataset successfully changed!".format(recipe_name))
    pass


def prepare_visual_recipe_for_run(project: DSSProject, recipe_name: str, recipe_datasets_connection_type: str,
                                  recipe_engines_priority: list=['SQL', 'SPARK', 'DSS'], recipe_spark_configuration: str=""):
    """
    Sets visual recipe settings to make it ready for running.
    This implies: 
        - Optimizing the recipe engine.
        - Updating the recipe's output schema
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :param recipe_name: str: Name of the recipe.
    
    :param recipe_datasets_connection_type: str: Connection type of the datasets connected
        to the recipe (inputs and outputs). 
            - Examples: 'Filesystem', 'SQL', 'Snowflake', 'PostgreSQL', 'BigQuery', 'S3', ...
    
    :param recipe_engines_priority: list: List of the engines to prioritize in the process of imputing an
        engine to the recipe. Its values should be ordered by decreasing priority.
            - Example: ['SQL', 'SPARK', 'DSS'] means that 'SQL' should be prioritized over 
            'SPARK' and 'DSS' if they are available.
    
    :param recipe_spark_configuration: string: Name of the recipe's spark configuration, if some needs to be set.
        Available spark configurations can be found by going in a recipe 'Advanced' settings.
    """
    check_object_is_project(project)
    # Engine update:
    available_engines = get_recipe_available_engines(project, recipe_name)
    recipe_engine = [engine for engine in recipe_engines_priority if engine in available_engines][0]
    if recipe_datasets_connection_type in ["Redshift", "Synapse", "BigQuery"]:
        recipe_engine = "SQL"
    if recipe_engine == "SPARK":
        if recipe_spark_configuration:
            set_spark_configuration_on_recipe(project, recipe_name, recipe_spark_configuration)
    switch_recipe_engine(project, recipe_name, recipe_engine)
    
    # Recipe outputs schema's update:
    update_recipe_ouput_schema(project, recipe_name)
    pass


def set_spark_configuration_on_recipe(project: DSSProject, recipe_name: str, new_spark_configuration: str):
    """
    Sets the spark configuration of a recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param new_spark_configuration: string: Name of the recipe's spark configuration.
        Available spark configurations can be found by going in a recipe 'Advanced' settings.
    """
    ALLOWED_RECIPE_TYPES = ["shaker", "sampling", "grouping", "distinct", "window", "join",
                            "fuzzyjoin", "split", "topn", "sort", "pivot", "vstack", "pyspark"]
    check_object_is_project(project)
    print("Setting spark configuration '{}' on recipe '{}' ...".format(new_spark_configuration, recipe_name))
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_type = recipe_settings.type
    if recipe_type in ["shaker"]:
        recipe_settings.recipe_settings["params"]["engineParams"]["spark"]["sparkConfig"]["inheritConf"] = new_spark_configuration
    elif recipe_type in ["sampling"]:
        recipe_settings.recipe_settings["params"]["engineParams"]["sparkSQL"]["sparkConfig"]["inheritConf"] = new_spark_configuration
    elif recipe_type in ["grouping", "distinct", "window", "join", "fuzzyjoin", "split", "topn", "sort", "pivot", "vstack"]:
        recipe_payload = recipe_settings.get_json_payload()
        recipe_payload["engineParams"]["sparkSQL"]["sparkConfig"]["inheritConf"] = new_spark_configuration
        recipe_settings.set_json_payload(recipe_payload)
    elif recipe_type == "pyspark":
        recipe_settings.recipe_settings["params"]["sparkConfig"]["inheritConf"] = new_spark_configuration
    else:
        log_message = f"Handling recipes of type '{recipe_type}' is not supported by this function. "\
            f"Please choose a recipe type in '{ALLOWED_RECIPE_TYPES}'"
        raise ValueError(log_message)
    recipe_settings.save()
    print("Spark configuration '{}' successfully set on recipe '{}'!".format(new_spark_configuration, recipe_name))
    pass


def set_filter_expression_on_visual_recipe(project: DSSProject, recipe_name: str, filter_scope:str, formula_expression:str):
    """
    Sets a visual recipe pre/post-filter expression, with a DSS formula.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param filter_scope: str: Scope of the filter. Available options are:
        - 'pre_filter': if you want to set a pre-filter on the recipe.
            DISCLAIMER: Only the recipes ["grouping", "distinct", "window", "split", "topn", "sort", "pivot"] are 
            compatible with this option.
        - 'post_filter': if you want to set a post-filter on the recipe.
            DISCLAIMER: Only the recipes ["grouping", "distinct", "window", "join", "geojoin", "vstack"] are 
            compatible with this option.
    :param formula_expression: str: Expression of the formula leading to the computed column, following the 
    DSS formula language (https://doc.dataiku.com/dss/latest/formula/index.html).
    """
    SCOPE_ALLOWED_RECIPE_TYPES = {
        "pre_filter": ["grouping", "distinct", "window", "split", "topn", "sort", "pivot"],
        "post_filter": ["grouping", "distinct", "window", "join", "geojoin", "vstack"]
        }
    if filter_scope == "pre_filter":
        filter_prefix = "pre"
    elif filter_scope == "post_filter":
        filter_prefix = "post"
    else:
        log_message = f"You set a wrong value for the parameter 'filter_scope'! Actual value is '{filter_scope}' and "\
        f"allowed values are ['pre_filter', 'post_filter]."
        raise ValueError(log_message)
    allowed_recipe_types = SCOPE_ALLOWED_RECIPE_TYPES[filter_scope]
    UI_DATA_SETTINGS = {'mode': 'CUSTOM',
                        '$latestOperator': '&&',
                        '$filterOptions': 'CUSTOM',
                        'conditions': []
                       }
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_payload = recipe_settings.get_json_payload()
    recipe_type = recipe_settings.type
    
    if recipe_type not in allowed_recipe_types:
        log_message = f"Handling recipes of type '{recipe_type}' is not supported by this function for "\
            f"'{filter_prefix}-filters'. Please choose a recipe type in '{allowed_recipe_types}'"
        raise ValueError(log_message)
    
    print(f"Updating the visual recipe '{recipe_name}' {filter_prefix} filter expression ...")
    if f"{filter_prefix}Filter" not in recipe_payload.keys():
        recipe_payload[f"{filter_prefix}Filter"] = {
            "enabled": True
        }
    if "enabled" not in recipe_payload[f"{filter_prefix}Filter"].keys():
        recipe_payload[f"{filter_prefix}Filter"]["enabled"] = True
    
    recipe_payload[f"{filter_prefix}Filter"]["uiData"] = UI_DATA_SETTINGS
    recipe_payload[f"{filter_prefix}Filter"]["distinct"] = False
    filter_is_disabled = (not recipe_payload[f"{filter_prefix}Filter"]["enabled"])
    if filter_is_disabled:
        recipe_payload[f"{filter_prefix}Filter"]["enabled"] = True
    recipe_payload[f"{filter_prefix}Filter"]["expression"] = formula_expression
    recipe_settings.set_json_payload(recipe_payload)
    recipe_settings.save()
    print(f"Visual recipe '{recipe_name}' {filter_prefix} filter expression successfully updated!")
    pass


def get_recipe_description(project: DSSProject, recipe_name: str, description_type: str="short_description"):
    """
    Retrieves the description of a project recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param description_type: str: The type of description to modify.
        The available options are:
            - 'short_description': To enrich the recipe short description.
            - 'long_description': To enrich the recipe long description.
    :returns: recipe_description: str: Description of the project recipe.
    """
    check_object_is_project(project)
    recipe_settings, _ = get_recipe_settings_and_dictionary(project, recipe_name)
    if description_type == "short_description":
        recipe_description = recipe_settings.short_description 
    else:
        recipe_description = recipe_settings.description
    return recipe_description


def modify_recipe_description(project: DSSProject, recipe_name: str, description_modification: str,
                               description_type: str="short_description", type_of_modification: str="replace_all",
                               descriptions_separator: str="\n\n"):
    """
    Modifies the description of a project recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param description_modification: str: The description to modify the recipe with.
    :param description_type: str: The type of description to modify.
        The available options are:
            - 'short_description': To enrich the recipe short description.
            - 'long_description': To enrich the recipe long description.
    :param type_of_modification: str: The type of description modification to apply.
        The available options are:
            - 'replace_all': If you want to replace the existing description.
            - 'add_before': If you want to add your description before the existing description.
            - 'add_after': If you want to add your description after the existing description.
    :param descriptions_separator: str: The separator to use between each description.
        This only applies when 'type_of_modification' equals to 'add_before' or 'add_after'.
    """
    check_object_is_project(project)
    recipe_settings, _ = get_recipe_settings_and_dictionary(project, recipe_name)
    existing_description = get_recipe_description(project, recipe_name, description_type)
    if not existing_description:
        existing_description = ""
        
    if type_of_modification == "replace_all":
        new_description = description_modification
    
    elif type_of_modification == "add_before":
        new_description = f"{description_modification}{descriptions_separator}{existing_description}"
    
    elif type_of_modification == "add_after":
        new_description = f"{existing_description}{descriptions_separator}{description_modification}"
    
    if description_type == "short_description":
        recipe_settings.short_description = new_description
    else:
        recipe_settings.description = new_description
    recipe_settings.save()