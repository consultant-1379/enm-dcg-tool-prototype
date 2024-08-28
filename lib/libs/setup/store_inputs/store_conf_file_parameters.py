from libs.logging.logger import Logger
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration
import re

class StoreConfFileParameters():

    @staticmethod
    def create():
        try:
            Terminal.chmod(600, FilePaths.join_path(Configuration.configuration_dir, ".origin_lcs.conf"))
            if FilePaths.path_exists(Configuration.lcs_conf_path):
                Terminal.copy(Configuration.lcs_conf_path,
                              FilePaths.join_path(Configuration.configuration_dir, ".lcs.conf.old"))
            Terminal.copy(FilePaths.join_path(Configuration.configuration_dir, ".origin_lcs.conf"),
                          Configuration.lcs_conf_path)
        except IOError:
            pass

    @staticmethod
    def store(parameters, conf_file):
        """
        Store these parameters in the lcs.conf

        WARNING: the method edits the YAML file as a normal text file (without using the yaml package)
        so it may contain bugs of unconsidered exceptions
        please maintain this class when an exception found
        :param parameters: The objects/instances of the class in libs/setup/parameter.py
        :param conf_file: The file needs to be edited
        :return:
        """

        # read the whole conf file
        with open(conf_file, 'r') as f:
            lines = f.readlines()
        if Configuration.upload_choice == False:
            new_lines = [str.replace('Automatic_upload: True','Automatic_upload: False')for str in lines]
        else:
            new_lines = [str.replace('Automatic_upload: False','Automatic_upload: True')for str in lines]
        # leave a mark so the program knows if the setup has been done before
        # for each parameter in this setup
        for each in parameters:
            pattern = r"^%s:.*\n$" % (each.name)
            edited_line = "%s: %s\n" % (each.name, each.input)

            # find the parameter in the conf file
            for index in range(0, len(new_lines)):
                if (re.match(pattern, new_lines[index])):
                    new_lines[index] = edited_line
                    break

            # if the parameter is not found in the file
            else:

                # Add a new line to the file
                new_lines.append("\n" + edited_line)

        # store the data to a temp file
        tmp_new_conf_file = conf_file + ".edited"
        with open(tmp_new_conf_file, 'w') as f:
            f.writelines(new_lines)
        Logger.info('parameters stored in the conf file', setup=True)
        # replace the old lcs.conf with the edited one
        Terminal.mv(tmp_new_conf_file, conf_file, True)
        Terminal.chmod(755, conf_file)
