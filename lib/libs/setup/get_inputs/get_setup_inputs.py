from libs.setup.parameter import Parameter
from libs.setup.get_inputs.get_input import GetInput
from libs.utilities.system.confirm import Confirm
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration


class GetSetupInputs:
    def __init__(self, parameters_dictionary):
        self.parameter_list = list()
        for each in parameters_dictionary:
            parameter = Parameter(each)

            if Configuration.cloud_server and parameter.physical_server_only:
                # if the tool is running on virtual ENM server, but the parameter is for physical server only
                # do nothing for it
                pass
            else:
                self.parameter_list.append(parameter)

    def get(self):
        try:
            for parameter in self.parameter_list:
                if GetInput(parameter).get() is False:
                    break
            if (not GetSetupInputs.confirm(self.parameter_list)):
                # if the user does not confirm the values
                Configuration.dont_display = True
                Configuration.cli_blank = False
                Configuration.ftp_no_upload = False
                Configuration.enm_cli_dont_display = False
                Configuration.upload_choice = False
                del self.parameter_list[:]
                print self.parameter_list
                from libs.setup.setup import Setup
                Setup.setup()
        except:
            pass

        return self.parameter_list

    @staticmethod
    def confirm(parameters):
        try:
            if Configuration.cloud_server == True:
                if Configuration.enm_cli_dont_display is True and Configuration.upload_choice is True:
                    parameters.pop(1), parameters.pop(1), parameters.pop(1)
                if Configuration.enm_cli_dont_display is True and Configuration.upload_choice is False:
                    parameters.pop(1), parameters.pop(1), parameters.pop(1), parameters.pop(2), parameters.pop(2), parameters.pop(2)
                if Configuration.upload_choice is False:
                    parameters.pop(5), parameters.pop(5), parameters.pop(5)
            else:
                if Configuration.enm_cli_dont_display is True and Configuration.upload_choice is True:
                    parameters.pop(1), parameters.pop(1), parameters.pop(1)
                if Configuration.enm_cli_dont_display is True and Configuration.upload_choice is False:
                    parameters.pop(1), parameters.pop(1), parameters.pop(1)
                    parameters.pop(5), parameters.pop(5), parameters.pop(5)
                if Configuration.upload_choice is False:
                    parameters.pop(8), parameters.pop(8), parameters.pop(8)
        except:
            pass
        Output.green("You have just provided the following information.", setup=True)
        for each in parameters:
            if type(each.input) != str:
                each.input = ''
            value = each.input
            if len(value) == 0:
                # print out eight stars to represent the password
                value = ''
            elif each.confidential:
                value = '*' * 8

            Output.white("\t%s: %s" % (each.displaying_name, value), setup=True)
            Configuration.setup = True
        return Confirm.confirm('Verify the information shown above', setup=True)
