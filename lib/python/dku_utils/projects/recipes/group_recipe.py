import dataikuapi
from .recipe_commons import get_recipe_settings_and_dictionary
from dku_utils.projects.datasets.dataset_commons import create_dataset_in_connection
from dku_utils.type_checking import DSSProject, check_object_is_project


def instantiate_group_recipe(project: DSSProject, recipe_name: str, recipe_input_dataset_name: str,
                             recipe_output_dataset_name: str, connection_name: str):
    """
    Instantiates a group recipe in the flow.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_input_dataset_name: str: Name of the dataset that must be the recipe input.
    :param recipe_output_dataset_name: str: Name of the dataset that must be the recipe output.
    :param :connection_name: str: Name of the recipe output dataset connection.
    """
    check_object_is_project(project)
    print("Creating group recipe '{}' ...".format(recipe_name))
    builder = dataikuapi.GroupingRecipeCreator(recipe_name, project)
    builder.with_input(recipe_input_dataset_name)    
    create_dataset_in_connection(project, recipe_output_dataset_name, connection_name)
    builder.with_output(recipe_output_dataset_name)
    builder.build()
    print("Group recipe '{}' sucessfully created!".format(recipe_name))
    pass


def define_group_recipe_aggregation_key(project: DSSProject, recipe_name: str, group_key: list, replace_existing_key: bool):
    """
    Changes the aggregation key of a group recipe. It can either add a column in the group key
        or replace the existing group key.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param group_key: list: List of the column names part of the group key update. 
    :param replace_existing_key: bool: Precise if you want to replace the existing group key or instead add columns
        mentioned in 'group_key' to the current recipe aggregation key.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    if replace_existing_key:
        recipe_settings.clear_grouping_keys()
    for column in group_key:
        recipe_settings.add_grouping_key(column)
    recipe_settings.save()
    pass


def define_group_recipe_aggregations(project: DSSProject, recipe_name: str, column_aggregations_mapping: dict,
                                     bool_compute_global_count: bool):
    """
    Set aggregations done by a group recipe.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param column_aggregations_mapping: dict: Mapping between the columns and the list of aggregations to apply to each one.
        Example: {'column_1': ['min', 'concat'], 'column_2': ['avg', 'sum']} 
    :param bool_compute_global_count: bool: Precise whether you want to compute the global count of the recipe or not.
    """
    POSSIBLE_AGGREGATIONS = ["countDistinct", "min", "max", "avg", "sum", "stddev",
                             "count", "first", "last", "concat", "concatDistinct"]
    check_object_is_project(project)
    print("Updating recipe '{}' aggregations ...".format(recipe_name))
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_json_payload = recipe_settings.get_json_payload()
    recipe_aggregations = []
    for column in column_aggregations_mapping.keys():
        column_asked_aggregations = column_aggregations_mapping[column]
        recipe_column_settings = recipe_settings.get_or_create_column_settings(column)
        for aggregation in POSSIBLE_AGGREGATIONS:
            if aggregation in column_asked_aggregations:
                recipe_column_settings[aggregation] = True
            else:
                recipe_column_settings[aggregation] = False
        recipe_aggregations.append(recipe_column_settings)
    recipe_json_payload["values"] = recipe_aggregations
    recipe_settings.set_json_payload(recipe_json_payload)
    recipe_settings.set_global_count_enabled(bool_compute_global_count)
    recipe_settings.save()
    print("Recipe '{}' aggregations updated !".format(recipe_name))
    pass


def override_group_recipe_output_column_names(project: DSSProject, recipe_name: str, column_name_overrides: dict):
    """
    Overrides the names of the output columns of a group recipe.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param column_name_overrides: dict: Columns overrides, with format:
        {'default_name_from_the_group_recipe_1': 'new_name_1',
        'default_name_from_the_group_recipe_2': 'new_name_2'}
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_json_payload = recipe_settings.get_json_payload()
    recipe_json_payload["outputColumnNameOverrides"] = column_name_overrides
    recipe_settings.set_json_payload(recipe_json_payload)
    recipe_settings.save()
    pass


def change_group_recipe_concatenation(project: DSSProject, recipe_name: str, column_name: str, bool_activate_concatenation: bool,
                                      separator: str):
    """
    Updates, for one column, the settings related to the 'concat' aggregation of the group recipe

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param column_name: str: Name of the column where we want to change the 'concat' settings.
    :param bool_activate_concatenation: bool: Precise whether 'concat' should be activated or not in the recipe.
    :param separator: str: Precise the values separator that should be used in the concatenation process.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_payload = recipe_settings.get_json_payload()
    recipe_aggregations = recipe_payload["values"]
    
    recipe_new_aggregations = []
    for column_aggregation in recipe_aggregations:
        column_of_interest = column_aggregation["column"]
        if column_of_interest == column_name:
            column_aggregation["concat"] = bool_activate_concatenation
            column_aggregation["concatSeparator"] = separator
        recipe_new_aggregations.append(column_aggregation)
    recipe_payload["values"] = recipe_new_aggregations
    recipe_settings.set_json_payload(recipe_payload)
    recipe_settings.save()
    pass