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


class Arguments:
    """Trieda pre spracovanie vstupných argumentov skriptu"""

    def __init__(self):
        self.source = ""
        self.input = ""
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
                    try:
                        self.input = open(file, "r")
                    except:
                        Exit(Exit.EXIT_INPUT)
                case _:
                    Exit(Exit.EXIT_PARAM)

    def Source(self):
        return self.source

    def Input(self):
        return self.input


class Exit:
    """Trieda slúžiaca na ukončenie programu podľa zadaného exit kódu"""

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
    EXIT_OPERAND = 57
    EXIT_STRING = 58

    def __init__(self, type, help=None):
        err_message = ""
        match type:
            case self.EXIT_SUCCESS:
                if help == True:
                    print(
                        "Názov:\ninterpret.py - interpret jazyka IPPcode23 v XML reprezentácii kódu\n\nPoužitie:\n    python3 interpret.py [MOŽNOSTI]\nPopis:\n    interpret.py vykoná interpretáciu XML reprezentácie kódu zo zdrojovového súboru\nMOŽNOSTI\n    --help\n        Vypíše pomocnú hlášku pre skript interpet.py\n    --source=file\n        Vstupný súbor s XML reprezentaciou zdrojového kódu\n    --input=file\n        Súbor so vstupmi pre samotú interpretáciu zadaného zdrojového kódu", file=sys.stdout)
                sys.exit(type)
            case self.EXIT_PARAM:
                err_message = "CHYBA:\nZadaná chybná kombinácia alebo chybný počet argumentov skriptu interpret.py\n"
            case self.EXIT_INPUT:
                err_message = "CHYBA:\nNie je možné otvoriť vstupné súbory"
            case self.EXIT_XML_FORMAT:
                err_message = "CHYBA:\nXML nie je well-formed - chybný XML formát"
            case self.EXIT_XML_STRUCTURE:
                err_message = "CHYBA:\nŠtruktúra XML nie je správna"
            case self.EXIT_SEMANTIC:
                err_message = "CHYBA:\nPri sémantických kontrolách vstupného kódu v IPPcode23 nastala chyba"
            case self.EXIT_TYPE:
                err_message = "CHYBA:\nPri typových kontrolách vstupného kódu v IPPcode23 nastala chyba"
            case self.EXIT_VARIABLE:
                err_message = "CHYBA:\nPrístup k neexistujúcej premennej"
            case self.EXIT_FRAME:
                err_message = "CHYBA:\nPrístup k neexistujúcemu rámcu"
            case self.EXIT_VALUE:
                err_message = "CHYBA:\nChýbajúca hodnota napr. v premennej,zasobniku volani alebo na zasobniku"
            case self.EXIT_OPERAND:
                err_message = "CHYBA:\nChybná hodnota operandu"
            case self.EXIT_STRING:
                err_message = "CHYBA:\nChybná práca s reťazcom"

        print(err_message, file=sys.stderr)
        sys.exit(type)


class xml():
    """Trieda, ktorá spracuje zadaný vstupný súbor s xml reprezentáciou kódu"""

    def __init__(self, args):
        self.args = args
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
                # kontrola arg
                arg_min = self.arg_count(instruction)
                if arg_min == 0 and (arg1 != "" or arg2 != "" or arg3 != ""):
                    Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 1 and (arg2 != "" or arg3 != "" or (arg1 == "" and args_list[0]["type"] != "string")): 
                        Exit(Exit.EXIT_XML_STRUCTURE)
                elif arg_min == 2 and (arg1 == "" or arg3 != "" or (arg2 == "" and args_list[1]["type"] != "string")):
                    Exit(Exit.EXIT_XML_STRUCTURE)       
                elif arg_min == 3 and (arg1 == "" or (arg2 == "" and args_list[1]["type"] != "string") or (arg3 == "" and args_list[2]["type"] != "string")):
                    Exit(Exit.EXIT_XML_STRUCTURE)
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
        """Usporiada inštukcie do správneho poradia"""
        self.instruction_list = sorted(
            self.instruction_list, key=lambda x: int(x.order))
        index = 0
        for instruction in self.instruction_list:
            instruction.order = index
            index += 1


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

    def move(self, frame):
        frame.move(self)

    def createFrame(self, frame):
        frame.create()

    def pushFrame(self, frame):
        frame.push()

    def popFrame(self, frame):
        frame.pop()

    def defVar(self, frame):
        frame.defVar(self)

    def type(self, frame):
        frame.type(self)

    def pushs(self, frame, stack):
        stack.pushs(self, frame)

    def pops(self, frame, stack):
        stack.pops(self, frame)

    def add(self, frame):
        Arithmetic.add(self, frame)

    def sub(self, frame):
        Arithmetic.sub(self, frame)

    def mul(self, frame):
        Arithmetic.mul(self, frame)

    def idiv(self, frame):
        Arithmetic.idiv(self, frame)

    def lt(self, frame):
        Relational.lt(self, frame)

    def gt(self, frame):
        Relational.gt(self, frame)

    def eq(self, frame):
        Relational.eq(self, frame)

    def andI(self, frame):
        Logical.andI(self, frame)

    def notI(self, frame):
        Logical.notI(self, frame)

    def orI(self, frame):
        Logical.orI(self, frame)

    def writeI(self, frame):
        IO.writeI(self, frame, output_stream=sys.stdout)

    def read(self, frame, xml):
        IO.read(self, frame, xml)

    def exit(self, frame):
        IO.exit(self, frame)

    def dprint(self, frame):
        IO.dprint(self, frame)

    def int2char(self, frame):
        String.int2char(self, frame)

    def stri2int(self, frame):
        String.stri2int(self, frame)

    def concat(self, frame):
        String.concat(self, frame)

    def strlen(self, frame):
        String.strlen(self, frame)

    def getchar(self, frame):
        String.getchar(self, frame)

    def setchar(self, frame):
        String.setchar(self, frame)

    def breakI(self, frame):
        IO.breakI(self, frame)

    def call(self, frame):
        programFlow.call(self, frame)

    def label(self, frame):
        programFlow.label(self, frame)

    def jump(self, frame, interpret):
        return programFlow.jump(self, frame, interpret)

    def jumpifeq(self, frame, interpret):
        return programFlow.jumpifeq(self, frame,interpret)

    def jumpifneq(self, frame, interpret):
        return programFlow.jumpifneq(self, frame, interpret)


class Interpret:

    def __init__(self, xml):
        self.xml = xml
        self.Instruction_list = xml.instruction_list
        self.counter = 0
        self.frame = Frame()
        self.stack = Stack()
        self.labels = []
        self.callStack = []

    def handleInstructions(self):
        program_counter = 0
        while (program_counter < len(self.Instruction_list)):
            instruction = self.Instruction_list[program_counter]
            # print(instruction.opcode)
            match instruction.opcode.upper():
                case "CREATEFRAME":
                    instruction.createFrame(self.frame)
                case "PUSHFRAME":
                    instruction.pushFrame(self.frame)
                case "POPFRAME":
                    instruction.popFrame(self.frame)
                case "RETURN":
                    pass
                    # instruction.returnI(self.frame)
                case "BREAK":
                    instruction.breakI(self.frame)
                case "DEFVAR":
                    instruction.defVar(self.frame)
                case "POPS":
                    instruction.pops(self.frame, self.stack)
                case "CALL":
                    instruction.call(self.frame)
                case "LABEL":
                    pass
                case "JUMP":
                    retValue = instruction.jump(self.frame, self)
                    if retValue < len(self.Instruction_list):
                        program_counter = retValue
                    else:
                        break
                case "PUSHS":
                    instruction.pushs(self.frame, self.stack)
                case "WRITE":
                    instruction.writeI(self.frame)
                case "EXIT":
                    instruction.exit(self.frame)
                case "DPRINT":
                    instruction.dprint(self.frame)
                case "MOVE":
                    instruction.move(self.frame)
                case "INT2CHAR":
                    instruction.int2char(self.frame)
                case "STRLEN":
                    instruction.strlen(self.frame)
                case "TYPE":
                    instruction.type(self.frame)
                case "NOT":
                    instruction.notI(self.frame)
                case "READ":
                    instruction.read(self.frame, self.xml)
                case "ADD":
                    instruction.add(self.frame)
                case "SUB":
                    instruction.sub(self.frame)
                case "MUL":
                    instruction.mul(self.frame)
                case "IDIV":
                    instruction.idiv(self.frame)
                case "LT":
                    instruction.lt(self.frame)
                case "GT":
                    instruction.gt(self.frame)
                case "EQ":
                    instruction.eq(self.frame)
                case "AND":
                    instruction.andI(self.frame)
                case "OR":
                    instruction.orI(self.frame)
                case "STRI2INT":
                    instruction.stri2int(self.frame)
                case "CONCAT":
                    instruction.concat(self.frame)
                case "GETCHAR":
                    instruction.getchar(self.frame)
                case "SETCHAR":
                    instruction.setchar(self.frame)
                case "JUMPIFEQ":
                    retValue = instruction.jumpifeq(self.frame,self)
                    if retValue != False and retValue < len(self.Instruction_list):
                        program_counter = retValue
                         
                case "JUMPIFNEQ":
                    retValue = instruction.jumpifneq(self.frame,self)
                    if retValue != False and retValue < len(self.Instruction_list):
                        program_counter = retValue
                case _:
                    Exit(Exit.EXIT_XML_STRUCTURE)
            program_counter += 1

    def handleLabels(self):
        for instruction in self.Instruction_list:
            if instruction.opcode.upper() == "LABEL":
                if instruction.arg1 not in self.labels:
                    self.labels.append(instruction.arg1)
                else:
                    Exit(Exit.EXIT_SEMANTIC)


class Arithmetic:

    @staticmethod
    def base(instr, frame, operation):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                frame.isDefined(instr.arg1)
                if ((instr.args[1]["type"] == "var" and frame.isDefined(instr.arg2)) or instr.args[1]["type"] == "int") and ((instr.args[2]["type"] == "var" and frame.isDefined(instr.arg3)) or instr.args[2]["type"] == "int"):
                    oldFrame = frame.isDefined(instr.arg1)
                    arg2value = Arithmetic.getIntValue(frame, instr.arg2)
                    arg3value = Arithmetic.getIntValue(frame, instr.arg3)
                    try:
                        match operation:
                            case "add":
                                if arg2value != None and arg3value != None:
                                    variable.value = arg2value + arg3value
                            case "sub":
                                if arg2value != None and arg3value != None:
                                    variable.value = arg2value - arg3value
                            case "mul":
                                if arg2value != None and arg3value != None:
                                    variable.value = arg2value * arg3value
                            case "idiv":
                                if arg2value != None and arg3value != None:
                                    if arg3value != 0:
                                        variable.value = arg2value // arg3value
                                    else:
                                        raise SystemExit
                    except SystemExit:
                        Exit(Exit.EXIT_OPERAND)
                    except:
                        Exit(Exit.EXIT_XML_STRUCTURE)
                    variable = Arithmetic.setNone(variable, "int")
                    variable.type = "int"
                    frame.frame_now[frame.isDefined(
                        instr.arg1)].remove(variable)
                    frame.frame_now[oldFrame].append(variable)
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
    def hexToDec(number):
        try:
            number = int(number, 16)
        except:
            return number
        return number

    @staticmethod
    def octaToDec(number):
        try:
            number = int(number, 8)
        except:
            return number
        return number

    @staticmethod
    def stringToInt(number):
        try:
            number = int(number)
        except:
            return number
        return number

    @staticmethod
    def isNone(number):
        if number == None:
            Exit(Exit.EXIT_VALUE)

    @staticmethod
    def setNone(variable, type):
        if variable.value == None:
            variable.value = 0
            variable.type = type
        return variable

    @staticmethod
    def getIntValue(frame, instruction_argument, readFlag=None):
        number = None
        if instruction_argument != None and frame.isVar(instruction_argument) and readFlag == None:
            number = frame.getValueFromVar(instruction_argument)
            if type(number) != int:
                Exit(Exit.EXIT_TYPE)
        elif instruction_argument != None and re.match(r'^(\+|\-){0,1}0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*$', instruction_argument):
            number = Arithmetic.hexToDec(instruction_argument)
        elif instruction_argument != None and re.match(r'^(\+|\-){0,1}0[oO]?[0-7]+(_[0-7]+)*$', instruction_argument):
            number = Arithmetic.octaToDec(instruction_argument)
        elif instruction_argument != None and re.match(r'^(\+|\-){0,1}(([1-9][0-9]*(_[0-9]+)*)|0)$', instruction_argument):
            number = Arithmetic.stringToInt(instruction_argument)
        else:
            if readFlag == True:
                return None
            Exit(Exit.EXIT_XML_STRUCTURE)
        return number


class Relational:
    @staticmethod
    def base(instr, frame, operation):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                arg2value = None
                arg3value = None
                arg2var = None
                arg3var = None
                # BAD RETURN CODE
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                if frame.isVar(instr.arg3):
                    arg3var = frame.getVar(instr.arg3)
                    # getvalue nil
                if (instr.args[1]["type"] == "nil" or instr.args[2]["type"] == "nil") and operation != "eq" or (arg2var != None and arg2var.type == "nil" and arg3var != None and arg3var.type == "nil"  and operation != "eq"):
                    Exit(Exit.EXIT_TYPE) 
                elif instr.args[1]["type"] == "nil" and instr.args[2]["type"] == "nil" and operation == "eq" or (arg2var != None and arg2var.type == "nil" and arg3var != None and arg3var.type == "nil"  and operation == "eq"):
                    variable.type = "bool"
                    variable.value = "true"
                    break
                elif instr.args[1]["type"] == "nil" and operation == "eq" or (arg2var != None and arg2var.type == "nil" and operation == "eq"):
                    variable.type = "bool"
                    variable.value = "false"
                    break
                elif instr.args[2]["type"] == "nil" and operation == "eq" or (arg3var != None and arg3var.type == "nil" and operation == "eq"):
                    variable.type = "bool"
                    variable.value = "false"
                    break   
                    
                if (instr.args[1]["type"] == instr.args[2]["type"] and instr.args[1]["type"] != "var"):
                    match instr.args[1]["type"]:
                        case "int":
                            arg2value = Arithmetic.getIntValue(
                                frame, instr.arg2)
                            arg3value = Arithmetic.getIntValue(
                                frame, instr.arg3)
                        case "string":
                            arg2value = IO.handleString(instr.arg2)
                            arg3value = IO.handleString(instr.arg3)
                        case "bool":
                            arg2value = instr.arg2
                            arg3value = instr.arg3
                elif (arg2var != None and arg2var.type == instr.args[2]["type"]):
                    match arg2var.type:
                        case "int":
                            arg2value = arg2var.value
                            arg3value = Arithmetic.getIntValue(
                                frame, instr.arg3)
                        case "string":
                            arg2value = IO.handleString(arg2var.value)
                            arg3value = IO.handleString(instr.arg3)
                        case "bool":
                            arg2value = arg2var.value
                            arg3value = instr.arg3
                elif (arg3var != None and arg3var.type == instr.args[1]["type"]):
                    match arg3var.type:
                        case "int":
                            arg2value = Arithmetic.getIntValue(
                                frame, instr.arg2)
                            arg3value = arg3var.value
                        case "string":
                            arg2value = IO.handleString(instr.arg2)
                            arg3value = IO.handleString(arg3var.value)
                        case "bool":
                            arg2value = instr.arg2
                            arg3value = arg3var.value
                elif (arg2var != None and arg3var != None and arg2var.type == arg2var.type):
                    match arg2var.type:
                        case "int":
                            arg2value = arg2var.value
                            arg3value = arg3var.value
                        case "string":
                            arg2value = IO.handleString(arg2var.value)
                            arg3value = IO.handleString(arg3var.value)
                        case "bool":
                            arg2value = arg2var.value
                            arg3value = arg3var.value
                            
                else:
                    Exit(Exit.EXIT_TYPE)
                if arg2value in ["true","false"] and arg3value in ["true","false"]:
                    match operation:
                        case "gt":
                            if arg2value == "true" and arg3value == "false":
                                variable.value = "true"
                            else:
                                variable.value = "false"     
                        case "lt":
                            if arg2value == "false" and arg3value == "true":
                                variable.value = "true"
                            else:
                                variable.value = "false"
                        case "eq":
                            variable.value = arg2value == arg3value
                if arg2value != None and arg3value != None and type(arg2value) == int and type(arg3value) == int:
                    match operation:
                        case "gt":
                            variable.value = arg2value > arg3value 
                        case "lt":
                            variable.value = arg2value < arg3value
                        case "eq":
                            variable.value = arg2value == arg3value
                elif arg2value != None and arg3value != None and type(arg2value) == str and type(arg3value) == str:
                    match operation:
                        case "gt":
                            variable.value = arg2value > arg3value 
                        case "lt":
                            variable.value = arg2value < arg3value
                        case "eq":
                            variable.value = arg2value == arg3value
                
                else:
                    Exit(Exit.EXIT_TYPE)
                variable = Arithmetic.setNone(variable, "bool")
                variable.type = "bool"
                if variable.value == True:
                    variable.value = "true"
                elif variable.value == False:
                    variable.value = "false"
                frame.frame_now[frame.isDefined(
                    instr.arg1)].remove(variable)
                frame.frame_now[oldFrame].append(variable)
                

    @staticmethod
    def gt(instr, frame):
        Relational.base(instr, frame, "gt")

    @staticmethod
    def lt(instr, frame):
        Relational.base(instr, frame, "lt")

    @staticmethod
    def eq(instr, frame):
        Relational.base(instr, frame, "eq")


class Logical:

    @staticmethod
    def base(instr, frame, operation):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                arg2var = None
                arg3var = None
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                    if arg2var.type != "bool":
                        Exit(Exit.EXIT_TYPE)
                if frame.isVar(instr.arg3):
                    arg3var = frame.getVar(instr.arg3)
                    if arg3var.type != "bool":
                        Exit(Exit.EXIT_TYPE)
                if instr.args[1]["type"] in ["bool", "var"] and operation == "not":
                    if arg2var != None:
                        variable.value = Logical.notImpl(arg2var.value)
                    else:
                        variable.value = Logical.notImpl(instr.arg2)
                elif instr.args[1]["type"] in ["bool", "var"] and instr.args[2]["type"] in ["bool", "var"] and operation == "and":
                    if arg2var != None and arg3var != None:
                        variable.value = Logical.andImpl(
                            arg2var.value, arg3var.value)
                    elif arg2var == None and arg3var != None:
                        variable.value = Logical.andImpl(
                            instr.arg2, arg3var.value)
                    elif arg2var != None and arg3var == None:
                        variable.value = Logical.andImpl(
                            arg2var.value, instr.arg3)
                    else:
                        variable.value = Logical.andImpl(
                            instr.arg2, instr.arg3)
                elif instr.args[1]["type"] in ["bool", "var"] and instr.args[2]["type"] in ["bool", "var"] and operation == "or":
                    if arg2var != None and arg3var != None:
                        variable.value = Logical.orImpl(
                            arg2var.value, arg3var.value)
                    elif arg2var == None and arg3var != None:
                        variable.value = Logical.orImpl(
                            instr.arg2, arg3var.value)
                    elif arg2var != None and arg3var == None:
                        variable.value = Logical.orImpl(
                            arg2var.value, instr.arg3)
                    else:
                        variable.value = Logical.orImpl(instr.arg2, instr.arg3)
                else:
                    Exit(Exit.EXIT_TYPE)

                variable.type = "bool"
                frame.frame_now[frame.isDefined(
                    instr.arg1)].remove(variable)
                frame.frame_now[oldFrame].append(variable)

    @staticmethod
    def andI(instr, frame):
        Logical.base(instr, frame, "and")

    @staticmethod
    def orI(instr, frame):
        Logical.base(instr, frame, "or")

    @staticmethod
    def notI(instr, frame):
        Logical.base(instr, frame, "not")

    @staticmethod
    def notImpl(value):
        if value == "true":
            value = "false"
        else:
            value = "true"
        return value

    @staticmethod
    def andImpl(value1, value2):
        retValue = None
        if value1 == "true" and value2 == "true":
            retValue = "true"
        elif (value1 == "true" and value2 == "false") or (value1 == "false" and value2 == "true") or (value1 == "false" and value2 == "false"):
            retValue = "false"
        else:
            # error
            pass
        return retValue

    @staticmethod
    def orImpl(value1, value2):
        retValue = None
        if value1 == "true" and value2 == "true":
            retValue = "true"
        elif (value1 == "true" and value2 == "false") or (value1 == "false" and value2 == "true"):
            retValue = "true"
        elif (value1 == "false" and value2 == "false"):
            retValue = "false"
        else:
            # error
            pass
        return retValue


class String:
    @staticmethod
    def int2char(instr, frame):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                arg2var = None
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                    if arg2var.type != "int":
                        Exit(Exit.EXIT_TYPE)
                if instr.args[1]["type"] in ["var", "int"]:
                    if arg2var != None:
                        variable.value = arg2var.value
                    else:
                        variable.value = instr.arg2
                else:
                    Exit(Exit.EXIT_TYPE)

                try:
                    variable.value = chr(int(variable.value))
                except:
                    Exit(Exit.EXIT_STRING)

                variable.type = "string"
                frame.frame_now[frame.isDefined(
                    instr.arg1)].remove(variable)
                frame.frame_now[oldFrame].append(variable)

    @staticmethod
    def stri2int(instr, frame):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                arg2var = None
                arg3var = None
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                    if arg2var.type != "string":
                        Exit(Exit.EXIT_TYPE)
                if frame.isVar(instr.arg3):
                    arg3var = frame.getVar(instr.arg3)
                    if arg3var.type != "int":
                        Exit(Exit.EXIT_TYPE)
                if instr.args[1]["type"] in ["var", "string"] and instr.args[2]["type"] in ["var", "int"]:
                    if arg2var != None:
                        arg2value = arg2var.value
                    else:
                        arg2value = instr.arg2
                    arg2value = IO.handleString(arg2value)
                    arg3value = Arithmetic.getIntValue(frame, instr.arg3)
                    if (arg3value != None and arg2value != None) and not (0 <= arg3value < len(arg2value)):
                        Exit(Exit.EXIT_STRING)
                    if arg3value != None and arg2value != None:
                        variable.value = ord(arg2value[arg3value])
                        variable.type = "int"
                    frame.frame_now[frame.isDefined(
                        instr.arg1)].remove(variable)
                    frame.frame_now[oldFrame].append(variable)
                else:
                    Exit(Exit.EXIT_TYPE)

    @staticmethod
    def concat(instr, frame):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                arg2var = None
                arg3var = None
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                    if arg2var.type != "string":
                        Exit(Exit.EXIT_TYPE)
                if frame.isVar(instr.arg3):
                    arg3var = frame.getVar(instr.arg3)
                    if arg3var.type != "string":
                        Exit(Exit.EXIT_TYPE)
                if instr.args[1]["type"] in ["var", "string"] and instr.args[2]["type"] in ["var", "string"]:
                    if arg2var != None:
                        arg2value = IO.handleString(arg2var.value)
                    else:
                        arg2value = IO.handleString(instr.arg2)
                    if arg3var != None:
                        arg3value = IO.handleString(arg3var.value)
                    else:
                        arg3value = IO.handleString(instr.arg3)

                    if arg2value == 'None':
                        arg2value = ""
                    if arg3value == 'None':
                        arg3value = ""
                    variable.value = arg2value + arg3value
                    variable.type = "string"
                    frame.frame_now[frame.isDefined(
                        instr.arg1)].remove(variable)
                    frame.frame_now[oldFrame].append(variable)
                else:
                    Exit(Exit.EXIT_TYPE)
                break

    @staticmethod
    def strlen(instr, frame):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                arg2var = None
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                    if arg2var.type != "string":
                        Exit(Exit.EXIT_TYPE)
                if instr.args[1]["type"] in ["var", "string"]:
                    if arg2var != None:
                        arg2value = IO.handleString(arg2var.value)
                    else:
                        arg2value = IO.handleString(instr.arg2)

                        if arg2value == 'None':
                            arg2value = ""
                        variable.value = len(arg2value)
                        variable.type = "int"
                        frame.frame_now[frame.isDefined(
                            instr.arg1)].remove(variable)
                        frame.frame_now[oldFrame].append(variable)
                else:
                    Exit(Exit.EXIT_TYPE)

    @staticmethod
    def getchar(instr, frame):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                arg2var = None
                arg3var = None
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                    if arg2var.type != "string":
                        Exit(Exit.EXIT_TYPE)
                if frame.isVar(instr.arg3):
                    arg3var = frame.getVar(instr.arg3)
                    if arg3var.type != "int":
                        Exit(Exit.EXIT_TYPE)
                if instr.args[1]["type"] in ["var", "string"] and instr.args[2]["type"] in ["var", "int"]:
                    if arg2var != None:
                        arg2value = arg2var.value
                    else:
                        arg2value = instr.arg2
                    arg2value = IO.handleString(arg2value)
                    arg3value = Arithmetic.getIntValue(frame, instr.arg3)
                    if (arg3value != None and arg2value != None) and not (0 <= arg3value < len(arg2value)):
                        Exit(Exit.EXIT_STRING)
                    if arg3value != None and arg2value != None:
                        variable.value = arg2value[arg3value]
                        variable.type = "string"
                    frame.frame_now[frame.isDefined(
                        instr.arg1)].remove(variable)
                    frame.frame_now[oldFrame].append(variable)
                else:
                    Exit(Exit.EXIT_TYPE)

    @staticmethod
    def setchar(instr, frame):
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                if variable.type == None or variable.value == None:
                    Exit(Exit.EXIT_VALUE)
                if variable.type != "string":
                    Exit(Exit.EXIT_TYPE)
                oldFrame = frame.isDefined(instr.arg1)
                arg2var = None
                arg3var = None
                if frame.isVar(instr.arg2):
                    arg2var = frame.getVar(instr.arg2)
                    if arg2var.type != "int":
                        Exit(Exit.EXIT_TYPE)
                if frame.isVar(instr.arg3):
                    arg3var = frame.getVar(instr.arg3)
                    if arg3var.type != "string":
                        Exit(Exit.EXIT_TYPE)
                if instr.args[1]["type"] in ["var", "int"] and instr.args[2]["type"] in ["var", "string"]:

                    if arg3var != None:
                        arg3value = arg3var.value
                    else:
                        arg3value = instr.arg3
                    arg2value = Arithmetic.getIntValue(frame, instr.arg2)
                    arg3value = IO.handleString(arg3value)
                    if (arg3value != None and arg2value != None) and not (0 <= arg2value < len(variable.value)):
                        Exit(Exit.EXIT_STRING)
                    if arg3value != 'None' and arg2value != None:
                        variable.value = variable.value[:arg2value] + \
                            arg3value[0] + variable.value[arg2value+1:]
                        variable.type = "string"
                    else:
                        Exit(Exit.EXIT_STRING)
                    frame.frame_now[frame.isDefined(
                        instr.arg1)].remove(variable)
                    frame.frame_now[oldFrame].append(variable)
                else:
                    Exit(Exit.EXIT_TYPE)


class programFlow():

    @staticmethod 
    def base(instr, frame, interpret):
        label = None
        jumpPosition = None
        if instr.args[0]["type"] != "label":
            Exit(Exit.EXIT_TYPE)
        if not interpret.labels:
            Exit(Exit.EXIT_SEMANTIC)
        for labelToCheck in interpret.labels:
            if labelToCheck == instr.arg1:
                label = labelToCheck
                break
        if label == None:
            Exit(Exit.EXIT_SEMANTIC)
        for instruction in interpret.Instruction_list:
            if instruction.arg1 == label and instruction.opcode == "LABEL":
                jumpPosition = instruction.order
        if jumpPosition != None:
            return jumpPosition
        
        
    @staticmethod
    def jump(instr, frame, interpret):
        return programFlow.base(instr, frame, interpret)
        

    @staticmethod
    def jumpifeq(instr, frame, interpret):
        jumpPosition = programFlow.base(instr, frame, interpret)
        if instr.args[1]["type"] in ["int","var","nil"] and instr.args[2]["type"] in ["int","var","nil"]:
            arg1val = None
            arg1type = None
            arg2val = None
            arg2type = None
            
            if frame.isVar(instr.arg2):
                arg1type = frame.getVar(instr.arg2).type
                if arg1type != "nil": 
                    arg1val = Arithmetic.getIntValue(frame,instr.arg2)
                else:
                    arg1val = "nil"
            else:
                arg1type = instr.args[1]["type"]
                if arg1type != "nil":   
                    arg1val = Arithmetic.getIntValue(frame,instr.arg2)
                else:
                    arg1val = "nil"
      
            if frame.isVar(instr.arg3):
                arg2type = frame.getVar(instr.arg3).type
                if arg2type != "nil": 
                    arg2val = Arithmetic.getIntValue(frame,instr.arg3)
                else:
                    arg2val = "nil"
            else:
                arg2type = instr.args[2]["type"]
                if arg2type != "nil":   
                    arg2val = Arithmetic.getIntValue(frame,instr.arg3)
                else:
                    arg2val = "nil"
                    
            if arg1val == arg2val:
                return jumpPosition
            else:
                return False
        elif instr.args[1]["type"] in ["string","var","nil"] and instr.args[2]["type"] in ["string","var","nil"]:
            arg1val = None
            arg1type = None
            arg2val = None
            arg2type = None
            if frame.isVar(instr.arg2):
                arg1val = IO.handleString(frame.getVar(instr.arg2).value)
                arg1type = frame.getVar(instr.arg2).type
            else:
                arg1val = IO.handleString(instr.arg2)
                arg1type = instr.args[1]["type"]
            if frame.isVar(instr.arg3):
                arg2val = IO.handleString(frame.getVar(instr.arg3).value)
                arg2type = frame.getVar(instr.arg3).type
            else:
                arg2val = IO.handleString(instr.arg3)
                arg2type = instr.args[2]["type"]
                
            if arg1val == arg2val:
                return jumpPosition
            else:
                return False
        elif instr.args[1]["type"] in ["bool","var", "nil"] and instr.args[2]["type"] in ["bool","var", "nil"]:
            arg1val = None
            arg1type = None
            arg2val = None
            arg2type = None
            if frame.isVar(instr.arg2):
                arg1val = frame.getVar(instr.arg2).value
                arg1type = frame.getVar(instr.arg2).type
            else:
                arg1val = instr.arg2
                arg1type = instr.args[1]["type"]
            if frame.isVar(instr.arg3):
                arg2val = frame.getVar(instr.arg3).value
                arg2type = frame.getVar(instr.arg3).type
            else:
                arg2val = instr.arg3
                arg2type = instr.args[2]["type"]
                
            if arg1val == arg2val:
                return jumpPosition
            else:
                return False
        else:
            Exit(Exit.EXIT_TYPE)
        
        

    @staticmethod
    def jumpifneq(instr, frame,interpret):
        jumpPosition = programFlow.base(instr, frame, interpret)
        if instr.args[1]["type"] in ["int","var","nil"] and instr.args[2]["type"] in ["int","var","nil"]:
            arg1val = None
            arg1type = None
            arg2val = None
            arg2type = None
            
            if frame.isVar(instr.arg2):
                arg1type = frame.getVar(instr.arg2).type
                if arg1type != "nil": 
                    arg1val = Arithmetic.getIntValue(frame,instr.arg2)
                else:
                    arg1val = "nil"
            else:
                arg1type = instr.args[1]["type"]
                if arg1type != "nil":   
                    arg1val = Arithmetic.getIntValue(frame,instr.arg2)
                else:
                    arg1val = "nil"
      
            if frame.isVar(instr.arg3):
                arg2type = frame.getVar(instr.arg3).type
                if arg2type != "nil": 
                    arg2val = Arithmetic.getIntValue(frame,instr.arg3)
                else:
                    arg2val = "nil"
            else:
                arg2type = instr.args[2]["type"]
                if arg2type != "nil":   
                    arg2val = Arithmetic.getIntValue(frame,instr.arg3)
                else:
                    arg2val = "nil"
                    
            if arg1val != arg2val:
                return jumpPosition
            else:
                return False
        elif instr.args[1]["type"] in ["string","var","nil"] and instr.args[2]["type"] in ["string","var","nil"]:
            arg1val = None
            arg1type = None
            arg2val = None
            arg2type = None
            if frame.isVar(instr.arg2):
                arg1val = IO.handleString(frame.getVar(instr.arg2).value)
                arg1type = frame.getVar(instr.arg2).type
            else:
                arg1val = IO.handleString(instr.arg2)
                arg1type = instr.args[1]["type"]
            if frame.isVar(instr.arg3):
                arg2val = IO.handleString(frame.getVar(instr.arg3).value)
                arg2type = frame.getVar(instr.arg3).type
            else:
                arg2val = IO.handleString(instr.arg3)
                arg2type = instr.args[2]["type"]
                
            if arg1val != arg2val:
                return jumpPosition
            else:
                return False
        elif instr.args[1]["type"] in ["bool","var", "nil"] and instr.args[2]["type"] in ["bool","var", "nil"]:
            arg1val = None
            arg1type = None
            arg2val = None
            arg2type = None
            if frame.isVar(instr.arg2):
                arg1val = frame.getVar(instr.arg2).value
                arg1type = frame.getVar(instr.arg2).type
            else:
                arg1val = instr.arg2
                arg1type = instr.args[1]["type"]
            if frame.isVar(instr.arg3):
                arg2val = frame.getVar(instr.arg3).value
                arg2type = frame.getVar(instr.arg3).type
            else:
                arg2val = instr.arg3
                arg2type = instr.args[2]["type"]
                
            if arg1val != arg2val:
                return jumpPosition
            else:
                return False
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def call(instr, frame):
        pass

    @staticmethod
    def label(instr, frame):
        pass


class IO():

    @staticmethod
    # overit spracovanie argumentov - iba jeden input alebo source mozu byt prazdny
    def read(instr, frame, xml):
        frame.retFrame(instr)
        for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
            if variable.name == instr.arg1:
                oldFrame = frame.isDefined(instr.arg1)
                if instr.arg2 == "int":
                    if xml.args.input == "":
                        try:
                            user_input = input()
                        except:
                            user_input = None
                        variable.value = Arithmetic.getIntValue(
                            frame, user_input, readFlag=True)
                    else:
                        try:
                            user_input = xml.args.input.readline().replace('\n', "")
                        except:
                            user_input = None
                        variable.value = Arithmetic.getIntValue(
                            frame, user_input, readFlag=True)
                    variable.type = "int"
                    if variable.value == None:
                        variable.type = "nil"
                        variable.value = "nil"
                elif instr.arg2 == "bool":
                    if xml.args.input == "":
                        try:
                            user_input = input()
                        except:
                            user_input = None
                    else:
                        try:
                            user_input = xml.args.input.readline().replace('\n', "")
                        except:
                            user_input = None
                    variable.type = "bool"
                    if user_input == None:
                        variable.type = "nil"
                        variable.value = "nil"
                    elif user_input.upper() == "TRUE":
                        variable.value = "true"
                    else:
                        variable.value = "false"
                elif instr.arg2 == "string":
                    if xml.args.input == "":
                        try:
                            user_input = input()
                        except:
                            user_input = None
                    else:
                        try:
                            user_input = xml.args.input.readline().replace('\n', "")
                        except:
                            user_input = None

                    if user_input != None:
                        variable.value = IO.handleString(user_input)
                        variable.type = "string"
                    else:
                        variable.type = "nil"
                        variable.value = "nil"
                else:
                    Exit(Exit.EXIT_XML_STRUCTURE)
                frame.frame_now[frame.isDefined(instr.arg1)].remove(variable)
                frame.frame_now[oldFrame].append(variable)
                break

    @staticmethod
    def writeI(instr, frame, output_stream):
        if instr.args[0]["type"] == "bool":
            print(instr.arg1, end='', file=output_stream)
        elif instr.args[0]["type"] == "nil":
            print("", end='', file=output_stream)
        elif instr.args[0]["type"] == "var":
            if frame.isVar(instr.arg1):
                for variable in frame.frame_now[frame.isDefined(instr.arg1)]:
                    if variable.name == instr.arg1:
                        if variable.value != None and variable.type != "nil":
                            if variable.type == "string":
                                print(IO.handleString(variable.value),
                                      end='', file=output_stream)
                            else:
                                print(variable.value, end='',
                                      file=output_stream)  # zatial takto
                        elif variable.value != None and variable.type == "nil":
                            print("", end='', file=output_stream)
                        else:
                            Exit(Exit.EXIT_VALUE)
        elif instr.args[0]["type"] == "string":
            print(IO.handleString(instr.arg1), end='', file=output_stream)
        else:
            if instr.arg1 != None:
                print(instr.arg1, end='', file=output_stream)
            else:
                Exit(Exit.EXIT_VALUE)

    @staticmethod
    def exit(instr, frame):
        if instr.args[0]["type"] in ["var", "int"]:
            value = Arithmetic.getIntValue(frame, instr.arg1)
            if value != None:
                if 0 <= value <= 49:
                    Exit(value)
                else:
                    Exit(Exit.EXIT_OPERAND)
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def dprint(instr, frame):
        IO.writeI(instr, frame, output_stream=sys.stderr)

    @staticmethod
    def breakI(instr, frame):
        print(
            f"\nOpcode: {instr.opcode}\nOrder: {instr.order}\nObsah rámcov:", file=sys.stderr)
        if frame.frame_now["GF"]:
            print("Global frame:", file=sys.stderr)
            frame.print("GF")
        elif frame.frame_now["LF"]:
            print("Local frame:", file=sys.stderr)
            frame.print("LF")
        elif frame.frame_now["TF"]:
            print("Temporary frame:", file=sys.stderr)
            frame.print("TF")

    @staticmethod
    def handleString(value):
        try:
            # value = value.replace('\\032', ' ')
            value = re.sub(r'&lt;', '<', value)
            value = re.sub(r'&gt;', '>', value)
            value = re.sub(r'&amp;', '&', value)
            value = re.sub(r'&quot;', '"', value)
            value = re.sub(r'&apos;', '\'', value)
            while re.search(r'\\\d{3}', value):
                sub = re.search(r'\\\d{3}', value)
                if sub != None:
                    value = re.sub(r'\\\d{3}', chr(
                        int(sub[0][1:])), value, count=1)
                else:
                    raise SystemExit
        except:
            return value
        return value


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
            if instr.args[0]["type"] == "int":
                instr.arg1 = Arithmetic.getIntValue(frame,instr.arg1)
            elif instr.args[0]["type"] == "string":
                instr.arg1 = IO.handleString(instr.arg1)
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

    def print(self, toPrint):
        for variable in self.frame_now[toPrint]:
            print(variable.name, file=sys.stderr)

    def move(self, instr):
        self.retFrame(instr)
        for variable in self.frame_now[str(self.isDefined(instr.arg1))]:
            if variable.name == instr.arg1:
                oldFrame = self.isDefined(instr.arg1)
                if instr.args[1]["type"] == "int" or instr.args[1]["type"] == "bool" or instr.args[1]["type"] == "string" or instr.args[1]["type"] == "nil":
                    match instr.args[1]["type"]:
                        case "int":
                            variable.value = Arithmetic.getIntValue(
                                self, instr.arg2)
                        case _:
                            variable.value = instr.arg2
                    variable.type = instr.args[1]["type"]
                elif instr.args[1]["type"] == "var":
                    var = self.getVar(instr.arg2)
                    if var != None:
                        variable.value = var.value
                        variable.type = var.type
                else:
                    pass  # nejake osetrenie

                self.frame_now[str(self.isDefined(
                    instr.arg1))].remove(variable)
                self.frame_now[str(oldFrame)].append(variable)

    def type(self, instr):
        for variable in self.frame_now[str(self.isDefined(instr.arg1))]:
            if variable.name == instr.arg1:
                oldFrame = self.isDefined(instr.arg1)
                if instr.args[1]["type"] == "var":
                    var = self.getVar(instr.arg2, type_flag=True)
                    if var != None:
                        if var.value == None:
                            variable.value = ""
                        else:
                            variable.value = var.type
                elif instr.args[1]["type"] in ["int", "bool", "string", "nil"]:
                    variable.value = instr.args[1]["type"]
                variable.type = "string"
                self.frame_now[str(self.isDefined(
                    instr.arg1))].remove(variable)
                self.frame_now[str(oldFrame)].append(variable)

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
            self.frame_now["LF"] = []
        for variable in self.frame_now["TF"]:
            variable.name = re.sub("^TF", "LF", variable.name)
            variable.frame = "LF"
            self.frame_now["LF"].append(variable)
        self.frame_now["TF"].clear()
        self.temp_frame = False
        self.local_frame = True

    def pop(self):
        self.isFrame("LF")
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
        if not self.isVar(arg):
            return False
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

    def getValueFromVar(self, arg):
        for variable in self.frame_now[str(self.isDefined(arg))]:
            if variable.name == arg:
                if variable.value == None:
                    Exit(Exit.EXIT_VALUE)
                return variable.value

    def getVar(self, arg, type_flag=None):
        for variable in self.frame_now[str(self.isDefined(arg))]:
            if variable.name == arg:
                if variable.value == None and type_flag == None:
                    Exit(Exit.EXIT_VALUE)
                return variable
        return None


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
