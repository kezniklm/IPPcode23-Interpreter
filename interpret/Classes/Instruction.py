##
# @file Instruction.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

class Instruction:
    """Trieda obsahujúca všetky potrebné informácie o každej inštrukcii a volanie implementácie každej jednotlivej inštrukcie"""

    def __init__(self, opcode, order, list_of_args, arg1, arg2, arg3):
        self.opcode = opcode
        self.order = order
        self.args = list_of_args
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
