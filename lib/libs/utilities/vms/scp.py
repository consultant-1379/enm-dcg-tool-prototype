from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class SCP():
    def __init__(self, vm_instance, username=None, using_sudo=True, StrictHostKeyChecking=False):
        """

        :param vm_instance: The vm instance name (e.g. svc-3-cmserv) or the IP address (e.g. 10.247.246.61)
        :param username: Leave it as the default value
        :param using_sudo: Leave it as the default value
        :param StrictHostKeyChecking: Leave it as the default value

        """
        self.vm_instance = vm_instance

        if (username == None):
            username = Configuration.vm_user_name
        key_filename = Configuration.vm_private_key
        self.using_sudo = using_sudo

        #######################################
        # Build up the command

        # scp command
        command = 'scp'

        # Confirmation for the first time connecting to an unknown vm
        if not (StrictHostKeyChecking):
            command += ' -o StrictHostKeyChecking=no'

        # Set up the vm private key
        command += ' -i %s' % (key_filename)

        # username and hostname
        command += ' %s@%s' % (username, vm_instance)

        self.scp_prefix = command

    def copy_file(self, source, destination):
        command = '%s:%s %s' % (self.scp_prefix, source, destination)
        Terminal.system(command, self.using_sudo)
