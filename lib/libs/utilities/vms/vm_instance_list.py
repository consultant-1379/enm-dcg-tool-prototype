from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class VMInstanceList():
    def __init__(self, vm_name):
        self.vm = vm_name

    def get(self):
        if (Configuration.cloud_server):
            get_vm_info = 'consul members'
            column_of_vm_names = 1

        else:
            get_vm_info = "cat '%s'" % (Configuration.hosts_file_name)
            column_of_vm_names = 2

        get_vm_column = "awk '{print $%s}'" % (str(column_of_vm_names))
        get_vm_instances = "egrep -w '%s'" % (self.vm)
        self.command = ' | '.join([get_vm_info, get_vm_column, get_vm_instances])

        output = Terminal.popen_read(self.command)
        return output.split('\n')[:-1]
