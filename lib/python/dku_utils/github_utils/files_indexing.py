import base64
import requests
from dku_utils.python_utils.python_scripts import extract_entities_from_python_script


class gitHubRepoCrawler:
    """
    Handles Github repositories to easily index files and python entities.
    """
    
    def __init__(self, repository_owner: str, repository_name: str, repository_root: str="/", github_token: str="", 
                 repository_branch: str="main", index_python_file_entities: bool=True):
        """
        :param repository_owner: str: Owner of the Github repository.
            The owner is available right after 'https://github.com/' in the URL of the repository.
        :param repository_name: str: Name of the Github repository.
        :param repository_root: str: Root of the Github reprository to start from in order to index files.
        :param github_token: str: Github token to use for authentification. The following URL explains how 
            to create a github token: https://docs.github.com/en/enterprise-server@3.6/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
        :param repository_branch: str: Branch of the Github repository.
        :param index_python_file_entities: bool: Precises whether the python file entities (classes, functions, constants)
            should be indexed or not.
        """
        self.base_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}'
        self.github_token = github_token
        self.repository_root = repository_root
        self.indexed_directories_paths = []
        self.indexed_file_paths = []
        self.indexed_file_names = []
        self.directories_to_crawl = []
        self.indexed_python_files_entities = None
        self.indexed_python_entity_types = None
        self.repository_branch = repository_branch
        self.crawl_repository()
        if index_python_file_entities:
            self.index_all_python_file_entities()
        pass   
    
    def crawl_repository(self):
        """
        Crawls through the Github repository to index directories and files.
        """
        root_sub_directories, root_files = self.get_sub_directories_and_files(self.repository_root)
        self.indexed_directories_paths.append(self.repository_root)
        if isinstance(root_files, list):
            self.indexed_file_paths += root_files
            self.update_file_names()
        
        self.directories_to_crawl = root_sub_directories.copy()
        while len(self.directories_to_crawl) > 0:
            directories_to_remove = []
            found_directories = []
            for directory in self.directories_to_crawl:                
                sub_directories, files = self.get_sub_directories_and_files(directory)
                
                if directory not in self.indexed_directories_paths:
                    self.indexed_directories_paths.append(directory)
                if directory not in directories_to_remove:
                    directories_to_remove.append(directory)
                
                if isinstance(sub_directories, list):
                    found_directories += sub_directories
                
                if isinstance(files, list):
                    self.indexed_file_paths += files
                    self.update_file_names()
            
            for directory_to_remove in directories_to_remove:
                if directory_to_remove in self.directories_to_crawl:
                    self.directories_to_crawl.remove(directory_to_remove)
            
            for found_directory in found_directories:
                if found_directory not in self.directories_to_crawl:
                    self.directories_to_crawl.append(found_directory)
        print(f"All repository has been successfully crawled, staring from '{self.repository_root}'")
        pass
    
    def get_request_url(self, content_path):
        """
        Computes a request URL to access the Github repository.
        """
        request_url = f'{self.base_url}/contents/{content_path}?ref={self.repository_branch}'
        return request_url
    
    def get_request_header(self):
        """
        Computes a request header to access the Github repository.
        """
        request_header = {'Authorization': f'Bearer {self.github_token}'}
        return request_header

    def get_sub_directories_and_files(self, directory_path: str):
        """
        Retrieves sub-directories and files for a given Github repository parent directory.
        
        :param directory_path: str: Directory to retrieve sub-directories and files from.

        :return: directory_sub_directories: list: List of directories that are childs of the parent directory. 
        :return: directory_files: list: List of files that are childs of the parent directory.
        """
        print(f"Crawling directory: {directory_path} ...")
        directory_sub_directories = []
        directory_files = []
        response = requests.get(self.get_request_url(directory_path), headers=self.get_request_header())
        if response.status_code == 200:
            response = response.json()
            for element in response:
                element_type = element["type"]
                if element_type == "dir":
                    directory_sub_directories.append(element["path"])
                elif element_type == "file":
                    directory_files.append(element["path"])
        
            return directory_sub_directories, directory_files
        else:
            return None, None
    
    def read_file_content(self, file_path: str):
        """
        Reads the content of a Github repository file given its path.
        
        :param file_path: str: Path of the file to read content from.
        :return: file_string: str: Content of the file.
        """
        response = requests.get(self.get_request_url(file_path), headers=self.get_request_header())
        file_string = ""
        if response.status_code == 200:
            file_string = base64.b64decode(response.json().get('content'))
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

        :return: python_files_entities: list: List of all the Python file entities found in the Github repository.
        :return: entity_types: list: List of the distinct type of entities found in the Github repository.
        """
        python_files_entities = {}
        entity_types = set()
        for file_path in list_of_file_paths:
            if ".py" in file_path:
                print(f"Indexing file '{file_path}' ...")
                file_content = self.read_file_content(file_path).decode("utf-8")
                python_string_body_entities = extract_entities_from_python_script(file_content, ["constants", "functions", "classes"])
                for body_entity in python_string_body_entities:
                    entity_name = body_entity["name"]
                    entity_type = body_entity["type"]
                    entity_types.add(body_entity["type"])
                    if entity_name not in python_files_entities.keys():
                        python_files_entities[entity_name] = []
                    python_files_entities[entity_name].append({"type": entity_type, "location": file_path})
                
        entity_types = list(entity_types)
        return python_files_entities, entity_types
    
    def get_file_paths(self, file_name: str):
        """
        Retrieves the paths of a Github repository file given its name.
        
        :param file_name: str: Name of the file to retrieve paths for.
        :return: file_paths: list: Paths where the file was found in the Github repository.
        """
        file_paths = []
        for repository_file_name, repository_file_path in zip(self.indexed_file_names, self.indexed_file_paths):
            if repository_file_name == file_name:
                file_paths.append(repository_file_path)
        return file_paths

    def update_file_names(self):
        """
        Updates the list of indexed file names.
        """
        self.indexed_file_names = [file_path.split('/')[-1] for file_path in self.indexed_file_paths]
        pass