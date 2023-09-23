##
# @file Constant.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

class Constant:
    def __init__(self, const_type, value):
        self.type = const_type
        self.value = value
