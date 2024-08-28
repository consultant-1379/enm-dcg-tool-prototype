class String():
    @staticmethod
    def join(list_of_str):
        """
        if input is [a, b, c], output the string "a, b and c"
        :param list_of_str:
        :return:
        """
        if (type(list_of_str) == str):
            list_of_str = [list_of_str]
        if (len(list_of_str) == 1):
            return list_of_str[0]
        elif (len(list_of_str) == 0):
            return ''
        else:
            string = ", ".join(list_of_str[:-1])
            string += " and %s" % (list_of_str[-1])
            return string
