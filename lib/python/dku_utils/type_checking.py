import dataiku
from dataiku.core.dataset import Dataset
from dataiku.core.managed_folder import Folder
from dataiku.core.saved_model import Model
from dataikuapi.dss.dataset import DSSDataset
from dataikuapi.dss.managedfolder import DSSManagedFolder
from dataikuapi.dss.project import DSSProject
from dataikuapi.dss.savedmodel import DSSSavedModel
from dataikuapi.dss.ml import DSSMLTask
from dataikuapi.dss.projectlibrary import DSSLibraryFile, DSSLibraryFolder


def get_object_type_and_id(object):
    """
    Retrieves a project object type and id.
    
    :param: object: Element to extract type and id.
    :returns: object_type str: Type of the object.
    :returns: object_id str: ID of the object.
    """
    if isinstance(object, DSSDataset):
        return "DATASET", object.id
    elif isinstance(object, Dataset):
        return "DATASET", object.short_name
    elif isinstance(object, DSSManagedFolder):
        return "MANAGED_FOLDER", object.id
    elif isinstance(object, Folder):
        return "MANAGED_FOLDER", object.get_id()
    elif isinstance(object, Model):
        return "SAVED_MODEL", object.get_id()
    elif isinstance(object, DSSSavedModel):
        return "SAVED_MODEL", object.id
    else:
        raise TypeError(f"{type(object)} is not a recognized type for object sharing")
    

def object_is_project(project: DSSProject):
    """
    Precises if an object is a dataiku project or not.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    """
    if isinstance(project, DSSProject):
        return True
    else:
        return False


def check_object_is_project(project: DSSProject):
    """
    Checks if an object is a dataiku project.
    
    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    """
    if object_is_project(project):
        return True
    else:
        raise TypeError(f"The object passed to the function, '{project}' is of type '{type(project)}'. "\
        f"Expected type is '{DSSProject}'! You can get such object using functions " \
            "'get_current_project_and_variables' and 'get_project_and_variables'")


def project_key_exists(project_key: str):
    """
    Precises if a project key exists or not.

    :param project_key: str: The project key of interest.
    """
    all_project_keys = dataiku.api_client().list_project_keys()
    if project_key in all_project_keys:
        return True
    else: 
        return False


def check_project_key_exists(project_key: str):
    """
    Checks if a project key exists on an instance.

    :param project_key: str: The project key of interest.
    """
    if project_key_exists(project_key):
        return True
    else:
        raise ValueError(f"The project key '{project_key}' does not exists on the instance!")
    

def object_is_library_file(library_file: DSSLibraryFile):
    """
    Precises if an object is a dataiku project library file object or not.

    :param library_file: DSSLibraryFile: A library file object.
    """
    if isinstance(library_file, DSSLibraryFile):
        return True
    else:
        return False
    

def object_is_library_folder(library_folder: DSSLibraryFolder):
    """
    Precises if an object is a dataiku project library folder object or not.

    :param library_folder: DSSLibraryFolder: A library folder object.
    """
    if isinstance(library_folder, DSSLibraryFolder):
        return True
    else:
        return False