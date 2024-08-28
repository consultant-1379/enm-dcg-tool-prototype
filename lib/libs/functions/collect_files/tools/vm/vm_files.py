from libs.functions.collect_files.tools.collect_files_superclass import CollectFilesSuperclass
from libs.functions.collect_files.tools.vm.vm_connect_collect import VMConnectCollect
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.utilities.vms.global_search import GlobalSearch
from libs.utilities.vms.instace_insert import InstanceInsert
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys


class VMFiles(CollectFilesSuperclass):
    def __init__(self, function):
        self.vm_instances = InstanceInsert(function)
        self.correct_list = self.vm_instances.correct_list()
        self.correct_vms = self.vm_instances.correct_list_vms()
        self.incorrect_list = self.vm_instances.incorrect_list()
        self.controllers = list()
        files = Dictionary.get_value(function, AppKeys.files)
        self.files = list(dict.fromkeys(files))
        self.vms = Dictionary.get_value(function, AppKeys.instances)

        for each_instance in self.correct_list:
            self.controllers.append(VMConnectCollect(each_instance, function))

        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    @staticmethod
    def server_type():
        return 'vm'

    def run(self):
        # todo print message telling you have started to collect files from some vms
        # todo: collect VM files to the following directory, please see the template at config_templates/collect_files.yml
        # todo: print messages telling the user the files have been collected on some vms
        # todo  double check the following output messages
        vms = GlobalSearch(self.vms).get_correct_list()
        successful_vms = list()
        if len(vms) != 0:
            if 'server.log' in self.files[0].split('/'):
                Output.yellow("\nCollecting", new_line=False, print_trigger=self.print_trigger), Output.white(
                    '[%s' % str(self.files[0]).replace("'", "") + '*]', new_line=False,
                    print_trigger=self.print_trigger), Output.yellow("from the following VMs",
                                                                     print_trigger=self.print_trigger)
                Output.white(str(vms).replace('[', '').replace(']', '').replace("'", ""),
                             print_trigger=self.print_trigger)
            else:
                Output.yellow("\nCollecting", new_line=False, print_trigger=self.print_trigger), Output.white(
                    '%s' % str(self.files).replace("'", ""), new_line=False,
                    print_trigger=self.print_trigger), Output.yellow("from the following VMs",
                                                                     print_trigger=self.print_trigger)
                Output.white(str(vms).replace('[', '').replace(']', '').replace("'", ""))
        for each in self.controllers:
            if each.run():
                successful_vms.append(each.instance_name)
        successful_vms = str(successful_vms)
        successful_vms = successful_vms.translate(None, "[']")

        self.incorrect_list = str(self.incorrect_list)
        self.incorrect_list = self.incorrect_list.translate(None, "[']")

        if len(successful_vms) != 0:
            Output.green("File Collection Succeeded on: [%s]\n" % str(successful_vms),print_trigger=self.print_trigger)
        if len(self.incorrect_list) != 0:
            Output.red("File Collection Failed on: [%s]\n" % str(self.incorrect_list),print_trigger=self.print_trigger)
        #

        # Output.white(successful_vms + "\n")
        #
        # Output.green("File collection finished")
        # # if (len(successful_vms) == 0):
        # #     Output.yellow('No logs have been collected from VMs.\n')
        # # else:
        # #     Output.green('Use case log files collected.\n')

