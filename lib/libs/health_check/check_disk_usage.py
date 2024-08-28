from libs.health_check.mounts import Mounts
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.file_system import FileSystem


class CheckDiskUsage:

    def __init__(self):
        if not self.check_disk_usage():
            Output.red('Disk space error. Stored log files usage has exceeded %s%% of the disk size. '
                       'Cleanup the file system at "%s" before running the tool.' % (
                                Configuration.file_system_max_usage, Configuration.directory_to_check_disk_usage))
            Terminal.exit()

    @staticmethod
    def check_disk_usage():
        """
        If the disk is overflow, the tool cannot be run
        :return:
        """
        if Configuration.cloud_server and Configuration.report_mount_umount:
            # todo: check disk usage on the cloud server
            if Configuration.report_output_dir == "/ericsson/enm/dumps/lcs/":
                Mounts.mount_dumps()
                checked_directory = Configuration.directory_to_check_disk_usage
                usage = FileSystem.get_disk_usage(checked_directory, cloud=True)
                max_usage = Configuration.file_system_max_usage * 0.01
                if usage > max_usage:
                    Mounts.umount_dumps()
                    return False
            Mounts.umount_dumps()
            return True
        else:
            # check disk usage on physical server
            checked_directory = Configuration.directory_to_check_disk_usage
            usage = FileSystem.get_disk_usage(checked_directory)
            max_usage = Configuration.file_system_max_usage * 0.01
            if usage > max_usage:
                return False
            return True
