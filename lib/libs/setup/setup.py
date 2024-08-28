from libs.logging.logger import Logger
from libs.setup.get_inputs.get_setup_inputs import GetSetupInputs
from libs.setup.store_inputs.store_conf_file_parameters import StoreConfFileParameters
from libs.setup.store_inputs.store_db_parameters import StoreDBParameters
from libs.start_up.cloud_server import CloudServer
from libs.utilities.data_structures.dictionary import Dictionary
from libs.utilities.file.file_reader import FileReader
from libs.utilities.system.output import Output
from libs.variables.configuration import Configuration
import os


class Setup():
    @staticmethod
    def setup():
        CloudServer()
        file_path = Configuration.setup_detail_file
        setup_detail = FileReader(file_path).get()
        if Configuration.dont_display == False:
            Output.yellow("WARNING lcs.conf settings will get overridden if you have already run setup.", setup=True)

        Output.white(Dictionary.get_value(setup_detail, 'introduction', '', type=str), setup=True)
        # ask the user for each parameter
        parameter_dict = Dictionary.get_value(setup_detail, 'parameters', type=list, file_path=file_path)
        if Configuration.cloud_server is True:
            for each in parameter_dict:
                value = Dictionary.get_value(each,'displaying_name')
                if value == 'Password':
                    index = list(parameter_dict).index(each)
                    parameter_dict.pop(index)
            for each in parameter_dict:
                value = Dictionary.get_value(each, 'displaying_name')
                if value == 'Username':
                    index = list(parameter_dict).index(each)
                    parameter_dict.pop(index)
            for each in parameter_dict:
                value = Dictionary.get_value(each, 'displaying_name')
                if value == 'Root Password':
                    index = list(parameter_dict).index(each)
                    parameter_dict.pop(index)

        parameters = GetSetupInputs(parameter_dict).get()
        # divide all parameters into database parameters and lcs.conf file parameters
        db_parameters = list()
        conf_file_parameters = list()
        for each in parameters:
            if each.stored_in_db:
                db_parameters.append(each)
                Logger.info('storing parameters in Database', setup=True)
            else:
                conf_file_parameters.append(each)

        # store inputs database

        #rename_db_file = Configuration.database_file + ".old"
        try:
            command = "rm -f %s" %Configuration.old_database_file
            os.system(command)
            command = "mv -f %s %s" % (Configuration.database_file,Configuration.old_database_file)
            os.system(command)
            command = "rm -f %s" % Configuration.database_file
            os.system(command)
        except:
            pass

        StoreDBParameters.store(db_parameters, Configuration.database_file)
        # create conf files
        StoreConfFileParameters.create()
        # store inputs conf
        StoreConfFileParameters.store(conf_file_parameters, Configuration.lcs_conf_path)

        # setup complete
        Output.green(Dictionary.get_value(setup_detail, 'last_message', '', type=str), setup=True)
