<?php
/** 
 * @file parse.php
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

define("HELP_STRING", "Názov:\n   parse.php - lexikálny a syntaktický analyzátor jazyka IPPcode23\n\nPoužitie:\n        php8.1 parse.php [MOŽNOSTI]\n\nPopis:\n    parse.php vykoná lexikálnu a syntaktickú analýzu na zdrojovom súbore\n    zapísanom v jazyku IPPcode23 a vygeneruje XML reprezentáciu kódu\n\nMOŽNOSTI\n    --help\n        Vypíše pomocnú hlášku pre skript parse.php");

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
function arg_check(int $argc, array $argv): void
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
    if (!preg_match('/^(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)(_|-|\$|&|%|\*|!|\?|[0-9][A-Z]|[a-z]|[0-9]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$/', $token))
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
    if (!(preg_match('/^(LF|TF|GF)@(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)+[0-9]*(_|-|\$|&|%|\*|!|\?|[A-Z]|[a-z]|[A-Z]|\?|!|\*|&|%|_|-|\$)*$/', $token) || preg_match('/^string@([^\s#\\\\]|\\\\\d{3})*$$/', $token) || preg_match('/^bool@(true|false)$/', $token) || preg_match('/^nil@nil$/', $token) || preg_match('/^int@(\+|-){0,1}(([1-9][0-9]*(_[0-9]+)*)|0)$/', $token) || preg_match('/^int@(\+|-){0,1}0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*$/', $token) || preg_match('/^int@(\+|-){0,1}0[oO]?[0-7]+(_[0-7]+)*+$/', $token)))
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

/**
 * Spracuje tokeny, ktoré majú typ - symbol
 * @param string $data
 * @return array
 */
function process_symb(string $data): array
{
    if (preg_match('/^int@.*$/', $data))
    {
        $data = preg_replace('/^int@/', '', $data);
        $type = "int";
    }
    elseif (preg_match('/^string@.*$/', $data))
    {
        $data = preg_replace('/^string@/', '', $data);
        $type = "string";
    }
    elseif (preg_match('/^bool@.*$/', $data))
    {
        $data = preg_replace('/^bool@/', '', $data);
        $type = "bool";
    }
    elseif (preg_match('/^nil@.*$/', $data))
    {
        $data = preg_replace('/^nil@/', '', $data);
        $type = "nil";
    }
    else
    {
        $type = "var";
    }

    $array_to_return = array($data, $type);

    return $array_to_return;
}

/**
 * Vytvorí hlavičku XML reprezentácie kódu
 * @return void
 */
function write_xml_header(): void
{
    global $xml;
    $xml = xmlwriter_open_memory();
    xmlwriter_set_indent($xml, true);
    $xml->res = xmlwriter_set_indent_string($xml, '  ');
    xmlwriter_start_document($xml, '1.0', 'UTF-8');
    xmlwriter_start_element($xml, 'program');
    xmlwriter_start_attribute($xml, 'language');
    xmlwriter_text($xml, 'IPPcode23');
    xmlwriter_end_attribute($xml);
}

/**
 * Vytvorí inštrukciu v XML reprezentácii kódu
 * @param int $inst_number Poradie inštrukcie
 * @param array $stream Pole obsahujúce meno a parametre inštrukcie
 * @return void
 */
function write_instruction(int $inst_number, array $stream): void
{
    global $xml;
    xmlwriter_start_element($xml, 'instruction');
    xmlwriter_start_attribute($xml, 'order');
    xmlwriter_text($xml, $inst_number);
    xmlwriter_end_attribute($xml);
    xmlwriter_start_attribute($xml, "opcode");
    xmlwriter_text($xml, strtoupper($stream[ZERO_OPS]));
    xmlwriter_end_attribute($xml);
}

/**
 * Vytvorí argument v XML reprezentácii kódu
 * @param string $type Typ operandu inštrukcie
 * @param array $stream Pole obsahujúce meno a parametre inštrukcie
 * @param int $argument_number Poradie vytváraného operandu
 * @return void
 */
function write_argument(string $type, array $stream, int $argument_number): void
{
    global $xml;

    if ($type === "symb")
    {
        $output_array = process_symb($stream[$argument_number]);
        $data = $output_array[0];
        $type = $output_array[1];
    }

    xmlwriter_start_element($xml, 'arg' . $argument_number);
    xmlwriter_start_attribute($xml, 'type');
    xmlwriter_text($xml, $type);
    xmlwriter_end_attribute($xml);
    if ($type === "int" || $type === "string" || $type === "bool" || $type === "nil")
    {
        xmlwriter_text($xml, $data);
    }
    else
        xmlwriter_text($xml, $stream[$argument_number]);

    xmlwriter_end_element($xml);
}

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

    write_instruction($inst_number, $stream);

    switch ($operand_count)
    {
        case ONE_OP:
            write_argument($type_1, $stream, ONE_OP);
            break;
        case TWO_OPS:
            write_argument($type_1, $stream, ONE_OP);
            write_argument($type_2, $stream, TWO_OPS);
            break;
        case THREE_OPS:
            write_argument($type_1, $stream, ONE_OP);
            write_argument($type_2, $stream, TWO_OPS);
            write_argument($type_3, $stream, THREE_OPS);
            break;
    }
    xmlwriter_end_element($xml);
}

/**Vytvorenie povinnej hlavičky */
write_xml_header();

/** @var $instruction - Počet inštrukcií*/
$instruction = 1;

/** @var $header_flag - Značí prítomnosť hlavičky - IPPcode23 */
$header_flag = false;

/**Overenie vstupných argumentov skriptu */
arg_check($argc, $argv);

/**Spracovanie inštrukcií zo štandardného vstupu */
while ($line = fgets(STDIN))
{
    $clean = explode(' ', trim($line, "\n"));

    /**Odstránenie komentárov a bielych znakov zo vstupu */
    /** @var $comment_flag - Značí prítomnosť komentára */
    $comment_flag = false;
    $new_clean = [];

    foreach ($clean as $word)
    {
        if (preg_match('/^\s*#.*$/', $word) || preg_match('/#.*$/', $word))
        {
            $comment_flag = true;
            $new_clean[] = preg_replace('/#.*$/', '', $word);
        }
        elseif ($comment_flag == false && $word != "")
        {
            $new_clean[] = preg_replace('/^\s*$/', '', $word);
        }
    }

    /**Odstránenie prázdnych riadkov (whitespaces) zo vstupu */
    if (empty($new_clean[0]) || $new_clean[0] == "")
    {
        continue;
    }

    /**Kontrola prítomnosti hlavičky - IPPcode23 */
    if ($header_flag == false)
    {
        if (strtoupper($new_clean[0]) !== ".IPPCODE23" || !empty($new_clean[FIRST_OP]))
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
    switch (strtoupper($new_clean[0]))
    {
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            check_op_number($new_clean, ZERO_OPS);
            create_XML($new_clean, ZERO_OPS, $instruction++, NULL, NULL, NULL);
            break;
        case "DEFVAR":
        case "POPS":
            check_op_number($new_clean, ONE_OP);
            var_check($new_clean[FIRST_OP]);
            create_XML($new_clean, ONE_OP, $instruction++, "var", NULL, NULL);
            break;
        case "LABEL":
        case "CALL":
        case "JUMP":
            check_op_number($new_clean, ONE_OP);
            label_check($new_clean[FIRST_OP]);
            create_XML($new_clean, ONE_OP, $instruction++, "label", NULL, NULL);
            break;
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            check_op_number($new_clean, ONE_OP);
            symb_check($new_clean[FIRST_OP]);
            create_XML($new_clean, ONE_OP, $instruction++, "symb", NULL, NULL);
            break;
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
        case "NOT":
            check_op_number($new_clean, TWO_OPS);
            var_check($new_clean[FIRST_OP]);
            symb_check($new_clean[SECOND_OP]);
            create_XML($new_clean, TWO_OPS, $instruction++, "var", "symb", NULL);
            break;
        case "READ":
            check_op_number($new_clean, TWO_OPS);
            var_check($new_clean[FIRST_OP]);
            type_check($new_clean[SECOND_OP]);
            create_XML($new_clean, TWO_OPS, $instruction++, "var", "type", NULL);
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
            check_op_number($new_clean, THREE_OPS);
            var_check($new_clean[FIRST_OP]);
            symb_check($new_clean[SECOND_OP]);
            symb_check($new_clean[THIRD_OP]);
            create_XML($new_clean, THREE_OPS, $instruction++, "var", "symb", "symb");
            break;
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            check_op_number($new_clean, THREE_OPS);
            label_check($new_clean[FIRST_OP]);
            symb_check($new_clean[SECOND_OP]);
            symb_check($new_clean[THIRD_OP]);
            create_XML($new_clean, THREE_OPS, $instruction++, "label", "symb", "symb");
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