class LoggersInVM(object):
    def __init__(self, vm_client_name, logger_list):
        self.vm_client_name = vm_client_name
        self.logger_list = logger_list

    def get_vm(self):
        return self.vm_client_name

    def get_loggers(self):
        return self.logger_list

    def __str__(self):
        return "vm: %s\n\tloggers:%s\n" % (self.vm_client_name, self.logger_list)

    def __repr__(self):
        return str(self)
