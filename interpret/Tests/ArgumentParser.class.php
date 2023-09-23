<?php
if (!isset($HELPER)) include 'helper.php';

$ARG_PARSE = 1;

/**
 * Trida pro uchovavani nactenych parametru prikazove radky.
 */
class Arguments
{
    /**
     * Priznak vyvolani napovedy
     * @var boolean
     */
    public $help = false;

    /**
     * Cesta k adresari s testy.
     * @var string
     */
    public $directory = ".";

    /**
     * Priznak rekurzivniho vyhledavani testu.
     * @var boolean
     */
    public $recursive = false;

    /**
     * Cesta k souboru, kde se nachazi analyzator kodu.
     * @var string
     */
    public $parseScript = "parse.php";

    /**
     * Cesta k souboru, kde se nachazi interpret.py
     * @var string
     */
    public $intScript = "interpret.py";

    /**
     * Priznak, ze se maji spoustet pouze testy analyzatoru kodu
     * @var boolean
     */
    public $parseOnly = false;

    /**
     * Priznak, ze se maji spustit pouze testy interpretu.
     * @var boolean
     */
    public $intOnly = false;

    /**
     * Cesta k porovnavacimu nastroji XML vystupu.
     * @var string
     */
    public $jexamxml = '.';

    /**
     * Cesta ke konfiguraci nastroje JEXAMXML.
     * @var string
     */
    public $jexamxmlConfig = null;

    /**
     * Vlastni bezkolizni volitelny parametr pro beh v ladicim rezimu. 
     * Vypisuje na stderr, ktery test byl prave provaden
     *
     * @var boolean
     */
    public $debug = false;

    public function __construct()
    {
        $this->jexamxmlConfig = dirname('/pub/courses/ipp/jexamxml/jexamxml.jar') . "/options";
    }

    public function setDirectory($dir)
    {
        $this->checkExists($dir, true);
        $this->directory = $dir;
    }

    public function setParseScript($filepath)
    {
        $filepath = realpath($filepath);
        $this->checkExists($filepath);
        $this->parseScript = $filepath;
    }

    public function setIntScript($filepath)
    {
        $filepath = realpath($filepath);
        $this->checkExists($filepath);
        $this->intScript = $filepath;
    }

    public function setJexamxmlPath($path)
    {
        $path = realpath($path);
        $this->checkExists($path);
        $this->jexamxml = $path;
        $this->jexamxmlConfig = dirname($path) . "/options";
    }

    private function checkExists($path, $isDirectory = false)
    {
        if (!file_exists($path)) {
            $type = $isDirectory ? 'Directory' : 'File';
            throw new ErrorException("$type '$path' not exists", AppCodes::CannotOpenInputFileOrDirectory);
        }
    }
}

/**
 * Hlavni funkce pro nacitani parametru prikazove radky.
 * @return Arguments
 */
function parseCommandLineArgs()
{
    try {
        $args = new Arguments();
        $optArgs = getopt("", ["help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:", "debug"]);

        if (key_exists("help", $optArgs)) {
            if (count($optArgs) > 1)
                throw new ErrorException("--help cannot be combined with another parameters.", AppCodes::InvalidParameters);

            $args->help = true;
        }

        $args->recursive = key_exists("recursive", $optArgs);
        $args->intOnly = key_exists("int-only", $optArgs);
        $args->parseOnly = key_exists("parse-only", $optArgs);
        $args->debug = key_exists("debug", $optArgs);

        if (key_exists("directory", $optArgs)) $args->setDirectory($optArgs["directory"]);
        if (key_exists("parse-script", $optArgs)) $args->setParseScript($optArgs["parse-script"]);
        if (key_exists("int-script", $optArgs)) $args->setIntScript($optArgs["int-script"]);
        if (key_exists("jexamxml", $optArgs)) $args->setJexamxmlPath($optArgs["jexamxml"]);

        if ($args->parseOnly && $args->intOnly)
            throw new ErrorException("--int-only and --parse-only cannot be combined.", AppCodes::InvalidParameters);

        if ($args->parseOnly && key_exists("int-script", $optArgs))
            throw new ErrorException("--int-script cannot be combined with --parse-only", AppCodes::InvalidParameters);

        if ($args->intOnly && key_exists("parse-script", $optArgs))
            throw new ErrorException("--parse-script cannot be combined with --int-only", AppCodes::InvalidParameters);

        return $args;
    } catch (ErrorException $e) {
        errorExit($e->getCode(), $e->getMessage());
    }
}
