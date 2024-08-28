from __future__ import print_function

class Print:
    WHITE = 'white'
    RED = 'red'
    BLACK = 'black'
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'blue'
    PURPLE = 'purple'
    CYAN = 'cyan'

    # default Black Background
    _DEFAULT_BACKGROUND = 'black'

    _DEFAULT_TEXT_COLOR = 'white'

    _background_colors = {
        'black': 40,
        'red': 41,
        'green': 42,
        'yellow': 43,
        'blue': 44,
        'purple': 45,
        'cyan': 46}

    _text_colors = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'purple': 35,
        'cyan': 36,
        'white': 0}

    @staticmethod
    def _ANSI_escape_code(text, color, new_line, background):
        """
        Method used to print with color
        :param text: input string
        :param color: color from dictionary
        :param new_line: True/False = \n at end of line or not
        :return:
        """

        # formats the object to a string
        text = str(text)

        # replace the escape characters
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '\t')

        # decide the end symbol
        if (new_line):
            end_symbol = "\n"
        else:
            end_symbol = ""

        # color formatter
        formatter = "\033[%sm"

        text_color = formatter % Print._text_colors.get(color)
        last_letter = formatter % Print._text_colors.get(Print.WHITE)

        print("%s%s %s" % (text_color,text,last_letter),
              end=end_symbol)

        # if there is no line break, flush the output string
        if (not new_line):
            import sys
            sys.stdout.flush()

    @staticmethod
    def clean_line():
        """
        Refreshes the current line in the terminal to a blank line
        :return:
        """
        import os
        _, columns = os.popen('stty size', 'r').read().split()
        spaces = ' ' * (int(columns))
        Print.white("\r%s\r" % (spaces), new_line=False)

    @staticmethod
    def white(text='', new_line=True, background=None, trigger=True):
        """
        prints to Terminal in white
        :param text: String variable to log/print (default = "")
        :param new_line: if true will add /n to end of line
        :return:
        """
        if trigger is True:
            Print._ANSI_escape_code(text, Print.WHITE, new_line, background)

    @staticmethod
    def red(text='', new_line=True, background=None, trigger=True):
        if trigger is True:
            Print._ANSI_escape_code(text, Print.RED, new_line, background)

    @staticmethod
    def green(text='', new_line=True, background=None, trigger=True):
        if trigger is True:
            Print._ANSI_escape_code(text, Print.GREEN, new_line, background)

    @staticmethod
    def yellow(text='', new_line=True, background=None, trigger=True):
        if trigger is True:
            Print._ANSI_escape_code(text, Print.YELLOW, new_line, background)

    @staticmethod
    def blue(text='', new_line=True, background=None, trigger=True):
        if trigger is True:
            Print._ANSI_escape_code(text, Print.BLUE, new_line, background)