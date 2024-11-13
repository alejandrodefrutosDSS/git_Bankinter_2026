from .recipe_commons import get_recipe_settings_and_dictionary
from dku_utils.type_checking import DSSProject, check_object_is_project
from dku_utils.projects.datasets.dataset_commons import create_dataset_in_connection
from dku_utils.projects.project_commons import get_all_project_dataset_names
from typing import List, Optional


def instantiate_prepare_recipe(project, recipe_name, recipe_input_dataset_name,
                               recipe_output_dataset_name, connection_name):
    """
    Instantiates a prepare recipe in the flow.
    
    :param project: dataikuapi.dss.project.DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_input_dataset_name: str: Name of the dataset that must be the recipe input.
    :param recipe_output_dataset_name: str: Name of the dataset that must be the recipe output.
    :param connection_name: str: Name of the recipe output dataset connection.
    """
    print("Creating prepare recipe '{}' ...".format(recipe_name))
    builder = project.new_recipe(name=recipe_name, type="prepare")
    builder.with_input(recipe_input_dataset_name)
    project_datasets = get_all_project_dataset_names(project)
    if recipe_output_dataset_name not in project_datasets:   
        create_dataset_in_connection(project, recipe_output_dataset_name, connection_name)
    builder.with_output(recipe_output_dataset_name)
    builder.build()
    print("Prepare recipe '{}' sucessfully created!".format(recipe_name))
    pass

def compute_prepare_move_step(columns_to_move: List[str], 
                              relative_position: str, 
                              reference_column: Optional[str] = None)-> dict:
    """
    Computes the JSON associated with a 'Move' step.

    :param columns_to_move: List[str]: List of all the columns to move.
    :param relative_position: str: Position of the column to move: either 
                                    "BEFORE_COLUMN", "AT_START", "AFTER_COLUMN",
                                      or "AT_END"
    :param reference_column: str: If relative_position in ["BEFORE_COLUMN", 
                                    "AFTER_COLUMN"],name of the column next to 
                                    which the other column is moved.
    
    :returns: move_step: dict: JSON of the prepare 'Move' step.
    """
    move_step = {}

    if relative_position not in ["BEFORE_COLUMN", "AT_START", "AFTER_COLUMN", 
                                 "AT_END"]:
        raise ValueError("The value of the relative position is not valid. The \
                         value must be either 'BEFORE_COLUMN', 'AT_START', \
                         'AFTER_COLUMN', or 'AT_END'")
        
    else:
        if len(columns_to_move) == 1:
            columns_to_apply = "SINGLE_COLUMN"
        else:
            columns_to_apply = "COLUMNS"
        
        if relative_position in ["AT_START", "AT_END"]:
            reference_column = ""
        
        move_step = {'preview': False,
                     'metaType': 'PROCESSOR',
                     'disabled': False,
                     'type': 'ColumnReorder',
                     'params': {'referenceColumn': reference_column,
                                  'columns': columns_to_move,
                                  'reorderAction': relative_position,
                                  'appliesTo': columns_to_apply},
                     'alwaysShowComment': False}

    return move_step

def compute_prepare_round_step(columns: List[str]=[], rounding_mode: str="ROUND", significant_digits: int=0, decimal_places: int=0):
    """
    Computes the JSON associated with a 'Round' step.

    :param columns: List[str]: List of all the columns where to round numbers.
    :param rounding_mode: str: Mode of the round method: either "ROUND", "FLOOR", or "CEIL"
    :param significant_digits: int: Significant digits. Control the precision of the number.
    :param decimal_places: int: Decimal places. How many numbers to show after the decimal point.
    
    :returns: round_step: dict: JSON of the prepare 'Round' step.
    """
    round_step = {}

    if rounding_mode not in ["ROUND", "FLOOR", "CEIL"]:
        print("The value of the rounding mode is not valid.")
        
    elif len(columns) == 1:
        round_step = {'preview': False,
                 'metaType': 'PROCESSOR',
                 'disabled': False,
                 'type': 'RoundProcessor',
                 'params': {'mode': rounding_mode,
                  'places': decimal_places,
                  'columns': columns,
                  'precision': significant_digits,
                  'appliesTo': "SINGLE_COLUMN"},
                 'alwaysShowComment': False}
        
    elif len(columns) > 1:
        round_step = {'preview': False,
                 'metaType': 'PROCESSOR',
                 'disabled': False,
                 'type': 'RoundProcessor',
                 'params': {'mode': rounding_mode,
                  'places': decimal_places,
                  'columns': columns,
                  'precision': significant_digits,
                  'appliesTo': "COLUMNS"},
                 'alwaysShowComment': False}           
            
    return round_step

def compute_prepare_fill_empty_cells_step(columns: List[str]=[], value_to_fill_with: str="0"):
    """
    Computes the JSON associated with a 'Fill Empty Cells' step.

    :param columns: List[str]: List of all the columns where to fill the empty cells.
    :param value_to_fill_with: str: Value to fill in the empty cells.
    
    :returns: fill_empty_cells_step: dict: JSON of the prepare 'Fill empty cells' step.
    """
    fill_empty_cells_step = {}

    if len(columns) == 1:
        fill_empty_cells_step = {'preview': False,
                    'metaType': 'PROCESSOR',
                    'disabled': False,
                    'type': 'FillEmptyWithValue',
                    'params': {
                        "columns": columns,
                        "appliesTo": "SINGLE_COLUMN",
                        "value": value_to_fill_with
                        },
                    'alwaysShowComment': False}
    
    elif len(columns) > 1:
        fill_empty_cells_step = {'preview': False,
                    'metaType': 'PROCESSOR',
                    'disabled': False,
                    'type': 'FillEmptyWithValue',
                    'params': {
                        "columns": columns,
                        "appliesTo": "COLUMNS",
                        "value": value_to_fill_with
                        },
                    'alwaysShowComment': False}

    return fill_empty_cells_step


def compute_prepare_rename_step(column_to_rename: str, new_column_name: str):
    """
    Computes the JSON associated with a prepare 'rename' step.

    :param column_to_rename: str: Name of the column to rename.
    :param new_column_name: str: New name the column to rename should have. 
    
    :returns: rename_step: dict: JSON of the prepare 'rename' step.
    """
    rename_step = {"preview": False,
                   "metaType": "PROCESSOR",
                   "disabled": False,
                   "type": "ColumnRenamer",
                   "params": {"renamings": [
                       {"from": "{}".format(column_to_rename),
                        "to": "{}".format(new_column_name)}]},
                   "alwaysShowComment": False}
    return rename_step


def compute_prepare_formula_step(column_name: str, formula_expression: str):
    """
    Computes the JSON associated with a column applying a prepare recipe formula.

    :param column_to_rename: str: Name of the column to generate.
    :param formula_expression: str: Expression of the formula leading to the computed column, following the 
        DSS formula language (https://doc.dataiku.com/dss/latest/formula/index.html).
    
    :returns: formula_step: dict: JSON of the prepare 'formula' step.
    """
    formula_step = {'preview': False,
                    'metaType': 'PROCESSOR',
                    'disabled': False,
                    'type': 'CreateColumnWithGREL',
                    'params': {
                        'expression': formula_expression,
                        'column': column_name
                        },
                    'alwaysShowComment': False}
    return formula_step


def compute_prepare_keep_or_delete_step(columns_of_interest: list, bool_keep_columns: bool):
    """
    Computes the JSON associated with a keep/delete prepare recipe step.

    :param columns_of_interest: list: Name of the column to generate.
    :param bool_keep_columns: bool: Parameter precising if the columns mentioned in 
        'columns_of_interest' should be kept (if it is equal to 'True')
        or deleted (if it is equal to 'False').
    
    :returns: formula_step: dict: JSON of the prepare 'keep/delete' step.
    """
    keep_or_delete_step = {'preview': False,
                           'metaType': 'PROCESSOR',
                           'disabled': False,
                           'type': 'ColumnsSelector',
                           'params': {'columns': columns_of_interest,
                                      'keep': bool_keep_columns,
                                      'appliesTo': 'COLUMNS'},
                           'alwaysShowComment': False}
    return keep_or_delete_step


def reset_prepare_recipe_steps(project: DSSProject, recipe_name: str):
    """
    Reset all steps of a prepare recipe .

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param :recipe_name: str: Name of the plugin recipe.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_json_payload = recipe_settings.get_json_payload()
    recipe_json_payload["steps"] = []
    recipe_settings.set_json_payload(recipe_json_payload)
    recipe_settings.save()
    pass


def add_step_in_prepare_recipe(project: DSSProject, recipe_name: str, step: dict, step_comment: str="",
                               show_step_comment: bool=True):
    """
    Adds a step in a prepare recipe .

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param :recipe_name: str: Name of the plugin recipe.
    :param :step: dict: Definition of the prepare recipe step in JSON format.
    :param :step_comment: str: Comment to link to the recipe step.
    :param :show_step_comment: bool: Parameter precising whether the step comment should be displayed or not
        in the recipe.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_json_payload = recipe_settings.get_json_payload()
    step["alwaysShowComment"] = show_step_comment
    if step_comment != "":
        step["comment"] = step_comment
    recipe_json_payload["steps"].append(step)
    recipe_settings.set_json_payload(recipe_json_payload)
    recipe_settings.save()
    pass


def compute_prepare_recipe_group_step(group_step_label: str, group_sub_steps: list, group_step_comment: str="",
                                      show_group_step_comment: bool=True):
    """
    Computes the JSON associated with a prepare recipe grouping step.

    :param :group_step_label: str: Label to link to the group step.
    :param :group_sub_steps: list: List containing all the group sub-steps, each being in JSON format.
    :param :group_step_comment: str: Comment to link to the group step.
    :param :show_group_step_comment: bool: Parameter precising whether the group step comment should be displayed or not
        in the recipe.
    
    :returns: group_step: dict: JSON of the prepare grouping step.
    """
    group_step = {'metaType': 'GROUP',
                       'name': group_step_label,
                       'steps': group_sub_steps,
                       'alwaysShowComment': show_group_step_comment,
                       'preview': False,
                       'disabled': False}
    if group_step_comment != "":
        group_step["comment"] = group_step_comment
    return group_step


def compute_prepare_recipe_columns_percent_of_total_steps(columns_of_interest: list,
                                                          name_for_columns_sum: str,
                                                          grouped_step_label: str,
                                                          bool_remove_columns_sum: bool,
                                                          bool_remove_initial_columns: bool):
    """
    Takes a set of numerical columns to scale them by their sum. The computed column values then corresponds to the 
        percent of their total. All steps leading to this computation are grouped together in a prepare grouping step.

    :param :columns_of_interest: list: The set of columns to scale by their sum.
    
    :param :name_for_columns_sum: str: Name of the column corresponding to the sum of all columns
        defined in 'columns_of_interest'.
    
    :param :grouped_step_label: str: Label to link to the group step containing all computation sub-steps.
    
    :param :bool_remove_columns_sum: bool: Parameter precising whether the column 'name_for_columns_sum' should be removed
        after the computation or not.
    
    :param :bool_remove_initial_columns: bool: Parameter precising whether the columns defined in 
        'bool_remove_initial_columns' should be removed  after the computation or not.

    :returns: group_step: dict: JSON of the prepare grouping step.
    """
    all_steps = []
    total_column_expression = ""
    columns_last_index = len(columns_of_interest) - 1
    columns_percent_of_total_steps = []
    for column_index, column_name in enumerate(columns_of_interest):
        if column_index != columns_last_index:
            column_expression_end = " + "
        else:
            column_expression_end = ""
        total_column_expression += "if(isNonBlank({0}), {0}, 0){1}".format(column_name, column_expression_end)
        column_percent_of_total_expression = "if(isNonBlank({0}), {0}/{1}, 0)".format(column_name, name_for_columns_sum)
        column_percent_of_total_name = "{}_fraction".format(column_name)
        column_percent_of_total_step = compute_prepare_formula_step(column_percent_of_total_name,
                                                                    column_percent_of_total_expression)
        columns_percent_of_total_steps.append(column_percent_of_total_step)
    total_column_formula_step = compute_prepare_formula_step(name_for_columns_sum, total_column_expression)
    
    all_steps.append(total_column_formula_step)
    all_steps += columns_percent_of_total_steps
    columns_to_remove = []
    if bool_remove_initial_columns:
        columns_to_remove += columns_of_interest
    if bool_remove_columns_sum:
        columns_to_remove.append(name_for_columns_sum)
    if bool_remove_initial_columns or bool_remove_columns_sum:
        columns_deletion_step = compute_prepare_keep_or_delete_step(columns_to_remove, False)
        all_steps.append(columns_deletion_step)
    
    recipe_columns_percent_of_total_group_step = compute_prepare_recipe_group_step(grouped_step_label,
                                                                                   all_steps,
                                                                                   group_step_comment="",
                                                                                   show_group_step_comment=True)
    return recipe_columns_percent_of_total_group_step

def compute_prepare_date_difference_step(origin_date_column: str, end_date_column: str, output_column_name: str,
                                         time_unit: str="DAYS"):
    """
    Computes the JSON associated with a prepare 'DateDifference' step.

    :param origin_date_column: str: Name of the origin date column.
    :param end_date_column: str: Name of the end date column.
    :param output_column_name: str: Name of the output column.
    :param time_unit: str: Unit of the output difference (default is 'DAYS').

    :returns: date_difference_step: dict: JSON of the prepare 'DateDifference' step.
    """
    date_difference_step = {
        "preview": False,
        "metaType": "PROCESSOR",
        "disabled": False,
        "type": "DateDifference",
        "params": {
            "input1": origin_date_column,
            "input2": end_date_column,
            "output": output_column_name,
            "outputUnit": time_unit,
            "compareTo": "COLUMN",
            "reverse": False
        },
        "alwaysShowComment": False
    }
    return date_difference_step