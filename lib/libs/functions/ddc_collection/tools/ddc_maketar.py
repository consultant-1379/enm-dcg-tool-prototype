import subprocess

from libs.logging.logger import Logger
from libs.utilities.system.terminal import Terminal
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration


class DDCMaketar():
    ddc_maketar_command = '/opt/ericsson/ERICddc/bin/ddc MAKETAR'

    @staticmethod
    def execute():
        """
        Execute the make tar command in the ENM
        :return: True if the command has been executed successfully. Vise versa
        """
        if (Configuration.cloud_server):

            # execute on cloud server
            return DDCMaketar.execute_for_cloud()
        else:

            # execute on physical server
            return DDCMaketar.execute_for_physical()

    @staticmethod
    def execute_for_physical():
        Terminal.system(DDCMaketar.ddc_maketar_command, superuser=True)
        return True

    @staticmethod
    def execute_for_cloud():

        instance_list = GlobalSearch("esmon").get_correct_list()
        command_to_exec = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i %s %s@%s 2>/dev/null \"sudo %s\" > /dev/null 2>&1" \
                          " > /dev/null 2>&1" % (Configuration.vm_private_key,
                          Configuration.vm_user_name, instance_list[0], DDCMaketar.ddc_maketar_command)

        if len(instance_list) < 1:
            # no instance is available
            return False
        # use the first esmon instance to execute the command
        reply = Terminal.system("ping -c 1 " + instance_list[0] + " > /dev/null 2>&1")
        if reply == 0:
            execution = subprocess.Popen(command_to_exec, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, close_fds=True)
            theInfo = execution.communicate()[0].strip()

            if execution.returncode == 0:
                return True
            elif execution.returncode == 1:
                Logger.warning("DDC Maketar command not executed correctly")
                Logger.error(theInfo)
            else:
                Logger.warning("DDC MakeTar Command Issue")
                return False
