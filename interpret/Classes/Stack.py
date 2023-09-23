##
# @file Stack.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

from Classes.Arithmetic import Arithmetic
from Classes.Constant import Constant
from Classes.Exit import Exit
from Classes.IO import IO
from Classes.Logical import Logical
from Classes.ProgramFlow import ProgramFlow


class Stack:
    """Trieda združujúca všetky operácie nad dátovým zásobníkom"""

    def __init__(self):
        self.dataStack = []

    def pushs(self, instr, frame):
        """Vloži na zásobník hodnotu prvého operandu inštrukcie

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        if frame.is_defined(instr.arg1) == "TF" or frame.is_defined(instr.arg1) == "LF" or frame.is_defined(
                instr.arg1) == "GF":
            variable = frame.get_var(instr.arg1, none_check=False)
            if variable.value is None or variable.type is None:
                Exit(Exit.EXIT_VALUE)
            new_const = Constant(variable.type, variable.value)
            self.dataStack.append(new_const)
        else:
            if instr.args[0]["type"] == "int":
                instr.arg1 = Arithmetic.get_int_value(frame, instr.arg1)
            elif instr.args[0]["type"] == "float":
                instr.arg1 = Arithmetic.get_float_from_string(
                    frame, instr.arg1)
            elif instr.args[0]["type"] == "string":
                instr.arg1 = IO.handle_string(instr.arg1)
            new_const = Constant(instr.args[0]["type"], instr.arg1)
            self.dataStack.append(new_const)

    def pops(self, instr, frame):
        """Vyberie zo zásobníka hodnotu a vloži ju do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        if frame.is_defined(instr.arg1) == "TF" or frame.is_defined(instr.arg1) == "LF" or frame.is_defined(
                instr.arg1) == "GF":
            temp = self.dataStack.pop()
            variable = frame.get_var(instr.arg1, none_check=False)
            index = frame.frame_now[frame.is_defined(
                instr.arg1)].index(variable)
            frame.frame_now[frame.is_defined(
                instr.arg1)][index].value = temp.value
            frame.frame_now[frame.is_defined(
                instr.arg1)][index].type = temp.type

    def clears(self):
        """Vyprázdní dátový zásobník"""
        self.dataStack.clear()

    def arithmetic_stack_base(self, frame, operation):
        """Vykoná aritmetickú operáciu na operandoch umiestnených na zásobníku podľa zadanej operácie

        Args:
            frame (_type_): Rámec
            operation (_type_): Operácia
        """
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        arg2 = self.dataStack.pop()
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        arg1 = self.dataStack.pop()

        if arg1.type == arg2.type == "int":
            arg1val = Arithmetic.get_int_value(frame, arg1.value)
            arg2val = Arithmetic.get_int_value(frame, arg2.value)
            if operation == "add" and type(arg1val) == int and type(arg2val) == int:
                arg1.value = arg1val + arg2val
            elif operation == "sub" and type(arg1val) == int and type(arg2val) == int:
                arg1.value = arg1val - arg2val
            elif operation == "mul" and type(arg1val) == int and type(arg2val) == int:
                arg1.value = arg1val * arg2val
            elif operation == "idiv" and type(arg1val) == int and type(arg2val) == int:
                arg1.value = arg1val // arg2val
            else:
                Exit(Exit.EXIT_XML_STRUCTURE)
            self.dataStack.append(arg1)
        else:
            Exit(Exit.EXIT_TYPE)

    def relational_stack_base(self, frame, operation):
        """Vykoná relačnú operáciu na operandoch umiestnených na zásobníku podľa zadanej operácie

        Args:
            frame (_type_): Rámec
            operation (_type_): lt, gt alebo eq
        """
        arg1, arg1type, arg1val, arg2, arg2type, arg2val = self.check_stack_arguments()

        if arg1type == "nil" and arg2type == "nil" and operation != "eq":
            Exit(Exit.EXIT_TYPE)
        elif arg1type == "nil" and arg2type == "nil" and operation == "eq":
            arg1.type = "bool"
            arg1.value = "true"
            self.dataStack.append(arg1)
            return
        elif (arg1type == "nil" or arg2type == "nil") and operation == "eq":
            arg1.type = "bool"
            arg1.value = "false"
            self.dataStack.append(arg1)
            return

        if arg1type == arg2type:
            match arg2type:
                case "int":
                    arg1val = Arithmetic.get_int_value(frame, arg1.value)
                    arg2val = Arithmetic.get_int_value(frame, arg2.value)
                    if type(arg1val) == int and type(arg2val) == int:
                        match operation:
                            case "gt":
                                arg1.value = arg1val > arg2val
                            case "lt":
                                arg1.value = arg1val < arg2val
                            case "eq":
                                arg1.value = arg1val == arg2val
                case "float":
                    arg1val = Arithmetic.get_float_from_string(
                        frame, arg1.value)
                    arg2val = Arithmetic.get_float_from_string(
                        frame, arg2.value)
                    if type(arg1val) == float and type(arg2val) == float:
                        match operation:
                            case "gt":
                                arg1.value = arg1val > arg2val
                            case "lt":
                                arg1.value = arg1val < arg2val
                            case "eq":
                                arg1.value = arg1val == arg2val
                case "string":
                    arg1val = IO.handle_string(arg1val)
                    arg2val = IO.handle_string(arg2val)
                    match operation:
                        case "gt":
                            arg1.value = arg1val > arg2val
                        case "lt":
                            arg1.value = arg1val < arg2val
                        case "eq":
                            arg1.value = arg1val == arg2val
                case "bool":
                    match operation:
                        case "gt":
                            if arg1val == "true" and arg2val == "false":
                                arg1.value = "true"
                            else:
                                arg1.value = "false"
                        case "lt":
                            if arg1val == "false" and arg2val == "true":
                                arg1.value = "true"
                            else:
                                arg1.value = "false"
                        case "eq":
                            arg1.value = arg1val == arg2val

        else:
            Exit(Exit.EXIT_TYPE)

        arg1.type = "bool"
        if arg1.value:
            arg1.value = "true"
        elif not arg1.value:
            arg1.value = "false"
        self.dataStack.append(arg1)

    def logical_stack_base(self, operation):
        """Vykoná logickú operáciu na operandoch umiestnených na zásobníku podľa zadanej operácie

        Args:
            self (_type_): Rámec
            operation (_type_): and, or alebo not
        """
        arg2val = None
        arg2type = None
        if not self.dataStack and operation != "not":
            Exit(Exit.EXIT_VALUE)
        if operation != "not":
            arg2 = self.dataStack.pop()
            arg2val = arg2.value
            arg2type = arg2.type
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        arg1 = self.dataStack.pop()
        arg1val = arg1.value
        arg1type = arg1.type

        if arg1type == "bool" and operation == "not":
            arg1.value = Logical.not_impl(arg1val)
        elif operation == "and" and arg1type == "bool" and arg2type == "bool":
            arg1.value = Logical.and_impl(
                arg1val, arg2val)
        elif arg1type == "bool" and arg2type == "bool" and operation == "or":
            arg1.value = Logical.or_impl(arg1val, arg2val)
        else:
            Exit(Exit.EXIT_TYPE)

        arg1.type = "bool"
        self.dataStack.append(arg1)

    def program_flow_stack_base(self, instr, frame, interpret, operation):
        """Vykoná skok pri rovnosti (operácia ifeq) alebo nerovnosti (operácia ifneq) prvého a druhého argumentu na zásobníku

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            interpret (_type_): Interpret pre prístup k návestiam
            operation (_type_): Operácia ifeq alebo ifneq

        Returns:
            _type_: Pozícia na ktorom sa návestie nachádza
        """

        jump_position = ProgramFlow.jump(instr, interpret)
        arg1type, arg1val, arg2type, arg2val = self.get_instr_args()

        if arg1type in ["int", "nil"] and arg2type in ["int", "nil"]:
            if arg1type != "nil":
                arg1val = Arithmetic.get_int_value(frame, arg1val)
            else:
                arg1val = "nil"

            if arg2type != "nil":
                arg2val = Arithmetic.get_int_value(frame, arg2val)
            else:
                arg2val = "nil"

            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jump_position
            else:
                return False
        elif arg1type in ["float", "nil"] and arg2type in ["float", "nil"]:
            if arg1type != "nil":
                arg1val = Arithmetic.get_float_from_string(frame, arg1val)
            else:
                arg1val = "nil"

            if arg2type != "nil":
                arg2val = Arithmetic.get_float_from_string(frame, arg2val)
            else:
                arg2val = "nil"

            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jump_position
            else:
                return False
        elif arg1type in ["string", "nil"] and arg2type in ["string", "nil"]:
            arg1val = IO.handle_string(arg1val)
            arg2val = IO.handle_string(arg2val)
            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jump_position
            else:
                return False
        elif arg1type in ["bool", "nil"] and arg2type in ["bool", "nil"]:
            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jump_position
            else:
                return False
        else:
            Exit(Exit.EXIT_TYPE)

    def get_instr_args(self):
        arg1, arg1type, arg1val, arg2, arg2type, arg2val = self.check_stack_arguments()
        return arg1type, arg1val, arg2type, arg2val

    def adds(self, frame):
        self.arithmetic_stack_base(frame, "add")

    def subs(self, frame):
        self.arithmetic_stack_base(frame, "sub")

    def muls(self, frame):
        self.arithmetic_stack_base(frame, "mul")

    def idivs(self, frame):
        self.arithmetic_stack_base(frame, "idiv")

    def lts(self, frame):
        self.relational_stack_base(frame, "lt")

    def gts(self, frame):
        self.relational_stack_base(frame, "gt")

    def eqs(self, frame):
        self.relational_stack_base(frame, "eq")

    def ands(self):
        self.logical_stack_base("and")

    def ors(self):
        self.logical_stack_base("or")

    def nots(self):
        self.logical_stack_base("not")

    def int2chars(self):
        """Prevedie číselnú hodnotu druhého argumentu na znak a uloží ho na zásobník

        Args:
            self (_type_): Inštrukcia
        """
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        arg1 = self.dataStack.pop()
        arg1val = arg1.value
        arg1type = arg1.type
        if arg1type != "int":
            Exit(Exit.EXIT_TYPE)
        try:
            arg1.value = chr(int(arg1val))
        except:
            Exit(Exit.EXIT_STRING)
        arg1.type = "string"
        self.dataStack.append(arg1)

    def stri2ints(self, frame):
        """Uloží číselnú hodnotu znaku (prvý operand) na pozícii (druhý operand) na zásobník

        Args:
            self (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        arg1, arg1type, arg1val, arg2type, arg2val = self.check_stack_arguments()

        if arg1type == "string" and arg2type == "int":
            arg1val = IO.handle_string(arg1val)
            arg2val = Arithmetic.get_int_value(frame, arg2val)
            if (arg2val is not None and arg1val is not None) and not (0 <= arg2val < len(arg1val)):
                Exit(Exit.EXIT_STRING)
            if arg2val is not None and arg1val is not None:
                arg1.value = ord(arg1val[arg2val])
                arg1.type = "int"
        else:
            Exit(Exit.EXIT_TYPE)
        self.dataStack.append(arg1)

    def check_stack_arguments(self):
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        arg2 = self.dataStack.pop()
        arg2val = arg2.value
        arg2type = arg2.type
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        arg1 = self.dataStack.pop()
        arg1val = arg1.value
        arg1type = arg1.type
        return arg1, arg1type, arg1val, arg2, arg2type, arg2val

    def jumpifeqs(self, instr, frame, interpret):
        return self.program_flow_stack_base(instr, frame, interpret, "ifeq")

    def jumpifneqs(self, instr, frame, interpret):
        return self.program_flow_stack_base(instr, frame, interpret, "ifneq")
