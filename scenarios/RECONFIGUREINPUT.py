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

TO_DASHBOARD_FLOWZONE_DS = ["logs_llm_usage_prepared"]
EVENTSERVER_FLOWZONE_DS = ["eventserver_cru_logs", "eventserver_llmusage_logs_cleaned"]
CLOUD_FLOWZONE_DS = ["compute_resource_usage_logs", "logs_filtered_unnested"]

TO_DASHBOARD_FLOWZONE_RECIPES = ["compute_llm_logs_prep"]
EVENTSERVER_FLOWZONE_RECIPES = ["compute_eventserver_llmusage"]
CLOUD_FLOWZONE_RECIPES = ["compute_audit_logs_prepared"]

project_key = dataiku.get_custom_variables()["projectKey"]
client = dataiku.api_client()
project = client.get_project(project_key)
variables = project.get_variables()

logs_origin = variables["local"]["logs_origin"]
logs_connection = variables["local"]["logs_connection"]
logs_partitioning_activated = variables["local"]["logs_partitioning_activated"]
logs_partitioning_period = variables["local"]["logs_partitioning_period"]
logs_partitioning_pattern = variables["local"]["logs_partitioning_pattern"]

connecting_dataset_name = "" # dataset that will connect to the "to_dashboard" flow zone.
ALL_DS = TO_DASHBOARD_FLOWZONE_DS
if logs_origin == "cloud" or logs_origin == "demo":
    connecting_dataset_name = "logs_filtered_unnested"
    ALL_DS = ALL_DS + CLOUD_FLOWZONE_DS
elif logs_origin == "event_server":
    connecting_dataset_name = "eventserver_llmusage_logs_cleaned"
    ALL_DS = ALL_DS + EVENTSERVER_FLOWZONE_DS
else:
    raise "Unexpected log origin."

# Change connection type for all dataset in the selected flow branch.
for ds_name in ALL_DS:
    ds = project.get_dataset(ds_name)
    ds_settings = ds.get_settings()
    print(ds_settings.settings)
    ds_settings.settings["params"]["connection"] = logs_connection
    ds_settings.settings["type"] = get_connection_type(project, ds_name, logs_connection)
    if logs_partitioning_activated:
        ds_settings.remove_partitioning()
        ds_settings.add_time_partitioning_dimension(logs_partitioning_period, logs_partitioning_period)
        ds_settings.set_partitioning_file_pattern(logs_partitioning_pattern)
    else:
        ds_settings.remove_partitioning()

    ds_settings.save()
    
recipe = project.get_recipe("compute_llm_logs_prep")
recipe_settings = recipe.get_settings()
current_inputs = recipe_settings.get_flat_input_refs()
assert len(current_inputs) == 1, f"Expected exactly one input to recipe 'compute_llm_logs_prep'."

recipe_settings.replace_input(current_inputs[0], connecting_dataset_name)
recipe_settings.save()
