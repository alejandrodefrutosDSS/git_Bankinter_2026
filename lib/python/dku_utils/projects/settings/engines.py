from dku_utils.type_checking import DSSProject, check_object_is_project


def get_project_engines_priority(project: DSSProject):
    """Retrieves the engines priority set in a project settings.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    
    :returns: flow_engines_priority: str: The prokect's engines priority.
    """
    check_object_is_project(project)
    flow_engines_priority = project.get_settings().settings["settings"]["recipeEnginesPreferences"]["enginesPreferenceOrder"]
    return flow_engines_priority