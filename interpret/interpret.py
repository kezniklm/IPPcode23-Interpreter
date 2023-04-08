##
# @file interpret.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

import xml.etree.ElementTree as ET
import sys
import re


class Arguments:
    """! Trieda pre spracovanie vstupných argumentov skriptu"""

    SCRIPT_NAME = 0
    MAX_ARGUMENTS = 2

    def __init__(self):
        self.source = ""
        self.input = ""
        args = sys.argv[Arguments.SCRIPT_NAME + 1:]
        if len(args) > Arguments.MAX_ARGUMENTS:
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
                    try:
                        self.input = open(file, "r")
                    except:
                        Exit(Exit.EXIT_INPUT)
                case _:
                    Exit(Exit.EXIT_PARAM)
        if self.source == "" and self.input == "":
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
                        "Názov:\ninterpret.py - interpret jazyka IPPcode23 v XML reprezentácii kódu\n\nPoužitie:\n    python3 interpret.py [MOŽNOSTI]\nPopis:\n    interpret.py vykoná interpretáciu XML reprezentácie kódu zo zdrojovového súboru\n\nMOŽNOSTI\n    --help\n        Vypíše pomocnú hlášku pre skript interpet.py\n    --source=file\n        Vstupný súbor s XML reprezentaciou zdrojového kódu\n    --input=file\n        Súbor so vstupmi pre samotú interpretáciu zadaného zdrojového kódu", file=sys.stdout)
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


class XML():
    """Spracuje, skontroluje a rozparsuje zadaný vstupný súbor s XML reprezentáciou kódu"""

    def __init__(self, args):
        """Pomocou knižnice xml.etree.ElementTree spracuje vstupný XML súbor

        Args:
            args (_type_): Spracované argumenty
        """

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
        """Skontroluje spracovanú XML reprezentáciu kódu"""

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
                if 'opcode' in child.attrib:
                    self.arg_count(child.attrib['opcode'].upper())
                else:
                    Exit(Exit.EXIT_XML_STRUCTURE)
                if "order" not in child.attrib or not re.match(r'^[1-9][0-9]*$', child.attrib['order']) or "opcode" not in child.attrib:
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

    def arg_count(self, instruction):
        """Vráti a skontroluje počet argumentov zadanej inštrukcie

        Args:
            instruction (_type_): Inštrukcia, ktorej počet má byť skontrolovaný

        Returns:
            _type_: Počet argumentov
        """
        arg_min = -1
        match instruction.upper():
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

                # Kontrola počtu argumentov
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
    """Trieda obsahujúca všetky potrebné informácie o každej inštrukcii a volanie implementácie každej jednotlivej inštrukcie"""

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

    def orI(self, frame):
        Logical.orI(self, frame)

    def notI(self, frame):
        Logical.notI(self, frame)

    def int2char(self, frame):
        String.int2char(self, frame)

    def stri2int(self, frame):
        String.stri2int(self, frame)

    def read(self, frame, xml):
        IO.read(self, frame, xml)

    def writeI(self, frame):
        IO.writeI(self, frame, output_stream=sys.stdout)

    def concat(self, frame):
        String.concat(self, frame)

    def strlen(self, frame):
        String.strlen(self, frame)

    def getchar(self, frame):
        String.getchar(self, frame)

    def setchar(self, frame):
        String.setchar(self, frame)

    def type(self, frame):
        frame.type(self)

    def jump(self, interpret):
        return ProgramFlow.jump(self, interpret)

    def jumpifeq(self, frame, interpret):
        return ProgramFlow.jumpifeq(self, frame, interpret)

    def jumpifneq(self, frame, interpret):
        return ProgramFlow.jumpifneq(self, frame, interpret)

    def exit(self, frame):
        IO.exit(self, frame)

    def dprint(self, frame):
        IO.dprint(self, frame)

    def breakI(self, frame):
        IO.breakI(self, frame)


class Interpret:
    """Trieda obsahujúca XML reprezentáciu kódu, list inštrukcií, jednotlivé rámce, zásobníky, návestia a zásobník volaní """

    def __init__(self, xml):
        self.xml = xml
        self.Instruction_list = xml.instruction_list
        self.frame = Frame()
        self.stack = Stack()
        self.labels = []
        self.callStack = []

    def handleInstructions(self):
        """Vykoná jednotlivé inštrukcie v poradí určenom pomocou order"""
        program_counter = 0
        while (program_counter < len(self.Instruction_list)):
            instruction = self.Instruction_list[program_counter]
            match instruction.opcode.upper():
                case "CREATEFRAME":
                    instruction.createFrame(self.frame)
                case "PUSHFRAME":
                    instruction.pushFrame(self.frame)
                case "POPFRAME":
                    instruction.popFrame(self.frame)
                case "RETURN":
                    if self.callStack:
                        program_counter = self.callStack.pop()
                    else:
                        Exit(Exit.EXIT_VALUE)
                case "BREAK":
                    instruction.breakI(self.frame)
                case "DEFVAR":
                    instruction.defVar(self.frame)
                case "POPS":
                    instruction.pops(self.frame, self.stack)
                case "CALL":
                    self.callStack.append(program_counter)
                    retValue = instruction.jump(self)
                    if retValue < len(self.Instruction_list):
                        program_counter = retValue
                    else:
                        break
                case "LABEL":
                    pass
                case "JUMP":
                    retValue = instruction.jump(self)
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
                    retValue = instruction.jumpifeq(self.frame, self)
                    if retValue != False and retValue < len(self.Instruction_list):
                        program_counter = retValue

                case "JUMPIFNEQ":
                    retValue = instruction.jumpifneq(self.frame, self)
                    if retValue != False and retValue < len(self.Instruction_list):
                        program_counter = retValue
                case _:
                    Exit(Exit.EXIT_XML_STRUCTURE)
            program_counter += 1

    def handleLabels(self):
        """Spracuje jednotlivé návestia ešte pred vykonaním jednotlivých inštrukcií"""
        for instruction in self.Instruction_list:
            if instruction.opcode.upper() == "LABEL":
                if instruction.arg1 not in self.labels:
                    self.labels.append(instruction.arg1)
                else:
                    Exit(Exit.EXIT_SEMANTIC)


class Arithmetic:
    """Trieda združujúca všetky aritmetické operácie"""

    @staticmethod
    def base(instr, frame, operation):
        variable = frame.getVar(instr.arg1, none_check=False) 
         
        if frame.isVar(instr.arg2):
            arg2type = frame.getVar(instr.arg2).type
        else:
            arg2type = instr.args[1]["type"]
        if frame.isVar(instr.arg3):
            arg3type = frame.getVar(instr.arg3).type
        else:
            arg3type = instr.args[2]["type"]
        
        if arg2type == "int" and arg3type == "int":
            arg2val = Arithmetic.getIntValue(frame, instr.arg2)
            arg3val = Arithmetic.getIntValue(frame, instr.arg3)
            if arg2val != None and arg3val != None:
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
                variable = Arithmetic.setNone(variable, "int")
            variable.type = "int"
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
    def octaToDec(number):
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
    def stringToInt(number):
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
        """Prekonvertuje číslo v reťazci na decimálny integer

        Args:
            frame (_type_): Rámec
            instruction_argument (_type_): Číslo v reťazci
            readFlag (_type_, optional): V prípade inštrukcie READ nebude vykonávaná kontrola na správnosť formátu čísla

        Returns:
            _type_: Decimálny integer
        """
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
        """Podľa zadanej operácie vykoná relačnú operáciu na operandoch inštrukcie

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            operation (_type_): lt, gt alebo eq
        """
        variable = frame.getVar(instr.arg1, none_check=False) 
               
        if frame.isVar(instr.arg2):
            arg2val = frame.getVar(instr.arg2).value
            arg2type = frame.getVar(instr.arg2).type
        else:
            arg2val = instr.arg2
            arg2type = instr.args[1]["type"]
        if frame.isVar(instr.arg3):
            arg3val = frame.getVar(instr.arg3).value
            arg3type = frame.getVar(instr.arg3).type
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
                    arg2val = Arithmetic.getIntValue(frame, instr.arg2)
                    arg3val = Arithmetic.getIntValue(frame, instr.arg3)
                    if type(arg2val) == int and type(arg3val) == int:
                        match operation:
                            case "gt":
                                variable.value = arg2val > arg3val
                            case "lt":
                                variable.value = arg2val < arg3val
                            case "eq":
                                variable.value = arg2val == arg3val
                case "string":
                    arg2val = IO.handleString(arg2val)
                    arg3val = IO.handleString(arg3val)
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
        if variable.value == True:
            variable.value = "true"
        elif variable.value == False:
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
        variable = frame.getVar(instr.arg1, none_check=False)
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
        return retValue


class String:
    """Trieda združujúca všetky operácie s reťazcami"""
    @staticmethod
    def int2char(instr, frame):
        """Prevedie číselnú hodnotu druhého argumentu na znak a uloží ho do premennej

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.getVar(instr.arg1, none_check=False)
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

    @staticmethod
    def stri2int(instr, frame):
        """Uloží číselnú hodnotu znaku (druhý argument) na pozícii (tretí argument) do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.getVar(instr.arg1, none_check=False)
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
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def concat(instr, frame):
        """Spojí reťazec (druhý argument) s druhým reťazcom (tretí argument) a výsledok uloží do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.getVar(instr.arg1, none_check=False)
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
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def strlen(instr, frame):
        """Uloží dĺžku reťazca (druhý argument) do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.getVar(instr.arg1, none_check=False)
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
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def getchar(instr, frame):
        """Uloží reťazec (druhý argument) na pozícii (tretí argument) do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.getVar(instr.arg1, none_check=False)
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
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def setchar(instr, frame):
        """Zmodifikuje znak reťazca uloženého v premennej (prvý argument) na pozícii (druhý argument) na znak v reťazci (tretí argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        variable = frame.getVar(instr.arg1, none_check=False)
        arg2var = None
        arg3var = None
        if variable.type == None or variable.value == None:
            Exit(Exit.EXIT_VALUE)
        if variable.type != "string":
            Exit(Exit.EXIT_TYPE)
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
        else:
            Exit(Exit.EXIT_TYPE)


class ProgramFlow():
    """Trieda združujúca všetky operácie ovplyvňujuce tok programu"""
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
    def jumpifBase(instr, frame, interpret, operation):
        """Vykoná skok pri rovnosti (operácia ifeq) alebo nerovnosti (operácia ifneq) druhého a tretieho  argumentu

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            interpret (_type_): Interpret pre prístup k návestiam
            operation (_type_): Operácia ifeq alebo ifneq

        Returns:
            _type_: Pozícia na ktorom sa návestie nachádza
        """
        jumpPosition = ProgramFlow.jump(instr, interpret)
        if frame.isVar(instr.arg2):
            arg1type = frame.getVar(instr.arg2).type
            arg1val = frame.getVar(instr.arg2).value
        else:
            arg1type = instr.args[1]["type"]
            arg1val = instr.arg2

        if frame.isVar(instr.arg3):
            arg2type = frame.getVar(instr.arg3).type
            arg2val = frame.getVar(instr.arg3).value
        else:
            arg2type = instr.args[2]["type"]
            arg2val = instr.arg3
        if arg1type in ["int", "nil"] and arg2type in ["int", "nil"]:
            if arg1type != "nil":
                arg1val = Arithmetic.getIntValue(frame, instr.arg2)
            else:
                arg1val = "nil"

            if arg2type != "nil":
                arg2val = Arithmetic.getIntValue(frame, instr.arg3)
            else:
                arg2val = "nil"

            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jumpPosition
            else:
                return False
        elif arg1type in ["string", "nil"] and arg2type in ["string", "nil"]:
            arg1val = IO.handleString(arg1val)
            arg2val = IO.handleString(arg2val)
            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jumpPosition
            else:
                return False
        elif arg1type in ["bool", "nil"] and arg2type in ["bool",  "nil"]:
            if (arg1val == arg2val and operation == "ifeq") or (arg1val != arg2val and operation == "ifneq"):
                return jumpPosition
            else:
                return False
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def jumpifeq(instr, frame, interpret):
        return ProgramFlow.jumpifBase(instr, frame, interpret, "ifeq")

    @staticmethod
    def jumpifneq(instr, frame, interpret):
        return ProgramFlow.jumpifBase(instr, frame, interpret, "ifneq")


class IO():
    """Trieda združujúca všetky vstupnom-výstupné operácie"""
    @staticmethod
    def read(instr, frame, xml):
        """Načíta vstup  typu (druhý argument) zo štandardného vstupu alebo zo súboru pri zadanom argumentu --input=file a uloží výsledok do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            xml (_type_): XML
        """
        variable = frame.getVar(instr.arg1, none_check=False)
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
                
        if user_input == None:
            variable.type = "nil"
            variable.value = "nil"
        elif instr.arg2 == "int":
            if type(user_input) == int:
                variable.value = user_input
            else:
                variable.value = Arithmetic.getIntValue(frame, user_input, readFlag=True)
                variable.type = "int"
                if variable.value == None:
                    variable.type = "nil"
                    variable.value = "nil"
        elif instr.arg2 == "bool":
            variable.type = "bool"
            if user_input.upper() == "TRUE":
                variable.value = "true"
            else:
                variable.value = "false"
        elif instr.arg2 == "string":
            variable.value = IO.handleString(user_input)
            variable.type = "string"       
        else:
            Exit(Exit.EXIT_XML_STRUCTURE)
        

    @staticmethod
    def writeI(instr, frame, output_stream):
        """Vypíše na štandardný výstup alebo štandardný chybový výstup hodnotu prvého argumentu

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            output_stream (_type_): Štandardný výstup alebo štandardný chybový výstup
        """
        if frame.isVar(instr.arg1):
            arg1type = frame.getVar(instr.arg1).type
            arg1val = frame.getVar(instr.arg1).value
        else:
            arg1type = instr.args[0]["type"]
            arg1val = instr.arg1
        if arg1type == "bool":
            print(arg1val, end='', file=output_stream)
        elif arg1type == "nil":
            print("", end='', file=output_stream)
        elif arg1type == "string":
            print(IO.handleString(arg1val), end='', file=output_stream)
        elif arg1type == "int":
            if type(arg1val) == int:
                print(arg1val, end='', file=output_stream)
            else:
                print(Arithmetic.getIntValue(frame, arg1val),
                      end='', file=output_stream)
        else:
            Exit(Exit.EXIT_VALUE)

    @staticmethod
    def exit(instr, frame):
        """Ukončí vykonávanie programu s návratovým kódom podľa prvého argumentu

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
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
        """Vypíše na štandardný chybový výstup stav interpretu

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
        """
        print(
            f"\nOpcode: {instr.opcode}\nObsah rámcov:", file=sys.stderr)
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
        """Spracuje reťazec - vymení escape sekvencie a špeciálne xml znaky za ich znakovú reprezentáciu

        Args:
            value (_type_): Reťazec na spracovanie

        Returns:
            _type_: Spracovaný reťazec
        """
        try:
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
                    raise Exception
        except:
            return value
        return value


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
        if frame.isDefined(instr.arg1) == "TF" or frame.isDefined(instr.arg1) == "LF" or frame.isDefined(instr.arg1) == "GF":
            variable = frame.getVar(instr.arg1, none_check=False)
            if variable.value == None or variable.type == None:
                Exit(Exit.EXIT_VALUE)
            self.dataStack.append(variable)
            frame.frame_now[frame.isDefined(
                instr.arg1)].remove(variable)
        else:
            if instr.args[0]["type"] == "int":
                instr.arg1 = Arithmetic.getIntValue(frame, instr.arg1)
            elif instr.args[0]["type"] == "string":
                instr.arg1 = IO.handleString(instr.arg1)
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
        if frame.isDefined(instr.arg1) == "TF" or frame.isDefined(instr.arg1) == "LF" or frame.isDefined(instr.arg1) == "GF":
            temp = self.dataStack.pop()
            variable = frame.getVar(instr.arg1, none_check=False)
            index = frame.frame_now[frame.isDefined(
                instr.arg1)].index(variable)
            frame.frame_now[frame.isDefined(
                instr.arg1)][index].value = temp.value
            frame.frame_now[frame.isDefined(
                instr.arg1)][index].type = temp.type


class Frame:
    """Trieda združujúca operácie nad jednotlivými rámcami"""

    def __init__(self):
        self.frame_now = {"GF": [], "LF": [], "TF": []}
        self.frameStack = []
        self.local_frame = False
        self.temp_frame = False

    def print(self, toPrint):
        """Vypíše obsah rámca na štandardný chybový výstup

        Args:
            toPrint (_type_): Rámec, ktorý má byť vypísaný
        """
        for variable in self.frame_now[toPrint]:
            print(variable.name, file=sys.stderr)

    def move(self, instr):
        """Presunie hodnotu z druhého argumentu do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
        """
        variable = self.getVar(instr.arg1, none_check=False)
        if variable != None and (instr.args[1]["type"] == "int" or instr.args[1]["type"] == "bool" or instr.args[1]["type"] == "string" or instr.args[1]["type"] == "nil"):
            match instr.args[1]["type"]:
                case "int":
                    variable.value = Arithmetic.getIntValue(
                        self, instr.arg2)
                case _:
                    variable.value = IO.handleString(instr.arg2)
            variable.type = instr.args[1]["type"]
        elif variable != None and instr.args[1]["type"] == "var":
            var = self.getVar(instr.arg2)
            if var != None:
                variable.value = var.value
                variable.type = var.type

    def type(self, instr):
        """Vloží typ druhého argumentu do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
        """
        variable = self.getVar(instr.arg1, none_check=False)
        if variable != None and instr.args[1]["type"] == "var":
            var = self.getVar(instr.arg2, none_check=True)
            if var != None:
                if var.value == None:
                    variable.value = ""
                else:
                    variable.value = var.type
                variable.type = "string"
        elif variable != None and instr.args[1]["type"] in ["int", "bool", "string", "nil"]:
            variable.value = instr.args[1]["type"]
            variable.type = "string"

    def defVar(self, instr):
        """Definuje premennú v jej zadanom rámci

        Args:
            instr (_type_): Inštrukcia
        """
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
        """Vytvorí dočasný zásobník"""
        self.temp_frame = True
        self.frame_now["TF"].clear()

    def push(self):
        """Vloží dočasný rámec do zásobníka lokálnych rámcov"""
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
        """Vyberie lokálny rámec a vloží ho do dočasného rámca"""
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
        """Overí, či existuje zadaný rámec

        Args:
            frame (_type_): Rámec, ktorého existencia má byť skontrolovaná
        """
        if frame == "TF" and self.temp_frame == False:
            Exit(Exit.EXIT_FRAME)
        elif frame == "LF" and self.local_frame == False:
            Exit(Exit.EXIT_FRAME)

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

    def getValueFromVar(self, arg):
        variable = self.getVar(arg)
        if variable != None:
            return variable.value
        return None

    def getVar(self, arg, none_check=None):
        for variable in self.frame_now[str(self.isDefined(arg))]:
            if variable.name == arg:
                if variable.value == None and none_check == None:
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
    XML = XML(args)
    XML.check()
    XML.parse()
    XML.sort()
    Interpret = Interpret(XML)
    Interpret.handleLabels()
    Interpret.handleInstructions()


if __name__ == '__main__':
    Program()
    Exit(Exit.EXIT_SUCCESS)
