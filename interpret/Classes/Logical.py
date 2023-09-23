##
# @file Logical.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

from Classes.Exit import Exit


class Logical:
    """Trieda združujúca všetky logické operátory"""

    @staticmethod
    def base(instr, frame, operation):
        """Podľa zadanej operácie vykoná logickú operáciu na operandoch inštrukcie

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            operation (_type_): and, or alebo not
        """
        variable = frame.get_var(instr.arg1, none_check=False)
        arg2var = None
        arg3var = None
        if frame.is_var(instr.arg2):
            arg2var = frame.get_var(instr.arg2)
            if arg2var.type != "bool":
                Exit(Exit.EXIT_TYPE)
        if frame.is_var(instr.arg3):
            arg3var = frame.get_var(instr.arg3)
            if arg3var.type != "bool":
                Exit(Exit.EXIT_TYPE)
        if instr.args[1]["type"] in ["bool", "var"] and operation == "not":
            if arg2var is not None:
                variable.value = Logical.not_impl(arg2var.value)
            else:
                variable.value = Logical.not_impl(instr.arg2)
        elif instr.args[1]["type"] in ["bool", "var"] and instr.args[2]["type"] in ["bool",
                                                                                    "var"] and operation == "and":
            if arg2var is not None and arg3var is not None:
                variable.value = Logical.and_impl(
                    arg2var.value, arg3var.value)
            elif arg2var is None and arg3var is not None:
                variable.value = Logical.and_impl(
                    instr.arg2, arg3var.value)
            elif arg2var is not None and arg3var is None:
                variable.value = Logical.and_impl(
                    arg2var.value, instr.arg3)
            else:
                variable.value = Logical.and_impl(
                    instr.arg2, instr.arg3)
        elif instr.args[1]["type"] in ["bool", "var"] and instr.args[2]["type"] in ["bool",
                                                                                    "var"] and operation == "or":
            if arg2var is not None and arg3var is not None:
                variable.value = Logical.or_impl(
                    arg2var.value, arg3var.value)
            elif arg2var is None and arg3var is not None:
                variable.value = Logical.or_impl(
                    instr.arg2, arg3var.value)
            elif arg2var is not None and arg3var is None:
                variable.value = Logical.or_impl(
                    arg2var.value, instr.arg3)
            else:
                variable.value = Logical.or_impl(instr.arg2, instr.arg3)
        else:
            Exit(Exit.EXIT_TYPE)

        variable.type = "bool"

    @staticmethod
    def and_i(instr, frame):
        Logical.base(instr, frame, "and")

    @staticmethod
    def or_i(instr, frame):
        Logical.base(instr, frame, "or")

    @staticmethod
    def not_i(instr, frame):
        Logical.base(instr, frame, "not")

    @staticmethod
    def not_impl(value):
        if value == "true":
            value = "false"
        else:
            value = "true"
        return value

    @staticmethod
    def and_impl(value1, value2):
        ret_value = None
        if value1 == "true" and value2 == "true":
            ret_value = "true"
        elif (value1 == "true" and value2 == "false") or (value1 == "false" and value2 == "true") or (
                value1 == "false" and value2 == "false"):
            ret_value = "false"
        return ret_value

    @staticmethod
    def or_impl(value1, value2):
        ret_value = None
        if value1 == "true" and value2 == "true":
            ret_value = "true"
        elif (value1 == "true" and value2 == "false") or (value1 == "false" and value2 == "true"):
            ret_value = "true"
        elif value1 == "false" and value2 == "false":
            ret_value = "false"
        return ret_value
