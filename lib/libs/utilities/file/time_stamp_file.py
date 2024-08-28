from libs.utilities.system.timing import Timing


class TimeStampFile():
    def __init__(self, file_name, location):
        time_stamp = Timing().strftime()
        path = location + file_name + '_' + time_stamp
        self.file = open(path, 'w')

    def write(self, string):
        self.file.write(string)

    def close(self):
        self.file.close()
