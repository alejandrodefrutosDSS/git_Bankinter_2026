from dku_utils.type_checking import DSSProject, check_object_is_project
from dku_utils.projects.deployed_models.deployed_model_commons import get_deployed_model_id
from dku_utils.projects.folders.folder_commons import get_managed_folder_id


def compute_object_to_share_settings(
    object_name: str, object_type: str, rules: list, enable_quick_sharing: bool = False
):
    """
    Structures a dictionary with the settings to share a project object.

    :param: object_name: str: Name of the project object to share.
    :param: object_type: str: Type of the project object to share.
    :param: rules: list: List of the sharing rules.
    :param: enable_quick_sharing: bool: Is the quick sharing activated for this project object.

    :returns: object_to_share_settings dict: Setting to share the project object.
    """
    object_to_share_settings = {
        "type": object_type,
        "localName": object_name,
        "quickSharingEnabled": enable_quick_sharing,
        "rules": rules,
    }
    return object_to_share_settings


def share_object_with_name(
    project: DSSProject,
    object_name: str,
    object_type: str,
    target_project_key: str,
    enable_quick_sharing=False,
):
    """
    Shares a project object with another targeted project based on its name and type.

    :param: project DSSProject: Project owning the object to share.
    :param: object_name str: Name of the project object to share.
    :param: object_type str: Type of the project object to share (must be in ["DATASET","MANAGED_FOLDER", "SAVED_MODEL"]).
    :param: target_project_key str: Project key of the target project where to share the project object.
    :param: enable_quick_sharing bool : Is the quick sharing activated for this element.
    """
    check_object_is_project(project)
    assert object_type in [
        "DATASET",
        "MANAGED_FOLDER",
        "SAVED_MODEL",
    ], f'{object_type} is not in ["DATASET","MANAGED_FOLDER", "SAVED_MODEL"]'

    if object_type == "MANAGED_FOLDER":
        object_id = get_managed_folder_id(project, object_name)
    elif object_type == "SAVED_MODEL":
        object_id = get_deployed_model_id(project, object_name)
    else:
        object_id = object_name

    share_object_with_id(
        project,
        object_id,
        object_type,
        target_project_key=target_project_key,
        enable_quick_sharing=enable_quick_sharing,
    )


def share_object_with_id(
    project: DSSProject,
    object_id: str,
    object_type: str,
    target_project_key: str,
    enable_quick_sharing=False,
):
    """
    Shares a project object with another targeted project based on its id and type.

    :param: project DSSProject: Project owning the object to share.
    :param: object_id str: ID of the project object to share.
    :param: object_type str: Type of the project object to share.
    :param: target_project_key str: Project key of the target project where to share the project object.
    :param: enable_quick_sharing bool : Is the quick sharing activated for this element.
    """
    check_object_is_project(project)
    project_settings = project.get_settings()
    previous_shared_objects = project_settings.get_raw()["exposedObjects"]["objects"]

    # we check if this specific object is already shared to avoid erasing previous sharing
    matching_shared_objects = list(
        filter(
            lambda dct: (dct["localName"] == object_id)
            and (dct["type"] == object_type),
            previous_shared_objects,
        )
    )
    unmatching_shared_objects = list(
        filter(
            lambda dct: (dct["localName"] != object_id) or (dct["type"] != object_type),
            project_settings.get_raw()["exposedObjects"]["objects"],
        )
    )

    if len(matching_shared_objects) > 0:
        # there's previous sharing
        base_rules = matching_shared_objects[0]["rules"]
        already_shared_objects = list(
            filter(lambda dct: dct["targetProject"] == target_project_key, base_rules)
        )
        if len(already_shared_objects) > 0:
            # this object is already shared to the target project
            return None
    else:
        base_rules = []

    new_rule = {"targetProject": target_project_key, "appearOnFlow": True}
    base_rules.append(new_rule)

    object_sharing_settings = compute_object_to_share_settings(
        object_name=object_id,
        object_type=object_type,
        rules=base_rules,
        enable_quick_sharing=enable_quick_sharing,
    )

    unmatching_shared_objects.append(object_sharing_settings)
    project_settings.get_raw()["exposedObjects"]["objects"] = unmatching_shared_objects

    project_settings.save()


def unshare_object_with_name(
    project: DSSProject,
    object_name: str,
    object_type: str,
    target_project_key: str,
    enable_quick_sharing=False,
):
    """
    Unshares a project object from a targeted project, based on its name and type .

    :param: project DSSProject: Project owning the object to share.
    :param: object_name str: Name of the project object to unshare.
    :param: object_type str: Type of the project object to unshare (must be in ["DATASET","MANAGED_FOLDER", "SAVED_MODEL"]).
    :param: target_project_key str: Project key of the project where the object is shared.
    :param: enable_quick_sharing bool : Is the quick sharing activated for this element.
    """
    check_object_is_project(project)
    assert object_type in [
        "DATASET",
        "MANAGED_FOLDER",
        "SAVED_MODEL",
    ], f'{object_type} is not in ["DATASET","MANAGED_FOLDER", "SAVED_MODEL"]'

    if object_type == "MANAGED_FOLDER":
        object_id = get_managed_folder_id(project, object_name)
    elif object_type == "SAVED_MODEL":
        object_id = get_deployed_model_id(project, object_name)
    else:
        object_id = object_name

    unshare_object_with_id(
        project,
        object_id,
        object_type,
        target_project_key=target_project_key,
        enable_quick_sharing=enable_quick_sharing,
    )


def unshare_object_with_id(
    project: DSSProject,
    object_id: str,
    object_type: str,
    target_project_key: str,
    enable_quick_sharing=False,
):
    """
    Unshares a project object from a targeted project, based on its name and type.

    :param: project DSSProject: Project owning the object to share.
    :param: object_id str: ID of the project object to unshare.
    :param: object_type str: Type of the project object to unshare (must be in ["DATASET","MANAGED_FOLDER", "SAVED_MODEL"]).
    :param: target_project_key str: Project key of the project where the object is shared.
    :param: enable_quick_sharing bool : Is the quick sharing activated for this element.
    """
    check_object_is_project(project)
    project_settings = project.get_settings()
    previous_shared_objects = project_settings.get_raw()["exposedObjects"]["objects"]

    # we check if this specific object is already shared to avoid erasing previous sharing
    matching_shared_objects = list(
        filter(
            lambda dct: (dct["localName"] == object_id)
            and (dct["type"] == object_type),
            previous_shared_objects,
        )
    )

    unmatching_shared_objects = list(
        filter(
            lambda dct: (dct["localName"] != object_id) or (dct["type"] != object_type),
            project_settings.get_raw()["exposedObjects"]["objects"],
        )
    )

    if len(matching_shared_objects) > 0:
        # there's previous sharing
        base_rules = matching_shared_objects[0]["rules"]
        other_project_rules = list(
            filter(lambda dct: dct["targetProject"] != target_project_key, base_rules)
        )
    else:
        # Object is not already shared
        return None

    if len(other_project_rules) > 0:
        # there's still project where this object is shared
        # compute a new dict to replace in the project settings
        object_sharing = compute_object_to_share_settings(
            object_name=object_id,
            object_type=object_type,
            rules=other_project_rules,
            enable_quick_sharing=enable_quick_sharing,
        )
        unmatching_shared_objects.append(object_sharing)

    project_settings.get_raw()["exposedObjects"]["objects"] = unmatching_shared_objects
    project_settings.save()