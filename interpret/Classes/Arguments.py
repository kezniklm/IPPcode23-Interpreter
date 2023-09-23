##
# @file Arguments.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

import sys

from Classes.Exit import Exit


class Arguments:
    """Trieda pre spracovanie vstupných argumentov skriptu"""

    # Constants
    SCRIPT_NAME = 0
    MAX_ARGUMENTS = 2

    def __init__(self):
        self.source = ""
        self.input = ""
        args = sys.argv[Arguments.SCRIPT_NAME + 1:]

        # Check the number of arguments
        if len(args) > Arguments.MAX_ARGUMENTS:
            Exit(Exit.EXIT_PARAM)

        for argument in args:
            # Split the argument on "="
            split_argument = argument.split("=")
            match split_argument:
                case ['--help']:
                    if len(args) == 1:
                        Exit(Exit.EXIT_SUCCESS, True)
                    else:
                        Exit(Exit.EXIT_PARAM)
                case ['--source', file]:
                    if not file:
                        Exit(Exit.EXIT_INPUT)
                    self.source = file
                case ['--input', file]:
                    try:
                        self.input = open(file, "r")
                    except:
                        Exit(Exit.EXIT_INPUT)
                case _:
                    Exit(Exit.EXIT_PARAM)

        # Check if either source or input is provided
        if self.source == "" and self.input == "":
            Exit(Exit.EXIT_PARAM)

    def get_source(self):
        return self.source

    def get_input(self):
        return self.input
