##
# @file Relational.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

from Classes.Arithmetic import Arithmetic
from Classes.Exit import Exit
from Classes.IO import IO


class Relational:
    @staticmethod
    def base(instr, frame, operation):
        """Podľa zadanej operácie vykoná relačnú operáciu na operandoch inštrukcie

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            operation (_type_): lt, gt alebo eq
        """
        variable = frame.get_var(instr.arg1, none_check=False)

        if frame.is_var(instr.arg2):
            arg2val = frame.get_var(instr.arg2).value
            arg2type = frame.get_var(instr.arg2).type
        else:
            arg2val = instr.arg2
            arg2type = instr.args[1]["type"]
        if frame.is_var(instr.arg3):
            arg3val = frame.get_var(instr.arg3).value
            arg3type = frame.get_var(instr.arg3).type
        else:
            arg3val = instr.arg3
            arg3type = instr.args[2]["type"]

        if arg2type == "nil" and arg3type == "nil" and operation != "eq":
            Exit(Exit.EXIT_TYPE)
        elif arg2type == "nil" and arg3type == "nil" and operation == "eq":
            variable.type = "bool"
            variable.value = "true"
            return
        elif (arg2type == "nil" or arg3type == "nil") and operation == "eq":
            variable.type = "bool"
            variable.value = "false"
            return

        if arg2type == arg3type:
            match arg2type:
                case "int":
                    arg2val = Arithmetic.get_int_value(frame, instr.arg2)
                    arg3val = Arithmetic.get_int_value(frame, instr.arg3)
                    if type(arg2val) == int and type(arg3val) == int:
                        match operation:
                            case "gt":
                                variable.value = arg2val > arg3val
                            case "lt":
                                variable.value = arg2val < arg3val
                            case "eq":
                                variable.value = arg2val == arg3val
                case "float":
                    arg2val = Arithmetic.get_float_from_string(
                        frame, instr.arg2)
                    arg3val = Arithmetic.get_float_from_string(
                        frame, instr.arg3)
                    if type(arg2val) == float and type(arg3val) == float:
                        match operation:
                            case "gt":
                                variable.value = arg2val > arg3val
                            case "lt":
                                variable.value = arg2val < arg3val
                            case "eq":
                                variable.value = arg2val == arg3val
                case "string":
                    arg2val = IO.handle_string(arg2val)
                    arg3val = IO.handle_string(arg3val)
                    match operation:
                        case "gt":
                            variable.value = arg2val > arg3val
                        case "lt":
                            variable.value = arg2val < arg3val
                        case "eq":
                            variable.value = arg2val == arg3val
                case "bool":
                    match operation:
                        case "gt":
                            if arg2val == "true" and arg3val == "false":
                                variable.value = "true"
                            else:
                                variable.value = "false"
                        case "lt":
                            if arg2val == "false" and arg3val == "true":
                                variable.value = "true"
                            else:
                                variable.value = "false"
                        case "eq":
                            variable.value = arg2val == arg3val

        else:
            Exit(Exit.EXIT_TYPE)

        variable.type = "bool"
        if variable.value:
            variable.value = "true"
        elif not variable.value:
            variable.value = "false"

    @staticmethod
    def gt(instr, frame):
        Relational.base(instr, frame, "gt")

    @staticmethod
    def lt(instr, frame):
        Relational.base(instr, frame, "lt")

    @staticmethod
    def eq(instr, frame):
        Relational.base(instr, frame, "eq")
