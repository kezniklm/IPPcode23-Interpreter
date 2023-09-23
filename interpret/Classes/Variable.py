##
# @file Variable.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

class Variable:
    def __init__(self, name, frame, var_type=None, value=None):
        self.name = name
        self.frame = frame
        self.type = var_type
        self.value = value
