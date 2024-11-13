from .recipe_commons import (get_recipe_input_datasets,
                             get_recipe_settings_and_dictionary)
from dku_utils.projects.datasets.dataset_commons import (get_dataset_schema,
                                        extract_dataset_schema_information)
from dku_utils.type_checking import DSSProject, check_object_is_project


def define_window_recipe_aggregations(project: DSSProject, recipe_name:str, column_aggregations_mapping: dict, retrieved_columns_selection_mode: str="EXPLICIT"):
    """
    Updates the aggregations set in a window recipe.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :param recipe_name: str: Name of the recipe.
    
    :param column_aggregations_mapping: dict: Mapping between the columns and the list of aggregations to apply to each one.
        - Example: {'column_1': ['value', 'min', 'max'], 'column_2': ['value', 'avg', 'sum']} 
        - NOTE: use the aggregation 'value', from WINDOW_POSSIBLE_AGGREGATIONS if you want the column value to be retrieved.
            <-> Equivalent of the 'Retrieve' in the visual recipe.
        - NOTE: All columns not present in column_aggregations_mapping.keys() will:
            - Have their aggregations disabled. 
            - Not have their values retrieved --> set at least the aggregation 'column_xyz': ['value']
                if you want to keep the column 'column_xyz' values.
    
    :param retrieved_columns_selection_mode: str: Sets whether:
        -  If the value equals 'EXPLICIT': Only the explicitely selected columns should be retrieved [Default behavior]
        -  If the value equals 'ALL': All the columns should be retrieved.
    """
    WINDOW_POSSIBLE_AGGREGATIONS = ["last", "lagDiff", "max", "column", "count", "$idx", "sum",
                              "concat", "type",  "lead", "concatDistinct",  "min", "avg",
                              "lag", "$selected", "stddev", "value", "leadDiff", "first"]
    WINDOW_DEFAULT_AGGREGATIONS = ["column", "$idx", "type"]
    WINDOW_AGGREGATIONS_TO_CHANGE = [aggregation for aggregation in WINDOW_POSSIBLE_AGGREGATIONS
                                     if aggregation not in WINDOW_DEFAULT_AGGREGATIONS]
    ALLOWED_COLUMNS_SELECTION_MODES = ["EXPLICIT", "ALL"]
    check_object_is_project(project)
    
    if retrieved_columns_selection_mode not in ALLOWED_COLUMNS_SELECTION_MODES:
        log_message = f"You set a wrong value to the parameter 'retrieved_columns_selection_mode':"\
            f"allowed values are '{ALLOWED_COLUMNS_SELECTION_MODES}'"
        raise ValueError(log_message)
    
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_payload = recipe_settings.get_json_payload()
    recipe_input_dataset_name = get_recipe_input_datasets(project, recipe_name)[0]
    recipe_input_dataset_schema = get_dataset_schema(project, recipe_input_dataset_name)
    recipe_input_columns, recipe_input_column_datatypes = extract_dataset_schema_information(recipe_input_dataset_schema)
    column_indexes = range(len(recipe_input_columns))
    column_with_aggregations = column_aggregations_mapping.keys()
    window_new_aggregations = []
    for column_index, column_name, column_datatype in zip(column_indexes, recipe_input_columns, recipe_input_column_datatypes):
        column_aggregation_settings = {
            "column": column_name,
            "$idx": column_index,
            "type": column_datatype
        }
        if column_name in column_with_aggregations:
            column_aggregations_to_enable = column_aggregations_mapping[column_name]
            for aggregation in WINDOW_AGGREGATIONS_TO_CHANGE:
                if aggregation in column_aggregations_to_enable:
                    column_aggregation_settings[aggregation] = True
                else:
                    column_aggregation_settings[aggregation] = False
        else:
            for aggregation in WINDOW_AGGREGATIONS_TO_CHANGE:
                column_aggregation_settings[aggregation] = False            
        window_new_aggregations.append(column_aggregation_settings)
    
    recipe_payload["values"] = window_new_aggregations
    recipe_payload["retrievedColumnsSelectionMode"] = retrieved_columns_selection_mode
    recipe_settings.set_json_payload(recipe_payload)
    recipe_settings.save()
    print("Window recipe '{}' successfully updated !".format(recipe_name))
    pass


def generate_window_recipe_orders(column_names: list, columns_bool_descending_mapping: list):
    """
    Computes the order payload part of a single window recipe's window.

    :param column_names: list: List of columns.
        Example: ['column_1', 'column_2', 'column_3']
    
    :param columns_bool_descending_mapping: list: List of boolean indicating if each column
        present in 'column_names' should be ordered descending  or not.
        Example: [True, False, True]

    :returns: window_orders: list: List containing window orders 
    """
    window_orders = []
    for column_name, bool_descending_mapping in zip(column_names, columns_bool_descending_mapping):
        window_orders.append({'column': column_name, 'desc': bool_descending_mapping})
    return window_orders


def set_window_orders(project: DSSProject, recipe_name: str, column_names: list, columns_bool_descending_mapping: list,
                      window_index: int=0):
    """
    Updates the 'WINDOW ORDER' section of a single window recipe's window.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :param recipe_name: str: Name of the recipe.
    
    :param column_names: list: List of columns.
        Example: ['column_1', 'column_2', 'column_3']
    
    :param columns_bool_descending_mapping: list: List of boolean indicating if each column
        present in 'column_names' should be ordered descending  or not.
        Example: [True, False, True]
    
    :param window_index: int: Index of the window in the recipe.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_payload = recipe_settings.get_json_payload()
    window_orders = generate_window_recipe_orders(column_names, columns_bool_descending_mapping)
    recipe_payload["windows"][window_index]["orders"] = window_orders
    recipe_settings.set_json_payload(recipe_payload)
    recipe_settings.save()
    pass


def set_row_based_window_frame(project: DSSProject, recipe_name: str, number_of_rows_before=None, number_of_rows_after=None,
                               window_index: int=0):
    """
    Updates the 'WINDOW FRAME' section of a window recipe's window, based on its rows, by setting the
        'Limit preceding rows' and 'Limit following rows' options.
        
        DISCLAIMER: This function only works in the context of a window frame set with the option
            'Limit the number of preceding/following rows'. 
            <-> It won't work with the option 'Limit window on a value range of the order column'.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :param recipe_name: str: Name of the recipe.
    
    :param number_of_rows_before: int: Number of rows to include in the window, before each row.
        Leave it to 'None' if you don't want to set the 'Limit preceding rows' option.
    
    :param number_of_rows_after: int: Number of rows to include in the window, after each row.
        Leave it to 'None' if you don't want to set the 'Limit following rows' option.
    
    :param window_index: int: Index of the window in the recipe.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_payload = recipe_settings.get_json_payload()
    
    order_has_been_set = recipe_payload["windows"][window_index]["enableOrdering"]
    
    if order_has_been_set:
        recipe_payload["windows"][window_index]["enableLimits"] = True

        if number_of_rows_before is None:
            recipe_payload["windows"][window_index]["limitPreceding"] = False
            recipe_payload["windows"][window_index]["precedingRows"] = 0
        else:
            recipe_payload["windows"][window_index]["limitPreceding"] = True
            recipe_payload["windows"][window_index]["precedingRows"] = number_of_rows_before

        if number_of_rows_after is None:
            recipe_payload["windows"][window_index]["limitFollowing"] = False
            recipe_payload["windows"][window_index]["followingRows"] = 0
        else:
            recipe_payload["windows"][window_index]["limitFollowing"] = True
            recipe_payload["windows"][window_index]["followingRows"] = number_of_rows_after

        recipe_settings.set_json_payload(recipe_payload)
        recipe_settings.save()
    else:
        log_message = f"No 'ORDER COLUMNS' has been set on the widow recipe '{recipe_name}'. "\
        "Please set an order first, either manually or using the function 'set_window_orders'."
        raise Exception(log_message)
    pass


def set_lag_or_lead_offset_on_window_recipe_columns(project, recipe_name: str, column_names: list,
                                                    type_of_aggregations: list, lead_or_lag_offset: str):
    """
    Sets 'lag' and/or 'lead' aggregation offsets on a window recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param column_names: list: Name of the columns on which the 'lead' or 'lag' aggregations should be applied.
    :param type_of_aggregations: list: Type of aggregations to apply on the columns. Available choices are:
        - 'lag': 'lag' aggregations will be computed.
        - 'lead': 'lead' aggregations will be computed.
    :param lead_or_lag_offset: str: Precise the offsets to apply in the 'lag' and/or 'lead' aggredations. Use:
        - '1' to get the preceding/following
        - '1,2' for the two preceding/following
        - Etc...
    """
    print(f"Editing '{type_of_aggregations}' for columns '{column_names}' in  window recipe '{recipe_name}' ...")
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_payload = recipe_settings.get_json_payload()
    window_column_aggregation_settings = recipe_payload["values"]
    new_window_column_aggregation_settings = []
    for column_aggregation_settings in window_column_aggregation_settings:
        column_name = column_aggregation_settings["column"]
        if column_name in column_names:
            if "lag" in type_of_aggregations:
                column_aggregation_settings["lagValues"] = f"{lead_or_lag_offset}"
            if "lead" in type_of_aggregations:
                column_aggregation_settings["leadValues"] = f"{lead_or_lag_offset}"
        new_window_column_aggregation_settings.append(column_aggregation_settings)
        recipe_payload["values"] = new_window_column_aggregation_settings
    recipe_settings.set_json_payload(recipe_payload)
    recipe_settings.save()
    print("Window recipe '{}' successfully updated !".format(recipe_name))
    pass