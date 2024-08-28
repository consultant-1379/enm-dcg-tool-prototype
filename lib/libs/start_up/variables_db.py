import sys

from libs.start_up.silent_setup import SilentSetup
from libs.variables.configuration import Configuration
from libs.utilities.system.file_paths import FilePaths
from libs.utilities.data_structures.encryption import Encryption
from libs.utilities.data_structures.database import Database
from libs.utilities.system.terminal import Terminal
from libs.utilities.system.output import Output
from libs.start_up.variables_options import VariableOption
import sqlite3


class VariableDb():

    def __init__(self):
        if Configuration.EOCM is not True:
            if not self.check_db():
                if SilentSetup() == False:
                    Terminal.exception("Configuration error: Please run. python "+sys.argv[1]+" --setup ")

            db = Database(Configuration.database_file)
            try:
                result = db.select('*', Configuration.database_table)
                for record in result:
                    key = record[0]
                    value = record[1]
                    is_encrypted = VariableOption.str2bool(record[2])
                    if (is_encrypted):
                        value = Encryption.decrypt(value)

                    setattr(Configuration, key, value)

            except(sqlite3.DatabaseError):
                if FilePaths.path_exists(Configuration.database_file):
                    Terminal.rm(Configuration.database_file)
                    Output.red("File Deleted")
                Terminal.exception("This is not a database file. Run --setup to create new file.")
            finally:
                db.close()


    def check_db(self):
        if not FilePaths.path_exists(Configuration.database_file):
            return False
        else:
            return True