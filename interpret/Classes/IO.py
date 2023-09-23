##
# @file IO.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

import re
import sys

from Classes.Arithmetic import Arithmetic
from Classes.Exit import Exit


class IO:
    """Trieda združujúca všetky vstupnom-výstupné operácie"""

    @staticmethod
    def read(instr, frame, xml):
        """Načíta vstup typu (druhý argument) zo štandardného vstupu alebo zo súboru pri zadanom argumentu --input=file a uloží výsledok do premennej (prvý argument)

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            xml (_type_): XML
        """
        variable = frame.get_var(instr.arg1, none_check=False)
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

        if user_input is None:
            variable.type = "nil"
            variable.value = "nil"
        elif instr.arg2 == "int":
            if type(user_input) == int:
                variable.value = user_input
            else:
                variable.value = Arithmetic.get_int_value(
                    frame, user_input, read_flag=True)
                variable.type = "int"
                if variable.value is None:
                    variable.type = "nil"
                    variable.value = "nil"
        elif instr.arg2 == "bool":
            variable.type = "bool"
            if user_input.upper() == "TRUE":
                variable.value = "true"
            else:
                variable.value = "false"
        elif instr.arg2 == "string":
            variable.value = IO.handle_string(user_input)
            variable.type = "string"
        elif instr.arg2 == "float":
            variable.type = "float"
            variable.value = Arithmetic.get_float_from_string(
                frame, user_input.strip())
        else:
            Exit(Exit.EXIT_XML_STRUCTURE)

    @staticmethod
    def write(instr, frame, output_stream):
        """Vypíše na štandardný výstup alebo štandardný chybový výstup hodnotu prvého argumentu

        Args:
            instr (_type_): Inštrukcia
            frame (_type_): Rámec
            output_stream (_type_): Štandardný výstup alebo štandardný chybový výstup
        """
        if frame.is_var(instr.arg1):
            arg1type = frame.get_var(instr.arg1).type
            arg1val = frame.get_var(instr.arg1).value
        else:
            arg1type = instr.args[0]["type"]
            arg1val = instr.arg1
        if arg1type == "bool":
            print(arg1val, end='', file=output_stream)
        elif arg1type == "nil":
            print("", end='', file=output_stream)
        elif arg1type == "string":
            print(IO.handle_string(arg1val), end='', file=output_stream)
        elif arg1type == "int":
            if type(arg1val) == int:
                print(arg1val, end='', file=output_stream)
            else:
                print(Arithmetic.get_int_value(frame, arg1val),
                      end='', file=output_stream)
        elif arg1type == "float":
            arg1val = Arithmetic.get_float_from_string(frame, arg1val)
            print(Arithmetic.get_int_value(frame, arg1val),
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
            value = Arithmetic.get_int_value(frame, instr.arg1)
            if value is not None:
                if 0 <= value <= 49:
                    Exit(value)
                else:
                    Exit(Exit.EXIT_OPERAND)
        else:
            Exit(Exit.EXIT_TYPE)

    @staticmethod
    def dprint(instr, frame):
        IO.write(instr, frame, output_stream=sys.stderr)

    @staticmethod
    def break_i(instr, frame):
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
    def handle_string(value):
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
                if sub is not None:
                    value = re.sub(r'\\\d{3}', chr(
                        int(sub[0][1:])), value, count=1)
                else:
                    raise Exception
        except:
            return value
        return value
