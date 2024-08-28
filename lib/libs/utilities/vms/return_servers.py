from libs.lcs_error import LCSError
from libs.utilities.data_structures.dictionary import Dictionary
import copy

from libs.variables.keys import AppKeys


class ReturnServers:

    def __init__(self):
        pass

    @staticmethod
    def return_vms(input_list):
        """
        get a list a vm instances which inside the JBOSS function
        :param input_list:
        :return:
        """
        list_copy = copy.deepcopy(input_list)
        output_dictionary = dict()
        vm_names = list()

        for each in list_copy:
            instances = Dictionary.get_value(each, AppKeys.instances, default=list())
            if (type(instances) == str):
                vm_names.append(instances)
            elif (type(instances) == list):
                vm_names += instances
            else:
                raise LCSError("The instances is neither a list nor a string")

        Dictionary.set_value(output_dictionary, AppKeys.instances, vm_names)

        return output_dictionary
