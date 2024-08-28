from libs.utilities.data_structures.dictionary import Dictionary


class Parameter():
    name = 'name'
    displaying_name = 'displaying_name'
    prompt = 'prompt'
    default = 'default'
    confidential = 'confidential'
    stored_in_db = 'stored_in_db'
    physical_server_only = 'physical_server_only'
    check_file = 'check_file'
    check_dir = 'check_dir'

    def __init__(self, parameter_dict):
        self.name = Dictionary.get_value(parameter_dict, Parameter.name)
        self.displaying_name = Dictionary.get_value(parameter_dict, Parameter.displaying_name, default=self.name,
                                                    type=str)
        self.prompt = Dictionary.get_value(parameter_dict, Parameter.prompt, default=None, type=str)
        self.default = Dictionary.get_value(parameter_dict, Parameter.default, default=None, type=str)
        self.confidential = Dictionary.get_value(parameter_dict, Parameter.confidential, default=False)
        self.stored_in_db = Dictionary.get_value(parameter_dict, Parameter.stored_in_db, default=False)
        self.physical_server_only = Dictionary.get_value(parameter_dict, Parameter.physical_server_only, default=False)
        self.check_file = Dictionary.get_value(parameter_dict, Parameter.check_file, default=False, type=bool)
        self.check_dir = Dictionary.get_value(parameter_dict, Parameter.check_dir, default=False, type=bool)
        self.input = None
