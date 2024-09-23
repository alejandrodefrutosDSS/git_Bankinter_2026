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

connecting_dataset_name = "" # dataset that will connect to the "to_dashboard" flow zone.
input_dataset_name = ""
if logs_origin == "cloud" or logs_origin == "demo":
    connecting_dataset_name = "logs_filtered_unnested"
    input_dataset_name = "compute_resource_usage_logs"
elif logs_origin == "event_server":
    connecting_dataset_name = "eventserver_llmusage_logs_cleaned"
    input_dataset_name = "eventserver_cru_logs"
else:
    raise "Unexpected log origin."

input_dataset = project.get_dataset(input_dataset_name)
input_dataset_settings = input_dataset.get_settings()
input_dataset_settings.settings["params"]["connection"] = logs_connection
input_dataset_settings.settings["type"] = get_connection_type(project, input_dataset_name, logs_connection)
input_dataset_settings.save()

logs_partitioning_activated = variables["local"]["logs_partitioning_activated"]
logs_partitioning_period = variables["local"]["logs_partitioning_period"]
logs_partitioning_pattern = variables["local"]["logs_partitioning_pattern"]
    
recipe = project.get_recipe("compute_llm_logs_prep")
recipe_settings = recipe.get_settings()
current_inputs = recipe_settings.get_flat_input_refs()
assert len(current_inputs) == 1, f"Expected exactly one input to recipe 'compute_llm_logs_prep'."

recipe_settings.replace_input(current_inputs[0], connecting_dataset_name)
recipe_settings.save()
