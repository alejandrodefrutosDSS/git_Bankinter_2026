import dataiku
import dataikuapi
from dku_utils.projects.datasets.dataset_commons import get_dataset_in_connection_settings
from dku_utils.projects.connections.connection_change_filesystem import change_filesystem_dataset_format, switch_managed_dataset_connection_to_local_filesytem_storage, switch_managed_dataset_connection_to_cloud_storage
import json

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

TO_DASHBOARD_FLOWZONE_DS = ["logs_llm_usage_prepared", "logs_llm_usage_prepared_by_Project"]
EVENTSERVER_FLOWZONE_DS = ["eventserver_llmusage_logs_cleaned"]
EVENTSERVER_INPUT_DS = ["eventserver_cru_logs"]
CLOUD_FLOWZONE_DS = ["logs_filtered_unnested"]
CLOUD_INPUT_DS = ["compute_resource_usage_logs"]

TO_DASHBOARD_FLOWZONE_RECIPES = ["compute_llm_logs_prep", "compute_logs_llm_usage_prepared_by_Project"]
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
managed_dataset_connection = variables["local"]["managed_dataset_connection"]

connecting_dataset_name = "" # dataset that will connect to the "to_dashboard" flow zone.
ALL_DS = TO_DASHBOARD_FLOWZONE_DS
ALL_MANAGED_DS = TO_DASHBOARD_FLOWZONE_DS
ALL_RECIPES = TO_DASHBOARD_FLOWZONE_RECIPES
if logs_origin == "cloud":
    connecting_dataset_name = "logs_filtered_unnested"
    ALL_DS = ALL_DS + CLOUD_INPUT_DS + CLOUD_FLOWZONE_DS
    ALL_MANAGED_DS = ALL_MANAGED_DS + CLOUD_FLOWZONE_DS
    ALL_RECIPES = ALL_RECIPES + CLOUD_FLOWZONE_RECIPES
elif logs_origin == "event_server":
    connecting_dataset_name = "eventserver_llmusage_logs_cleaned"
    ALL_DS = ALL_DS + EVENTSERVER_INPUT_DS + EVENTSERVER_FLOWZONE_DS
    ALL_MANAGED_DS = ALL_MANAGED_DS + EVENTSERVER_FLOWZONE_DS
    ALL_RECIPES = ALL_RECIPES + EVENTSERVER_FLOWZONE_RECIPES
else:
    raise "Unexpected log origin."

# Configure connection type and partitioning for all datasets in the selected flow branch.
for ds_name in ALL_DS:
    ds = project.get_dataset(ds_name)
    ds_settings = ds.get_settings()
    ds_settings.settings["params"]["connection"] = logs_connection
    ds_settings.settings["type"] = get_connection_type(project, ds_name, logs_connection)
    ds_settings.remove_partitioning()
    if logs_partitioning_activated:
        ds_settings.add_time_partitioning_dimension(logs_partitioning_period, logs_partitioning_period)
        ds_settings.set_partitioning_file_pattern(logs_partitioning_pattern)
        ds_settings.get_raw()["partitioning"]["considerMissingRequestedPartitionsAsEmpty"] = True

    ds_settings.save()

# Configure recipes dependencies.
for recipe_name in ALL_RECIPES:
    recipe = project.get_recipe(recipe_name)
    recipe_settings = recipe.get_settings()
    recipe_inputs = recipe_settings.get_recipe_inputs()
    if logs_partitioning_activated:
        recipe_output = recipe_settings.get_flat_output_refs()[0]
        recipe_inputs["main"]["items"][0]["deps"] = [{"out": recipe_output, "idim": logs_partitioning_period, "odim": logs_partitioning_period, "func": "equals", "params": {}, "expandVariables": False}]
    else:
        recipe_inputs["main"]["items"][0]["deps"] = []
    recipe_settings.save()

# Configure connecting compute_logs_llm_usage_prepared_by_Project_complete recipe dependencies
recipe = project.get_recipe("compute_logs_llm_usage_prepared_by_Project_complete")
recipe_settings = recipe.get_settings()
recipe_inputs = recipe_settings.get_recipe_inputs()
if logs_partitioning_activated:
    recipe_output = recipe_settings.get_flat_output_refs()[0]
    recipe_inputs["main"]["items"][0]["deps"] = [
        {"out": recipe_output, "idim": logs_partitioning_period, "func": "all_available", "params": {}, "expandVariables": False}
    ]
else:
    recipe_inputs["main"]["items"][0]["deps"] = []
    
recipe_settings.save()

# Configure connection type for all managed datasets downstream of inputs datasets.
ALL_MANAGED_DS = ALL_MANAGED_DS + ["logs_llm_usage_prepared_by_Project_complete", "budget_joined", "budget_joined_prepared", "budget_for_dashboard", "over_budget_notifications"]

print("toto")
managed_dataset_connection_type = get_dataset_in_connection_settings(project, managed_dataset_connection)["type"]
print(get_dataset_in_connection_settings(project, managed_dataset_connection))
print(managed_dataset_connection_type)
print("titou")

for ds_name in ALL_MANAGED_DS:
    if managed_dataset_connection_type == "Filesystem":
        switch_managed_dataset_connection_to_local_filesytem_storage(project, ds_name, managed_dataset_connection)
        change_filesystem_dataset_format(project, ds_name, "csv", change_dataset_format_type=True)
    else:
        switch_managed_dataset_connection_to_cloud_storage(project, ds_name, managed_dataset_connection)

# Configure flow routing between flow branches.
recipe = project.get_recipe("compute_llm_logs_prep")
recipe_settings = recipe.get_settings()
current_inputs = recipe_settings.get_flat_input_refs()
assert len(current_inputs) == 1, f"Expected exactly one input to recipe 'compute_llm_logs_prep'."

recipe_settings.replace_input(current_inputs[0], connecting_dataset_name)
recipe_settings.save()
