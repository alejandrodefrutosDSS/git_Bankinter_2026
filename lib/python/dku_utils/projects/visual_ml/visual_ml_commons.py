import pandas as pd
import re
import time
from .custom_metrics import ALL_METRICS_SETTINGS
from .features_preprocessing import DEFAULT_NUMERICAL_FEATURES_HANDLING, DEFAULT_CATEGORICAL_FEATURES_HANDLING
from dku_utils.projects.datasets.dataset_commons import get_dataset_schema_information
from dku_utils.type_checking import DSSProject, DSSMLTask, check_object_is_project


def get_ml_task_and_settings(project: DSSProject, visual_analysis_id:str , ml_task_id:str):
    """
    Retrieves a 'ml_task' object as well as its settings.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param visual_analysis_id: str: ID of the LAB visual analysis.
    :param visual_analysis_id: str: ID of the LAB visual analysis.

    :returns: ml_task: dataikuapi.dss.ml.DSSMLTask: DSS MLTask object. 
    :returns: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    """
    check_object_is_project(project)
    visual_analysis = project.get_analysis(visual_analysis_id)
    ml_task = visual_analysis.get_ml_task(ml_task_id)
    ml_task_settings = ml_task.get_settings()
    return ml_task, ml_task_settings


def enable_features_in_ml_task_settings(ml_task_settings, list_of_features_to_enable: list):
    """
    Enables the use of a set of features within a ML task.

    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :param list_of_features_to_enable: list: List of the ML task features to enable.
    """
    for feature in list_of_features_to_enable:
        ml_task_settings.use_feature(feature)
    ml_task_settings.save()
    pass


def reject_features_from_ml_task_settings(ml_task_settings, list_of_features_to_reject: list):
    """
    Rejects the use of a set of features within a ML task.

    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :param list_of_features_to_reject: list: List of the ML task features to reject.
    """
    for feature in list_of_features_to_reject:
        ml_task_settings.reject_feature(feature)
    ml_task_settings.save()
    pass


def remove_unavailable_features_from_ml_task_features_handling(project: DSSProject, ml_task_settings,
                                                               ml_task_train_dataset_name: str):
    """
    Updates a ML task features handling so that it does not contains settings for the features
        that are not anymore present in a dataset.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :param ml_task_train_dataset_name: str: Name of the train dataset linked with the ML task.
    """
    check_object_is_project(project)
    ml_task_dataset_columns, __ = get_dataset_schema_information(project, ml_task_train_dataset_name)
    print("Removing unavailable features handling from ml_task")
    new_per_feature_handling = {}
    previous_per_feature_handling = ml_task_settings.get_raw()["preprocessing"]["per_feature"]
    previously_handled_features = list(previous_per_feature_handling.keys())
    
    for column in ml_task_dataset_columns:
        if column in previously_handled_features:
            new_per_feature_handling[column] = previous_per_feature_handling[column]
    
    ml_task_settings.get_raw()["preprocessing"]["per_feature"] = new_per_feature_handling
    ml_task_settings.save()
    features_removed_from_the_features_handling = [column_name for column_name in previously_handled_features
                                                   if column_name not in new_per_feature_handling.keys()]
    print("Features removed from the ml_task are: '{}'".format(features_removed_from_the_features_handling))
    pass


def add_available_features_missing_in_ml_task_features_handling(project: DSSProject, ml_task_settings,
                                                                ml_task_train_dataset_name: str):
    """
    Adds default preprocessing parameters to new dataset features that are missing in a 'ml_task' features handling.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :param ml_task_train_dataset_name: str: Name of the train dataset associated with the ml_task.
    """
    check_object_is_project(project)
    dataset_columns, dataset_column_datatypes = get_dataset_schema_information(project, ml_task_train_dataset_name)    
    ml_task_available_features = get_ml_task_available_features(ml_task_settings)
    columns_with_missing_features_preprocessing = [column_name for column_name in dataset_columns
                                                   if column_name not in ml_task_available_features]
    print("Following columns will be added to the ml_task preprocessing '{}'".format(columns_with_missing_features_preprocessing))
    for column_name, column_datatype in zip(dataset_columns, dataset_column_datatypes):
        if column_name in columns_with_missing_features_preprocessing:
            if column_datatype in ["int", "bigint", "double"]:
                column_preprocessing_parameters = DEFAULT_NUMERICAL_FEATURES_HANDLING
            else:
                column_preprocessing_parameters = DEFAULT_CATEGORICAL_FEATURES_HANDLING
            set_feature_preprocessing_in_ml_task(ml_task_settings, column_name, column_preprocessing_parameters)
    pass


def update_ml_task_feature_preprocessing(ml_task_settings, column_name: str,
                                        new_preprocessing_parameters: dict,
                                        force_feature_preprocessing_creation: bool=True):
    """
    Updtates the feature handling of a 'ml_task' column.
    
    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :param column_name: str: Name of the column to edit the feature handling on.
    
    :param: new_preprocessing_parameters: dict: Column feature preprocessing to set.
        - This is a dictionary having parameters similar to what we would get with a
            ml_task_settings.get_feature_preprocessing("COLUMN_NAME").
        - Some examples of columns feature handling can be found in ./features_preprocessing.
    
    :param: force_feature_preprocessing_creation: bool: Boolean parameter to force the feature_preprocessing creation if
        it does not exist yet in the 'ml_task'.
        DEPRECATION_WARNING: You should not use that parameter and prefer using the function 
        'add_available_features_missing_in_ml_task_features_handling' before using function 'update_ml_task_feature_preprocessing'
    """
    print("Updating feature '{}' preprocessing with parameters '{}'".format(column_name, new_preprocessing_parameters))
    success_log_message = "Feature '{}' preprocessing Updated !\n".format(column_name, new_preprocessing_parameters)
    
    try:
        current_preprocessing_parameters = ml_task_settings.get_feature_preprocessing(column_name)
        current_preprocessing_parameters_labels = list(current_preprocessing_parameters.keys())
        new_preprocessing_parameters_labels = list(new_preprocessing_parameters.keys())
        for label in current_preprocessing_parameters_labels:
            ml_task_settings.get_feature_preprocessing(column_name).pop(label)

        for label in new_preprocessing_parameters_labels:
            ml_task_settings.get_feature_preprocessing(column_name).update({label: new_preprocessing_parameters[label]})
        
        print(success_log_message)
    
    except KeyError:
        if force_feature_preprocessing_creation:
            deprecation_log_message = \
            "DEPRECATION_WARNING: you should not use parameter 'force_feature_preprocessing_creation': prefer using "\
            "function 'add_available_features_missing_in_ml_task_features_handling' before using the function 'update_ml_task_feature_preprocessing'."
            print(deprecation_log_message)
            print("Feature '{}' preprocessing parameters does not exist and will be created ...".format(column_name))
            set_feature_preprocessing_in_ml_task(ml_task_settings, column_name, new_preprocessing_parameters)
            print(success_log_message)
        else:
            print("WARNING ! Feature '{}' preprocessing parameters does not exist: you should use function "\
                  "'add_available_features_missing_in_ml_task_features_handling' before using the function 'update_ml_task_feature_preprocessing'".format(column_name))
    ml_task_settings.save()
    pass


def set_feature_preprocessing_in_ml_task(ml_task_settings, column_name: str, column_preprocessing_parameters: dict):
    """
    Sets the feature handling of a column in a 'ml_task'.
        Make sure the feature handling of that column exist by using first 'add_available_features_missing_in_ml_task_features_handling'.
    
    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :param column_name: str: Name of the column to edit the feature handling on.
    
    :param column_preprocessing_parameters: dict: Column feature preprocessing to set.
        - This is a dictionary having parameters similar to what we would get with a
            ml_task_settings.get_feature_preprocessing("COLUMN_NAME").
        - Some examples of columns feature handling can be found in ./features_preprocessing.
    """
    print("Adding feature '{}' in features handling...".format(column_name))
    ml_task_settings.get_raw()["preprocessing"]["per_feature"][column_name] = column_preprocessing_parameters
    ml_task_settings.save()
    print("Feature '{}' successfully added in features handling!".format(column_name))
    pass


def get_ml_task_available_features(ml_task_settings):
    """
    Retrieves the list of all the features available in a ML task.
    
    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :returns: ml_task_available_features: list: List of all the features available in the ML task.
    """
    ml_task_available_features = list(ml_task_settings.mltask_settings["preprocessing"]["per_feature"].keys())
    return ml_task_available_features


def get_ml_task_input_and_rejected_features(ml_task_settings):
    """
    Retrieves the lists of all the features in a ML task that are inputs and rejected.
    
    :param: ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
        '[MLTaskType]' varies depending on the type of MLTask (Regression, Classification, Clustering).
    
    :returns: ml_task_input_features: list: List of all the features that are model inputs.
    :returns: ml_task_rejected_features: list: List of all the features that are rejected in the model .
    """
    ml_task_input_features = []
    ml_task_rejected_features = []
    ml_task_available_features = get_ml_task_available_features(ml_task_settings)
    for feature_name in ml_task_available_features:
        feature_preprocessing = ml_task_settings.mltask_settings["preprocessing"]["per_feature"][feature_name]
        if feature_preprocessing["role"] == "INPUT":
            ml_task_input_features.append(feature_name)
        if feature_preprocessing["role"] == "REJECT":
            ml_task_rejected_features.append(feature_name)
    return ml_task_input_features, ml_task_rejected_features


def recompute_ml_task_sets(ml_task: DSSMLTask):
    """
    Recomputes the train and test sets associated with a ML task.
        
    :param: ml_task: DSSMLTask: DSS MLTask object.
    """
    print("Recomputing ML task train and test sets...")
    ml_task_settings = ml_task.get_settings()
    ml_task_settings.get_raw()['splitParams']['instanceIdRefresher'] += 1
    ml_task_settings.save()
    print("ML task train and test sets recomputed!")
    pass


def recompute_ml_task_sampling(ml_task: DSSMLTask):
    """Recomputes the the sampling of a ML task.
        
    :param: ml_task: DSSMLTask: DSS MLTask object.
    """
    print("Recomputing ML task sampling...")
    ml_task_settings = ml_task.get_settings()
    ml_task_settings_dict = ml_task_settings.get_raw()
    if "sampling" in ml_task_settings_dict:
        ml_task_settings.get_raw()["sampling"]["instanceIdRefresher"] += 1
    elif "splitParams" in ml_task_settings_dict:
        ml_task_settings.get_raw()["splitParams"]["instanceIdRefresher"] += 1
    else:
        log_message = "The sampling settings could not be recomputed: could not find the 'instanceIdRefresher'"
        raise Exception(log_message)
    ml_task_settings.save()
    print("ML task sampling recomputed!")
    pass


def get_models_metrics_dataframe(ml_task: DSSMLTask, list_of_model_ids: list):
    """
    Retrieves a dataframe containing information about the metrics of performance
        associated with trained models.
        
    :param: ml_task: DSSMLTask: DSS MLTask object.
    :param: list_of_model_ids: list: List of trained model IDs.
    
    :returns: models_metrics_df: pandas.core.frame.DataFrame: Pandas DataFrame
        containing metrics associated with each trained model.
    """
    if len(list_of_model_ids) == 0:
        log_message = "Not any model set in variable 'list_of_model_ids'! Please check its content "\
        "or if ml_task has some trained models."
        raise ValueError(log_message)
    models_metrics = []
    
    for model_id in list_of_model_ids:
        model_details = ml_task.get_trained_model_details(model_id)
        model_metrics = model_details.get_performance_metrics()
        models_metrics.append(model_metrics)
    
    models_metrics_df = pd.DataFrame(models_metrics)
    models_metrics_columns = list(models_metrics_df.columns)
    models_metrics_df["model_id"] = list_of_model_ids
    models_metrics_df = models_metrics_df[["model_id"]+models_metrics_columns]
    return models_metrics_df


def get_last_session_trained_model_ids(ml_task: DSSMLTask):
    """
    Retrieves the IDs of the models trained during the last ML task session.
        
    :param: ml_task: DSSMLTask: DSS MLTask object.

    :returns: last_session_trained_model_ids: list: List of all models IDs trained in the last ML task session.
    """
    models_per_sessions_dataframe = get_models_per_sessions_dataframe(ml_task)
    models_per_sessions_dataframe = models_per_sessions_dataframe\
    [models_per_sessions_dataframe["session_id_numerical"] ==\
     models_per_sessions_dataframe["last_session_id_numerical"]]
    last_session_trained_model_ids = list(models_per_sessions_dataframe["model_id"])
    return last_session_trained_model_ids


def train_models_then_deploy_best_from_last_session(ml_task: DSSMLTask, 
                                                    metric_name: str, 
                                                    bool_greater_metric_is_better: bool,
                                                    bool_compute_sub_population_analysis: bool,
                                                    sub_population_analysis_variables: list,
                                                    sub_population_analysis_test_set_fraction_to_sample: float,
                                                    bool_compute_partial_dependencies: bool,
                                                    partial_dependencies_variables: list,
                                                    partial_dependencies_test_set_fraction_to_sample: float,
                                                    flow_training_recipe_name: str,
                                                    flow_saved_model_id: str,
                                                    subpopulation_analysis_computation_strategy:str ='compute_all_at_once',
                                                    partial_dependencies_computation_strategy:str ='compute_all_at_once'):
    """
    Train models defined in a ML task in a new training session. 
        Then the model that get the bests performances in the training session is deployed on an existing flow model. 
        (DISCLAIMER: the type of model deployed can be different from the one previously deployed in the flow).
        
    :param: ml_task: DSSMLTask: DSS MLTask object.
    
    :param metric_name: str: Name of the metric against which models are compared.
        Some of the native DSS metrics are:
        - Regression: {'EVS': 'Explained Variance Score',
            'mape': 'Mean Absolute Percentage Error',
            'mae': 'Mean Absolute Error',
            'mse': 'Mean Squared Error',
            'rmse': 'Root Mean Square Error',
            'rmsle': 'Root Mean Square Logarithmic Error',
            'r2': 'R2 Score',
            'pearson': 'Pearson',
            'customScore': 'Custom code'}
        - Classification: {'f1': 'F1 score', 
            'accuracy': 'Accuracy',
            'precision': 'Precision',
            'recall': 'Recall',
            'COST_MATRIX': 'Cost matrix',
            'auc': 'Area Under the Curve',
            'logLoss': 'Log loss',
            'CUMULATIVE_LIFT': 'Cumulative lift',
            'customScore': 'Custom code'}
        - Clustering: {'silhouette': 'Silhouette coefficient'}
    
    :param bool_greater_metric_is_better: bool: Boolean parameter to precise if having a greater metric is beter.
    
    :param: bool_compute_sub_population_analysis: bool: Parameter precising if a Subpopulation analysis must be
        computed on the model test set, before it is deployed.
    
    :param: sub_population_analysis_variables: list: List of the features on which the subpopulation analysis
        must be computed.
        --> 'sub_population_analysis_variables' can also be set to the value "*" to select all mltask input features.
    
    :param: sub_population_analysis_test_set_fraction_to_sample: float: Fraction/percent (Value must be in ]0, 1] !)
        of the trained model test set to use in the Subpopulation analysis computation.
    
    :param: bool_compute_partial_dependencies: bool: Parameter precising if a Partial dependencies must be
        computed on the model test set, before it is deployed.
    
    :param: partial_dependencies_variables: list: List of the features on which the partial dependencies
        must be computed.
        --> 'partial_dependencies_variables' can also be set to the value "*" to select all mltask input features.
    
    :param: partial_dependencies_test_set_fraction_to_sample: float: Fraction/percent (Value must be in ]0, 1] !)
        of the trained model test set to use in the Partial dependencies computation.
    
    :param flow_training_recipe_name: str: Name of the flow model training recipe associated with the ML task.
    
    :param flow_saved_model_id: str: ID of the flow deployed model associated with the ML task.

    :param computation_strategy: str: Precises how to compute the variables subpopulation analyzes. Accepted values are:
        - 'compute_all_at_once': Choose this value if you want the subpopulation analyzes to be computed for all variables
            at once, within the same api-call. The function will fail if an issue is encountered on one variable.
        - 'compute_step_by_step': Choose this value if you want the subpopulation analyzes to be computed one by one,
            using several api-calls. If an issue is encountered on one variable, the subpopulation analysis will fail for this
            one, but the function won't fail.

    :param computation_strategy: str: Precises how to compute the variables partial dependencies. Accepted values are:
        - 'compute_all_at_once': Choose this value if you want the partial dependencies to be computed for all variables
            at once, within the same api-call. The function will fail if an issue is encountered on one variable.
        - 'compute_step_by_step': Choose this value if you want the partial dependencies to be computed one by one,
            using several api-calls. If an issue is encountered on one variable, the partial dependencies will fail for this
            one, but the function won't fail.
    """
    ml_task_settings = ml_task.get_settings()
    # Model retrain:
    print("Models training ...")
    previously_trained_models_ids = ml_task.get_trained_models_ids()
    train_start_time = time.time()
    ml_task.train()
    train_end_time = time.time()
    print("Models trained !")
    models_training_duration = (train_end_time - train_start_time) / 60.0
    print("Models train duration : {} min ...\n".format(models_training_duration))
    all_trained_models_ids = ml_task.get_trained_models_ids()
    print("Looking for the model having the best performances among the last trained models ...")
    last_session_models_ids = [model_id for model_id in all_trained_models_ids
                               if model_id not in previously_trained_models_ids]
    models_metrics_dataframe = get_models_metrics_dataframe(ml_task, last_session_models_ids)
    if bool_greater_metric_is_better:
        sort_metrics_ascending = False
    else:
        sort_metrics_ascending = True
    
    custom_metrics = ALL_METRICS_SETTINGS.keys()
    sort_column = metric_name
    if metric_name not in models_metrics_dataframe.columns:
        if metric_name in custom_metrics:
            sort_column = "customScore"
    try:
        models_metrics_dataframe.sort_values(by=sort_column, ascending=sort_metrics_ascending,
                                             axis=0, inplace=True)
    except KeyError:
        models_metrics_dataframe.sort_values(by=sort_column.lower(), ascending=sort_metrics_ascending,
                                             axis=0, inplace=True)
        
    models_metrics_dataframe.index = range(len(models_metrics_dataframe))
    best_model_in_last_session = models_metrics_dataframe["model_id"][0]
    print("Best model is '{}'!".format(best_model_in_last_session))
    if bool_compute_sub_population_analysis:
        if len(sub_population_analysis_variables) > 0:
            if sub_population_analysis_variables == "*":
                sub_population_analysis_variables, __ = get_ml_task_input_and_rejected_features(ml_task_settings)
            compute_sub_population_analysis(ml_task, best_model_in_last_session, sub_population_analysis_variables,
                                            sub_population_analysis_test_set_fraction_to_sample,
                                            subpopulation_analysis_computation_strategy)
        else:
            print("Subpopulation analysis has not been computed because no variables were set in 'sub_population_analysis_variables'!")

    if bool_compute_partial_dependencies:
        if len(partial_dependencies_variables) > 0:
            if partial_dependencies_variables == "*":
                partial_dependencies_variables, __ = get_ml_task_input_and_rejected_features(ml_task_settings)
            compute_partial_dependencies(ml_task, best_model_in_last_session, partial_dependencies_variables,
                                         partial_dependencies_test_set_fraction_to_sample,
                                         partial_dependencies_computation_strategy
                                         )
        else:
            print("Partial dependencies has not been computed because no variables were set in 'partial_dependencies_variables'!")
    print("Deploying the best model ...")
    ml_task.redeploy_to_flow(model_id=best_model_in_last_session,
                             recipe_name=flow_training_recipe_name,
                             saved_model_id=flow_saved_model_id,
                             activate=True)
    print("Model with the best performances has been deployed!")
    pass


def get_models_per_sessions_dataframe(ml_task: DSSMLTask):
    """
    Retrieves a pandas DataFrame containing relations between trained models and their sessions IDs.
        
    :param: ml_task: DSSMLTask: DSS MLTask object.

    :returns: models_per_sessions_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing relations between trained models and their sessions IDs.
    """
    SESSION_INDEX_IN_MODEL_ID = 4
    all_trained_model_ids = ml_task.get_trained_models_ids()
    all_sessions_data = []
    all_session_ids_numerical = []
    for model_id in all_trained_model_ids:
        model_session_id = model_id.split('-')[SESSION_INDEX_IN_MODEL_ID]
        model_session_id_numerical = int(re.sub('s', '', model_session_id))
        all_session_ids_numerical.append(model_session_id_numerical)
        all_sessions_data.append({"session_id": model_session_id,
                                  "session_id_numerical": model_session_id_numerical,
                                  "model_id": model_id})
    if len(all_session_ids_numerical) > 0:
        last_session_id_numerical = max(all_session_ids_numerical)
        models_per_sessions_dataframe = pd.DataFrame(all_sessions_data)
        models_per_sessions_dataframe.sort_values(by="session_id_numerical", axis=0, ascending=False, inplace=True)
        models_per_sessions_dataframe["last_session_id_numerical"] = last_session_id_numerical
        models_per_sessions_dataframe.index = range(len(models_per_sessions_dataframe))
    else:
        models_per_sessions_dataframe = pd.DataFrame(columns=["session_id", "session_id_numerical",
                                                              "model_id", "last_session_id_numerical"])
    return models_per_sessions_dataframe


def get_ml_task_best_model_id(ml_task: DSSMLTask, list_of_model_ids: list, metric_name: str, bool_greater_metric_is_better: bool):
    """
    Retrieves the model ID that get the best performance in the ML task.
    
    :param: ml_task: DSSMLTask: DSS MLTask object.
    
    :param: list_of_model_ids: list: List of trained model IDs.
    
    :param metric_name: str: Name of the metric against which models are compared.
        Some of the native DSS metrics are:
        - Regression: {'evs': 'Explained Variance Score',
            'mape': 'Mean Absolute Percentage Error',
            'mae': 'Mean Absolute Error',
            'mse': 'Mean Squared Error',
            'rmse': 'Root Mean Square Error',
            'rmsle': 'Root Mean Square Logarithmic Error',
            'r2': 'R2 Score',
            'pearson': 'Pearson correlation',
            'customScore': 'Custom code'}
        - Classification: {'f1': 'F1 score', 
            'accuracy': 'Accuracy',
            'precision': 'Precision',
            'recall': 'Recall',
            'calibrationLoss': 'Calibration loss',
            'auc': 'Area Under the Curve',
            'logLoss': 'Log loss',
            'averagePrecision': 'Average precision',
            'customScore': 'Custom code'} 
        - Clustering: {'silhouette': 'Silhouette coefficient'}
    
    :param bool_greater_metric_is_better: bool: Boolean parameter to precise if having a greater metric is beter.
    
    :returns: ml_task_best_model str: Model ID from 'list_of_model_ids' that get the best performance in the ML task.
    """
    models_metrics_dataframe = get_models_metrics_dataframe(ml_task, list_of_model_ids)
    if bool_greater_metric_is_better:
        sort_metrics_ascending = False
    else:
        sort_metrics_ascending = True
    
    custom_metrics = ALL_METRICS_SETTINGS.keys()
    sort_column = metric_name
    if metric_name not in models_metrics_dataframe.columns:
        if metric_name in custom_metrics:
            sort_column = "customScore"
    models_metrics_dataframe.sort_values(by=sort_column,
                                         ascending=sort_metrics_ascending,
                                         axis=0,
                                         inplace=True)
    models_metrics_dataframe.index = range(len(models_metrics_dataframe))
    ml_task_best_model = models_metrics_dataframe["model_id"][0]
    return ml_task_best_model


def get_trained_model_test_set_size(ml_task: DSSMLTask, trained_model_id: str):
    """
    Retrieves the test set size of a ML task trained model.

    :param: ml_task: DSSMLTask: DSS MLTask object.
    :param: trained_model_id: str: ID of the ML task trained model.
    
    :returns: model_test_set_size int: Model's test set size.
    """
    model_details = ml_task.get_trained_model_details(trained_model_id)
    model_test_set_size = model_details.details["splitDesc"]["testRows"]
    return model_test_set_size


def compute_sub_population_analysis(ml_task: DSSMLTask, trained_model_id: str, sub_population_analysis_variables: list,
                                    test_set_fraction_to_sample: float, computation_strategy:str= "compute_all_at_once"):
    """
    Computes a Subpopulation analysis on a ML task trained model test set.

    :param: ml_task: DSSMLTask: DSS MLTask object.
    
    :param: trained_model_id: str: ID of the ML task trained model.
    
    :param: sub_population_analysis_variables: list: List of the features on which the subpopulation analysis
        must be computed.
    
    :param: test_set_fraction_to_sample: float: Fraction/percent (Value must be in ]0, 1] !)
        of the trained model test set to use in the Subpopulation analysis computation.
    
    :param computation_strategy: str: Precises how to compute the variables subpopulation analyzes. Accepted values are:
        - 'compute_all_at_once': Choose this value if you want the subpopulation analyzes to be computed for all variables
            at once, within the same api-call. The function will fail if an issue is encountered on one variable.
        - 'compute_step_by_step': Choose this value if you want the subpopulation analyzes to be computed one by one,
            using several api-calls. If an issue is encountered on one variable, the subpopulation analysis will fail for this
            one, but the function won't fail.
    """
    if (test_set_fraction_to_sample < 0) or (test_set_fraction_to_sample > 1):
        log_message = "Parameter '{}' must be in ]0, 1] ! Please update it.".format(test_set_fraction_to_sample)
        raise ValueError(log_message)
    sub_population_analysis_start_time = time.time()
    model_test_set_size = get_trained_model_test_set_size(ml_task, trained_model_id)
    sample_size_in_sub_population_analysis = int(model_test_set_size * test_set_fraction_to_sample)
    model_details = ml_task.get_trained_model_details(trained_model_id)
    
    if computation_strategy == 'compute_all_at_once':
        print("Computing the subpopulation analysis (model_id = '{}') on the test set, with variables '{}'\n"\
              .format(trained_model_id, sub_population_analysis_variables))
        model_details.compute_subpopulation_analyses(split_by=sub_population_analysis_variables,
                                                    wait=True,
                                                    sample_size=sample_size_in_sub_population_analysis,
                                                    n_jobs=-1)
    elif computation_strategy == 'compute_step_by_step':
        for variable_name in sub_population_analysis_variables:
            try:
                print("Computing the subpopulation analysis (model_id = '{}') on the test set, on the variable '{}'\n"\
                      .format(trained_model_id, variable_name))
                model_details.compute_subpopulation_analyses(split_by=[variable_name],
                                                             wait=True,
                                                             sample_size=sample_size_in_sub_population_analysis,
                                                             n_jobs=-1)
            except Exception as e:
                log_message = "An exception has been met during the computation of the subpopulation analysis "\
                f"on the variable '{variable_name}': it will be ignored. The exception was '{type(e).__name__} : {e}'."
                print(log_message)

    sub_population_analysis_end_time = time.time()
    print("Subpopulation analysis computed!\n")
    sub_population_analysis_duration = (sub_population_analysis_end_time - sub_population_analysis_start_time) / 60.0
    print("Subpopulation analysis computation time : {} min ...\n".format(sub_population_analysis_duration))
    pass


def compute_partial_dependencies(ml_task: DSSMLTask, trained_model_id: str, partial_dependencies_variables: list,
                                 test_set_fraction_to_sample: float, computation_strategy:str= "compute_all_at_once"):
    """
    Computes a Partial dependencies on a ML task trained model test set.

    :param: ml_task: DSSMLTask: DSS MLTask object.
    
    :param: trained_model_id: str: ID of the ML task trained model.
    
    :param: partial_dependencies_variables: list: List of the features on which the partial dependencies
        must be computed.
    
    :param: test_set_fraction_to_sample: float: Fraction/percent (Value must be in ]0, 1] !)
        of the trained model test set to use in the partial dependencies computation.
    
    :param computation_strategy: str: Precises how to compute the variables partial dependencies. Accepted values are:
        - 'compute_all_at_once': Choose this value if you want the partial dependencies to be computed for all variables
            at once, within the same api-call. The function will fail if an issue is encountered on one variable.
        - 'compute_step_by_step': Choose this value if you want the partial dependencies to be computed one by one,
            using several api-calls. If an issue is encountered on one variable, the partial dependencies will fail for this
            one, but the function won't fail.
    """
    if (test_set_fraction_to_sample < 0) or (test_set_fraction_to_sample > 1):
        log_message = "Parameter '{}' must be in ]0, 1] ! Please update it.".format(test_set_fraction_to_sample)
        raise ValueError(log_message)
    
    partial_dependencies_start_time = time.time()
    model_test_set_size = get_trained_model_test_set_size(ml_task, trained_model_id)
    sample_size_in_partial_dependencies = int(model_test_set_size * test_set_fraction_to_sample)
    model_details = ml_task.get_trained_model_details(trained_model_id)

    if computation_strategy == 'compute_all_at_once':
        print("Computing the partial depencencies (model_id = '{}') on the test set, with variables '{}'\n"\
              .format(trained_model_id, partial_dependencies_variables))
        model_details.compute_partial_dependencies(partial_dependencies_variables,
                                                   wait=True,
                                                   sample_size=sample_size_in_partial_dependencies,
                                                   n_jobs=-1)
    
    elif computation_strategy == 'compute_step_by_step':
        for variable_name in partial_dependencies_variables:
            try:
                print("Computing the partial depencencies (model_id = '{}') on the test set, on the variable '{}'\n"\
                      .format(trained_model_id, variable_name))
                model_details.compute_partial_dependencies([variable_name],
                                                             wait=True,
                                                             sample_size=sample_size_in_partial_dependencies,
                                                             n_jobs=-1)
            except Exception as e:
                log_message = "An exception has been met during the computation of the partial dependencies "\
                f"on the variable '{variable_name}': it will be ignored. The exception was '{type(e).__name__} : {e}'."
                print(log_message)
    partial_dependencies_end_time = time.time()
    print("Partial depencencies computed!\n")
    partial_dependencies_duration = (partial_dependencies_end_time - partial_dependencies_start_time) / 60.0
    print("Partial depencencies computation time : {} min ...\n".format(partial_dependencies_duration))
    pass
  

def get_deployed_model_active_version_id(project: DSSProject, deployed_model_id: str):
    """
    Retrieves the ID of the active model within a deployed model .
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :param: deployed_model_id: str: ID of the deployed model.
    
    :returns model_active_version_id: str: ID of the active version within the deployed model.
    """
    check_object_is_project(project)
    deployed_model = project.get_saved_model(deployed_model_id)
    model_active_version_id = deployed_model.get_active_version()["id"]
    return model_active_version_id


def set_custom_optimization_metric_in_ml_task(ml_task_settings,
                                              custom_metric_settings: dict):
    """
    Sets a custom optization metric in a ml_task.
    
    :param ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
    
    :param custom_metric_settings: dict: Dictionary containing the settings of the custom metric. 
        It must have the keys:
           - 'metric_function_definition_code' that maps to the [str] Code for the custom optimisation metric 
           - 'greater_is_better' that maps to a [bool] value precising whether the custom metric function 
               returns a score (True, default) or a loss (False). Score functions return higher values as the 
               model improves, whereas loss functions return lower values.
           - 'use_probas': that maps to a [bool] value that, if True, will use the classes' probas or the predicted value (for classification).
        
        Example: 
        {'code': '\ndef score(y_valid, y_pred):\n    diff = y_valid - y_pred\n    wape = 100 * diff.abs().sum()/y_valid.sum()\n    return wape\n',
         'greater_is_better': False,
         'use_probas': False}
    """
    add_custom_evaluation_metric_in_ml_task(ml_task_settings, custom_metric_settings)
    ml_task_settings.get_raw()["modeling"]["metrics"]["evaluationMetric"] = "CUSTOM"
    ml_task_settings.get_raw()["modeling"]["metrics"]["customEvaluationMetricName"] = custom_metric_settings["name"]
    ml_task_settings.save()
    pass


def add_custom_evaluation_metric_in_ml_task(ml_task_settings, custom_metric_settings: dict):
    """
    Adds a custom metric to evaluate the model in a ml_task.
    
    :param ml_task_settings: dataikuapi.dss.ml.DSS[MLTaskType]MLTaskSettings: DSS MLTask settings object.
    
    :param custom_metric_settings: dict: Dictionary containing the settings of the custom metric. 
        It must have the keys:
         - 'metric_function_definition_code' that maps to the [str] Code for the custom optimisation metric 
         - 'greater_is_better' that maps to a [bool] value precising whether the custom metric function 
             returns a score (True, default) or a loss (False). Score functions return higher values as the 
             model improves, whereas loss functions return lower values.
         - 'use_probas': that maps to a [bool] value that, if True, will use the classes' probas or the predicted 
    
      Example: 
      {'name': 'Weighted Absolute Percentage Error (WAPE)',
       'code': '\ndef score(y_valid, y_pred):\n    diff = y_valid - y_pred\n    wape = 100 * diff.abs().sum()/y_valid.sum()\n    return wape\n',
       'description': 'The Weighted Absolute Percentage Error (WAPE) is a metric used to evaluate the accuracy of forecasts \nor predictions.',
       'greater_is_better': False,
       'use_probas': False}
    """
    ml_task_custom_metrics = ml_task_settings.get_raw()["modeling"]["metrics"]["customMetrics"]
    dss_metric_settings = {
        "name": custom_metric_settings["name"],
        "metricCode": custom_metric_settings["code"],
        "description": custom_metric_settings.get("description"),
        "greaterIsBetter": custom_metric_settings["greater_is_better"],
        "needsProbability": custom_metric_settings["use_probas"]
    }
    if dss_metric_settings not in ml_task_custom_metrics:
        ml_task_custom_metrics.append(dss_metric_settings)
    ml_task_settings.get_raw()["modeling"]["metrics"]["customMetrics"] = ml_task_custom_metrics
    ml_task_settings.save()
    pass
