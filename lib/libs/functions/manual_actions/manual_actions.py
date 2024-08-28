from libs.functions.function_superclass import FunctionSuperclass
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.system.output import Output
from libs.utilities.system.print_text import Print
from libs.utilities.system.terminal import Terminal
from libs.variables.keys import AppKeys
from libs.variables.configuration import Configuration


class ManualActions(FunctionSuperclass):
    def __init__(self, function, app, config_stack):
        if not FunctionSuperclass.check_name_equal(function[AppKeys.func_name], ManualActions.func_name()):
            Terminal.exception("This function was wrongly passed in Manual Actions")
        if Configuration.manual_endYamlFile is False:
            self.actions = function[AppKeys.actions]
        # print trigger for startYAML
        self.print_trigger = True
        if Configuration.manual_startYamlFile is True:
            self.print_trigger = False

    def run(self):

        if not Configuration.manual_actions:
            return
        if Configuration.manual_endYamlFile is True:
            Terminal.mkdir(Configuration.storing_logs_dir + 'manual_actions')
            Output.yellow('\n#################################################',print_trigger=self.print_trigger)
            Output.yellow('If any extra logs or screenshot(s) needs to be added in the LCS tar file.\nPlease store them under the directory below.',print_trigger=self.print_trigger)
            Output.white('"%smanual_actions"' % Configuration.storing_logs_dir,print_trigger=self.print_trigger)
            Output.yellow('#################################################',print_trigger=self.print_trigger)
            while True:
                Output.yellow('\nWhen Finished type "Done": ',print_trigger=self.print_trigger)
                ans = Terminal.input('')
                if ans == 'Done':
                    break
                else:
                    Print.white('Invalid input',trigger=self.print_trigger)
        else:
            text = list()
            text += ['Do the following manual actions and store the output/screenshots in the directory "%s"'
                     % Configuration.storing_logs_dir]

            title_number = 1
            for action in self.actions:
                rows, columns = Terminal.popen_read('stty size').split()
                text += ['', '%s' % ('-' * (int(columns))), '']

                # Get action title
                title = Dictionary.get_value(action, AppKeys.action_title, '')

                text += [str(title_number) + '. ' + title]
                title_number += 1

                # Get action steps
                steps = Dictionary.get_value(action, AppKeys.action_list, list())

                step_number = 1
                for each in steps:
                    item = '\t(' + str(step_number) + "). "

                    item += each
                    text += [item]
                    step_number += 1

            for each_line in text:
                Output.white(each_line,print_trigger=self.print_trigger)
            print '\n'

            Terminal.any_input()

    @staticmethod
    def func_name():
        return "Manual Actions"
