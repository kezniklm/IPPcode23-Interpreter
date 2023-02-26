""" 
@file interpret.py

@brief Interpret XML reprezentácie jazyka IPPcode23

@author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>    
"""
import argparse as ap
import xml.etree.ElementTree as ET
import sys
import re

SCRIPT_NAME = 0
MAX_ARGUMENTS = 2
    
EXIT_SUCCESS = 0
EXIT_PARAM = 10

class Arguments:
    """Trieda pre spracovanie vstupných argumentov skriptu"""
    def __init__(self):
        self.source = ""
        self.args = sys.argv[SCRIPT_NAME + 1:]
        if len(self.args) > MAX_ARGUMENTS:
            Errors(EXIT_PARAM)
        for argument in self.args:
            if argument == "--help" and len(self.args) == 1:
                print ("help string", file = sys.stdout)
                sys.exit(EXIT_SUCCESS)
            elif argument == "--help" and len(self.args) != 1:
                Errors(EXIT_PARAM)
                


class Errors:
    """Trieda pre spracovanie chybových hlášiek"""
    def __init__(self, type):
        self.err_message = ""
        match type:
            case EXIT_PARAM:
                self.err_message = "Zadaná chybná kombinácia alebo chybný počet argumentov skriptu interpret.py\n"

        print (self.err_message, file = sys.stdout)
        sys.exit(type)
            

if __name__ == '__main__':
    Arguments()
    #sourceFile, inputFile = arguments()
    #programmeRunner(sourceFile, inputFile)    
    