from dku_utils.type_checking import DSSMLTask


def configure_mltask_kmeans_with_explicit_value_mode(ml_task_settings, n_clusters: list=[5], 
                            seed: int=1337, parallelism: int=2, enable_model_use=True):
    """
    Set the number of clusters (and other settings) for the kmeans algorithm with an explicit value mode to set 
    the number of clusters.
    
    :param ml_task_settings: DSSMLTask: the ML task.
    :param n_clusters: list[int]: the list of the number(s) of clusters saved as integer(s).
    :param seed: int: Used to generate reproducible results. 0 or no value means 
                        that no known seed is used (results will not be fully reproducible)
    :param parallelism: int: Number of cores used for parallel training. If -1 all CPUs are used. 
                                For values below -1, (n_cpus + 1 + value) are used: ie for -2, all CPUs 
                                but one are used.
    :param enable_model_use: bool: Activate or deactivate the KMeans algorithm

    """
    
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["k"] = n_clusters
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["enabled"] = enable_model_use
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["seed"] = seed
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["n_jobs"] = parallelism 
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["useClusterRange"] = False 
    ml_task_settings.save()
    print("The kmeans settings have been saved!")
    pass

def configure_mltask_kmeans_with_range_mode(ml_task_settings, min_clusters: int=3, max_clusters: int=7,
                                            nb_clusters_btwn_min_max: int=3,  
                                            seed: int=1337, parallelism: int=2, enable_model_use=True):
    """
    Set the number of clusters (and other settings) for the kmeans algorithm with the range mode.
    
    :param ml_task_settings: DSSMLTask: the ML task.
    :param min_clusters: int: the minimum number of clusters.
    :param max_clusters: int: the maximum number of clusters.
    :param nb_clusters_btwn_min_max: int: the count of the different numbers of 
                                            clusters within the min max range.
    :param seed: int: Used to generate reproducible results. 0 or no value means 
                        that no known seed is used (results will not be fully reproducible)
    :param parallelism: int: Number of cores used for parallel training. If -1 all CPUs are used. 
                                For values below -1, (n_cpus + 1 + value) are used: ie for -2, all CPUs 
                                but one are used.
    :param enable_model_use: bool: Activate or deactivate the KMeans algorithm

    """
    # Check the values of min, max and nb_clusters_btwn_min_max
    if min_clusters > max_clusters:
        raise ValueError("Input error: the min value is superior than the max value.")
        
    if nb_clusters_btwn_min_max > (max_clusters-min_clusters+1):
        raise ValueError("Input error: there are less cluster sizes within the range of the minimum and maximum values "
                "than the number you asked for.") 
    
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["range"]["min"] = min_clusters
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["range"]["max"] = max_clusters
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["range"]["nbValues"] = nb_clusters_btwn_min_max
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["useClusterRange"] = True

    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["enabled"] = enable_model_use
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]['k'] = []
        
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["seed"] = seed
    ml_task_settings.get_raw()["modeling"]["kmeans_clustering"]["n_jobs"] = parallelism 
    ml_task_settings.save()
    print("The kmeans settings have been saved!")
    return

def get_per_clusters_features_distribution_data(ml_task: DSSMLTask, model_id: str):
    """
    Retrieves the distribution information of a clustering modeling features, for each learned cluster.
        
    :param: ml_task: dataikuapi.dss.ml.DSSMLTask: DSS MLTask object. 
    :param model_id: str: ID of the model from which we want to retrieve the information, as we get from
        'ml_task.get_trained_models_ids()'.
    
    :returns: per_clusters_features_distribution_data: dict: Dictionary containing
        for each feature, its distribution per cluster data.
        Example: {"feature_1": {"cluster_0": {'min': 45.0, 'max': 99.0, 'median': 53.0, ...},
                                "cluster_1": {'min': 17.0, 'max': 44.0, 'median': 53.0, ...},
                                ....
                                },
                    ...
                }
    """
    model_details = ml_task.get_trained_model_details(model_id)
    features_clusters_profiling_data = model_details.details["clustersProfiling"]
    per_clusters_features_distribution_data = {}
    for feature_profiling_data in features_clusters_profiling_data:
        feature_name = feature_profiling_data["variable"]
        per_clusters_features_distribution_data[feature_name] = {}
        feature_per_clusters_distribution = feature_profiling_data["per_cluster"]
        for cluster_distribution_data in feature_per_clusters_distribution:
            cluster_name = cluster_distribution_data["cluster_name"]
            cluster_distribution_data.pop('cluster_name', None)
            per_clusters_features_distribution_data[feature_name][cluster_name] =\
            cluster_distribution_data
        pass
    pass
    return per_clusters_features_distribution_data


def rename_dss_default_clusters(ml_task: DSSMLTask, model_id: str, cluster_renamings: dict):
    """
    Renames default clusters computed by DSS. 
    
    :param: ml_task: dataikuapi.dss.ml.DSSMLTask: DSS MLTask object. 
    :param: clusters_renaming: dict: Dictionary containing the mapping between the default cluster labels 
        and their new names. 
        Example = {'cluster_0': 'new_name_for_cluster_0',
                   'cluster_1': 'new_name_for_cluster_1',
                   'cluster_2': 'new_name_for_cluster_2'}
    
    """
    model_details = ml_task.get_trained_model_details(model_id)
    metadata_set_by_user = model_details.get_user_meta()
    for dss_cluster_name in cluster_renamings.keys():
        model_details.get_user_meta()["clusterMetas"][dss_cluster_name]["name"] = cluster_renamings[dss_cluster_name]
    model_details.save_user_meta()
    pass