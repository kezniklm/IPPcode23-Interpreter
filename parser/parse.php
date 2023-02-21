<?php
/************************
*
*   Projekt: IPPcode23
*   Autor: Matej Keznikl
*  
*************************/

    ini_set('display_errors', 'stderr');
    define("EXIT_SUCCESS",0);
    define("EXIT_PARAM",10);
    define("EXIT_HEADER",21);
    define("EXIT_OPCODE",22);
    define("EXIT_SYNTAX", 23);

    define("WITHOUT_ARG",0);
    define("FIRST_ARG",1);
    define("SECOND_ARG",2);
    define("THIRD_ARG",3);
    define("FOURTH_ARG",4);

    define("ZERO_ARGS",0);
    define("ONE_ARG",1);
    define("TWO_ARGS",2);
    define("THREE_ARGS",3);
    define("HELP_STRING","    Názov: 
        parse.php - lexikálny a syntaktický analyzátor jazyka IPPcode23

    Použitie: 
        php8.1 parse.php [MOŽNOSTI]

    Popis: 
        parse.php vykoná lexikálnu a syntaktickú analýzu na zdrojovom súbore 
        zapísanom v jazyku IPPcode23 a vygeneruje XML reprezentáciu kódu

    MOŽNOSTI
        --help 
            Vypíše pomocnú hlášku pre skript parse.php");

    function param_err():void
    {
        error_log("CHYBA: Je možné zadať maximálne jeden argument\n");
        exit(EXIT_PARAM); 
    }
    function head_err():void
    {
        error_log("CHYBA: Chýbajúca alebo chybná hlavička\n");
        exit(EXIT_HEADER);
    }
    function opcode_err():void
    {
        error_log("CHYBA: Zle zapísaný operačný kód v zdrojovom kóde zapísanom v IPPcode23\n"); 
        exit(EXIT_OPCODE);
    }

    function syntax_err(): void
    {
        error_log("CHYBA: Syntaktická chyba zdrojového kódu zapísaného v IPPcode23\n"); 
        exit(EXIT_SYNTAX);
    }

    //Overenie mena premennej podľa REGEX
    function var_check($token): void
    {
        if(!preg_match('/^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$/',$token))
        {
            syntax_err();
        }
        return;
    }

    //Overenie mena návestia podľa REGEX
    function label_check($token): void
    {
        if(!preg_match('/^(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)+$/',$token))
        {
            syntax_err(); 
        }
        return;
    }

    //Overenie symbolu podľa REGEX
    function symb_check($token): void
    {
        if(!(preg_match('/^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)+[0-9]*(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$/',$token) || preg_match('/^string@([^\s#\\\\]|\\\\\d{3})*$$/',$token) || preg_match('/^bool@(true|false)$/',$token) || preg_match('/^nil@nil$/',$token) || preg_match('/^int@(\+|-){0,1}[0-9]+$/',$token)))
        {
            syntax_err();
        }
        return;
    }

    //Overenie symbolu podľa REGEX
    function type_check($token): void
    {
        if(!preg_match('/^(int|string|bool)$/',$token))
        {
            syntax_err(); 
        }
        return;
    }

    function check_arg_number($stream,$arg_count):void
    {
        switch ($arg_count):
            case ZERO_ARGS:
                if(!empty($stream[FIRST_ARG]))
                { 
                    syntax_err();
                }
                break;
            case ONE_ARG:
                if(empty($stream[FIRST_ARG]) || !empty($stream[SECOND_ARG]))
                {
                    syntax_err();
                }
                break;
            case TWO_ARGS:
                if(empty($stream[FIRST_ARG]) || empty($stream[SECOND_ARG]) || !empty($stream[THIRD_ARG]))
                {
                    syntax_err();
                }
                break;
            case THREE_ARGS:
                if(empty($stream[FIRST_ARG]) || empty($stream[SECOND_ARG]) || empty($stream[THIRD_ARG]) || !empty($stream[FOURTH_ARG]))
                {
                    syntax_err();
                }
                break;
            endswitch;
    }

    //Vytvorenie povinnej hlavičky
    $xml = xmlwriter_open_memory();
    xmlwriter_set_indent($xml, true);
    $res = xmlwriter_set_indent_string($xml, '  ');
    xmlwriter_start_document($xml, '1.0', 'UTF-8');
    xmlwriter_start_element($xml, 'program');
    xmlwriter_start_attribute($xml, 'language');
    xmlwriter_text($xml, 'IPPcode23');
    xmlwriter_end_attribute($xml);

    //Počet inštrukcií
    $instruction = 1;

    function print_XML($stream,$arg_count,$inst_number,$type_1,$type_2,$type_3): void
    {
        global $xml;

        if ($type_1 === "symb")
        {
            if(preg_match('/^int@.*$/',$stream[FIRST_ARG]))
            {
                $data_1 =  preg_replace('/^int@/','',$stream[FIRST_ARG]);
                $type_1 = "int";
            }
            elseif(preg_match('/^string@.*$/',$stream[FIRST_ARG]))
            {
                $data_1 =  preg_replace('/^string@/','',$stream[FIRST_ARG]);
                $type_1 = "string";
            }
            elseif(preg_match('/^bool@.*$/',$stream[FIRST_ARG]))
            {
                $data_1 =  preg_replace('/^bool@/','',$stream[FIRST_ARG]);
                $type_1 = "bool";
            }
            elseif(preg_match('/^nil@.*$/',$stream[FIRST_ARG]))
            {
                $data_1 =  preg_replace('/^nil@/','',$stream[FIRST_ARG]);
                $type_1 = "nil";
            }
            else $type_1 = "var";
        }

        if($type_2 === "symb")
        {
            if(preg_match('/^int@.*$/',$stream[SECOND_ARG]))
            {
                $data_2 =  preg_replace('/^int@/','',$stream[SECOND_ARG]);
                $type_2 = "int";
            }
            elseif(preg_match('/^string@.*$/',$stream[SECOND_ARG]))
            {
                $data_2 =  preg_replace('/^string@/','',$stream[SECOND_ARG]);
                $type_2 = "string";
            }
            elseif(preg_match('/^bool@.*$/',$stream[SECOND_ARG]))
            {
                $data_2 =  preg_replace('/^bool@/','',$stream[SECOND_ARG]);
                $type_2 = "bool";
            }
            elseif(preg_match('/^nil@.*$/',$stream[SECOND_ARG]))
            {
                $data_2 =  preg_replace('/^nil@/','',$stream[SECOND_ARG]);
                $type_2 = "nil";
            }    
            else $type_2 = "var"; 
        }

        if($type_3 === "symb")
        {
            if(preg_match('/^int@.*$/',$stream[THIRD_ARG]))
            {
                $data_3 =  preg_replace('/^int@/','',$stream[THIRD_ARG]);
                $type_3 = "int";
            }
            elseif(preg_match('/^string@.*$/',$stream[THIRD_ARG]))
            {
                $data_3 =  preg_replace('/^string@/','',$stream[THIRD_ARG]);
                $type_3 = "string";
            }
            elseif(preg_match('/^bool@.*$/',$stream[THIRD_ARG]))
            {
                $data_3 =  preg_replace('/^bool@/','',$stream[THIRD_ARG]);
                $type_3 = "bool";
            }  
            elseif(preg_match('/^nil@.*$/',$stream[THIRD_ARG]))
            {
                $data_3 =  preg_replace('/^nil@/','',$stream[THIRD_ARG]);
                $type_3 = "nil";
            }  
            else $type_3 = "var";
        }

        switch ($arg_count)
        {
            case ZERO_ARGS:
                xmlwriter_start_element($xml, 'instruction');
                xmlwriter_start_attribute($xml,'order' );
                xmlwriter_text($xml, $inst_number);
                xmlwriter_end_attribute($xml);
                xmlwriter_start_attribute($xml,"opcode");
                xmlwriter_text($xml,strtoupper($stream[WITHOUT_ARG]));
                xmlwriter_end_attribute($xml);
                xmlwriter_end_element($xml);
                break;
            case ONE_ARG:
                xmlwriter_start_element($xml, 'instruction');
                xmlwriter_start_attribute($xml,'order' );
                xmlwriter_text($xml, $inst_number);
                xmlwriter_end_attribute($xml);
                xmlwriter_start_attribute($xml,"opcode");
                xmlwriter_text($xml,strtoupper($stream[WITHOUT_ARG]));
                xmlwriter_end_attribute($xml);

                xmlwriter_start_element($xml, 'arg1');
                xmlwriter_start_attribute($xml,'type');
                xmlwriter_text($xml, $type_1);
                xmlwriter_end_attribute($xml);
                if($type_1 === "int" || $type_1 === "string" || $type_1 === "bool" || $type_1 === "nil")
                {
                    xmlwriter_text($xml,$data_1);
                }
                else xmlwriter_text($xml,$stream[FIRST_ARG]);
                
                xmlwriter_end_element($xml);
                xmlwriter_end_element($xml);
                break;
            case TWO_ARGS:
                xmlwriter_start_element($xml, 'instruction');
                xmlwriter_start_attribute($xml,'order' );
                xmlwriter_text($xml, $inst_number);
                xmlwriter_end_attribute($xml);
                xmlwriter_start_attribute($xml,"opcode");
                xmlwriter_text($xml,strtoupper($stream[WITHOUT_ARG]));
                xmlwriter_end_attribute($xml);

                xmlwriter_start_element($xml, 'arg1');
                xmlwriter_start_attribute($xml,'type');
                xmlwriter_text($xml, $type_1);
                xmlwriter_end_attribute($xml);
                xmlwriter_text($xml,$stream[FIRST_ARG]);
                xmlwriter_end_element($xml);

                xmlwriter_start_element($xml, 'arg2');
                xmlwriter_start_attribute($xml,'type');
                xmlwriter_text($xml, $type_2);
                xmlwriter_end_attribute($xml);
                if($type_2 === "int" || $type_2 === "string" || $type_2 === "bool" || $type_2 === "nil")
                {
                    xmlwriter_text($xml,$data_2);
                }
                else xmlwriter_text($xml,$stream[SECOND_ARG]);
                xmlwriter_end_element($xml);
                xmlwriter_end_element($xml);
                
                break;
            case THREE_ARGS:
                xmlwriter_start_element($xml, 'instruction');
                xmlwriter_start_attribute($xml,'order' );
                xmlwriter_text($xml, $inst_number);
                xmlwriter_end_attribute($xml);
                xmlwriter_start_attribute($xml,"opcode");
                xmlwriter_text($xml,strtoupper($stream[WITHOUT_ARG]));
                xmlwriter_end_attribute($xml);

                xmlwriter_start_element($xml, 'arg1');
                xmlwriter_start_attribute($xml,'type');
                xmlwriter_text($xml, $type_1);
                xmlwriter_end_attribute($xml);
                xmlwriter_text($xml,$stream[FIRST_ARG]);
                xmlwriter_end_element($xml);

                xmlwriter_start_element($xml, 'arg2');
                xmlwriter_start_attribute($xml,'type');
                xmlwriter_text($xml, $type_2);
                xmlwriter_end_attribute($xml);
                if($type_2 === "int" || $type_2 === "string" || $type_2 === "bool" || $type_2 === "nil")
                {
                    xmlwriter_text($xml,$data_2);
                }
                else xmlwriter_text($xml,$stream[SECOND_ARG]);
                xmlwriter_end_element($xml);

                xmlwriter_start_element($xml, 'arg3');
                xmlwriter_start_attribute($xml,'type');
                xmlwriter_text($xml, $type_3);
                xmlwriter_end_attribute($xml);
                if($type_3 === "int" || $type_3 === "string" || $type_3 === "bool" || $type_3 === "nil")
                {
                    xmlwriter_text($xml,$data_3);
                }
                else xmlwriter_text($xml,$stream[THIRD_ARG]);
                
                xmlwriter_end_element($xml);
                xmlwriter_end_element($xml);
                xmlwriter_end_element($xml);
                break;
        }
    }

    //Overenie argumentov
    if($argc == 2)
    {
        if($argv[1] == "--help")
        {
            echo(HELP_STRING . "\n");
            exit(EXIT_SUCCESS);
        }
        else
        {
            param_err();
        }
    }
    elseif ($argc > 2) 
    {
        param_err();
    }

    $header_flag = false;

    while($line = fgets(STDIN))
    {
        $max = 1024;
        $clean = explode(' ',trim($line,"\n"));

        //Odstránenie komentárov 
        $pos = 0;
        for($i = 0;$i < $max;$i++)
        {
            if(!empty($clean[$i]) && preg_match('/^#.*/',$clean[$i]))
            {
                if($i === 0)
                {
                    $pos++;
                }
                else $pos = $i;
                $clean[$i] = '';
            }
            if($pos !== 0 && !empty($clean[$i]))
            {
                $clean[$i] = '';
            }
        }
        $pos = 0;
        for($i = 0;$i < $max;$i++)
        {
            if(!empty($clean[$i]) && preg_match('/#/',$clean[$i]))
            {
                $clean[$i] = preg_filter('/#.*/','',$clean[$i]);
                $pos++;
                continue;
            }
            if($pos !== 0 && !empty($clean[$i]))
            { 
                $clean[$i] = '';
            }
        }

        //Odstránenie whitespacov
        $clean = preg_replace('/^\s*$/','',$clean);
        if(preg_match('/^\s*$/',$clean[0]))
        { 
            continue;  
        }

        //Preusporiadanie riadku
        $counter = 1;
        for($i = 1;$i < $max;$i++)
        {
            if(!empty($clean[$i]))
            {
                $clean[$counter++] = $clean[$i];
            }
        }
        
        //Kontrola hlavičky
        if($header_flag == false)
        {
            if ($clean[0] !== ".IPPcode23")
            {
                head_err();
            }
            else 
            {
                $header_flag = true;
                continue;
            }
        }
        
        switch (strtoupper($clean[0]))
        {
            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                check_arg_number($clean,ZERO_ARGS);
                print_XML($clean,ZERO_ARGS,$instruction++,NULL,NULL,NULL);
                break;
            case "DEFVAR":
            case "POPS":
                check_arg_number($clean,ONE_ARG);
                var_check($clean[FIRST_ARG]);
                print_XML($clean,ONE_ARG,$instruction++,"var",NULL,NULL);
                break;
            case "LABEL":
            case "CALL":
            case "JUMP":
                check_arg_number($clean,ONE_ARG);
                label_check($clean[FIRST_ARG]);
                print_XML($clean,ONE_ARG,$instruction++,"label",NULL,NULL);
                break;
            case "PUSHS":
            case "WRITE":
            case "EXIT":
            case "DPRINT":
                check_arg_number($clean,ONE_ARG);
                symb_check($clean[FIRST_ARG]);
                print_XML($clean,ONE_ARG,$instruction++,"symb",NULL,NULL); 
                break;
            case "MOVE":
            case "INT2CHAR":
            case "STRLEN":
            case "TYPE":
            case "NOT":
                check_arg_number($clean,TWO_ARGS);
                var_check($clean[FIRST_ARG]); 
                symb_check($clean[SECOND_ARG]);
                print_XML($clean,TWO_ARGS,$instruction++,"var","symb",NULL);
                break;
            case "READ":
                check_arg_number($clean,TWO_ARGS);
                var_check($clean[FIRST_ARG]);
                type_check($clean[SECOND_ARG]);
                print_XML($clean,TWO_ARGS,$instruction++,"var","type",NULL);
                break;
            case "ADD":
            case "SUB":
            case "MUL":
            case "IDIV":
            case "LT":
            case "GT":
            case "EQ":
            case "AND":
            case "OR":
            case "STRI2INT":
            case "CONCAT":
            case "GETCHAR":  
            case "SETCHAR":
                check_arg_number($clean,THREE_ARGS);
                var_check($clean[FIRST_ARG]);
                symb_check($clean[SECOND_ARG]);
                symb_check($clean[THIRD_ARG]);
                print_XML($clean,THREE_ARGS,$instruction++,"var","symb","symb");
                break;
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                check_arg_number($clean,THREE_ARGS);
                label_check($clean[FIRST_ARG]);
                symb_check($clean[SECOND_ARG]);
                symb_check($clean[THIRD_ARG]);
                print_XML($clean,THREE_ARGS,$instruction++,"label","symb","symb");
                break;
            default:
            opcode_err();
        }
    }

    if($header_flag === false)
    {
        head_err();
    }
    
    xmlwriter_end_document($xml);
    echo xmlwriter_output_memory($xml);
?>