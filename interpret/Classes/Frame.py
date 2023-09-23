##
# @file Frame.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

import re
import sys

from Classes.Arithmetic import Arithmetic
from Classes.Exit import Exit
from Classes.IO import IO
from Classes.Variable import Variable


class Frame:
    """Trieda združujúca operácie nad jednotlivými rámcami"""

    def __init__(self):
        self.frame_now = {"GF": [], "LF": [], "TF": []}
        self.frameStack = []
        self.local_frame = False
        self.temp_frame = False

    def print(self, to_print):
        """Vypíše obsah rámca na štandardný chybový výstup

        Args:
            to_print (_type_): Rámec, ktorý má byť vypísaný
        """
        for variable in self.frame_now[to_print]:
            print(variable.name, file=sys.stderr)

    def move(self, instr):
        """Presunie hodnotu z druhého argumentu do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
        """
        variable = self.get_var(instr.arg1, none_check=False)
        if variable is not None and (instr.args[1]["type"] == "int" or instr.args[1]["type"] == "bool" or instr.args[1][
            "type"] == "string" or instr.args[1]["type"] == "nil" or instr.args[1]["type"] == "float"):
            match instr.args[1]["type"]:
                case "int":
                    variable.value = Arithmetic.get_int_value(
                        self, instr.arg2)
                case "float":
                    variable.value = Arithmetic.get_dec_float(
                        self, instr.arg2)
                case _:
                    variable.value = IO.handle_string(instr.arg2)
            variable.type = instr.args[1]["type"]
        elif variable is not None and instr.args[1]["type"] == "var":
            var = self.get_var(instr.arg2)
            if var is not None:
                variable.value = var.value
                variable.type = var.type

    def type(self, instr):
        """Vloží typ druhého argumentu do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
        """
        variable = self.get_var(instr.arg1, none_check=False)
        if variable is not None and instr.args[1]["type"] == "var":
            var = self.get_var(instr.arg2, none_check=True)
            if var is not None:
                if var.value is None:
                    variable.value = ""
                else:
                    variable.value = var.type
                variable.type = "string"
        elif variable is not None and instr.args[1]["type"] in ["int", "bool", "string", "nil", "float"]:
            variable.value = instr.args[1]["type"]
            variable.type = "string"

    def def_var(self, instr):
        """Definuje premennú v jej zadanom rámci

        Args:
            instr (_type_): Inštrukcia
        """
        if re.match(
                r'\s*GF@([A-Z]|[a-z]|\*|%|_|-|\$)(%|\*|!|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|&|_|-|\$)*\s*$',
                instr.arg1):
            self.is_redefined(instr, "GF")
            self.frame_now["GF"].append(Variable(instr.arg1, "GF"))
        elif re.match(
                r'\s*LF@(_|\$|&|%|\*|!|[a-z]|\?|-)(\$|%|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|_|-)*\s*$',
                instr.arg1):
            self.is_frame("LF")
            self.is_redefined(instr, "LF")
            self.frame_now["LF"].append(Variable(instr.arg1, "LF"))
        elif re.match(
                r'\s*TF@(\?|[A-Z]|[a-z]|&|-|\$)([0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*\s*$',
                instr.arg1):
            self.is_frame("TF")
            self.is_redefined(instr, "TF")
            self.frame_now["TF"].append(Variable(instr.arg1, "TF"))
        else:
            Exit(Exit.EXIT_XML_STRUCTURE)

    def create(self):
        """Vytvorí dočasný zásobník"""
        self.temp_frame = True
        self.frame_now["TF"].clear()

    def push(self):
        """Vloží dočasný rámec do zásobníka lokálnych rámcov"""
        self.is_frame("TF")
        if self.local_frame:
            self.frameStack.append(self.frame_now["LF"])
            self.frame_now["LF"] = []
        for variable in self.frame_now["TF"]:
            variable.name = re.sub("^TF", "LF", variable.name)
            variable.frame = "LF"
            self.frame_now["LF"].append(variable)
        self.frame_now["TF"].clear()
        self.temp_frame = False
        self.local_frame = True

    def pop(self):
        """Vyberie lokálny rámec a vloží ho do dočasného rámca"""
        self.is_frame("LF")
        self.frame_now["TF"].clear()
        for variable in self.frame_now["LF"]:
            variable.name = re.sub("^LF", "TF", variable.name)
            variable.frame = "TF"
            self.frame_now["TF"].append(variable)
        self.temp_frame = True
        self.frame_now["LF"].clear()
        if not self.frameStack:
            self.local_frame = False
        else:
            self.local_frame = True
            self.frame_now["LF"] = self.frameStack.pop()

    def is_frame(self, frame):
        """Overí, či existuje zadaný rámec

        Args:
            frame (_type_): Rámec, ktorého existencia má byť skontrolovaná
        """
        if frame == "TF" and self.temp_frame == False:
            Exit(Exit.EXIT_FRAME)
        elif frame == "LF" and self.local_frame == False:
            Exit(Exit.EXIT_FRAME)

    def is_redefined(self, instr, frame):
        for instruction in self.frame_now[frame]:
            if instruction.name == instr.arg1:
                Exit(Exit.EXIT_SEMANTIC)

    def is_defined(self, arg):
        if not self.is_var(arg):
            return False
        for instruction in self.frame_now["TF"]:
            if instruction.name == arg:
                if re.match(r'^TF@', arg):
                    self.is_frame("TF")
                    return "TF"

        for instruction in self.frame_now["LF"]:
            if instruction.name == arg:
                if re.match(r'^LF@', arg):
                    self.is_frame("LF")
                    return "LF"

        for instruction in self.frame_now["GF"]:
            if instruction.name == arg:
                return "GF"

        if re.match(r'^TF@', arg):
            self.is_frame("TF")
        elif re.match(r'^LF@', arg):
            self.is_frame("LF")

        Exit(Exit.EXIT_VARIABLE)

    def is_var(self, arg):
        if re.match(
                r'^(LF|TF|GF)@(-|[A-Z]|[a-z]|\?|!|\*|&|%|_|\$)+[0-9]*(_|-|\$|&|%|\*|[a-z]|[A-Z]|\?|!)*$',
                arg):
            return True
        else:
            return False

    def get_value_from_var(self, arg):
        variable = self.get_var(arg)
        if variable is not None:
            return variable.value
        return None

    def get_var(self, arg, none_check=None):
        for variable in self.frame_now[str(self.is_defined(arg))]:
            if variable.name == arg:
                if variable.value is None and none_check is None:
                    Exit(Exit.EXIT_VALUE)
                return variable
        return None
