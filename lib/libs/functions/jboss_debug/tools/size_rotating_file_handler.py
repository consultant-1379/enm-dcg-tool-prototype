class SizeRotatingFileHandler():
    def __init__(self, client, file_handler_name, subsystem="logging"):
        """

        :param client: The client for enabling debug
        :param file_handler_name:
        :param subsystem:
        """
        self.file_handler_name = file_handler_name
        self.client = client
        self.subsystem = subsystem

    def enable_debug(self):
        self.execute("enable()")
        self.client.execute(
            '/ericsson/3pp/jboss/bin/jboss-cli.sh --connect "/subsystem=logging/root-logger=ROOT:change-root-log-level(level=INFO)"')

    def disable_debug(self):
        self.execute("disable()")

    def execute(self, command, attribute='size-rotating-file-handler'):
        self.client.execute(
            '/ericsson/3pp/jboss/bin/jboss-cli.sh --connect "/subsystem=%s/%s=%s:%s"' % (
                self.subsystem, attribute, self.file_handler_name, command), superuser=True)
        if (self.client.get_stdout() == ['{"outcome" => "success"}\n']):
            return True
        else:
            return False
