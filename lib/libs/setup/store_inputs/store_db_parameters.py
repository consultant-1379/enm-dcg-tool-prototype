from libs.logging.logger import Logger
from libs.utilities.data_structures.database import Database
from libs.utilities.system.terminal import Terminal
from libs.variables.configuration import Configuration


class StoreDBParameters():
    @staticmethod
    def store(parameters, database_file):
        """
        store the parameters in the database file
        :param parameters: The objects/instances of the class in libs/setup/parameter.py
        :param database_file: The database needs to be edited
        :return:
        """
        Logger.info('storing Parameters in database file', setup=True)
        db = Database(database_file)
        table = Configuration.database_table

        # drop the original table
        db.drop(table)
        db.create(table, 'key TEXT', 'value TEXT', 'is_confidential TEXT')
        for each in parameters:
            db.insert(table, each.name, each.input, str(each.confidential))
        db.close()

        # only root user has access to the db file
        Terminal.chmod(600, database_file)
        Logger.info('parameters stored in database', setup=True)
