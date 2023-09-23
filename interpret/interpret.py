##
# @file interpret.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

import sys

from Classes.Arguments import Arguments
from Classes.Arithmetic import Arithmetic
from Classes.Exit import Exit
from Classes.Frame import Frame
from Classes.IO import IO
from Classes.Logical import Logical
from Classes.ProgramFlow import ProgramFlow
from Classes.Relational import Relational
from Classes.Stack import Stack
from Classes.String import String
from Classes.XML import XML


class Interpret:
    """Trieda obsahujúca XML reprezentáciu kódu, list inštrukcií, jednotlivé rámce, zásobníky, návestia a zásobník
    volaní"""

    def __init__(self, xml):
        self.xml = xml
        self.Instruction_list = xml.instruction_list
        self.frame = Frame()
        self.stack = Stack()
        self.labels = []
        self.callStack = []

    def handle_instructions(self):
        """Vykoná jednotlivé inštrukcie v poradí určenom pomocou order"""
        program_counter = 0
        while program_counter < len(self.Instruction_list):
            instruction = self.Instruction_list[program_counter]
            match instruction.opcode.upper():
                case "CREATEFRAME":
                    self.frame.create()
                case "PUSHFRAME":
                    self.frame.push()
                case "POPFRAME":
                    self.frame.pop()
                case "RETURN":
                    if self.callStack:
                        program_counter = self.callStack.pop()
                    else:
                        Exit(Exit.EXIT_VALUE)
                case "BREAK":
                    IO.break_i(instruction, self.frame)
                case "DEFVAR":
                    self.frame.def_var(instruction)
                case "POPS":
                    self.stack.pops(instruction, self.frame)
                case "CLEARS":
                    self.stack.clears()
                case "ADDS":
                    self.stack.adds(self.frame)
                case "SUBS":
                    self.stack.subs(self.frame)
                case "MULS":
                    self.stack.muls(self.frame)
                case "IDIVS":
                    self.stack.idivs(self.frame)
                case "LTS":
                    self.stack.lts(self.frame)
                case "GTS":
                    self.stack.gts(self.frame)
                case "EQS":
                    self.stack.eqs(self.frame)
                case "ANDS":
                    self.stack.ands()
                case "ORS":
                    self.stack.ors()
                case "NOTS":
                    self.stack.nots()
                case "INT2CHARS":
                    self.stack.int2chars()
                case "STRI2INTS":
                    self.stack.stri2ints(self.frame)
                case "JUMPIFEQS":
                    ret_value = self.stack.jumpifeqs(
                        instruction, self.frame, self)
                    if ret_value != False and ret_value < len(self.Instruction_list):
                        program_counter = ret_value
                case "JUMPIFNEQS":
                    ret_value = self.stack.jumpifneqs(
                        instruction, self.frame, self)
                    if ret_value != False and ret_value < len(self.Instruction_list):
                        program_counter = ret_value
                case "CALL":
                    self.callStack.append(program_counter)
                    ret_value = ProgramFlow.jump(instruction, self)
                    if ret_value < len(self.Instruction_list):
                        program_counter = ret_value
                    else:
                        break
                case "LABEL":
                    pass
                case "JUMP":
                    ret_value = ProgramFlow.jump(instruction, self)
                    if ret_value < len(self.Instruction_list):
                        program_counter = ret_value
                    else:
                        break
                case "PUSHS":
                    self.stack.pushs(instruction, self.frame)
                case "WRITE":
                    IO.write(instruction, self.frame,
                             output_stream=sys.stdout)
                case "EXIT":
                    IO.exit(instruction, self.frame)
                case "DPRINT":
                    IO.dprint(instruction, self.frame)
                case "MOVE":
                    self.frame.move(instruction)
                case "INT2CHAR":
                    String.int2char(instruction, self.frame)
                case "INT2FLOAT":
                    Arithmetic.int2float(instruction, self.frame)
                case "FLOAT2INT":
                    Arithmetic.float2int(instruction, self.frame)
                case "STRLEN":
                    String.strlen(instruction, self.frame)
                case "TYPE":
                    self.frame.type(instruction)
                case "NOT":
                    Logical.not_i(instruction, self.frame)
                case "READ":
                    IO.read(instruction, self.frame, self.xml)
                case "ADD":
                    Arithmetic.add(instruction, self.frame)
                case "SUB":
                    Arithmetic.sub(instruction, self.frame)
                case "MUL":
                    Arithmetic.mul(instruction, self.frame)
                case "IDIV":
                    Arithmetic.idiv(instruction, self.frame)
                case "DIV":
                    Arithmetic.div(instruction, self.frame)
                case "LT":
                    Relational.lt(instruction, self.frame)
                case "GT":
                    Relational.gt(instruction, self.frame)
                case "EQ":
                    Relational.eq(instruction, self.frame)
                case "AND":
                    Logical.and_i(instruction, self.frame)
                case "OR":
                    Logical.or_i(instruction, self.frame)
                case "STRI2INT":
                    String.stri2int(instruction, self.frame)
                case "CONCAT":
                    String.concat(instruction, self.frame)
                case "GETCHAR":
                    String.getchar(instruction, self.frame)
                case "SETCHAR":
                    String.setchar(instruction, self.frame)
                case "JUMPIFEQ":
                    ret_value = ProgramFlow.jumpifeq(
                        instruction, self.frame, self)
                    if ret_value != False and ret_value < len(self.Instruction_list):
                        program_counter = ret_value

                case "JUMPIFNEQ":
                    ret_value = ProgramFlow.jumpifneq(
                        instruction, self.frame, self)
                    if ret_value != False and ret_value < len(self.Instruction_list):
                        program_counter = ret_value
                case _:
                    Exit(Exit.EXIT_XML_STRUCTURE)
            program_counter += 1

    def handle_labels(self):
        """Spracuje jednotlivé návestia ešte pred vykonaním jednotlivých inštrukcií"""
        for instruction in self.Instruction_list:
            if instruction.opcode.upper() == "LABEL":
                if instruction.arg1 not in self.labels:
                    self.labels.append(instruction.arg1)
                else:
                    Exit(Exit.EXIT_SEMANTIC)


if __name__ == '__main__':
    args = Arguments()
    XML = XML(args)
    XML.check()
    XML.parse()
    XML.sort()
    Interpret = Interpret(XML)
    Interpret.handle_labels()
    Interpret.handle_instructions()
    Exit(Exit.EXIT_SUCCESS)
