import copy

from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.keys import AppKeys


class InstanceInsert():
    """
    todo restructure this class and change the variable names
    """

    def incorrect_list(self):
        return self.incorrects

    def correct_list(self):
        return self.list_of_dicts

    def correct_list_vms(self):
        return self.correct

    def __init__(self, dictionary):
        result = list()

        names = Dictionary.get_value(dictionary, AppKeys.instances, default=list())

        search_result = GlobalSearch(names)
        self.correct = search_result.get_correct_list()
        for each in search_result.get_correct_list():
            vm_instance = copy.deepcopy(dictionary)
            Dictionary.remove_key(vm_instance, AppKeys.instances)
            Dictionary.set_value(vm_instance, AppKeys.instance, each)
            result.append(vm_instance)

        self.list_of_dicts = result

        self.incorrects = search_result.get_incorrect_list()
