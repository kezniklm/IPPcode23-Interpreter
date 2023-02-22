<?php
/** @file parse.php
 * 
 * @brief Lexikálny a syntaktický analyzátor zdrojového kódu v jazyku IPPcode23
 * 
 * @author Matej Keznikl <xkezni01@stud.fit.vutbr.cz>
 */

ini_set('display_errors', 'stderr');

/** Definícia konštánt - exit kódov */
define("EXIT_SUCCESS", 0);
define("EXIT_PARAM", 10);
define("EXIT_HEADER", 21);
define("EXIT_OPCODE", 22);
define("EXIT_SYNTAX", 23);

/** Definícia konštánt - poradie operandov funkcií */
define("FIRST_OP", 1);
define("SECOND_OP", 2);
define("THIRD_OP", 3);
define("FOURTH_OP", 4);

/** Definícia konštánt - počty operandov funkcií */
define("ZERO_OPS", 0);
define("ONE_OP", 1);
define("TWO_OPS", 2);
define("THREE_OPS", 3);

/** Maximálny rozsah pre prerovnanie poľa */
define("MAX", 1024);

define("HELP_STRING",
    "Názov: 
    parse.php - lexikálny a syntaktický analyzátor jazyka IPPcode23

Použitie: 
    php8.1 parse.php [MOŽNOSTI]

Popis: 
    parse.php vykoná lexikálnu a syntaktickú analýzu na zdrojovom súbore 
    zapísanom v jazyku IPPcode23 a vygeneruje XML reprezentáciu kódu

MOŽNOSTI
    --help 
        Vypíše pomocnú hlášku pre skript parse.php"
);

/**
 * V prípade nevhodného počtu operandov vypíše chybovú hlášku a zavolá funkciu exit()
 * @return void
 */
function param_err(): void
{
    error_log("CHYBA: Je možné zadať maximálne jeden argument\n");
    exit(EXIT_PARAM);
}

/**
 * V prípade chybnej alebo chýbajúcej hlavičky vypíše chybovú hlášku a zavolá funkciu exit()
 * @return void
 */
function head_err(): void
{
    error_log("CHYBA: Chýbajúca alebo chybná hlavička\n");
    exit(EXIT_HEADER);
}

/**
 * V prípade chybného operačného kódu vypíše chybovú hlášku a zavolá funkciu exit()
 * @return void
 */
function opcode_err(): void
{
    error_log("CHYBA: Zle zapísaný operačný kód v zdrojovom kóde zapísanom v IPPcode23\n");
    exit(EXIT_OPCODE);
}

/**
 * V prípade syntakticej alebo lexikálnej chyby vypíše chybovú hlášku a zavolá funkciu exit()
 * @return void
 */
function syntax_err(): void
{
    error_log("CHYBA: Syntaktická chyba zdrojového kódu zapísaného v IPPcode23\n");
    exit(EXIT_SYNTAX);
}

/**
 * Overí vstupné parametre skriptu parse.php
 * @param int $argc Počet vstupných argumentov
 * @param array $argv Pole argumentov
 * @return void
 */
function arg_check(int $argc,array $argv):void
{
    /**Overenie argumentov */
    if ($argc === 2)
    {
        if ($argv[1] == "--help")
        {
            echo (HELP_STRING . "\n");
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
}

/**
 * Overenie ⟨var⟩ podľa regulárneho výrazu
 * @param string $token Overovaný token
 * @return void
 */
function var_check(string $token): void
{
    if (!preg_match('/^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$/', $token))
    {
        syntax_err();
    }
}

/**
 * Overenie ⟨label⟩ podľa regulárneho výrazu
 * @param string $token Overovaný token
 * @return void
 */
function label_check(string $token): void
{
    if (!preg_match('/^(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)+$/', $token))
    {
        syntax_err();
    }
}

/**
 * Overenie ⟨symb⟩ podľa regulárneho výrazu
 * @param string $token Overovaný token
 * @return void
 */
function symb_check(string $token): void
{
    if (!(preg_match('/^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)+[0-9]*(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$/', $token) || preg_match('/^string@([^\s#\\\\]|\\\\\d{3})*$$/', $token) || preg_match('/^bool@(true|false)$/', $token) || preg_match('/^nil@nil$/', $token) || preg_match('/^int@(\+|-){0,1}[0-9]+$/', $token)))
    {
        syntax_err();
    }
}

/**
 * Overenie ⟨type⟩ podľa regulárneho výrazu
 * @param string $token Overovaný token
 * @return void
 */
function type_check(string $token): void
{
    if (!preg_match('/^(int|string|bool)$/', $token))
    {
        syntax_err();
    }
}

/**
 * Overenie počtu operandov inštrukcie
 * @param array $stream Pole obsahujúce meno a parametre inštrukcie
 * @param int $operand_count Počet argumentov
 * @return void
 */
function check_op_number(array $stream, int $operand_count): void
{
    switch ($operand_count):
        case ZERO_OPS:
            if (!empty($stream[FIRST_OP]))
            {
                syntax_err();
            }
            break;
        case ONE_OP:
            if (empty($stream[FIRST_OP]) || !empty($stream[SECOND_OP]))
            {
                syntax_err();
            }
            break;
        case TWO_OPS:
            if (empty($stream[FIRST_OP]) || empty($stream[SECOND_OP]) || !empty($stream[THIRD_OP]))
            {
                syntax_err();
            }
            break;
        case THREE_OPS:
            if (empty($stream[FIRST_OP]) || empty($stream[SECOND_OP]) || empty($stream[THIRD_OP]) || !empty($stream[FOURTH_OP]))
            {
                syntax_err();
            }
            break;
    endswitch;
}

/**Vytvorenie povinnej hlavičky */
$xml = xmlwriter_open_memory();
xmlwriter_set_indent($xml, true);
$res = xmlwriter_set_indent_string($xml, '  ');
xmlwriter_start_document($xml, '1.0', 'UTF-8');
xmlwriter_start_element($xml, 'program');
xmlwriter_start_attribute($xml, 'language');
xmlwriter_text($xml, 'IPPcode23');
xmlwriter_end_attribute($xml);

/** @var $instruction - Počet inštrukcií*/
$instruction = 1;

/**
 * Vytvorí XML reprezentáciu kódu
 * @param array $stream Pole obsahujúce meno a parametre inštrukcie
 * @param int $operand_count Počet operandov inštrukcie
 * @param int $inst_number Číslo aktuálne vykonávanej inštrukcie
 * @param string|null $type_1 Typ prvého operandu inštrukcie
 * @param string|null $type_2 Typ druhého operandu inštrukcie
 * @param string|null $type_3 Typ tretieho operandu inštrukcie
 * @return void
 */
function create_XML(array $stream, int $operand_count, int $inst_number, ?string $type_1, ?string $type_2, ?string $type_3): void
{
    global $xml;

    if ($type_1 === "symb")
    {
        if (preg_match('/^int@.*$/', $stream[FIRST_OP]))
        {
            $data_1 = preg_replace('/^int@/', '', $stream[FIRST_OP]);
            $type_1 = "int";
        }
        elseif (preg_match('/^string@.*$/', $stream[FIRST_OP]))
        {
            $data_1 = preg_replace('/^string@/', '', $stream[FIRST_OP]);
            $type_1 = "string";
        }
        elseif (preg_match('/^bool@.*$/', $stream[FIRST_OP]))
        {
            $data_1 = preg_replace('/^bool@/', '', $stream[FIRST_OP]);
            $type_1 = "bool";
        }
        elseif (preg_match('/^nil@.*$/', $stream[FIRST_OP]))
        {
            $data_1 = preg_replace('/^nil@/', '', $stream[FIRST_OP]);
            $type_1 = "nil";
        }
        else
        {
            $type_1 = "var";
        }
    }

    if ($type_2 === "symb")
    {
        if (preg_match('/^int@.*$/', $stream[SECOND_OP]))
        {
            $data_2 = preg_replace('/^int@/', '', $stream[SECOND_OP]);
            $type_2 = "int";
        }
        elseif (preg_match('/^string@.*$/', $stream[SECOND_OP]))
        {
            $data_2 = preg_replace('/^string@/', '', $stream[SECOND_OP]);
            $type_2 = "string";
        }
        elseif (preg_match('/^bool@.*$/', $stream[SECOND_OP]))
        {
            $data_2 = preg_replace('/^bool@/', '', $stream[SECOND_OP]);
            $type_2 = "bool";
        }
        elseif (preg_match('/^nil@.*$/', $stream[SECOND_OP]))
        {
            $data_2 = preg_replace('/^nil@/', '', $stream[SECOND_OP]);
            $type_2 = "nil";
        }
        else
            $type_2 = "var";
    }

    if ($type_3 === "symb")
    {
        if (preg_match('/^int@.*$/', $stream[THIRD_OP]))
        {
            $data_3 = preg_replace('/^int@/', '', $stream[THIRD_OP]);
            $type_3 = "int";
        }
        elseif (preg_match('/^string@.*$/', $stream[THIRD_OP]))
        {
            $data_3 = preg_replace('/^string@/', '', $stream[THIRD_OP]);
            $type_3 = "string";
        }
        elseif (preg_match('/^bool@.*$/', $stream[THIRD_OP]))
        {
            $data_3 = preg_replace('/^bool@/', '', $stream[THIRD_OP]);
            $type_3 = "bool";
        }
        elseif (preg_match('/^nil@.*$/', $stream[THIRD_OP]))
        {
            $data_3 = preg_replace('/^nil@/', '', $stream[THIRD_OP]);
            $type_3 = "nil";
        }
        else
            $type_3 = "var";
    }

    switch ($operand_count)
    {
        case ZERO_OPS:
            xmlwriter_start_element($xml, 'instruction');
            xmlwriter_start_attribute($xml, 'order');
            xmlwriter_text($xml, $inst_number);
            xmlwriter_end_attribute($xml);
            xmlwriter_start_attribute($xml, "opcode");
            xmlwriter_text($xml, strtoupper($stream[ZERO_OPS]));
            xmlwriter_end_attribute($xml);
            xmlwriter_end_element($xml);
            break;
        case ONE_OP:
            xmlwriter_start_element($xml, 'instruction');
            xmlwriter_start_attribute($xml, 'order');
            xmlwriter_text($xml, $inst_number);
            xmlwriter_end_attribute($xml);
            xmlwriter_start_attribute($xml, "opcode");
            xmlwriter_text($xml, strtoupper($stream[ZERO_OPS]));
            xmlwriter_end_attribute($xml);

            xmlwriter_start_element($xml, 'arg1');
            xmlwriter_start_attribute($xml, 'type');
            xmlwriter_text($xml, $type_1);
            xmlwriter_end_attribute($xml);
            if ($type_1 === "int" || $type_1 === "string" || $type_1 === "bool" || $type_1 === "nil")
            {
                xmlwriter_text($xml, $data_1);
            }
            else
                xmlwriter_text($xml, $stream[FIRST_OP]);

            xmlwriter_end_element($xml);
            xmlwriter_end_element($xml);
            break;
        case TWO_OPS:
            xmlwriter_start_element($xml, 'instruction');
            xmlwriter_start_attribute($xml, 'order');
            xmlwriter_text($xml, $inst_number);
            xmlwriter_end_attribute($xml);
            xmlwriter_start_attribute($xml, "opcode");
            xmlwriter_text($xml, strtoupper($stream[ZERO_OPS]));
            xmlwriter_end_attribute($xml);

            xmlwriter_start_element($xml, 'arg1');
            xmlwriter_start_attribute($xml, 'type');
            xmlwriter_text($xml, $type_1);
            xmlwriter_end_attribute($xml);
            xmlwriter_text($xml, $stream[FIRST_OP]);
            xmlwriter_end_element($xml);

            xmlwriter_start_element($xml, 'arg2');
            xmlwriter_start_attribute($xml, 'type');
            xmlwriter_text($xml, $type_2);
            xmlwriter_end_attribute($xml);
            if ($type_2 === "int" || $type_2 === "string" || $type_2 === "bool" || $type_2 === "nil")
            {
                xmlwriter_text($xml, $data_2);
            }
            else
                xmlwriter_text($xml, $stream[SECOND_OP]);
            xmlwriter_end_element($xml);
            xmlwriter_end_element($xml);

            break;
        case THREE_OPS:
            xmlwriter_start_element($xml, 'instruction');
            xmlwriter_start_attribute($xml, 'order');
            xmlwriter_text($xml, $inst_number);
            xmlwriter_end_attribute($xml);
            xmlwriter_start_attribute($xml, "opcode");
            xmlwriter_text($xml, strtoupper($stream[ZERO_OPS]));
            xmlwriter_end_attribute($xml);

            xmlwriter_start_element($xml, 'arg1');
            xmlwriter_start_attribute($xml, 'type');
            xmlwriter_text($xml, $type_1);
            xmlwriter_end_attribute($xml);
            xmlwriter_text($xml, $stream[FIRST_OP]);
            xmlwriter_end_element($xml);

            xmlwriter_start_element($xml, 'arg2');
            xmlwriter_start_attribute($xml, 'type');
            xmlwriter_text($xml, $type_2);
            xmlwriter_end_attribute($xml);
            if ($type_2 === "int" || $type_2 === "string" || $type_2 === "bool" || $type_2 === "nil")
            {
                xmlwriter_text($xml, $data_2);
            }
            else
                xmlwriter_text($xml, $stream[SECOND_OP]);
            xmlwriter_end_element($xml);

            xmlwriter_start_element($xml, 'arg3');
            xmlwriter_start_attribute($xml, 'type');
            xmlwriter_text($xml, $type_3);
            xmlwriter_end_attribute($xml);
            if ($type_3 === "int" || $type_3 === "string" || $type_3 === "bool" || $type_3 === "nil")
            {
                xmlwriter_text($xml, $data_3);
            }
            else
                xmlwriter_text($xml, $stream[THIRD_OP]);

            xmlwriter_end_element($xml);
            xmlwriter_end_element($xml);
            xmlwriter_end_element($xml);
            break;
    }
}

/** @var $header_flag - Značí prítomnosť hlavičky - IPPcode23 */
$header_flag = false;

/**Overenie vstupných argumentov skriptu */
arg_check($argc,$argv);

/**Spracovanie inštrukcií zo štandardného vstupu */
while ($line = fgets(STDIN))
{
    $clean = explode(' ', trim($line, "\n"));

    /**Odstránenie komentárov zo vstupu*/
    $pos = 0;
    for ($i = 0; $i < MAX; $i++)
    {
        if (!empty($clean[$i]) && preg_match('/^#.*/', $clean[$i]))
        {
            if ($i === 0)
            {
                $pos++;
            }
            else
                $pos = $i;
            $clean[$i] = '';
        }
        if ($pos !== 0 && !empty($clean[$i]))
        {
            $clean[$i] = '';
        }
    }
    $pos = 0;
    for ($i = 0; $i < MAX; $i++)
    {
        if (!empty($clean[$i]) && preg_match('/#/', $clean[$i]))
        {
            $clean[$i] = preg_filter('/#.*/', '', $clean[$i]);
            $pos++;
            continue;
        }
        if ($pos !== 0 && !empty($clean[$i]))
        {
            $clean[$i] = '';
        }
    }

    /** Preusporiadanie riadku v prípade zlého uloženia v poli */
    $counter = 0;
    for ($i = 0; $i < MAX; $i++)
    {
        if (!empty($clean[$i]))
        {
            $clean[$counter++] = $clean[$i];
        }
    }

    /**Odstránenie bielych znakov (whitespaces) zo vstupu */
    $clean = preg_replace('/^\s*$/', '', $clean);
    if (preg_match('/^\s*$/', $clean[0]))
    {
        continue;
    }

    /**Kontrola prítomnosti hlavičky - IPPcode23 */
    if ($header_flag == false)
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

    /**Overenie korektnosti zápisu inštrukcií a vytvorenie XML reprezentácie kódu */
    switch (strtoupper($clean[0]))
    {
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            check_op_number($clean, ZERO_OPS);
            create_XML($clean, ZERO_OPS, $instruction++, NULL, NULL, NULL);
            break;
        case "DEFVAR":
        case "POPS":
            check_op_number($clean, ONE_OP);
            var_check($clean[FIRST_OP]);
            create_XML($clean, ONE_OP, $instruction++, "var", NULL, NULL);
            break;
        case "LABEL":
        case "CALL":
        case "JUMP":
            check_op_number($clean, ONE_OP);
            label_check($clean[FIRST_OP]);
            create_XML($clean, ONE_OP, $instruction++, "label", NULL, NULL);
            break;
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            check_op_number($clean, ONE_OP);
            symb_check($clean[FIRST_OP]);
            create_XML($clean, ONE_OP, $instruction++, "symb", NULL, NULL);
            break;
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
        case "NOT":
            check_op_number($clean, TWO_OPS);
            var_check($clean[FIRST_OP]);
            symb_check($clean[SECOND_OP]);
            create_XML($clean, TWO_OPS, $instruction++, "var", "symb", NULL);
            break;
        case "READ":
            check_op_number($clean, TWO_OPS);
            var_check($clean[FIRST_OP]);
            type_check($clean[SECOND_OP]);
            create_XML($clean, TWO_OPS, $instruction++, "var", "type", NULL);
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
            check_op_number($clean, THREE_OPS);
            var_check($clean[FIRST_OP]);
            symb_check($clean[SECOND_OP]);
            symb_check($clean[THIRD_OP]);
            create_XML($clean, THREE_OPS, $instruction++, "var", "symb", "symb");
            break;
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            check_op_number($clean, THREE_OPS);
            label_check($clean[FIRST_OP]);
            symb_check($clean[SECOND_OP]);
            symb_check($clean[THIRD_OP]);
            create_XML($clean, THREE_OPS, $instruction++, "label", "symb", "symb");
            break;
        default:
            opcode_err();
    }
}

/**Kontrola prítomnosti hlavičky - IPPcode23 */
if ($header_flag === false)
{
    head_err();
}

/**Vypísanie XML reprezentácie kódu na štandardný výstup */
xmlwriter_end_document($xml);
echo xmlwriter_output_memory($xml);
exit(EXIT_SUCCESS);
?>