from libs.logging.verbose import Verbose
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration
from libs.utilities.system.terminal import Terminal

class CloudServer():

    def __init__(self):
        # Physical servers do not have the command "consul"
        text = Terminal.popen_read('rpm -qa | grep ERIClitpcore > /dev/null 2>&1 && echo "Vendor: HP"')
        # Ericsson hardware is provided by HP so if a machine is not HP we assume it is a virtual one
        if "Vendor: HP" in text:
            Verbose.white("Running on a physical server.")
            Configuration.cloud_server = False
        # else we assume the machine is a VM
        else:
            Verbose.white("Running on a cloud server.")
            Configuration.cloud_server = True