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
    EXIT_VARIABLE = 54
    EXIT_FRAME = 55

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
            case self.EXIT_VARIABLE:
                err_message = "Chyba - prístup k neexistujúcej premennej"
            case self.EXIT_FRAME:
                err_message = "Chyba - prístup k neexistujúcemu rámcu"
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
        instruction_order = 0
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
                                arg1 = re.sub(r"\s+", "", str(temp_token.text))
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
                        elif re.match(r'arg2$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(0, temp_token.attrib)
                                arg2 = re.sub(r"\s+", "", str(temp_token.text))
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
                        elif re.match(r'arg3$', temp_token.tag):
                            if "type" in temp_token.attrib and temp_token.attrib.get("type") != "":
                                args_list.insert(0, temp_token.attrib)
                                arg3 = re.sub(r"\s+", "", str(temp_token.text))
                            else:
                                Exit(Exit.EXIT_XML_STRUCTURE)
            if instruction_number == 1:
                instruction_number = 0
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
    
    def pushs(self,frame,stack):
        stack.pushs(self,frame)
        
        
        


class Interpret:

    def __init__(self, xml):
        self.Instruction_list = xml.instruction_list
        self.counter = 0
        self.frame = Frame()
        self.stack = Stack()

    def handleInstructions(self):
        for instruction in self.Instruction_list:
            # print(instruction.order)
            match instruction.opcode:
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
                    print()
                case "CALL":
                    print()
                case "LABEL":
                    print()
                case "JUMP":
                    print()
                case "PUSHS":
                    instruction.pushs(self.frame,self.stack)
                case "WRITE":
                    print()
                case "EXIT":
                    print()
                case "DPRINT":
                    print()

class Stack:
    def __init__(self):
        self.dataStack = []
    
    def pushs(self,instr,frame):
        frame.isDefined(instr)
        print ("k")
        

class Frame:
    def __init__(self):
        self.frame_now = {"GF": [], "LF": [], "TF": []}
        self.frameStack = []
        self.local_frame = False
        self.temp_frame = False

    def defVar(self, instr):
        if re.match(r'GF@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$', instr.arg1):
            self.isRedefined(instr, "GF")
            self.frame_now["GF"].append(var(instr.arg1, "GF"))
        elif re.match(r'LF@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$', instr.arg1):
            self.isFrame("LF")
            self.isRedefined(instr, "LF")
            self.frame_now["LF"].append(var(instr.arg1, "LF"))
        elif re.match(r'TF@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$', instr.arg1):
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

    #is redefined?
    def isRedefined(self, instr, frame):
        for instruction in self.frame_now[frame]:
            if instruction.name == instr.arg1:
                Exit(Exit.EXIT_SEMANTIC)
                
    def isDefined(self,instr):
        found = False
        for instruction in self.frame_now[str(self.whichFrame(instr))]:
            if instruction.name == instr.arg1:
                return True
        if found == False:
            Exit(Exit.EXIT_VARIABLE)
                
    def whichFrame(self,instr):
        if re.search('^GF',instr.arg1):
            return "GF"
        elif re.search('^TF',instr.arg1):
            return "TF"
        elif re.search('^LF',instr.arg1):
            return "LF"
        else:
            print ("Asi error")

       


class var:
    def __init__(self, name, frame, type=None):
        self.name = name
        self.frame = frame
        self.type = type


class Program:
    args = Arguments()
    XML = xml(args)
    XML.check()
    XML.parse()
    XML.sort()
    Interpret = Interpret(XML)
    Interpret.handleInstructions()


if __name__ == '__main__':
    Program()
    Exit(Exit.EXIT_SUCCESS)
