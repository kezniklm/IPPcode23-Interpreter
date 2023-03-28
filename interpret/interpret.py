"""
@file interpret.py

@brief Interpret XML reprezentácie jazyka IPPcode23

@author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>
"""
import xml.etree.ElementTree as ET
import sys
import re

SCRIPT_NAME = 0
MAX_ARGUMENTS = 2

ZERO_ARGUMENTS = 0
ONE_ARGUMENT = 1


class Arguments:
    """Trieda pre spracovanie vstupných argumentov skriptu"""

    def __init__(self):
        self.source = ""
        self.input = ""
        # self.argc = 0
        args = sys.argv[SCRIPT_NAME + 1:]
        if len(args) > MAX_ARGUMENTS:
            Exit(Exit.EXIT_PARAM)

        for argument in args:
            match(argument.split("=")):
                case ['--help']:
                    if len(args) == 1:
                        Exit(Exit.EXIT_SUCCESS, True)
                    else:
                        Exit(Exit.EXIT_PARAM)
                case ['--source', file]:
                    if not file:
                        Exit(Exit.EXIT_INPUT)
                    self.source = file
                case ['--input', file]:
                    # self.argc += 1
                    self.input = file
                case _:
                    Exit(Exit.EXIT_PARAM)

    def Source(self):
        return self.source

    def Input(self):
        return self.input


class Exit:
    """Trieda slúžiaca na ukončenie programu"""

    EXIT_SUCCESS = 0
    EXIT_PARAM = 10
    EXIT_INPUT = 11
    EXIT_OUTPUT = 12
    EXIT_XML_FORMAT = 31
    EXIT_XML_STRUCTURE = 32
    EXIT_SEMANTIC = 52
    EXIT_TYPE = 53
    EXIT_VARIABLE = 54
    EXIT_FRAME = 55
    EXIT_VALUE = 56

    def __init__(self, type, help=None):
        err_message = ""
        match type:
            case self.EXIT_SUCCESS:
                if help == True:
                    print("help string", file=sys.stdout)
                sys.exit(type)
            case self.EXIT_PARAM:
                err_message = "Zadaná chybná kombinácia alebo chybný počet argumentov skriptu interpret.py\n"
            case self.EXIT_INPUT:
                err_message = "Chyba pri otváraní vstupných súborov"
            case self.EXIT_XML_FORMAT:
                err_message = "Chybný XML formát vo vstupnom súbore"
            case self.EXIT_XML_STRUCTURE:
                err_message = "Chybná štruktúra XML"
            case self.EXIT_SEMANTIC:
                err_message = "Chyba pri sémantických kontrolách vstupného kódu v IPPcode23"
            case self.EXIT_TYPE:
                err_message = "Chyba pri typových kontrolách vstupného kódu v IPPcode23"
            case self.EXIT_VARIABLE:
                err_message = "Chyba - prístup k neexistujúcej premennej"
            case self.EXIT_FRAME:
                err_message = "Chyba - prístup k neexistujúcemu rámcu"
            case self.EXIT_VALUE:
                err_message = "Chyba -  stack"

            case _:
                err_message = "Zadaný zlý chybový kód"

        print(err_message, file=sys.stderr)
        sys.exit(type)


class xml():
    """XML comment"""

    def __init__(self, args):
        if args.Source():
            try:
                self.tree = ET.parse(args.Source())
            except ET.ParseError:
                Exit(Exit.EXIT_XML_FORMAT)
            except:
                Exit(Exit.EXIT_INPUT)
        else:
            try:
                self.tree = ET.parse(sys.stdin)
            except:
                Exit(Exit.EXIT_XML_FORMAT)
        try:
            self.root = self.tree.getroot()
        except:
            Exit(Exit.EXIT_XML_FORMAT)

    def check(self):

        arg_num = 0
        program_check = False
        last_instruction = ""
        order_list = []

        for child in self.root.iter():
            if not program_check:
                if self.root.tag != 'program' or "language" not in self.root.attrib or self.root.attrib['language'] != "IPPcode23":
                    Exit(Exit.EXIT_XML_STRUCTURE)
                else:
                    program_check = True
                    continue

            if re.match(r'arg[1-3]$', child.tag):
                arg_num += 1
            elif child.tag == "instruction":

                if "order" not in child.attrib or not re.match(r'^[1-9][0-9]*$', child.attrib['order']) or "opcode" not in child.attrib or child.attrib['opcode'].upper() not in Instruction.list:
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
        if (len(order_list) != len(set(order_list))):
            Exit(Exit.EXIT_XML_STRUCTURE)

         # TODO check xml version and encoding

    def arg_count(self, last_instruction):
        arg_min = -1
        match last_instruction.upper():
            case "CREATEFRAME" | "PUSHFRAME" | "POPFRAME" | "RETURN" | "BREAK":
                arg_min = 0
            case "POPS" | "DEFVAR":
                arg_min = 1
            case "CALL" | "LABEL" | "JUMP":
                arg_min = 1
            case "PUSHS" | "WRITE" | "EXIT" | "DPRINT":
                arg_min = 1
            case "MOVE" | "INT2CHAR" | "STRLEN" | "TYPE" | "NOT":
                arg_min = 2
            case "READ":
                arg_min = 2
            case "ADD" | "SUB" | "MUL" | "IDIV" | "LT" | "GT" | "EQ" | "OR" | "AND" | "STRI2INT" | "CONCAT" | "GETCHAR" | "SETCHAR":
                arg_min = 3
            case "JUMPIFEQ" | "JUMPIFNEQ":
                arg_min = 3
            case _:

                Exit(Exit.EXIT_XML_STRUCTURE)
        return arg_min

    def parse(self):
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
                        if re.match(r'arg1$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(0, temp_token.attrib)
                                arg1 = str(temp_token.text)
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
                        elif re.match(r'arg2$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(0, temp_token.attrib)
                                arg2 = str(temp_token.text)
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
                        elif re.match(r'arg3$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(0, temp_token.attrib)
                                arg3 = str(temp_token.text)
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
            if instruction_number == 1:
                # kontrola arg
                arg_min = self.arg_count(instruction)
                if arg_min == 0 and (arg1 != "" or arg2 != "" or arg3 != ""):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 1 and (arg1 == "" or arg2 != "" or arg3 != ""):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 2 and (arg1 == "" or arg2 == "" or arg3 != ""):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 3 and (arg1 == "" or arg2 == "" or arg3 == ""):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                instruction_number = 0
                args_list.reverse()
                new_Instruction = Instruction(
                    instruction, order, args_list, arg1, arg2, arg3)
                self.instruction_list.append(new_Instruction)
                instruction = ""
                args_list = []
                arg1 = ""
                arg2 = ""
                arg3 = ""

    def sort(self):
        """Sort"""
        self.instruction_list = sorted(
            self.instruction_list, key=lambda x: int(x.order))


class Instruction:
    list = {
        "CREATEFRAME": [None],
        "PUSHFRAME": [None],
        "POPFRAME": [None],
        "RETURN": [None],
        "BREAK": [None],
        "DEFVAR": ["var"],
        "POPS": ["var"],
        "CALL": ["label"],
        "LABEL": ["label"],
        "JUMP": ["label"],
        "PUSHS": ["symb"],
        "EXIT": ["symb"],
        "DPRINT": ["symb"],
        "WRITE": ["symb"],
        "MOVE": ["var", "symb"],
        "INT2CHAR": ["var", "symb"],
        "STRLEN": ["var", "symb"],
        "TYPE": ["var", "symb"],
        "READ": ["var", "type"],
        "ADD": ["var", "symb", "symb"],
        "SUB": ["var", "symb", "symb"],
        "MUL": ["var", "symb", "symb"],
        "IDIV": ["var", "symb", "symb"],
        "LT": ["var", "symb", "symb"],
        "GT": ["var", "symb", "symb"],
        "EQ": ["var", "symb", "symb"],
        "AND": ["var", "symb", "symb"],
        "OR": ["var", "symb", "symb"],
        "NOT": ["var", "symb", "symb"],
        "STRI2INT": ["var", "symb", "symb"],
        "CONCAT": ["var", "symb", "symb"],
        "GETCHAR": ["var", "symb", "symb"],
        "SETCHAR": ["var", "symb", "symb"],
        "JUMPIFEQ": ["label", "symb", "symb"],
        "JUMPIFNEQ": ["label", "symb", "symb"]
    }

    def __init__(self, opcode, order, list_of_args, arg1, arg2, arg3):
        self.opcode = opcode
        self.order = order
        self.args = list_of_args
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def createFrame(self, frame):
        frame.create()

    def pushFrame(self, frame):
        frame.push()

    def popFrame(self, frame):
        frame.pop()

    def defVar(self, frame):
        frame.defVar(self)

    def pushs(self, frame, stack):
        stack.pushs(self, frame)

    def pops(self, frame, stack):
        stack.pops(self, frame)

    def add(self, frame):
        Arithmetic.add(self, frame)


class Interpret:

    def __init__(self, xml):
        self.Instruction_list = xml.instruction_list
        self.counter = 0
        self.frame = Frame()
        self.stack = Stack()
        self.labels = []

    def handleInstructions(self):
        for instruction in self.Instruction_list:
            match instruction.opcode.upper():
                case "CREATEFRAME":
                    instruction.createFrame(self.frame)
                case "PUSHFRAME":
                    instruction.pushFrame(self.frame)
                case "POPFRAME":
                    instruction.popFrame(self.frame)
                case "RETURN":
                    print()
                case "BREAK":
                    print()
                case "DEFVAR":
                    instruction.defVar(self.frame)
                case "POPS":
                    instruction.pops(self.frame, self.stack)
                case "CALL":
                    print()
                case "LABEL":
                    print()
                case "JUMP":
                    print()
                case "PUSHS":
                    instruction.pushs(self.frame, self.stack)
                case "WRITE":
                    print()
                case "EXIT":
                    print()
                case "DPRINT":
                    print()
                case "MOVE":
                    print()
                case "INT2CHAR":
                    print()
                case "STRLEN":
                    print()
                case "TYPE":
                    print()
                case "NOT":
                    print()
                case "READ":
                    print()
                case "ADD":
                    instruction.add(self.frame)
                case "SUB":
                    print()
                case "MUL":
                    print()
                case "IDIV":
                    print()
                case "LT":
                    print()
                case "GT":
                    print()
                case "EQ":
                    print()
                case "AND":
                    print()
                case "OR":
                    print()
                case "STRI2INT":
                    print()
                case "CONCAT":
                    print()
                case "GETCHAR":
                    print()
                case "SETCHAR":
                    print()
                case "JUMPIFEQ":
                    print()
                case "JUMPIFNEQ":
                    print()
                case _:
                    Exit(Exit.EXIT_XML_STRUCTURE)

    def handleLabels(self):
        for instruction in self.Instruction_list:
            if instruction.opcode.upper() == "LABEL":
                if instruction.arg1 not in self.labels:
                    self.labels.append(instruction.arg1)
                else:
                    Exit(Exit.EXIT_SEMANTIC)


class Arithmetic:
    @staticmethod
    def add(instr, frame):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                frame.isDefined(instr.arg1)
                if ((instr.args[1]["type"] == "var" and frame.isDefined(instr.arg2)) or instr.args[1]["type"] == "int") and ((instr.args[2]["type"] == "var" and frame.isDefined(instr.arg3)) or instr.args[2]["type"] == "int"):
                    # osetrit hexa a octa
                    arg2value = None
                    arg3value = None
                    if frame.isVar(instr.arg2):
                        arg2value = frame.getValue(instr.arg2)
                    if frame.isVar(instr.arg3):
                        arg3value = frame.getValue(instr.arg3)

                    if variable.value == None:
                        variable.value = 0
                        variable.type = "int"

                    if arg2value == None and arg3value == None:
                        variable.value = int(
                            variable.value) + int(instr.arg2) + int(instr.arg3)
                    elif arg2value != None and arg3value == None:
                        variable.value = int(
                            variable.value) + int(arg2value) + int(instr.arg3)
                    elif arg2value == None and arg3value != None:
                        variable.value = int(
                            variable.value) + int(instr.arg2) + int(arg3value)
                    elif arg2value != None and arg3value != None:
                        variable.value = int(
                            variable.value) + int(arg2value) + int(arg3value)

                    variable.type = "int"
                    oldFrame = frame.isDefined(instr.arg1)
                    frame.frame_now[frame.isDefined(instr.arg1)].remove(variable)
                    frame.frame_now[oldFrame].append(variable)
                else:
                    Exit(Exit.EXIT_TYPE)
                    
class IO:
    
    @staticmethod
    def read(instr, frame):
        print()
        
    @staticmethod
    def write(instr, frame):
        print()


class Stack:
    def __init__(self):
        self.dataStack = []

    def pushs(self, instr, frame):
        if frame.isDefined(instr.arg1) == "TF" or frame.isDefined(instr.arg1) == "LF" or frame.isDefined(instr.arg1) == "GF":
            for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
                if variable.name == instr.arg1:
                    if variable.value == None or variable.type == None:
                        Exit(Exit.EXIT_VALUE)
                    self.dataStack.append(variable)
                    frame.frame_now[frame.isDefined(
                        instr.arg1)].remove(variable)
                    break
        else:
            new_const = Constant(instr.args[0]["type"], instr.arg1)
            self.dataStack.append(new_const)

    def pops(self, instr, frame):
        if not self.dataStack:
            Exit(Exit.EXIT_VALUE)
        if frame.isDefined(instr.arg1) == "TF" or frame.isDefined(instr.arg1) == "LF" or frame.isDefined(instr.arg1) == "GF":
            temp = self.dataStack.pop()
            var = -1
            for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
                if variable.name == instr.arg1:
                    var = variable
                    break
            index = frame.frame_now[frame.isDefined(instr.arg1)].index(var)
            frame.frame_now[frame.isDefined(
                instr.arg1)][index].value = temp.value
            frame.frame_now[frame.isDefined(
                instr.arg1)][index].type = temp.type


class Frame:
    def __init__(self):
        self.frame_now = {"GF": [], "LF": [], "TF": []}
        self.frameStack = []
        self.local_frame = False
        self.temp_frame = False

    def defVar(self, instr):
        if re.match(r'\s*GF@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*\s*$', instr.arg1):
            self.isRedefined(instr, "GF")
            self.frame_now["GF"].append(var(instr.arg1, "GF"))
        elif re.match(r'\s*LF@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*\s*$', instr.arg1):
            self.isFrame("LF")
            self.isRedefined(instr, "LF")
            self.frame_now["LF"].append(var(instr.arg1, "LF"))
        elif re.match(r'\s*TF@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*\s*$', instr.arg1):
            self.isFrame("TF")
            self.isRedefined(instr, "TF")
            self.frame_now["TF"].append(var(instr.arg1, "TF"))
        else:
            Exit(Exit.EXIT_XML_STRUCTURE)

    def create(self):
        self.temp_frame = True
        self.frame_now["TF"].clear()

    def push(self):
        self.isFrame("TF")
        if self.local_frame == True:
            self.frameStack.append(self.frame_now["LF"])
            self.frame_now["LF"].clear()
        for variable in self.frame_now["TF"]:
            variable.name = re.sub("^TF", "LF", variable.name)
            self.frame_now["LF"].append(variable)
        self.temp_frame = False
        self.local_frame = True

    def pop(self):
        self.isFrame("LF")
        self.frame_now["TF"].clear()
        for variable in self.frame_now["LF"]:
            variable.name = re.sub("^LF", "TF", variable.name)
            self.frame_now["TF"].append(variable)
        self.temp_frame = True
        if not self.frameStack:
            self.local_frame = False
            self.frame_now["LF"].clear()
        else:
            self.local_frame = True
            self.frameStack.pop()

    def isFrame(self, frame):
        if frame == "TF" and self.temp_frame == False:
            Exit(Exit.EXIT_FRAME)
        elif frame == "LF" and self.local_frame == False:
            Exit(Exit.EXIT_FRAME)

    # is redefined?
    def isRedefined(self, instr, frame):
        for instruction in self.frame_now[frame]:
            if instruction.name == instr.arg1:
                Exit(Exit.EXIT_SEMANTIC)

    def isDefined(self, arg):
        for instruction in self.frame_now["TF"]:
            if instruction.name == arg:
                if re.match(r'^TF@', arg):
                    self.isFrame("TF")
                    return "TF"

        for instruction in self.frame_now["LF"]:
            if instruction.name == arg:
                if re.match(r'^LF@', arg):
                    self.isFrame("LF")
                    return "LF"

        for instruction in self.frame_now["GF"]:
            if instruction.name == arg:
                return "GF"

        if re.match(r'^TF@', arg):
            self.isFrame("TF")
        elif re.match(r'^LF@', arg):
            self.isFrame("LF")

        if not self.isVar(arg):
            return "True"
        Exit(Exit.EXIT_VARIABLE)

    def isVar(self, arg):
        if re.match(r'^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)+[0-9]*(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$', arg):
            return True
        else:
            return False

    def retFrame(self, instr):
        if self.isDefined(instr.arg1) == "TF":
            return "TF"
        elif self.isDefined(instr.arg1) == "LF":
            return "LF"
        elif self.isDefined(instr.arg1) == "GF":
            return "GF"
        else:
            Exit(Exit.EXIT_VARIABLE)

    def getValue(self, arg):
        for variable in self.frame_now[str(self.isDefined(arg))]:
            if variable.name == arg:
                if variable.value == None:
                    Exit(Exit.EXIT_VALUE)
                return variable.value


class var:
    def __init__(self, name, frame, type=None, value=None):
        self.name = name
        self.frame = frame
        self.type = type
        self.value = value


class Constant:
    def __init__(self, type, value):
        self.type = type
        self.value = value


class Program:
    args = Arguments()
    XML = xml(args)
    XML.check()
    XML.parse()
    XML.sort()
    Interpret = Interpret(XML)
    Interpret.handleLabels()
    Interpret.handleInstructions()


if __name__ == '__main__':
    Program()
    Exit(Exit.EXIT_SUCCESS)
