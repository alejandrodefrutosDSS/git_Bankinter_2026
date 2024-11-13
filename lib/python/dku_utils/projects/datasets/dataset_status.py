from dku_utils.type_checking import DSSProject
from .dataset_commons import (get_dataset_settings_and_dictionary,
                              get_dataset_column_datatypes_mapping,
                              get_dataset_connection_name,
                              create_dataset_in_connection
                              )
from .datatypes import NUMERICAL_STORAGE_DATATYPES


INITIAL_COL_STATS_SETTINGS = {
    'type': 'col_stats',
    'enabled': False,
    'computeOnBuildMode': 'NO',
    'meta': {'name': 'Columns statistics', 'level': 2},
    'configuration': {'aggregates': []}
}

ALLOWED_COLUMN_STATISTICS = ["MIN", "MEAN", "MAX", "SUM", "COUNT",
                             "COUNT_NULL", "STDDEV", "COUNT_DISTINCT",
                             "HISTOGRAM"]

NUMERICAL_ONLY_COLUMN_STATISTICS = ["MEAN", "SUM", "STDDEV", "HISTOGRAM"]


def get_dataset_probe_indexes(project: DSSProject, dataset_name: str):
    """
    Retrieves indexes of the probes set on a dataset, within the settings list. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.

    :returns: dataset_probe_indexes: dict: Dictionary mapping each type of probe to it's index in the settings list.
    """
    dataset_probe_indexes = {}
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    existing_probes = dataset_settings.settings["metrics"]["probes"]
    for probe_index, probe_data in enumerate(existing_probes):
        probe_type = probe_data["type"]
        dataset_probe_indexes[probe_type] = probe_index
    return dataset_probe_indexes


def compute_dataset_metrics_and_get_report(project: DSSProject, dataset_name: str, partition_id="ALL"):
    """
    Compute metrics on a dataset and a report of these metric's computation outcomes. 
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param partition_id: str: Partitions identifier defining the computation's scope. Keep the default value 'ALL' if you 
        want the metrics to be computed on the entire dataset. Set a precise partition identifier if you want the metric 
        to be computed on a specific dataset partition.
        DISCLAIMER: Only set unique partition_id. The function won't work if several partition values are set.

    :returns: computed_metrics_data: dict: Dictionary mapping each computed metric with it's value.
        Output format is: {METRIC_ID: METRIC_VALUE}
        Example:
            {'reporting:METRICS_COMPUTATION_DURATION': '2273', 'col_stats:MAX:Age': '80.0', 'basic:COUNT_COLUMNS': '11'}
    :returns: computed_metrics_summary: str: Summary of all the computed metrics.
    :returns: metric_engine_runs_summary: str: Summary of the metric engine runs.
    """
    dataset = project.get_dataset(dataset_name)
    dataset_metrics_computation_report = dataset.compute_metrics(partition=partition_id)
    computation_has_results = dataset_metrics_computation_report["hasResult"]
    computed_metrics_data = {}
    computed_metrics_summary = ""
    metric_engine_runs_summary = ""
    if computation_has_results:
        dataset_metrics_computation_result = dataset_metrics_computation_report["result"]
        computed_metrics_summary += "Following metrics has been computed:\n"
        for metric_data in dataset_metrics_computation_result["computed"]:
            metric_id = metric_data["metricId"]
            metric_value = metric_data["value"]
            computed_metrics_data[metric_id] = metric_value
            computed_metrics_summary += f"- '{metric_id}' with value '{metric_value}'.\n"
        
        computation_runs = dataset_metrics_computation_result["runs"]
        for run in computation_runs:
            run_engine = run.get("engine")
            if not run_engine:
                run_engine = "Unkown engine"
            run_error = run.get("error")
            error_message = None
            if run_error:
                error_message = run_error.get("message")
            
            summary_part = f"Engine '{run_engine}' {'failed' if run_error else 'succeeded'} "\
            f"{'with' if error_message else 'without'} error message '{error_message if error_message else ''}'.\n"
            if summary_part not in metric_engine_runs_summary:
                metric_engine_runs_summary += summary_part
    else:
        computed_metrics_summary += "No metrics were computed"
        metric_engine_runs_summary += "No metrics run summary."
    
    return computed_metrics_data, computed_metrics_summary, metric_engine_runs_summary


def add_column_statistics_on_dataset_if_not_exists(project: DSSProject, dataset_name: str,
                                                   column_statistics_mapping: dict):
    """
    Adds some 'column statistic' metrics on a dataset, if they do not exist.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param column_statistics_mapping: dict: Mapping between the columns targeted by statisitics and the list of 
        statistics to compute on these columns.
        Allowed column statistics are  ['MIN', 'MEAN', 'MAX', 'SUM', 'COUNT', 
                                        'COUNT_NULL', 'STDDEV', 'COUNT_DISTINCT',
                                        'HISTOGRAM']
        Example: {
            'column_1': ['MEAN', 'SUM', 'STDDEV'],
            'column_2': ['MIN', 'COUNT_DISTINCT', 'COUNT']
        }
    """
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_column_datatypes_mapping = get_dataset_column_datatypes_mapping(project, dataset_name)
    dataset_metric_indexes = get_dataset_probe_indexes(project, dataset_name)
    cols_stats_index_in_probes = dataset_metric_indexes.get("col_stats")

    if cols_stats_index_in_probes:
        print(f"Some column statistic settings existed on dataset {dataset_name} and will be upgraded.")
        existing_col_stats = dataset_settings.settings["metrics"]["probes"][cols_stats_index_in_probes]        
    else:
        print(f"No column statistic settings existed on dataset {dataset_name}: they will be created.")
        existing_col_stats = INITIAL_COL_STATS_SETTINGS
    
    existing_col_stats["enabled"] = True
    already_configured_col_stats = existing_col_stats["configuration"]["aggregates"]
    for column_name, column_statistics in column_statistics_mapping.items():
        column_datatype = dataset_column_datatypes_mapping[column_name]
        for column_statistic in column_statistics:
            column_statistic = column_statistic.upper()
            if column_statistic not in ALLOWED_COLUMN_STATISTICS:
                log_message = f"You asked to run statistic '{column_statistic}' on column '{column_name}' ."\
                f" The only allowed statistics are '{ALLOWED_COLUMN_STATISTICS}'!"
                raise ValueError(log_message)
            column_statistic_settings = {'column': column_name, 'aggregated': column_statistic}
            column_satistic_does_not_exists = (column_statistic_settings not in already_configured_col_stats)
            if column_statistic in NUMERICAL_ONLY_COLUMN_STATISTICS:
                if column_datatype not in NUMERICAL_STORAGE_DATATYPES:
                    log_message = f"Aggregation '{column_statistic}' can't be done on column '{column_name}' "\
                    f"that has datatype '{column_datatype}': it won't be added to the metrics!"
                    print(log_message)
                else:
                    if column_satistic_does_not_exists:
                        existing_col_stats["configuration"]["aggregates"].append(column_statistic_settings)
            else:
                if column_satistic_does_not_exists:
                    existing_col_stats["configuration"]["aggregates"].append(column_statistic_settings)
        
    if cols_stats_index_in_probes:
        dataset_settings.settings["metrics"]["probes"][cols_stats_index_in_probes] = existing_col_stats
    else:
        dataset_settings.settings["metrics"]["probes"].append(existing_col_stats)
    dataset_settings.save()    
    pass


def reset_dataset_metric_and_check_settings(project: DSSProject, dataset_name: str, function_scope: str="metrics"):
    """
    Resets the settings associated with dataset metrics and/or checks.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param function_scope: str: Precises the scope of the function. Available choices are:
        - 'metrics': Choose this option if you want to only reset the metrics settings.
        - 'checks': Choose this option if you want to only reset the checks settings.
        - 'metrics_and_checks': Choose this option if you want to reset both the metrics and the checks settings.
    """
    dataset_settings, __ = get_dataset_settings_and_dictionary(project, dataset_name, False)
    dataset_connection_name = get_dataset_connection_name(project, dataset_name)
    
    TMP_DATASET_NAME = "TMP_DATASET"
    create_dataset_in_connection(project, TMP_DATASET_NAME, dataset_connection_name)
    tmp_dataset_settings, __ =\
    get_dataset_settings_and_dictionary(project, TMP_DATASET_NAME, False)
    
    if "metrics" in function_scope:
        dataset_settings.settings["metrics"] = tmp_dataset_settings.settings["metrics"]
        dataset_settings.get_raw()["metrics"] = tmp_dataset_settings.get_raw()["metrics"]
    if "checks" in function_scope:
        dataset_settings.settings["checks"] = tmp_dataset_settings.settings["checks"]
        dataset_settings.get_raw()["checks"] = tmp_dataset_settings.get_raw()["checks"]
    dataset_settings.save()
    print(f"Removing dataset '{TMP_DATASET_NAME}' ...")
    project.get_dataset(TMP_DATASET_NAME).delete()
    print(f"Dataset '{TMP_DATASET_NAME}' has been successfully removed from connection '{dataset_connection_name}'.")
    pass


def get_column_statistic_metric_id(column_name: str, column_statistic: str):
    """
    Gets the id of a metric associated with a column statistic.
    
    :param column_name: str: Name of the column.
    :param column_name: str: Name of the column statistic.
        Allowed column statistics are  ['MIN', 'MEAN', 'MAX', 'SUM', 'COUNT', 
                                        'COUNT_NULL', 'STDDEV', 'COUNT_DISTINCT',
                                        'HISTOGRAM']
    :returns: column_statistic_metric_id: str: Metric associated with the column's statistic.
    """
    column_statistic_metric_id = f"col_stats:{column_statistic}:{column_name}"
    return column_statistic_metric_id


def get_dataset_last_column_statistics(project: DSSProject, dataset_name:str,
                                       column_statistics_mapping: dict, partition_id: str="ALL",
                                       bool_add_statistics_if_not_exists: bool=True):
    """
    Computes the last column statistics of a dataset, retrieves its information as well as information about its execution.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param dataset_name: str: Name of the dataset.
    :param column_statistics_mapping: dict: Mapping between the columns targeted by statisitics and the list of 
        statistics to compute on these columns.
        Allowed column statistics are  ['MIN', 'MEAN', 'MAX', 'SUM', 'COUNT', 
                                        'COUNT_NULL', 'STDDEV', 'COUNT_DISTINCT',
                                        'HISTOGRAM']
        Example: {
            'column_1': ['MEAN', 'SUM', 'STDDEV'],
            'column_2': ['MIN', 'COUNT_DISTINCT', 'COUNT']
        }
    :param partition_id: str: Partitions identifier defining the computation's scope.
        - Keep the default value 'ALL' if you want the column statistics to be computed on the entire dataset. 
        Set a precise partition identifier if you want the column statistic to be computed on a specific dataset partition.
        DISCLAIMER: Only set unique a partition_id. The function will fail if several partition values are set.
    :param bool_add_statistics_if_not_exists: bool: Adds column statistics if they does not yet exists on the dataset.

    :returns: computed_metrics_data: dict: Dictionary mapping each computed column statistic with it's value.
        Output format is:
            {'column_1': 
                {COLUMN_STATISTIC_ID: {'id': 'col_stats:COLUMN_STATISTIC_ID:column_1', 'value': VALUE}}
             'column_2': { ... }
            }
        Example:
            {'Age': {'MAX': {'id': 'col_stats:MAX:Age', 'value': '80.0'}}}

    :returns: computed_metrics_summary: str: Summary of all the computed column statistics.
    :returns: metric_engine_runs_summary: str: Summary of the column statistics engine runs.
    """
    possible_metric_ids = []
    possible_metric_ids_stats = {}
    last_column_statistics = {}
    expected_columns = list(column_statistics_mapping.keys())
    if bool_add_statistics_if_not_exists:
        add_column_statistics_on_dataset_if_not_exists(project, dataset_name, column_statistics_mapping)
    for column_name, column_statistics in column_statistics_mapping.items():
        column_statistics = [col_stat for col_stat in column_statistics if col_stat in ALLOWED_COLUMN_STATISTICS]
        if len(column_statistics) == 0:
            log_message = f"An irrelevant statistic is asked for column {column_name}!\n"\
            f"Asked statistics were '{column_statistics}' while allowed statistics are '{ALLOWED_COLUMN_STATISTICS}"
            raise ValueError(log_message)
        for col_stat in column_statistics:
            metric_id = get_column_statistic_metric_id(column_name, col_stat)
            possible_metric_ids.append(metric_id)
            possible_metric_ids_stats[metric_id] = col_stat

    computed_metrics_data, computed_metrics_summary, metric_engine_runs_summary=\
    compute_dataset_metrics_and_get_report(project, dataset_name, partition_id)
    found_metrics = list(computed_metrics_data.keys())
    for column_name in expected_columns:
        for metric_id in found_metrics:
            if metric_id in possible_metric_ids:
                metric_id_stat = possible_metric_ids_stats[metric_id]
                if column_name not in last_column_statistics.keys():
                    last_column_statistics[column_name] = {}
                last_column_statistics[column_name][metric_id_stat] = {
                    "id": metric_id, "value": computed_metrics_data[metric_id]
                }
    return last_column_statistics, computed_metrics_summary, metric_engine_runs_summary