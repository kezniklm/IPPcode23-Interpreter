<?php
$HELPER = 1;

/**
 * Trida pro definici vyctovych hodnot navratovych kodu.
 */
class AppCodes
{
    /*** Skript se ukoncuje uspechem. */
    public const Success = 0;

    /*** Doslo k chybe pri nacitani parametru. Napr. neplatna kombinace. */
    public const InvalidParameters = 10;

    /*** Nedari se otevrit vstupni soubor. Neexistuje, chybejici prava, atd... */
    public const CannotOpenInputFileOrDirectory = 11;
}


/**
 * Funkce k ukonceni aplikace z duvodu chyby.
 *
 * @param int $code Ciselny kod chyby.
 * @param string $message Zprava, ktera ma byt vypsana na standardni chybovy vystup. 
 * @return void
 * 
 * @see app_codes.php Ciselnik chybovych kodu.
 */
function errorExit($code, $message = null)
{
    fwrite(STDERR, "Error $code\n");

    if (!empty($message)) {
        fwrite(STDERR, "$message\n");
    }

    exit($code);
}

/**
 * Pomocna funkce pro vypis na standardni vystup, pripadne standardni chybovy vystup.
 *
 * @param string $message Vystupni zprava
 * @param bool useStderr Prepnuti vypisu na standardni chybovy vystup.
 * @return void
 */
function output($message = '', $useStderr = false)
{
    if ($useStderr)
        fwrite(STDERR, $message . PHP_EOL);
    else
        fwrite(STDOUT, $message . PHP_EOL);
}
