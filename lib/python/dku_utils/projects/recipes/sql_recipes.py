from dku_utils.type_checking import DSSProject
import pandas as pd
from .recipe_commons import get_recipe_settings_and_dictionary
from dku_utils.projects.recipes.recipe_commons import get_recipe_settings_and_dictionary
from dku_utils.type_checking import DSSProject, check_object_is_project
from dku_utils.projects.datasets.dataset_commons import create_dataset_in_connection


def instantiate_sql_recipe(project: DSSProject, recipe_name:str , recipe_type:str , recipe_input_dataset_name: str,
                             recipe_output_dataset_name:str , connection_name:str ):
    """
    Instantiates a sql recipe in the flow.
    
    :param project: dataikuapi.dss.project.DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_type: str: 'sql_script' or 'sql_query'
    :param recipe_input_dataset_name: str: Name of the dataset that must be the recipe input.
    :param recipe_output_dataset_name: str: Name of the dataset that must be the recipe output.
    :param :connection_name: str: Name of the recipe output dataset connection.
    """
    assert recipe_type in ['sql_script', 'sql_query']
    print("Creating sql recipe '{}' ...".format(recipe_name))
    builder = project.new_recipe(name=recipe_name, type=recipe_type)
    builder.with_input(recipe_input_dataset_name)    
    create_dataset_in_connection(project, recipe_output_dataset_name, connection_name)
    builder.with_output(recipe_output_dataset_name)
    builder.build()
    print("SQL recipe '{}' sucessfully created!".format(recipe_name))
    pass


def set_sql_recipe_inputs(project: DSSProject, recipe_name: str, recipe_inputs: list):
    """
    Sets the inputs of a sql recipe. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_inputs: list: List containing all recipe inputs.
    """
    check_object_is_project(project)
    print("Setting datasets '{}' as sql recipe '{}' inputs ...".format(recipe_inputs, recipe_name))
    recipe_settings, recipe_settings_dict = get_recipe_settings_and_dictionary(project, recipe_name, True)
    new_python_recipe_input_settings = []
    for dataset_name in recipe_inputs:
        new_python_recipe_input_settings.append({'ref': dataset_name, 'deps': []})
    recipe_settings_dict["inputs"]["main"]["items"] = new_python_recipe_input_settings
    recipe_settings.recipe_settings = recipe_settings_dict
    recipe_settings.save()
    print("SQL recipe '{}' inputs successfully set!".format(recipe_inputs, recipe_name))
    pass


def get_sql_recipe_script(project: DSSProject, recipe_name: str):
    """
    Retrieves the script of a python recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    
    :returns: recipe_sql_script: str: The python recipe script.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_sql_script = recipe_settings.get_code()
    return recipe_sql_script


def set_sql_recipe_script(project: DSSProject, recipe_name: str, new_script: str):
    """
    Sets the script of an sql recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param new_script: str: The new script to set in the recipe.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_settings.set_payload(new_script)
    recipe_settings.save()
    print('SQL recipe overwritten with the new script')
    pass
