import pandas as pd
from .recipe_commons import get_recipe_settings_and_dictionary
from dku_utils.python_utils.python_scripts import get_python_script_libraries_import_dataframe
from dku_utils.type_checking import DSSProject, check_object_is_project
from dku_utils.projects.datasets.dataset_commons import create_dataset_in_connection


def instantiate_python_recipe(project, recipe_name, recipe_input_dataset_name,
                             recipe_output_dataset_name, connection_name):
    """
    Instantiates a python recipe in the flow.
    
    :param project: dataikuapi.dss.project.DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_input_dataset_name: str: Name of the dataset that must be the recipe input.
    :param recipe_output_dataset_name: str: Name of the dataset that must be the recipe output.
    :param :connection_name: str: Name of the recipe output dataset connection.
    """
    print("Creating python recipe '{}' ...".format(recipe_name))
    builder = project.new_recipe(name=recipe_name, type="python")
    builder.with_input(recipe_input_dataset_name)    
    create_dataset_in_connection(project, recipe_output_dataset_name, connection_name)
    builder.with_output(recipe_output_dataset_name)
    builder.build()
    print("Python recipe '{}' sucessfully created!".format(recipe_name))
    pass

def set_python_recipe_inputs(project: DSSProject, recipe_name: str, recipe_inputs: list):
    """
    Sets the inputs of a python recipe. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_inputs: list: List containing all recipe inputs.
    """
    check_object_is_project(project)
    print("Setting datasets '{}' as python recipe '{}' inputs ...".format(recipe_inputs, recipe_name))
    recipe_settings, recipe_settings_dict = get_recipe_settings_and_dictionary(project, recipe_name, True)
    new_python_recipe_input_settings = []
    for dataset_name in recipe_inputs:
        new_python_recipe_input_settings.append({'ref': dataset_name, 'deps': []})
    recipe_settings_dict["inputs"]["main"]["items"] = new_python_recipe_input_settings
    recipe_settings.recipe_settings = recipe_settings_dict
    recipe_settings.save()
    print("Python recipe '{}' inputs successfully set!".format(recipe_inputs, recipe_name))
    pass


def set_python_recipe_outputs(project: DSSProject, recipe_name: str, recipe_outputs: list):
    """
    Sets the outputs of a python recipe. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_outputs: list: List containing all recipe output dataset names.
    """
    check_object_is_project(project)
    print("Setting datasets '{}' as python recipe '{}' outputs ...".format(recipe_outputs, recipe_name))
    recipe_settings, recipe_settings_dict = get_recipe_settings_and_dictionary(project, recipe_name, True)
    new_python_recipe_output_settings = []
    for dataset_name in recipe_outputs:
        new_python_recipe_output_settings.append({'ref': dataset_name, 'deps': []})
    recipe_settings_dict["outputs"]["main"]["items"] = new_python_recipe_output_settings
    recipe_settings.recipe_settings = recipe_settings_dict
    recipe_settings.save()
    print("Python recipe '{}' outputs successfully set!".format(recipe_outputs, recipe_name))
    pass


def get_python_recipe_script(project: DSSProject, recipe_name: str):
    """
    Retrieves the script of a python recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    
    :returns: recipe_python_script: str: The python recipe script.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_python_script = recipe_settings.get_code()
    return recipe_python_script


def set_python_recipe_script(project: DSSProject, recipe_name: str, new_script: str):
    """
    Sets the script of a python recipe.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param new_script: str: The new script to set in the recipe.
    """
    check_object_is_project(project)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_settings.set_code(new_script)
    recipe_settings.save()
    pass


def get_python_recipe_library_dependencies_dataframe(project: DSSProject, recipe_name: str):
    """
    Retrieves a DataFrame containing all python modules dependencies for a project's recipe.
        DISCLAIMER: Does not retrieves import done within functions.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    
    :returns: library_dependencies_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing information about all the imports done in the scenario python scripts.
    """
    check_object_is_project(project)
    print("Retrieving recipe '{}.{}' python dependencies ...".format(project.project_key, recipe_name))
    LIBRARY_DEPENDENCIES_SCHEMA = ["recipe_name", "imported_from",
                                  "imported", "all_import_information"]
    
    recipe_python_script = get_python_recipe_script(project, recipe_name)
    library_dependencies_dataframe = get_python_script_libraries_import_dataframe(recipe_python_script)
    library_dependencies_dataframe["recipe_name"] = recipe_name

    if len(library_dependencies_dataframe) == 0:
        library_dependencies_dataframe = pd.DataFrame(columns=LIBRARY_DEPENDENCIES_SCHEMA)
    else: 
        library_dependencies_dataframe = library_dependencies_dataframe[LIBRARY_DEPENDENCIES_SCHEMA]
    print("Recipe '{}.{}' python dependencies successfully retrieved!".format(project.project_key, recipe_name))
    return library_dependencies_dataframe