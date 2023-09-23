##
# @file Arithmetic.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>


import re

from Classes.Exit import Exit


class Arithmetic:
    """Trieda združujúca všetky aritmetické operácie"""

    @staticmethod
    def base(instr, frame, operation):
        variable = frame.get_var(instr.arg1, none_check=False)

        if frame.is_var(instr.arg2):
            arg2type = frame.get_var(instr.arg2).type
        else:
            arg2type = instr.args[1]["type"]
        if frame.is_var(instr.arg3):
            arg3type = frame.get_var(instr.arg3).type
        else:
            arg3type = instr.args[2]["type"]

        if arg2type == "int" and arg3type == "int":
            arg2val = Arithmetic.get_int_value(frame, instr.arg2)
            arg3val = Arithmetic.get_int_value(frame, instr.arg3)
            if arg2val is not None and arg3val is not None:
                try:
                    match operation:
                        case "add":
                            variable.value = arg2val + arg3val
                        case "sub":
                            variable.value = arg2val - arg3val
                        case "mul":
                            variable.value = arg2val * arg3val
                        case "idiv":
                            if arg3val != 0:
                                variable.value = arg2val // arg3val
                            else:
                                raise Exception
                except Exception:
                    Exit(Exit.EXIT_OPERAND)
                except:
                    Exit(Exit.EXIT_XML_STRUCTURE)
            else:
                variable = Arithmetic.set_none(variable, "int")
            variable.type = "int"
        elif arg2type == "float" and arg3type == "float":
            arg2val = Arithmetic.get_dec_float(frame, instr.arg2)
            arg3val = Arithmetic.get_dec_float(frame, instr.arg3)
            if arg2val is not None and arg3val is not None:
                try:
                    match operation:
                        case "add":
                            variable.value = arg2val + arg3val
                        case "sub":
                            variable.value = arg2val - arg3val
                        case "mul":
                            variable.value = arg2val * arg3val
                        case "div":
                            if arg3val != 0:
                                variable.value = arg2val / arg3val
                            else:
                                raise Exception
                except Exception:
                    Exit(Exit.EXIT_OPERAND)
                except:
                    Exit(Exit.EXIT_XML_STRUCTURE)
            variable.type = "float"
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def add(instr, frame):
        Arithmetic.base(instr, frame, operation="add")

    @staticmethod
    def sub(instr, frame):
        Arithmetic.base(instr, frame, operation="sub")

    @staticmethod
    def mul(instr, frame):
        Arithmetic.base(instr, frame, operation="mul")

    @staticmethod
    def idiv(instr, frame):
        Arithmetic.base(instr, frame, operation="idiv")

    @staticmethod
    def div(instr, frame):
        Arithmetic.base(instr, frame, operation="div")

    @staticmethod
    def int2float(instr, frame):
        float_value = None
        variable = frame.get_var(instr.arg1, none_check=False)
        if frame.is_var(instr.arg2):
            arg2type = frame.get_var(instr.arg2).type
        else:
            arg2type = instr.args[1]["type"]

        if arg2type == "int":
            arg2val = Arithmetic.get_int_value(frame, instr.arg2)
            if arg2val is not None:
                try:
                    float_value = float(arg2val)
                except:
                    Exit(Exit.EXIT_XML_STRUCTURE)
                variable.value = float_value
                variable.type = "float"
            else:
                Exit(Exit.EXIT_XML_STRUCTURE)
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def float2int(instr, frame):
        int_value = None
        variable = frame.get_var(instr.arg1, none_check=False)
        if frame.is_var(instr.arg2):
            arg2type = frame.get_var(instr.arg2).type
        else:
            arg2type = instr.args[1]["type"]
        if arg2type == "float":
            arg2val = Arithmetic.get_float_from_string(frame, instr.arg2)
            if arg2val is not None:
                try:
                    int_value = int(arg2val)
                except:
                    Exit(Exit.EXIT_XML_STRUCTURE)
                variable.value = int_value
                variable.type = "int"
            else:
                Exit(Exit.EXIT_XML_STRUCTURE)
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def hex_to_dec(number):
        """Prekonvertuje integer v hexadecimálnom formáte na decimálny

        Args:
            number (_type_): Číslo v hexadecimálnom formáte

        Returns:
            _type_: Číslo v decimálnom formáte
        """
        try:
            number = int(number, 16)
        except:
            return number
        return number

    @staticmethod
    def octa_to_dec(number):
        """Prekonvertuje integer v oktalovom formáte na decimálny

        Args:
            number (_type_): Číslo v oktalovom formáte

        Returns:
            _type_: Číslo v decimálnom formáte
        """
        try:
            number = int(number, 8)
        except:
            return number
        return number

    @staticmethod
    def string_to_int(number):
        """Prekonvertuje decimálne číslo v reťazci na decimálny integer

        Args:
            number (_type_): Decimálne číslo v reťazci

        Returns:
            _type_: Decimálny integer
        """
        try:
            number = int(number)
        except:
            return number
        return number

    @staticmethod
    def is_none(number):
        if number is None:
            Exit(Exit.EXIT_VALUE)

    @staticmethod
    def set_none(variable, variable_type):
        if variable.value is None:
            variable.value = 0
            variable.type = variable_type
        return variable

    @staticmethod
    def get_int_value(frame, instruction_argument, read_flag=None):
        """Prekonvertuje číslo v reťazci na decimálny integer

        Args:
            frame (_type_): Rámec
            instruction_argument (_type_): Číslo v reťazci
            read_flag (_type_, optional): V prípade inštrukcie READ nebude vykonávaná kontrola na správnosť formátu čísla

        Returns:
            _type_: Decimálny integer
        """
        number = None
        if type(instruction_argument) == int:
            return instruction_argument
        if instruction_argument is not None and frame.is_var(instruction_argument) and read_flag is None:
            number = frame.get_value_from_var(instruction_argument)
            if type(number) != int:
                Exit(Exit.EXIT_TYPE)
        elif instruction_argument is not None and re.match(r'^([+\-])?0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*$',
                                                           instruction_argument):
            number = Arithmetic.hex_to_dec(instruction_argument)
        elif instruction_argument is not None and re.match(r'^([+\-])?0[oO]?[0-7]+(_[0-7]+)*$', instruction_argument):
            number = Arithmetic.octa_to_dec(instruction_argument)
        elif instruction_argument is not None and re.match(r'^([+\-])?(([1-9][0-9]*(_[0-9]+)*)|0)$',
                                                           instruction_argument):
            number = Arithmetic.string_to_int(instruction_argument)
        else:
            if read_flag:
                return None
            Exit(Exit.EXIT_XML_STRUCTURE)
        return number

    @staticmethod
    def get_dec_float(frame, instruction_argument):
        decimal_argument = None
        if type(instruction_argument) == float:
            return instruction_argument
        elif frame.is_var(instruction_argument):
            argument = frame.get_var(
                instruction_argument, none_check=False).value
            if type(argument) == float:
                return argument
        else:
            argument = instruction_argument
        try:
            decimal_argument = float.fromhex(argument)
        except ValueError:
            return argument
        except:
            Exit(Exit.EXIT_XML_STRUCTURE)
        return decimal_argument

    @staticmethod
    def get_hex_float(frame, instruction_argument):
        hex_argument = None
        if type(instruction_argument) != float and frame.is_var(instruction_argument):
            argument = frame.get_var(
                instruction_argument, none_check=False).value
        else:
            argument = instruction_argument
        try:
            hex_argument = float.hex(argument)
        except ValueError:
            return argument
        except:
            Exit(Exit.EXIT_XML_STRUCTURE)
        return hex_argument

    @staticmethod
    def get_float_from_string(frame, instruction_argument):
        float_number = None
        if type(instruction_argument) == float:
            float_number = instruction_argument
        elif frame.is_var(instruction_argument):
            argument = frame.get_var(
                instruction_argument, none_check=False).value
            if type(argument) == float:
                return argument
        elif re.match(r'^[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?$', instruction_argument):
            try:
                float_number = float(instruction_argument)
            except:
                Exit(Exit.EXIT_XML_STRUCTURE)
        elif re.match(r'^[-+]?0x[\da-fA-F]+(\.[\da-fA-F]*)?(p[-+]?\d+)?$', instruction_argument):
            float_number = Arithmetic.get_dec_float(
                frame, instruction_argument)
        else:
            Exit(Exit.EXIT_XML_STRUCTURE)

        return float_number
