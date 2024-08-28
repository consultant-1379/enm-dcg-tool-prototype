import sys, tty, termios
from libs.logging.logger import Logger
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.utilities.system.pexpect_child import PexpectChild
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.utilities.vms.global_search import GlobalSearch
from libs.variables.configuration import Configuration
from libs.variables.keys import AppKeys
import pexpect


class ENMCliChecks():

    def __init__(self, function):
        self.role = None
        self.not_correct = False
        if AppKeys.enm_role in function:
            role_list = Dictionary.get_value(function, AppKeys.enm_role)
            if type(role_list) == str:
                role_list = [role_list]
            self.role = role_list[0]
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def full_check(self, number=1):
        if number >= 2:
            pass
        else:
            list_of_scripting_vms = GlobalSearch("scripting").get_correct_list()
            for each in list_of_scripting_vms:
                if self.ping_server(each) is False:
                    list_of_scripting_vms.remove(each)
            # if list empty cancel enmCli plugin
            if len(list_of_scripting_vms) == 0:
                Print.red("No scripting vm's available. Skipping ENMCLI Plugin", trigger=self.print_trigger)
                self.not_correct = True
                Configuration.enm_cli_check = True
                if self.not_correct is True:
                    Configuration.enm_cli_check = False
                    Configuration.cli_username = None
                    Configuration.cli_password = None
                    Configuration.cli_correct_vm = None
            else:
                if self.role is None:
                    self.check_method(list_of_scripting_vms)
                else:
                    if self.role != Configuration.cli_role:
                        Output.yellow("CLI role from YAML file differs from config CLI role", print_trigger=self.print_trigger)
                        Output.yellow("Enter login details for this new role: %s" % self.role, print_trigger=self.print_trigger)
                        count = 0
                        while count < 3:
                            details = self.get_psw_and_user()
                            username = details[0]
                            password = details[1]
                            three_times = self.try_connection(list_of_scripting_vms, username, password, count)
                            if three_times is True:
                                count = 3
                                Configuration.enm_cli_check = True
                                break
                            else:
                                if count == 2:
                                    self.not_correct = True
                            count = count + 1
                        # let program know the check for username,scripting vms and password has been done
                        if self.not_correct is True:
                            Configuration.enm_cli_check = False
                            Configuration.cli_username = None
                            Configuration.cli_password = None
                            Configuration.cli_correct_vm = None
                    else:
                        self.check_method(list_of_scripting_vms)

    def check_method(self, list_of_scripting_vms):
        user = Configuration.cli_username
        psw = Configuration.cli_password
        # generating all scripting vms in a list
        if user is None or user == "" or psw is None or psw == "":
            if Configuration.executing_username is None or Configuration.executing_password is None:
                count = 0
                while count < 3:
                    details = self.get_psw_and_user()
                    username = details[0]
                    password = details[1]
                    three_times = self.try_connection(list_of_scripting_vms, username, password, count)
                    if three_times is True:
                        count = 3
                        Configuration.enm_cli_check = True
                        break
                    else:
                        if count == 2:
                            self.not_correct = True
                    count = count + 1

        else:
            first_try = self.try_connection(list_of_scripting_vms, user, psw)
            if first_try is True:
                Configuration.enm_cli_check = True
            else:
                Output.red("Failed to login to SCP VM to execute ENM command.", print_trigger=self.print_trigger)
                count = 0
                while count < 3:
                    details = self.get_psw_and_user()
                    username = details[0]
                    password = details[1]
                    three_times = self.try_connection(list_of_scripting_vms, username, password, count)
                    if three_times is True:
                        count = 3
                        Configuration.enm_cli_check = True
                        break
                    else:
                        if count == 2:
                            self.not_correct = True
                    count = count+1

        # let program know the check for username,scripting vms and password has been done
        if self.not_correct is True:
            Configuration.enm_cli_check = False
            Configuration.cli_username = None
            Configuration.cli_password = None
            Configuration.cli_correct_vm = None

    @staticmethod
    def ping_server(server):
        """
        :param server:
        :return:
        """
        reply = Terminal.system("ping -c 1 " + server + " > /dev/null 2>&1")
        if reply == 0:
            return True
        else:
            return False

    def pass_to_asterisks(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def get_psw_and_user(self):
        list_of_details = []
        user = None
        Output.yellow('\nEnter ENM username: ', print_trigger=self.print_trigger)
        user = Terminal.input().strip()
        while user is None or user == "" or user.__contains__(" "):
            Output.yellow('\nPlease Input a Value', print_trigger=self.print_trigger)
            Output.yellow("\nValue Cannot contain spaces", print_trigger=self.print_trigger)
            user = Terminal.input().strip()
        list_of_details.append(user)
        Output.yellow("\nEnter ENM Password: ", print_trigger=self.print_trigger)
        key = ""
        while True:
            ch = self.pass_to_asterisks()
            num = len(key) + 1
            if ch == '\r':
                break
            elif ch == '\x08' or ch == '\x7f':
                new_num = num - 1
                key = key[:-1]
                if new_num > 0:
                    sys.stdout.write('\b \b')
            elif ch == '\x03':
                sys.exit(0)
            else:
                key += ch
                sys.stdout.write('*')
        psw = key
        list_of_details.append(psw)
        print
        return list_of_details

    def try_connection(self, list_of_scripting_vms, username, password, number=False):
        for each in list_of_scripting_vms:
            try:
                child = PexpectChild("ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %s@%s" % (username, each))
                child.expect("%s@%s's password:" % (username, each), timeout=5)
                child.sendline(password)
                expected = "Last login:.*"
                exception = "Permission denied.*"
                result = child.expect([expected, exception], timeout=5)
                if result == 0:
                    Configuration.executing_username = username
                    Configuration.executing_password = password
                    Configuration.executing_role = self.role
                    Configuration.cli_correct_vm = each
                    Logger.info("SCP VM used for ENM_CLI [%s], Username [%s]" % (Configuration.cli_correct_vm,Configuration.executing_username))
                    child.close()
                    self.not_correct = False
                    return True
                elif result == 1:
                    child.close()
                    if list_of_scripting_vms.index(each) == (len(list_of_scripting_vms) - 1):
                        if number is False:
                            pass
                        else:
                            Output.red("ENM Login Credentials Incorrect. [%s/3]" % (number + 1),print_trigger=self.print_trigger)
                        return False
            except pexpect.EOF and pexpect.TIMEOUT:
                Output.red("Unable to login to ENM.",print_trigger=self.print_trigger)