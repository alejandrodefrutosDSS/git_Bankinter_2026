from dku_utils.type_checking import (DSSProject, DSSLibraryFolder,
check_object_is_project, object_is_library_file, object_is_library_folder)
from dku_utils.python_utils.python_scripts import extract_entities_from_python_script


class dkuLibsCrawler:
    """
    Handles project libraries to easily index files and python entities.
    """
    
    def __init__(self, project: DSSProject, project_libraries_root="python", index_python_file_entities: bool=True):
        """
        :param project: DSSProject: A handle to interact with a project on the DSS instance.
        :param project_libraries_root: str: Root of the project libraries to start from in order to index files.
        :param index_python_file_entities: bool: Precises whether the python file entities (classes, functions, constants)
            should be indexed or not.
        """
        check_object_is_project(project)
        self.project = project
        self.library = self.project.get_library()
        self.libraries_root = self.library.get_folder(project_libraries_root)
        self.directories = []
        self.indexed_directories_paths = []
        self.indexed_files = []
        self.indexed_file_names = []
        self.indexed_file_paths = []
        self.directories_to_crawl = []
        self.indexed_python_files_entities = None
        self.indexed_python_entity_types = None
        self.crawl_library()
        if index_python_file_entities:
            self.index_all_python_file_entities()
        pass   
    
    def crawl_library(self):
        """
        Crawls through the library to index directories and files.
        """
        root_sub_directories, root_files = self.get_sub_directories_and_files(self.libraries_root)
        self.directories.append(self.libraries_root)
        if isinstance(root_files, list):
            self.indexed_files += root_files
            self.update_file_names()
        
        self.directories_to_crawl = root_sub_directories.copy()
        while len(self.directories_to_crawl) > 0:
            directories_to_remove = []
            found_directories = []
            for directory in self.directories_to_crawl:                
                sub_directories, files = self.get_sub_directories_and_files(directory)
                
                if directory not in self.directories:
                    self.directories.append(directory)
                if directory not in directories_to_remove:
                    directories_to_remove.append(directory)
                
                if isinstance(sub_directories, list):
                    found_directories += sub_directories
                
                if isinstance(files, list):
                    self.indexed_files += files
                    self.update_file_names()
            
            for directory_to_remove in directories_to_remove:
                if directory_to_remove in self.directories_to_crawl:
                    self.directories_to_crawl.remove(directory_to_remove)
            
            for found_directory in found_directories:
                if found_directory not in self.directories_to_crawl:
                    self.directories_to_crawl.append(found_directory)
        self.indexed_directories_paths = [library_node.path for library_node in self.directories]
        self.indexed_file_paths = [library_node.path for library_node in self.indexed_files]
        print(f"All repository has been successfully crawled, staring from '{self.libraries_root.path}'")
        pass

    def get_sub_directories_and_files(self, library_node: DSSLibraryFolder):
        """
        Retrieves sub-directories and files for a given library node.
        
        :param library_node: DSSLibraryFolder: Library node to retrieve sub-directories and files from.

        :return: directory_sub_directories: list: List of 'DSSLibraryFolder' that are childs of the library node. 
        :return: directory_files: list: List of 'DSSLibraryFile' that are childs of the library node.
        """
        print(f"Crawling directory: {library_node.path} ...")
        directory_sub_directories = []
        directory_files = []
        folder_children = list(library_node.children)
        for element in folder_children:
            if object_is_library_folder(element):
                directory_sub_directories.append(element)
            elif object_is_library_file(element):
                directory_files.append(element)
        return directory_sub_directories, directory_files
    
    def read_file_content(self, file_path: str):
        """
        Reads the content of a file given its path.
        
        :param file_path: str: Path of the file to read content from.
        :return: file_string: str: Content of the file.
        """
        file_string = self.library.get_file(file_path).read()
        return file_string
    
    def index_all_python_file_entities(self):
         """
         Indexes Python entities (classes, functions, constants) for all Github repository Python files in the indexed file paths.
         """
         self.indexed_python_files_entities, self.indexed_python_entity_types = self.index_python_file_entities(self.indexed_file_paths)
         pass

    def index_python_file_entities(self, list_of_file_paths: list):
        """
        Indexes Python entities (constants, functions, classes) for a given list of python file paths.
        
        :param list_of_file_paths: list: Paths of the Python files to index entities for.

        :return: python_files_entities: list: List of all the Python file entities found in the project library.
        :return: entity_types: list: List of the distinct type of entities found in the project library.
        """
        python_files_entities = {}
        entity_types = set()
        for file_path in list_of_file_paths:
            if ".py" in file_path:
                print(f"Indexing file '{file_path}' ...")
                file_content = self.read_file_content(file_path)
                python_string_body_entities = extract_entities_from_python_script(file_content, ["constants", "functions", "classes"])
                for body_entity in python_string_body_entities:
                    entity_name = body_entity["name"]
                    entity_type = body_entity["type"]
                    entity_types.add(body_entity["type"])
                    if entity_name not in python_files_entities.keys():
                        python_files_entities[entity_name] = []
                    python_files_entities[entity_name].append({"type": entity_type, "path": file_path})
        entity_types = list(entity_types)
        return python_files_entities, entity_types
    
    def get_file_paths(self, file_name: str):
        """
        Retrieves the paths of a project library file given its name.
        
        :param file_name: str: Name of the file to retrieve paths for.
        :return: file_paths: list: Paths where the file was found in the project library.
        """
        file_paths = []
        for library_file_name, library_file_path in zip(self.indexed_file_names, self.indexed_file_paths):
            if library_file_name == file_name:
                file_paths.append(library_file_path)
        return file_paths
    
    def update_file_names(self):
        """
        Updates the list of indexed file names.
        """
        self.indexed_file_names = [library_file.name for library_file in self.indexed_files]
        pass