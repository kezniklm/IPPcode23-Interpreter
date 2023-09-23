##
# @file Exit.py
#
# @brief Interpret XML reprezentácie jazyka IPPcode23
#
# @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>

import sys


class Exit:
    """Trieda slúžiaca na ukončenie programu podľa zadaného exit kódu"""

    # Exit code constants
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

    def __init__(self, error_type, help_flag=None):
        err_message = ""

        match error_type:
            case self.EXIT_SUCCESS:
                if help_flag:
                    help_message = (
                        "Názov:\ninterpret.py - interpret jazyka IPPcode23 v XML reprezentácii kódu\n\n"
                        "Použitie:\n    python3 interpret.py [MOŽNOSTI]\nPopis:\n    interpret.py vykoná "
                        "interpretáciu XML"
                        "reprezentácie kódu zo zdrojovového súboru\n\nMOŽNOSTI\n    --help\n        Vypíše pomocnú "
                        "hlášku pre skript interpet.py\n    --source=file\n        Vstupný súbor s XML reprezentaciou "
                        "zdrojového kódu\n    --input=file\n        Súbor so vstupmi pre samotú interpretáciu "
                        "zadaného zdrojového kódu"
                    )
                    print(help_message, file=sys.stdout)
                sys.exit(error_type)
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
                err_message = "CHYBA:\nChýbajúca hodnota napr. v premennej, zasobniku volani alebo na zasobniku"
            case self.EXIT_OPERAND:
                err_message = "CHYBA:\nChybná hodnota operandu"
            case self.EXIT_STRING:
                err_message = "CHYBA:\nChybná práca s reťazcom"

        print(err_message, file=sys.stderr)
        sys.exit(error_type)
