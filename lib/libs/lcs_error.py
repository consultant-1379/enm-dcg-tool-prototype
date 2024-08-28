from libs.utilities.system.output import Output


class LCSError(Exception):
    def __init__(self, message):
        Output.red(message)
        from libs.utilities.system.terminal import Terminal
        Terminal.exit(0)
        super(LCSError, self).__init__(message)
