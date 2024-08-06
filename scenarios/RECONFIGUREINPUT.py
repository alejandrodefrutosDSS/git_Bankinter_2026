import dataiku
import dataikuapi

def get_connection_type(project, dataset_name, connection_name):
    tmp_dataset_name = "_tmp_dataset"
    tmp_recipe_name = "_tmp_recipe"
    
    tmp_dataset = project.get_dataset(tmp_dataset_name)
    builder = dataikuapi.CodeRecipeCreator(tmp_recipe_name, "python", project)
    builder = builder.with_new_output_dataset(tmp_dataset_name, connection_name)
    
    tmp_dataset = project.get_dataset(tmp_dataset_name)
    tmp_dataset_settings = tmp_dataset.get_settings().settings
    
    tmp_dataset.delete()
    
    return tmp_dataset_settings["type"]

project_key = dataiku.get_custom_variables()["projectKey"]
client = dataiku.api_client()
project = client.get_project(project_key)
variables = project.get_variables()

logs_origin = variables["local"]["logs_origin"]
logs_connection = variables["local"]["logs_connection"]

if logs_origin == "cloud":
    dataset = project.get_dataset("compute_resource_usage_logs")
    dataset_settings = dataset.get_settings()
    dataset_settings.settings["params"]["connection"] = logs_connection
    dataset_settings.settings["type"] = get_connection_type(project, "compute_resource_usage_logs", logs_connection)
    dataset_settings.save()
    
    recipe = project.get_recipe("compute_llm_logs_prep")
    recipe_settings = recipe.get_settings()
    current_inputs = recipe_settings.get_flat_input_refs()
    assert len(current_inputs) == 1, f"Expected exactly one input to recipe 'compute_llm_logs_prep'."
    
if logs_origin == "event_server":
    es_dataset = project.get_dataset("eventserver_cru_logs")
    es_dataset_settings = es_dataset.get_settings()
    es_dataset_settings.settings["params"]["connection"] = logs_connection
    es_dataset_settings.settings["type"] = get_connection_type(project, "eventserver_cru_logs", logs_connection)
    es_dataset_settings.save()
