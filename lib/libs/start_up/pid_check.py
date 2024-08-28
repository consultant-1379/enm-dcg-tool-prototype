import os
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class PidCheck():

    def __init__(self):
        if os.path.exists('/tmp/.CtrlC'):
            Terminal.rm('/tmp/.CtrlC')
        if Configuration.use_tool_while_instance_running == False:
            if os.path.exists('/tmp/Log_tool_running'):
                with open('/tmp/Log_tool_running','r') as f:
                    pid = f.readline()
                self.pid = pid
                if self.is_running() == True:
                    pass
                else:
                    Terminal.rm('/tmp/Log_tool_running')

    def is_running(self):
        result = Terminal.system('ps -p %s >/dev/null 2>&1' % self.pid)
        if result == 0:
            Terminal.check_file_running()
        return True