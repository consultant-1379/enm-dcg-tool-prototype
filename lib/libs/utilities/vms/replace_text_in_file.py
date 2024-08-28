from libs.logging.verbose import Verbose
from libs.utilities.vms.paramiko_client import ParamikoClient



class ReplaceTextInFile():
    def __init__(self, vm_client_name, file_name):
        self.vm_name = vm_client_name
        self.file_name = file_name
        self.client = None

    def replace(self, text_pair_list):
        self.client = ParamikoClient(self.vm_name, using_sudo=True)
        if (self.client.connect()):
            for text_pair in text_pair_list:
                self.client.execute(
                    "sed -i 's/%s/%s/g' %s" % (text_pair.get_lod_text(), text_pair.get_new_text(), self.file_name))
            self.client.close()
        else:
            Verbose.red("Could not modify the file %s from remote vm %s, due to the previous error." % (
                    self.file_name, self.vm_name))


class TextPair():
    def __init__(self, old_text, new_text):
        self.old_text = old_text
        self.new_text = new_text

    def get_lod_text(self):
        return self.old_text

    def get_new_text(self):
        return self.new_text

    def reverse(self):
        temp = self.old_text
        self.old_text = self.new_text
        self.new_text = temp
