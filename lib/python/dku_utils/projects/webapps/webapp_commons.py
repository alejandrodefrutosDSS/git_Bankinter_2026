from dku_utils.type_checking import DSSProject, check_object_is_project


def check_webapp_exists(project: DSSProject, webapp_id: str):
    """Checks whether a webapp exists in a project or not.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param webapp_id: str: The ID of the webapp
    """
    check_object_is_project(project)
    project_webapps = [metadata.get("id") for metadata in project.list_webapps()]
    if webapp_id not in project_webapps:
        error_message = f"You asked for the webapp_id '{webapp_id}' that does not exist. "\
        f"The available project webapp IDs are :'{project_webapps}'"
        raise ValueError(error_message)
    pass
    

def get_webapp_settings_and_dictionary(project: DSSProject, webapp_id: str):
    """Retrieves the settings of a project webapp.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param webapp_id: str: The ID of the webapp

    :returns: webapp_settings: dataikuapi.dss.webapp.DSSWebAppSettings: Settings for a recipe.
    :returns: webapp_settings_dict: dict: Dictionary containing the webapp settings. 
    """
    check_object_is_project(project)
    check_webapp_exists(project, webapp_id)
    webapp = project.get_webapp(webapp_id)
    webapp_settings = webapp.get_settings()
    webapp_settings_dict = webapp_settings.get_raw()
    return webapp_settings, webapp_settings_dict


def get_webapp_config(project: DSSProject, webapp_id: str):
    """Retrieves the configuration of a project webapp.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param webapp_id: str: The ID of the webapp

    :returns: webapp_config: dict: The configuration of the webapplication. 
    """
    check_object_is_project(project)
    check_webapp_exists(project, webapp_id)
    __, webapp_settings_dict = get_webapp_settings_and_dictionary(project, webapp_id)
    webapp_config = webapp_settings_dict["config"]
    return webapp_config


def get_webapp_backend_state_and_log_tail(project: DSSProject, webapp_id: str):
    """Retrieves the webapp backend state as well the backend log tail.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param webapp_id: str: The ID of the webapp

    :returns: webapp_backend_state: str: Precises the webapp state:
        - 'BACKEND_RUNNING': If the webapp backend is running.
        - 'BACKEND_STOPPED': If the webapp backend is stopped.
        
    :returns: backend_log_tail: str: The webapp backend log tail.
    """
    check_object_is_project(project)
    check_webapp_exists(project, webapp_id)
    webapp = project.get_webapp(webapp_id)
    webapp_state = webapp.get_state()
    webapp_backend_state = "BACKEND_STOPPED"
    webapp_is_running = webapp_state.running
    if webapp_is_running:
        webapp_backend_state = "BACKEND_RUNNING"
        if "currentLogTail" in webapp_state.state.keys():
            backend_log_tail = "\n".join(
                line
                for line in webapp_state.state.get("currentLogTail", {})\
                .get("lines", []))
        else:
            backend_log_tail = "No log tail: Backend might still be starting..."
    else:
        backend_log_tail = "\n".join(
            line 
            for line in webapp_state.state.get("lastCrashLogTail", {})\
            .get("lines", []))
    return webapp_backend_state, backend_log_tail