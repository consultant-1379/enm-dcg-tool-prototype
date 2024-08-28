from libs.utilities.system.output import Output


class NumStrToList(object):
    def __init__(self, string, input_range):
        self.numbers = list()
        self.legal = False
        inputs = string.split(",")
        for each_range in inputs:
            num_range = (each_range.strip()).split("-")
            try:
                if (len(num_range) == 1):
                    self.numbers.append(int(num_range[0].strip()))
                elif (len(num_range) == 2):
                    for each in range(int(num_range[0].strip()), 1 + int(num_range[1].strip())):
                        self.numbers.append(int(each))
                else:
                    Output.red("Please use standard syntax (e.g. 1-3, 5, 6-8): ")
                    return
            except:
                Output.red("Please use standard syntax (e.g. 1-3, 5, 6-8): ")
                return

        self.legal = self.in_range(self.numbers, input_range)

    def convert(self):
        return self.numbers

    def is_legal(self):
        return self.legal

    def in_range(self, numbers, range):
        for each_number in numbers:
            if each_number not in range:
                Output.red("Please enter a number between %d and %d: " % (range[0], range[len(range) - 1]))
                return False
        return True
