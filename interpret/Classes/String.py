##
# @file String.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

from Classes.Arithmetic import Arithmetic
from Classes.Exit import Exit
from Classes.IO import IO


class String:
    """Trieda združujúca všetky operácie s reťazcami"""

    @staticmethod
    def int2char(instr, frame):
        """Prevedie číselnú hodnotu druhého argumentu na znak a uloží ho do premennej

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.get_var(instr.arg1, none_check=False)
        arg2var = None
        if frame.is_var(instr.arg2):
            arg2var = frame.get_var(instr.arg2)
            if arg2var.type != "int":
                Exit(Exit.EXIT_TYPE)
        if instr.args[1]["type"] in ["var", "int"]:
            if arg2var is not None:
                variable.value = arg2var.value
            else:
                variable.value = instr.arg2
        else:
            Exit(Exit.EXIT_TYPE)
        try:
            variable.value = chr(int(variable.value))
        except:
            Exit(Exit.EXIT_STRING)
        variable.type = "string"

    @staticmethod
    def stri2int(instr, frame):
        """Uloží číselnú hodnotu znaku (druhý argument) na pozícii (tretí argument) do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.get_var(instr.arg1, none_check=False)
        arg2var = None
        if frame.is_var(instr.arg2):
            arg2var = frame.get_var(instr.arg2)
            if arg2var.type != "string":
                Exit(Exit.EXIT_TYPE)
        if frame.is_var(instr.arg3):
            arg3var = frame.get_var(instr.arg3)
            if arg3var.type != "int":
                Exit(Exit.EXIT_TYPE)
        if instr.args[1]["type"] in ["var", "string"] and instr.args[2]["type"] in ["var", "int"]:
            if arg2var is not None:
                arg2value = arg2var.value
            else:
                arg2value = instr.arg2
            arg2value = IO.handle_string(arg2value)
            arg3value = Arithmetic.get_int_value(frame, instr.arg3)
            if (arg3value is not None and arg2value is not None) and not (0 <= arg3value < len(arg2value)):
                Exit(Exit.EXIT_STRING)
            if arg3value is not None and arg2value is not None:
                variable.value = ord(arg2value[arg3value])
                variable.type = "int"
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def concat(instr, frame):
        """Spojí reťazec (druhý argument) s druhým reťazcom (tretí argument) a výsledok uloží do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.get_var(instr.arg1, none_check=False)
        arg2var = None
        arg3var = None
        if frame.is_var(instr.arg2):
            arg2var = frame.get_var(instr.arg2)
            if arg2var.type != "string":
                Exit(Exit.EXIT_TYPE)
        if frame.is_var(instr.arg3):
            arg3var = frame.get_var(instr.arg3)
            if arg3var.type != "string":
                Exit(Exit.EXIT_TYPE)
        if instr.args[1]["type"] in ["var", "string"] and instr.args[2]["type"] in ["var", "string"]:
            if arg2var is not None:
                arg2value = IO.handle_string(arg2var.value)
            else:
                arg2value = IO.handle_string(instr.arg2)
            if arg3var is not None:
                arg3value = IO.handle_string(arg3var.value)
            else:
                arg3value = IO.handle_string(instr.arg3)
            if arg2value == 'None':
                arg2value = ""
            if arg3value == 'None':
                arg3value = ""
            variable.value = arg2value + arg3value
            variable.type = "string"
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def strlen(instr, frame):
        """Uloží dĺžku reťazca (druhý argument) do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.get_var(instr.arg1, none_check=False)
        arg2var = None
        if frame.is_var(instr.arg2):
            arg2var = frame.get_var(instr.arg2)
            if arg2var.type != "string":
                Exit(Exit.EXIT_TYPE)
        if instr.args[1]["type"] in ["var", "string"]:
            if arg2var is not None:
                arg2value = IO.handle_string(arg2var.value)
            else:
                arg2value = IO.handle_string(instr.arg2)
            if arg2value == 'None':
                arg2value = ""
            variable.value = len(arg2value)
            variable.type = "int"
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def getchar(instr, frame):
        """Uloží reťazec (druhý argument) na pozícii (tretí argument) do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.get_var(instr.arg1, none_check=False)
        arg2var = None
        if frame.is_var(instr.arg2):
            arg2var = frame.get_var(instr.arg2)
            if arg2var.type != "string":
                Exit(Exit.EXIT_TYPE)
        if frame.is_var(instr.arg3):
            arg3var = frame.get_var(instr.arg3)
            if arg3var.type != "int":
                Exit(Exit.EXIT_TYPE)
        if instr.args[1]["type"] in ["var", "string"] and instr.args[2]["type"] in ["var", "int"]:
            if arg2var is not None:
                arg2value = arg2var.value
            else:
                arg2value = instr.arg2
            arg2value = IO.handle_string(arg2value)
            arg3value = Arithmetic.get_int_value(frame, instr.arg3)
            if (arg3value is not None and arg2value is not None) and not (0 <= arg3value < len(arg2value)):
                Exit(Exit.EXIT_STRING)
            if arg3value is not None and arg2value is not None:
                variable.value = arg2value[arg3value]
                variable.type = "string"
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def setchar(instr, frame):
        """Zmodifikuje znak reťazca uloženého v premennej (prvý argument) na pozícii (druhý argument) na znak v reťazci (tretí argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.get_var(instr.arg1, none_check=False)
        arg2var = None
        arg3var = None
        if variable.type is None or variable.value is None:
            Exit(Exit.EXIT_VALUE)
        if variable.type != "string":
            Exit(Exit.EXIT_TYPE)
        if frame.is_var(instr.arg2):
            arg2var = frame.get_var(instr.arg2)
            if arg2var.type != "int":
                Exit(Exit.EXIT_TYPE)
        if frame.is_var(instr.arg3):
            arg3var = frame.get_var(instr.arg3)
            if arg3var.type != "string":
                Exit(Exit.EXIT_TYPE)
        if instr.args[1]["type"] in ["var", "int"] and instr.args[2]["type"] in ["var", "string"]:
            if arg3var is not None:
                arg3value = arg3var.value
            else:
                arg3value = instr.arg3
            arg2value = Arithmetic.get_int_value(frame, instr.arg2)
            arg3value = IO.handle_string(arg3value)
            if (arg3value is not None and arg2value is not None) and not (0 <= arg2value < len(variable.value)):
                Exit(Exit.EXIT_STRING)
            if arg3value != 'None' and arg2value is not None:
                variable.value = variable.value[:arg2value] + \
                                 arg3value[0] + variable.value[arg2value + 1:]
                variable.type = "string"
            else:
                Exit(Exit.EXIT_STRING)
        else:
            Exit(Exit.EXIT_TYPE)
