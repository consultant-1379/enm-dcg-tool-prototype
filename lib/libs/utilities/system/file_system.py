from libs.utilities.system.terminal import Terminal


class FileSystem():
    @staticmethod
    def get_disk_usage(folder_name,cloud=False):
        """
        Only works for physical servers
        :param folder_name:
        :return:
        """
        if cloud is True:
            output = Terminal.popen_read("df -h | grep %s | awk '{print $5}'" % (folder_name))
        else:
            output = Terminal.popen_read("df -h | grep %s | awk '{print $4}'" % (folder_name))
        percent = output.split('\n')[0]
        try:
            return float(percent.strip('%')) / 100
        except:
            return 0

    @staticmethod
    def mount_filesystem(device_name, directory, device_type=None):
        """
        Mount a directory to a device
        :param device_name: name of the device
        :param directory: the directory in local machine. and this directory will be the root directory of the device
        :param device_type: Can be left as default
        :return:
        """
        Terminal.mkdir(directory, superuser=True)
        mounting_command = "mount"
        if (device_type != None):
            mounting_command += " -t %s" % (device_type)
        mounting_command += " %s" % (device_name)
        mounting_command += " %s" % (directory)
        Terminal.system(mounting_command, superuser=True)
