import subprocess
from libs.start_up.jboss_check import JBossCheck
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration


class JbossError():


    def __init__(self):
        JBossCheck()
        self._unmount()

    def _unmount(self):
        if Configuration.report_output_dir == "/ericsson/enm/dumps/lcs/" and Configuration.report_mount_umount is True and Configuration.cloud_server is True:
            unmount_cmd = "sudo umount /ericsson/enm/dumps"
            pipe = subprocess.Popen(unmount_cmd, shell=True, stdout=subprocess.PIPE).stdout
            unmount_out = pipe.read()
            pipe.close()
            if unmount_out == "" or unmount_out is None:
                pass
            else:
                Output.red("Un-mounting operation of dumps directory issues occurred")

        # if Configuration.cloud_server is True:
        #     unmount_cmd = "sudo umount /var/tmp/.lcs_gp"
        #     pipe = subprocess.Popen(unmount_cmd, shell=True, stdout=subprocess.PIPE).stdout
        #     unmount_out = pipe.read()
        #     pipe.close()
        #     if unmount_out == "" or unmount_out is None:
        #         pass
        #     else:
        #         Output.red("Un-mounting operation of Global.properties issues occurred")
