import dis
import numpy as np
import pandas as pd
import ast


def get_python_script_libraries_import_dataframe(python_script_string: str):
    """
    Retrieves a DataFrame containing all information about the python modules imported in a python script string
    DISCLAIMER: Does not retrieves import done within functions.
    :param python_script_string: str: Any python script.

    :returns: python_script_libraries_import_dataframe: pandas.core.frame.DataFrame: Pandas DataFrame
        containing information about all the imports done in the python script.
    """
    LIBRARY_DEPENDENCIES_SCHEMA = ["imported_from", "imported", "all_import_information"]
    python_string_instructions = dis.get_instructions(python_script_string)
    python_string_import_types = np.array([])
    python_string_import_names = np.array([])
    for instruction in python_string_instructions:
        if "IMPORT" in instruction.opname:
            python_string_import_types = np.append(python_string_import_types, [instruction.opname])
            python_string_import_names = np.append(python_string_import_names, [instruction.argval])
    import_parent_indexes = list(np.where(python_string_import_types=="IMPORT_NAME")[0])
    last_import_parent_index = 0
    all_imports_information = []
    for instruction_index, import_name in enumerate(python_string_import_names):
        instruction_type = python_string_import_types[instruction_index]
        if instruction_type == "IMPORT_STAR":
            import_name = "*"
        import_information = {"imported": import_name}
        if instruction_index in import_parent_indexes:
            last_import_parent_index = instruction_index
            imported_from_name = ''
        else:
            imported_from_name = python_string_import_names[last_import_parent_index]
        
        import_information["imported_from"] = imported_from_name
        all_import_information = imported_from_name
        if imported_from_name != "":
            all_import_information += "."
        all_import_information += import_name
        import_information["all_import_information"] = all_import_information
        all_imports_information.append(import_information)
    python_script_libraries_import_dataframe = pd.DataFrame(all_imports_information)
    try:
        python_script_libraries_import_dataframe = python_script_libraries_import_dataframe[LIBRARY_DEPENDENCIES_SCHEMA]
    except KeyError:
        python_script_libraries_import_dataframe = pd.DataFrame([{"imported_from": "", "imported": "",
                                                                  "all_import_information": ""}], index=[0])
        python_script_libraries_import_dataframe = python_script_libraries_import_dataframe[LIBRARY_DEPENDENCIES_SCHEMA]
    return python_script_libraries_import_dataframe


def extract_entities_from_python_script(python_script: str, entities_to_extract: list):
    """
    Extracts python entities from a string. Extracted entities in the scope of this function are:
        - functions
        - classes
        - constants (DISCLAIMER: Constants have to follow the PEP8 standard and be written in uppercase)
    
    :param python_script: str: Any python script.
    :param entities_to_extract: list: The list of all the python entities to extract. 
        Accepted values are: ['functions', 'classes', 'constants']

    :returns: python_string_body_entities: list: List of 
    """
    tree = ast.parse(python_script)
    python_string_body_entities = []
    for node in ast.walk(tree):
        if node in tree.body:
            if "functions" in entities_to_extract:
                if isinstance(node, ast.FunctionDef):
                    python_string_body_entities.append({"name": node.name, "type": "function"})
            if "classes" in entities_to_extract:
                if isinstance(node, ast.ClassDef):
                    python_string_body_entities.append({"name": node.name, "type": "class"})
            if "constants" in entities_to_extract:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            python_string_body_entities.append({"name": target.id, "type": "constant"})
    return python_string_body_entities