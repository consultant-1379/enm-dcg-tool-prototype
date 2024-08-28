from libs.logging.logger import Logger
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class Confirm(object):
    @staticmethod
    def confirm(message=None,setup=False):
        if (message == None):
            message = "Are you sure?"
        yes = ['Yes']
        no = ['No']
        while True:
            Output.yellow(message + " [Yes] to confirm or [No] to cancel: ", setup=setup)
            input = Terminal.input('')
            Logger.info(input, setup=setup)
            if Configuration.setup is True:
                Configuration.setup = False
                if input == '':
                    return True
                elif (input in yes):
                    return True
                elif (input in no):
                    return False
                else:
                    Output.red("invaild input", setup=setup)
            else:
                if (input in yes):
                    return True
                elif (input in no):
                    return False
                else:
                    Output.red("invaild input", setup=setup)