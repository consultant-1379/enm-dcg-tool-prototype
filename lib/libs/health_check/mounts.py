import subprocess

from libs.lcs_error import LCSError
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.output import Output
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class Mounts:

    def __init__(self):
        if Configuration.cloud_server and Configuration.report_mount_umount:
            if not self.mount_dumps():
                raise LCSError('\nError, Could not Mount dumps file System')
            # if not self.mount_gp():
            #     raise LCSError("Cloud Server Global.properties search mounting caused crash")

    @staticmethod
    def mount_gp():
        if FilePaths.isdir("/var/tmp/.lcs_gp") is False:
            Terminal.system("sudo mkdir /var/tmp/.lcs_gp")
        mount_gp = "sudo mount nfsdata:/ericsson/data /var/tmp/.lcs_gp"
        pipe = subprocess.Popen(mount_gp, shell=True, stdout=subprocess.PIPE).stdout
        mount_gp_out = pipe.read()
        pipe.close()
        if mount_gp_out is None or mount_gp_out == "":
            pass
        else:
            return False
        return True

    @staticmethod
    def umount_gp():
        unmount_cmd = "sudo umount /var/tmp/.lcs_gp"
        pipe = subprocess.Popen(unmount_cmd, shell=True, stdout=subprocess.PIPE).stdout
        unmount_out = pipe.read()
        pipe.close()
        if unmount_out == "" or unmount_out is None:
            pass
        else:
            Output.red("Un-mounting operation of Global.properties issues occurred")

    @staticmethod
    def mount_dumps():
        check_mount = "mount | grep hcdumps"
        pipe = subprocess.Popen(check_mount, shell=True, stdout=subprocess.PIPE).stdout
        check_out = pipe.read()
        pipe.close()
        if check_out is None or check_out == "":
            if FilePaths.isdir("/ericsson/enm/dumps") is False:
                Terminal.system("sudo mkdir -p /ericsson/enm/dumps")
            Terminal.system("sudo mount nfshcdumps:/ericsson/hcdumps /ericsson/enm/dumps")
            pipe2 = subprocess.Popen(check_mount, shell=True, stdout=subprocess.PIPE).stdout
            check_out2 = pipe2.read()
            pipe.close()
            if check_out2 is None or check_out2 == "":
                return False
        else:
            pass
        if FilePaths.isdir("/ericsson/enm/dumps/lcs") is False:
            Terminal.system("sudo mkdir -p /ericsson/enm/dumps/lcs")
        return True

    @staticmethod
    def umount_dumps():
        unmount_cmd = "sudo umount /ericsson/enm/dumps"
        pipe = subprocess.Popen(unmount_cmd, shell=True, stdout=subprocess.PIPE).stdout
        unmount_out = pipe.read()
        pipe.close()
        if unmount_out == "" or unmount_out is None:
            pass
        else:
            Output.red("Un-mounting operation of dumps directory issues occurred")