##
# @file ProgramFlow.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

from Classes.Arithmetic import Arithmetic
from Classes.Exit import Exit
from Classes.IO import IO


class ProgramFlow:
    """Trieda združujúca všetky operácie ovplyvňujúce tok programu"""

    @staticmethod
    def jump(instr, interpret):
        """Vykoná skok na návestie (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            interpret (_type_): Interpret pre prístup k návestiam

        Returns:
            _type_: Pozícia na ktorom sa návestie nachádza
        """
        label = None
        jump_position = None
        if instr.args[0]["type"] != "label":
            Exit(Exit.EXIT_TYPE)
        if not interpret.labels:
            Exit(Exit.EXIT_SEMANTIC)
        for label_to_check in interpret.labels:
            if label_to_check == instr.arg1:
                label = label_to_check
                break
        if label is None:
            Exit(Exit.EXIT_SEMANTIC)
        for instruction in interpret.Instruction_list:
            if instruction.arg1 == label and instruction.opcode == "LABEL":
                jump_position = instruction.order
        if jump_position is not None:
            return jump_position

    @staticmethod
    def jumpif_base(instr, frame, interpret, operation):
        """Vykoná skok pri rovnosti (operácia ifeq) alebo nerovnosti (operácia ifneq) druhého a tretieho argumentu

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            interpret (_type_): Interpret pre prístup k návestiam
            operation (_type_): Operácia ifeq alebo ifneq

        Returns:
            _type_: Pozícia na ktorom sa návestie nachádza
        """
        jump_position = ProgramFlow.jump(instr, interpret)
        if frame.is_var(instr.arg2):
            arg1type = frame.get_var(instr.arg2).type
            arg1val = frame.get_var(instr.arg2).value
        else:
            arg1type = instr.args[1]["type"]
            arg1val = instr.arg2

        if frame.is_var(instr.arg3):
            arg2type = frame.get_var(instr.arg3).type
            arg2val = frame.get_var(instr.arg3).value
        else:
            arg2type = instr.args[2]["type"]
            arg2val = instr.arg3
        if arg1type in ["int", "nil"] and arg2type in ["int", "nil"]:
            if arg1type != "nil":
                arg1val = Arithmetic.get_int_value(frame, instr.arg2)
            else:
                arg1val = "nil"

            if arg2type != "nil":
                arg2val = Arithmetic.get_int_value(frame, instr.arg3)
            else:
                arg2val = "nil"

            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jump_position
            else:
                return False
        elif arg1type in ["float", "nil"] and arg2type in ["float", "nil"]:
            if arg1type != "nil":
                arg1val = Arithmetic.get_float_from_string(frame, instr.arg2)
            else:
                arg1val = "nil"

            if arg2type != "nil":
                arg2val = Arithmetic.get_float_from_string(frame, instr.arg3)
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

    @staticmethod
    def jumpifeq(instr, frame, interpret):
        return ProgramFlow.jumpif_base(instr, frame, interpret, "ifeq")

    @staticmethod
    def jumpifneq(instr, frame, interpret):
        return ProgramFlow.jumpif_base(instr, frame, interpret, "ifneq")
