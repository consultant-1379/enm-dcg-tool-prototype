import os
import signal
import sys
import glob

from libs.executors.menu_executor.net_sim import NetSim
from libs.executors.menu_executor.network_node_menu import NetworkNodeMenu
from libs.logging.logger import Logger
from libs.start_up_message.start_up_msg import StartUpMsg
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.variables.configuration import Configuration
from libs.utilities.system.terminal import Terminal


class DynamicMenu:

    def __init__(self, path):
        self.menus_list = []
        if type(path) is list:
            updated_path = path[0]
            self.path = updated_path
        else:
            self.path = path

        if self.yamlfilecheck() is True:
            if self.make_list() is True:
                from lcs_main import main
                main()

    def menu(self, printlist, page):
        # check for Ctrl-c press
        signal.signal(signal.SIGINT, self._dynamic_menu_ctrlc_handler)
        # check for Ctrl-Z press
        signal.signal(signal.SIGTSTP, self._dynamic_menu_ctrlc_handler)
        files = self.no_hidden_files(printlist)
        alph_list = sorted(files)
        col = Terminal.console_width()
        lower = self._lower(alph_list)
        under = self.underscore(lower)
        extension = self.remove_extension(under)
        menu_list = self.numberlist(extension)
        length_of_list = len(lower)
        if length_of_list != 0:
            os.system('clear')
            StartUpMsg.message()
            Print.green('#' * col)
            self.menu_list_logger()
            if page == 1:
                if Configuration.EOCM is True:
                    Print.yellow(("Log Collection Service EOCM Menu").center(col, ' '))
                else:
                    Print.yellow(("Log Collection Service Menu").center(col, ' '))
            else:
                path = os.path.basename(self.path)
                Print.yellow((path + ' Menu').replace('_', ' ').upper().center(col, ' '))
            Print.green('#' * col)
            if page == 1:
                Print.blue('0. Exit')
            else:
                Print.blue('0. Back')
            print(menu_list)
            if page == 1:
                if os.path.exists('/var/ericsson/ddc_data/config/server.txt') is True:
                    if os.stat('/var/ericsson/ddc_data/config/server.txt').st_size is not 0:
                        Configuration.displaying_net_sim = True
                        print '3. netsim'
            print ''
            Print.green('#' * col)
            while True:
                Print.yellow("Enter Choice")
                num_input = Terminal.input('')
                if (num_input.isdigit()):
                    if num_input == '0':
                        if page == 1:
                            Logger.info('User Pressed 0 to exit')
                            Terminal.exit(0)
                        else:
                            Configuration.page_num = int(Configuration.page_num) - 1
                            head, tail = os.path.split(self.path)
                            DynamicMenu(head)
                    elif num_input == '3' or int(num_input) == 3:
                        if Configuration.displaying_net_sim is True:
                            NetSim()
                            break
                        else:
                            Print.red('Invalid input')
                    elif num_input in menu_list and num_input != '':
                        item = int(num_input) - 1
                        if self.check_if_dir(alph_list[item]) is True:
                            Configuration.page_num = int(Configuration.page_num) + 1
                            if alph_list[item].split("(submenu)")[0].strip() == "NETWORK_ELEMENTS":
                                NetworkNodeMenu(self.path + '/' + alph_list[item].replace('(submenu)', '').replace(' ', ''))
                                break
                            else:
                                DynamicMenu(self.path + '/' + alph_list[item].replace('(submenu)', '').replace(' ', ''))
                                break
                        else:
                            if self.runmenu_item(alph_list[item], alph_list, page) is True:
                                break
                    else:
                        Print.red('Invalid input')
                else:
                    Print.red('Invalid input')
            return True
        else:
            Output.red('The path is not complete. Add the extended path')
            sys.exit(0)

    def make_list(self):
        path = self.path
        dir_list = os.listdir(path)
        files = self.files(path)
        dirs = []
        for dirName in dir_list:
            full_path = os.path.normpath(os.path.join(path, dirName))
            if os.path.isdir(full_path):
                dirs += self.directoryindicator([dirName])
        for each in files:
            dirs.append(each + '.yml')
        page = Configuration.page_num
        final_list = self.check_for_yaml_in_dir(dirs)
        if self.menu(final_list, page) is True:
            return True

    def files(self, path):
        import yaml
        new = list()
        files_only = glob.glob(path + '/*.yml*')
        yaml_file = self.extract_filename(files_only)
        new.append(yaml_file)
        files = []
        for each in new[0]:
            try:
                config = yaml.load(open(path + '/' + str(each) + '.yml'))
                if config['config_type'] == 'app':
                    files.append(each)
            except:
                pass
        return files

    def check_if_dir(self, item):
        path = self.path + '/' + item.replace('(submenu)', '').replace(' ', '')
        return os.path.isdir(path)

    def runmenu_item(self, item, menulist, page):
        if Configuration.yes_to_all is True:
            Logger.info('Executing %s option from menu' % item)
            path = self.path + '/' + item
            Configuration.menu_run_file = path
            Configuration.menu_next_list = self.path
            return True
        else:
            var = True
            while var is True:
                yes = ['Yes']
                no = ['No']
                Print.yellow('Are you sure you want to execute %s, Answer [Yes] to confirm or [No] to return to menu:'
                             % item)
                ans = Terminal.input('')
                if ans in yes:
                    Logger.info('Executing %s option from menu' % item)
                    path = self.path + '/' + item
                    Configuration.menu_run_file = path
                    Configuration.menu_next_list = self.path
                    break
                elif ans in no:
                    var = False
                    self.menu(menulist, page)
                else:
                    Output.red('Wrong Entry')
            return True

    def directoryindicator(self, dir_list):
        new = []
        for each in dir_list:
            if self.checkforyaml(self.path + '/' + each) is True:
                new.append(each + ' (submenu)')
        return new

    def check_for_yaml_in_dir(self, yaml_list):
        new = []
        for each in yaml_list:
            if os.path.isdir(self.path + '/' + each):
                if self.checkforyaml(self.path + '/' + each) is True:
                    new.append(each)
            else:
                new.append(each)
        return new

    def yamlfilecheck(self):
        listyaml = list()
        for root, dirs, files in os.walk(self.path):
            for yaml_file in files:
                if yaml_file.endswith(".yml"):
                    listyaml.append(yaml_file)
        if len(listyaml) == 0:
            Output.red('No yaml files in this directory')
            sys.exit()
        else:
            return True

    def menu_list_logger(self):
        names = os.path.basename(self.path)
        if Configuration.first is False:
            self.menus_list.append('Log Collection Service Menu')
            Logger.info(self.menus_list)
            Configuration.first = True
        else:
            if names == (str(Configuration.dynamic_menu_path[0]).replace('/', '')):
                names = 'Log Collection Service Menu'
            self.menus_list.append(' -> ' + names)
            Logger.info(self.menus_list)

    @staticmethod
    def checkforyaml(list_path):
        for root, dirs, files in os.walk(list_path):
            for yaml_files in files:
                if yaml_files.endswith(".yml"):
                    return True
                return False

    @staticmethod
    def no_hidden_files(filelist):
        files = []
        for each in filelist:
            if each.startswith('.'):
                pass
            else:
                files.append(each)
        return files

    @staticmethod
    def remove_extension(yaml_list):
        no_extension = []
        for each in yaml_list:
            if each.endswith('.yml'):
                no_extension.append(each.replace('.yml', ''))
            else:
                no_extension.append(each)
        return no_extension

    @staticmethod
    def _lower(item_list):
        lower = [each.lower() for each in item_list]
        return lower

    @staticmethod
    def underscore(item_list):
        under_scrore = []
        for each in item_list:
            temp = each.replace('_', ' ')
            under_scrore.append(temp)
        return under_scrore

    @staticmethod
    def extract_filename(paths):
        newlist = list()
        for each in paths:
            yaml_file = os.path.splitext(each)[0]
            file_name = os.path.basename(yaml_file)
            newlist.append(file_name)
        return newlist

    @staticmethod
    def numberlist(lists):
        new = ('\n'.join(['. '.join((str(name).zfill(1), num)) for name, num in enumerate(lists, 1)]))
        return new

    @staticmethod
    def _dynamic_menu_ctrlc_handler(sig,frame):
        Logger.error('Control C used to exit tool')
        Terminal.exit(0)
