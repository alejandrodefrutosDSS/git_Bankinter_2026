import dataikuapi
from dku_utils.projects.datasets.dataset_commons import create_dataset_in_connection
from dku_utils.type_checking import DSSProject, check_object_is_project


def instantiate_filter_recipe(project: DSSProject, recipe_name: str, recipe_input_dataset_name: str,
                             recipe_output_dataset_name: str, connection_name: str):
    """
    Instantiates a filter/sampling recipe in the flow.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_input_dataset_name: str: Name of the dataset that must be the recipe input.
    :param recipe_output_dataset_name: str: Name of the dataset that must be the recipe output.
    :param :connection_name: str: Name of the recipe output dataset connection.
    """
    check_object_is_project(project)
    print("Creating filter/sampling recipe '{}' ...".format(recipe_name))
    builder = dataikuapi.SamplingRecipeCreator(recipe_name, project)
    builder.with_input(recipe_input_dataset_name)    
    create_dataset_in_connection(project, recipe_output_dataset_name, connection_name)
    builder.with_output(recipe_output_dataset_name)
    builder.build()
    print("Filter/sampling recipe '{}' sucessfully created!".format(recipe_name))
    pass