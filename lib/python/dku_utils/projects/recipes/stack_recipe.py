import dataikuapi
from dku_utils.projects.datasets.dataset_commons import create_dataset_in_connection
from .recipe_commons import get_recipe_settings_and_dictionary
from dku_utils.type_checking import DSSProject, check_object_is_project


def instantiate_stack_recipe(project: DSSProject, recipe_name: str, recipe_input_datasets: list,
                             recipe_output_dataset_name: str, connection_name: str):
    """
    Instantiates a stack recipe in the flow.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param recipe_input_datasets: list: List containing all recipe input dataset names. 
    :param recipe_output_dataset_name: str: Name of the dataset that must be the recipe output.
    :param :connection_name: str: Name of the recipe output dataset connection.
    """
    check_object_is_project(project)
    print("Creating stack recipe '{}' ...".format(recipe_name))
    builder = dataikuapi.StackRecipeCreator(recipe_name, project)
    for dataset_name in recipe_input_datasets:
        builder.with_input(dataset_name)
        pass    
    create_dataset_in_connection(project, recipe_output_dataset_name, connection_name)
    builder.with_output(recipe_output_dataset_name)
    builder.build()
    print("Stack recipe '{}' sucessfully created!".format(recipe_name))
    pass


def set_stack_recipe_origin_column(project: DSSProject, recipe_name: str, origin_column_name: str,
                                   sorted_labels_for_origin_column: list):
    """
    Configures the 'Origin column' section of a stack recipe.

    :param project: DSSProject: A handle to interact with a project on the DSS instance.
    :param recipe_name: str: Name of the recipe.
    :param origin_column_name: str: Name of the origin column flagging each row datasource origin.
    :param sorted_labels_for_origin_column: list: List containing the labels to associate rows coming from
        each dataset. Labels should be in the same order as the recipe's input they refer to.
    """
    check_object_is_project(project)
    recipe = project.get_recipe(recipe_name)
    recipe_settings, __ = get_recipe_settings_and_dictionary(project, recipe_name, False)
    recipe_json_payload = recipe_settings.get_json_payload()
    recipe_json_payload["addOriginColumn"] = True
    recipe_json_payload["originColumnName"] = origin_column_name
    
    recipe_new_virtual_inputs = []
    loop_indexes = range(len(sorted_labels_for_origin_column))
    for loop_index, origin_column_label in zip(loop_indexes, sorted_labels_for_origin_column):
        recipe_virtual_input = {'preFilter': {'distinct': False, 'enabled': False},
                                'originLabel': origin_column_label,
                                'index': loop_index}
        recipe_new_virtual_inputs.append(recipe_virtual_input)
    
    recipe_json_payload["virtualInputs"] = recipe_new_virtual_inputs
    recipe_settings.set_json_payload(recipe_json_payload)
    recipe_settings.save()
    recipe.compute_schema_updates()
    pass
 

class programmaticStackHandler:
    """
    This class allows to programmatically update DSS 'vstack' recipes.
    """

    def __init__(self, project: DSSProject, recipe_name: str, main_dataset_name: str, main_dataset_origin_column_flag: str="",
                 union_type: str="UNION"):
        """        
        :param project: DSSProject: A handle to interact with a project on the DSS instance.
        :param recipe_name: str: Name of the recipe.
        :param main_dataset_name: str: Name of the recipe's main dataset (<-> The first dataset selected in the recipe).
        :param main_dataset_origin_column_flag: str: Value flagging the main dataset rows
        :param union_type: str: Types of the unions to apply on the main dataset.
            Union types supported by this class are:
                - 'UNION': Equivalent of the option 'Union of input schemas' in the visual recipe.
                - 'INTERSECT': Equivalent the option 'Intersection of input schemas' in the visual recipe.
        """
        check_object_is_project(project)
        self.project = project
        self.recipe_settings = project.get_recipe(recipe_name).get_settings()
        self.recipe_payload = self.recipe_settings.get_json_payload()
        self.recipe_input_dataset_names = []
        self.recipe_input_datasets_virtual_input_ids = {}
        self.recipe_last_virtual_input_id = 0 # Refers to the table associated with the recipe's inputs (<-> Input dataset unique identifier). 
        self.recipe_last_union_input_id = 0 # Refers to the inputs as we see them in the "Selected columns" and "Origin column" (<-> The same dataset can be added several times in a union).
        self.main_dataset_name = main_dataset_name
        self.main_dataset_origin_column_flag = main_dataset_origin_column_flag
        self.union_type = union_type
        self.initialize_recipe_settings()
        pass
    
    def initialize_recipe_settings(self):
        """
        Initializes all recipe's settings based on the main dataset.
        """
        self.update_union_type()
        self.initialize_recipe_inputs()
        self.initialize_recipe_virtual_inputs()
        self.initialize_origin_column()
        self.initialize_post_union_filter_expression()
        self.update_recipe_definition()
        pass

    def update_union_type(self):
        """
        Updates the union types of the recipe.
        """
        self.recipe_payload["mode"] = self.union_type
        pass

    def initialize_recipe_inputs(self):
        """
        Initializes the recipe's inputs settings by adding its main dataset.
        """
        self.recipe_settings.data["recipe"]["inputs"]["main"]["items"] = []
        self.add_input_in_recipe(self.main_dataset_name)
        pass
    
    def initialize_recipe_virtual_inputs(self):
        """
        Initializes the recipe's virtual inputs with the virtual input associated with the main dataset.
        """
        stack_recipe_virtual_input = self.compute_virtual_input(None,
                                                               self.main_dataset_name,
                                                               self.recipe_last_virtual_input_id,
                                                               self.main_dataset_origin_column_flag)
        self.recipe_input_datasets_virtual_input_ids = {self.main_dataset_name: self.recipe_last_virtual_input_id}
        self.recipe_payload["virtualInputs"] = [stack_recipe_virtual_input]
        pass
    
    def initialize_origin_column(self):
        """
        Initializes the recipe's origin columns.
        """
        self.recipe_payload["addOriginColumn"] = False
        pass

    def initialize_post_union_filter_expression(self):
        self.recipe_payload["postFilter"] = {}
        self.recipe_payload["postFilter"]["uiData"] = {}
        self.recipe_payload["postFilter"]["uiData"]["conditions"] = []
        self.recipe_payload["postFilter"]["expression"] = ""
        self.recipe_payload["postFilter"]["enabled"] = False
        pass
    
    def compute_virtual_input(self, pre_filter: dict, dataset_name: str, virtual_index: int, origin_column_flag: str=None):
        """
        Computes the settings associated with a stack recipe virtual inputs. 
            Virtual inputs directly refers to the table associated with the recipe's inputs.
        
        :param pre_filter: dict: Pre filter applied on the virtual input.
        :param dataset_name: str: Name of the dataset to stack.
        :param virtual_index: int: Dataset virtual index.
        :param: origin_column_flag: str: Value flagging the virtual input to union rows.

        :returns: stack_recipe_virtual_input: dict: A stack recipe virtual input.
        """
        if (pre_filter == None) or (pre_filter == {}):
            pre_filter = {'distinct': False, 'enabled': False}
        if (origin_column_flag is None) or (origin_column_flag == ""):
            origin_label = dataset_name
        else:
            origin_label = origin_column_flag
        stack_recipe_virtual_input = {'preFilter': pre_filter,
                                     'originLabel': origin_label,
                                     'index': virtual_index}
        return stack_recipe_virtual_input
    
    def check_if_recipe_input_dataset_exists(self, dataset_name: str):
        """
        Checks if a dataset is already defined in the recipe settings inputs.

        :param dataset_name: str: Name of the dataset.

        :returns: recipe_input_dataset_exists: bool: Boolean precising if the dataset
            is already among the recipe inputs.
        """
        recipe_input_dataset_exists = (dataset_name in self.recipe_input_dataset_names)
        return recipe_input_dataset_exists

    def add_input_in_recipe(self, dataset_name: str):
        """
        Adds a dataset to the inputs of a recipe 

        :param dataset_name: str: Name of the dataset.
        """
        self.recipe_input_dataset_names.append(dataset_name)
        self.recipe_settings.data["recipe"]["inputs"]["main"]["items"].append(
            {'deps': [], 'ref': dataset_name}
        )
        pass

    def check_if_virtual_input_dataset_exists(self, dataset_name: str):
        """
        Checks if a dataset is associated with a recipe virtual input/

        :param dataset_name: str: Name of the dataset.

        :returns: recipe_virtual_input_dataset_exists: bool: Boolean precising if the dataset
            already has a virtual input.
        """
        recipe_virtual_input_dataset_exists = (dataset_name in self.recipe_input_datasets_virtual_input_ids.keys())
        return recipe_virtual_input_dataset_exists

    def update_virtual_input_ids(self, dataset_name: str):
        """
        Updates the class virtual input IDs. 
            Virtual inputs directly refers to the table associated with the recipe's inputs.
        
        :param dataset_name: str: Name of the dataset.
        """
        self.recipe_last_virtual_input_id += 1
        self.recipe_input_datasets_virtual_input_ids[dataset_name] = self.recipe_last_virtual_input_id
        pass

    def update_virtual_inputs(self, dataset_name: str, origin_column_flag: str):
        """
        Updates recipe virtual input settings.
        
        :param dataset_name: str: Name of the dataset.
        :param: origin_column_flag: str: Value flagging the virtual input to union rows.
        """
        dataset_virtual_input_id = self.recipe_input_datasets_virtual_input_ids[dataset_name]
        stack_recipe_virtual_input = self.compute_virtual_input(None,
                                                               dataset_name,
                                                               dataset_virtual_input_id,
                                                               origin_column_flag)
        self.recipe_payload["virtualInputs"].append(stack_recipe_virtual_input)
        pass

    def update_union_input_ids(self):
        """
        Updates the class stack input IDs.
            Stack input IDs refers to the inputs as we see them in the "Stack" and "Selected columns"
            (<-> The same dataset can be added several time in a stack).
        """
        self.recipe_last_union_input_id += 1
        pass
        
    def update_recipe_definition(self):
        """
        Updates and save the stack recipe's definition.
        """
        self.recipe_settings.set_json_payload(self.recipe_payload)
        self.recipe_settings.save()
        pass
    
    def add_one_union_on_main_dataset(self, dataset_to_union_name: str, origin_column_flag: str=None):
        """
        Applies all recipe settings updates in order to programatically set a stack on the recipe.

        :param: dataset_to_union_name: str: Name of a dataset to stack on the recipe's 'main dataset'.
        :param: origin_column_flag: str: Value flagging the dataset to union rows.
        """
        recipe_input_dataset_exists = self.check_if_recipe_input_dataset_exists(dataset_to_union_name)
        if not recipe_input_dataset_exists:
            self.add_input_in_recipe(dataset_to_union_name)
        recipe_virtual_input_dataset_exists = self.check_if_virtual_input_dataset_exists(dataset_to_union_name)
        if not recipe_virtual_input_dataset_exists:
            self.update_virtual_input_ids(dataset_to_union_name)
        self.update_virtual_inputs(dataset_to_union_name, origin_column_flag)
        self.update_union_input_ids()
        self.update_recipe_definition()
        pass
    
    def activate_origin_column_flagging(self, origin_column_name: str):
        """
        Activates the use of the 'Origin column' flagging each rows of the datasets involved in the union.

        :param: origin_column_name: str: Name of the 'Origin column'.
        """
        self.recipe_payload["addOriginColumn"] = True
        self.recipe_payload["originColumnName"] = origin_column_name
        self.update_recipe_definition()
        pass
    
    def set_post_union_filter_expression(self, post_union_filter_formula_expression: str):
        """
        Sets the post stack rows filtering expression, with a DSS formula.
        
        :param post_union_filter_formula_expression: str: Expression of the formula leading to the computed column, following the 
        DSS formula language (https://doc.dataiku.com/dss/latest/formula/index.html).
        """
        self.recipe_payload["postFilter"]["uiData"]["mode"] = "CUSTOM"
        post_union_filter_is_disabled = (self.recipe_payload["postFilter"]["enabled"]==False)
        if post_union_filter_is_disabled:
            self.recipe_payload["postFilter"]["enabled"] = True
        self.recipe_payload["postFilter"]["expression"] = post_union_filter_formula_expression
        self.update_recipe_definition()
        pass
    pass