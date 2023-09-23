##
# @file XML.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

import re
import sys
from xml.etree import ElementTree as ElementTree

from Classes.Exit import Exit
from Classes.Instruction import Instruction


class XML:
    """Spracuje, skontroluje a rozparsuje zadaný vstupný súbor s XML reprezentáciou kódu"""

    def __init__(self, args):
        """Pomocou knižnice xml.etree.ElementTree spracuje vstupný XML súbor

        Args:
            args (_type_): Spracované argumenty
        """

        self.instruction_list = []
        self.args = args
        if args.get_source():
            try:
                self.tree = ElementTree.parse(args.get_source())
            except ElementTree.ParseError:
                Exit(Exit.EXIT_XML_FORMAT)
            except:
                Exit(Exit.EXIT_INPUT)
        else:
            try:
                self.tree = ElementTree.parse(sys.stdin)
            except:
                Exit(Exit.EXIT_XML_FORMAT)
        try:
            self.root = self.tree.getroot()
        except:
            Exit(Exit.EXIT_XML_FORMAT)

    def check(self):
        """Skontroluje spracovanú XML reprezentáciu kódu"""

        arg_num = 0
        program_check = False
        last_instruction = ""
        order_list = []

        for child in self.root.iter():
            if not program_check:
                if self.root.tag != 'program' or "language" not in self.root.attrib or self.root.attrib[
                    'language'] != "IPPcode23":
                    Exit(Exit.EXIT_XML_STRUCTURE)
                else:
                    program_check = True
                    continue

            if re.match(r'arg[1-3]$', child.tag):
                arg_num += 1
            elif child.tag == "instruction":
                if 'opcode' in child.attrib:
                    self.arg_count(child.attrib['opcode'].upper())
                else:
                    Exit(Exit.EXIT_XML_STRUCTURE)
                if "order" not in child.attrib or not re.match(r'^[1-9][0-9]*$',
                                                               child.attrib['order']) or "opcode" not in child.attrib:
                    Exit(Exit.EXIT_XML_STRUCTURE)
                else:
                    order_list.append(child.attrib['order'])
                    if last_instruction != "" and self.arg_count(last_instruction) != arg_num:
                        Exit(Exit.EXIT_XML_STRUCTURE)
                    arg_num = 0
                    last_instruction = child.attrib.get("opcode")
                    continue
            else:
                Exit(Exit.EXIT_XML_STRUCTURE)

        """Ošetrenie duplicitnej hodnoty order"""
        if len(order_list) != len(set(order_list)):
            Exit(Exit.EXIT_XML_STRUCTURE)

    @staticmethod
    def arg_count(instruction):
        """Vráti a skontroluje počet argumentov zadanej inštrukcie

        Args:
            instruction (_type_): Inštrukcia, ktorej počet má byť skontrolovaný

        Returns:
            _type_: Počet argumentov
        """
        arg_min = -1
        match instruction.upper():
            case "CREATEFRAME" | "PUSHFRAME" | "POPFRAME" | "RETURN" | "BREAK" | "CLEARS" | "ADDS" | "SUBS" | "MULS" | "IDIVS" | "LTS" | "GTS" | "EQS" | "ANDS" | "ORS" | "NOTS" | "INT2CHARS" | "STRI2INTS":
                arg_min = 0
            case "POPS" | "DEFVAR":
                arg_min = 1
            case "CALL" | "LABEL" | "JUMP" | "JUMPIFEQS" | "JUMPIFNEQS":
                arg_min = 1
            case "PUSHS" | "WRITE" | "EXIT" | "DPRINT":
                arg_min = 1
            case "MOVE" | "INT2CHAR" | "INT2FLOAT" | "FLOAT2INT" | "STRLEN" | "TYPE" | "NOT":
                arg_min = 2
            case "READ":
                arg_min = 2
            case "ADD" | "SUB" | "MUL" | "IDIV" | "DIV" | "LT" | "GT" | "EQ" | "OR" | "AND" | "STRI2INT" | "CONCAT" | "GETCHAR" | "SETCHAR":
                arg_min = 3
            case "JUMPIFEQ" | "JUMPIFNEQ":
                arg_min = 3
            case _:
                Exit(Exit.EXIT_XML_STRUCTURE)
        return arg_min

    def parse(self):
        """Spracuje jednotlivé inštrukcie z XML reprezentácie do jednotlivých inštancií triedy Instruction"""
        instruction = ""
        args_list = []
        instruction_number = 0
        self.instruction_list = []
        order = 0
        arg1 = ""
        arg2 = ""
        arg3 = ""
        for token in self.root.iter():
            if token.tag == "instruction":
                instruction = token.attrib.get("opcode")
                order = token.attrib.get("order")
                for temp_token in token.iter():
                    if temp_token.tag == "instruction":
                        instruction_number += 1
                    elif re.match(r'arg[1-3]$', temp_token.tag):
                        if re.match(r'^arg1$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(0, temp_token.attrib)
                                arg1 = str(temp_token.text).strip()
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
                        elif re.match(r'^arg2$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(1, temp_token.attrib)
                                arg2 = str(temp_token.text).strip()
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
                        elif re.match(r'^arg3$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(2, temp_token.attrib)
                                arg3 = str(temp_token.text).strip()
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
            if instruction_number == 1:

                # Kontrola počtu argumentov
                arg_min = self.arg_count(instruction)
                if arg_min == 0 and (arg1 != "" or arg2 != "" or arg3 != ""):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 1 and (arg2 != "" or arg3 != "" or (arg1 == "" and args_list[0]["type"] != "string")):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 2 and (arg1 == "" or arg3 != "" or (arg2 == "" and args_list[1]["type"] != "string")):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 3 and (arg1 == "" or (arg2 == "" and args_list[1]["type"] != "string") or (
                        arg3 == "" and args_list[2]["type"] != "string")):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                instruction_number = 0
                new_instruction = Instruction(
                    instruction, order, args_list, arg1, arg2, arg3)
                self.instruction_list.append(new_instruction)
                instruction = ""
                args_list = []
                arg1 = ""
                arg2 = ""
                arg3 = ""

    def sort(self):
        """Usporiada inštukcie do správneho poradia"""
        self.instruction_list = sorted(
            self.instruction_list, key=lambda x: int(x.order))
        index = 0
        for instruction in self.instruction_list:
            instruction.order = index
            index += 1
