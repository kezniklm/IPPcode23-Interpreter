<?php
$TEST_ITEM = 1;

/**
 * Trida reprezentujici vysledek jednoho testu.
 */
class TestResult
{
    /**
     * Vysledky testu analyzatoru kodu.
     * @var TestPartResult
     */
    public $parseResult = null;

    /**
     * Vysledky testu interpretu.
     * @var TestPartResult
     */
    public $intResult = null;

    /**
     * Funkce pro vyhodnoceni, zda test byl uspesny.
     * @return boolean
     */
    public function isOk()
    {
        if ($this->parseResult != null) {
            if ($this->parseResult->expectedExitCode < 30 && $this->parseResult->expectedExitCode != $this->parseResult->realExitCode)
                return false;

            if ($this->parseResult->diffState != 'not_tested' && $this->parseResult->diffState != 'ok')
                return false;
        }

        if ($this->intResult != null) {
            if ($this->intResult->expectedExitCode != $this->intResult->realExitCode)
                return false;

            if ($this->intResult->diffState != 'not_tested' && $this->intResult->diffState != 'ok')
                return false;
        }

        return true;
    }

    /**
     * Funkce pro ziskani textu v pripade neuspechu testu. Pokud byl test uspesny, tak vraci null.
     *
     * @return string
     */
    public function getMessage()
    {
        $pipeline = $this->parseResult != null && $this->intResult != null;

        if ($pipeline) {
            $res = $this->intResult->getMessage();
            return $res != null ? [$res] : $res;
        }

        $messages = [];

        if ($this->parseResult != null)
            $messages['parse'] = $this->parseResult->getMessage();

        if ($this->intResult != null)
            $messages['interpret'] = $this->intResult->getMessage();

        $result = array_filter($messages, function ($item) {
            return $item != null;
        });

        return count($result) == 0 ? null : $result;
    }
}

/**
 * Trida reprezentujici vysledek jedne casty jednoho testu.
 */
class TestPartResult
{
    /**
     * Ocekavany navratovy kod.
     * @var integer
     */
    public $expectedExitCode = 0;

    /**
     * Skutecny navratovy kod.
     * @var integer
     */
    public $realExitCode = 0;

    /**
     * Cesta k souboru, ve kterem se budou nachazet data vracena na standardni vystup.
     * @var string
     */
    public $stdoutFile = null;

    /**
     * Cesta k souboru, ve kterem se budou nachazet data vracenaw na standardni chybovy vystup.
     * @var string
     */
    public $stderrFile = null;

    /**
     * Stav popisujici vysledek porovanvacim nastrojem. 
     * Muze nabyvat hodnota 'ok', 'not_tested' a 'different'. 
     * @var string
     */
    public $diffState = 'not_tested';

    /**
     * Obsah standardniho vystupu. Pokud soubor neexistuje, tak bude nabyvat hodnoty null.
     * Data se do teto vlastnoti ulozi po zavolani metody clean().
     * @var string
     */
    private $stdout = null;

    /**
     * Obsah standardniho chyboveho vystupu. Pokud soubor neexistuje, tak bude nabyvat hodnoty null.
     * Data se do teto vlastnosti ulozi po zavolani metody clean().
     * @var string
     */
    private $stderr = null;

    /**
     * Rozdily vraceny porovnavacim nastrojem.
     * @var string
     */
    public $diffResult = null;

    /**
     * Funkce pro nacteni obsahu docasnych souboru a jejich uklid.
     *
     * @return void
     */
    public function clean()
    {
        $isOk = $this->isOk();

        if (file_exists($this->stdoutFile)) {
            if (!$isOk)
                $this->stdout = file_get_contents($this->stdoutFile);

            //@unlink($this->stdoutFile);
        }

        if (file_exists($this->stderrFile)) {
            if (!$isOk)
                $this->stderr = file_get_contents($this->stderrFile);

            @unlink($this->stderrFile);
        }
    }

    /**
     * Vyhodnoceni, zda tato cast testu byla uspesna.
     *
     * @return boolean
     */
    public function isOk()
    {
        $msg = $this->getMessage();
        return $msg == null;
    }

    /**
     * Ziskani zpravy o neuspesnosti casti testu. Pokud byl test uspesny.
     * @return string
     */
    public function getMessage()
    {
        if ($this->expectedExitCode != $this->realExitCode) {
            return ('Neočekávaný návratový kód: ' . $this->realExitCode . '. Očekáváno: ' . $this->expectedExitCode) . '<br>' .
                (empty($this->stdout) ? null : '<b>STDOUT:</b> &nbsp;&nbsp;&nbsp;' . htmlspecialchars($this->stdout) . '<br>') .
                (empty($this->stderr) ? null : '<b>STDERR:</b> &nbsp;&nbsp;&nbsp;' . htmlspecialchars($this->stderr));
        }

        if ($this->diffState == 'different')
            return 'Rozdílný výstup<br><pre>' . $this->diffResult . "</pre>";

        return null;
    }
}

/**
 * Trida reprezentujici jeden test.
 */
class TestItem
{
    /**
     * Cesta k adresari se soubory testu.
     * @var string
     */
    public $path;

    /**
     * Nazev testu.
     * @var string
     */
    public $name;

    /**
     * Priznak existence zdrojoveho kodu.
     * @var boolean
     */
    public $srcExists = false;

    /**
     * Priznak, ze existuje vstupni soubor.
     * @var boolean
     */
    public $inputExists = false;

    /**
     * Priznak, ze existuje soubor, ve kterem bude vystup testovaneho progamu.
     * @var boolean
     */
    public $outputExists = false;

    /**
     * Priznak, ze existuje soubor, ve kterem bude navratovy kod.
     * @var boolean
     */
    public $returnCodeExists = false;

    public function __construct($name, $path)
    {
        $this->path = $path;
        $this->name = $name;
    }

    private function getFullPath()
    {
        return realpath($this->path) . DIRECTORY_SEPARATOR . $this->name;
    }

    /**
     * Inicializace testu. Pokud nebude existovat zdrojovy kod testu, tak se vrati vyjimka.
     * Pokud neexistuje vstupni, nebo vystupni soubor, tak se automaticky vytvori prazdny.
     * Pokud nebude existovat soubor s ocekavanym navratovym kodem, tak se automaticky vytvori soubor naplneny hodnotou 0.
     */
    public function initTest()
    {
        if (!$this->srcExists)
            throw new Exception("Source file '" . $this->name . "' not found.");

        if (!$this->inputExists) touch($this->getFullPath() . ".in");
        if (!$this->outputExists) touch($this->getFullPath() . ".out");
        if (!$this->returnCodeExists) file_put_contents($this->getFullPath() . ".rc", "0");
    }

    /**
     * Spusteni testu.
     *
     * @param Arguments $config
     * @return TestResult
     */
    public function runTest($config)
    {
        $result = new TestResult();

        if (!$config->intOnly)
            $result->parseResult = $this->runParserTest($config);

        if (!$config->parseOnly)
            $result->intResult = $this->runInterpretTest($config, $result->parseResult);

        if ($result->parseResult != null) $result->parseResult->clean();
        if ($result->intResult != null) $result->intResult->clean();

        return $result;
    }

    /**
     * Spusteni testu interpretace.
     *
     * @param Arguments $config
     * @param TestPartResult $parseTestResult
     * @return TestPartResult
     */
    private function runInterpretTest($config, $parseTestResult)
    {
        $result = new TestPartResult();
        $fullPath = $this->getFullPath();

        if ($config->debug)
            output("Running interpret test: $fullPath", true);

        $result->expectedExitCode = intval(trim(file_get_contents("$fullPath.rc")));
        $result->stdoutFile = "$fullPath.int_out_tmp";
        $result->stderrFile = "$fullPath.int_err_tmp";

        $sourceCode = $parseTestResult != null ? $parseTestResult->stdoutFile : "$fullPath.src";
        $dataRedirection = "< \"$fullPath.in\" > \"" . $result->stdoutFile . "\" 2> \"" . $result->stderrFile . "\"";
        $pythonExecutablePath = "python3.10 \"" . $config->intScript . "\" --source=\"$sourceCode\" $dataRedirection";
        exec($pythonExecutablePath, $output, $retCode);
        
        $result->realExitCode = $retCode;
        if ($result->expectedExitCode != $retCode) return $result;
        if ($retCode != 0) return $result;

        exec("diff -u \"$fullPath.out\" \"" . $result->stdoutFile . "\"", $output, $retCode);
        if ($retCode != 0) {
            $result->diffState = 'different';

            $filteredDiff = array_filter($output, function ($line) {
                return strlen($line) > 0 && $line[0] != '\\';
            });
            $result->diffResult = implode(PHP_EOL, $filteredDiff);

            return $result;
        }

        $result->diffState = 'ok';
        return $result;
    }

    /**
     * Spusteni testu analyzatoru kodu.
     *
     * @param Arguments $config
     * @return TestPartResult
     */
    private function runParserTest($config)
    {
        $result = new TestPartResult();
        $fullPath = $this->getFullPath();

        if ($config->debug)
            output("Running parse.php test: $fullPath", True);

        $result->expectedExitCode = intval(trim(file_get_contents($fullPath . ".rc")));
        $result->stdoutFile = "$fullPath.out_tmp";
        $result->stderrFile = "$fullPath.err_tmp";

        $phpExecutablePath = "php8.1 \"" . $config->parseScript . "\" < \"$fullPath.src\" > \"" . $result->stdoutFile . "\" 2> \"" . $result->stderrFile . "\"";
        exec($phpExecutablePath, $output, $retCode);

        $result->realExitCode = $retCode;
        if ($result->expectedExitCode < 30 && $result->expectedExitCode != $retCode) return $result;
        if (!$config->parseOnly || $retCode != 0) return $result;

        $jexamxmlExecutablePath = "java -jar \"" . $config->jexamxml . "\" \"$fullPath.out\" \"" . $result->stdoutFile . "\" xml_diff.xml /D \"" . $config->jexamxmlConfig . "\"";
        exec($jexamxmlExecutablePath, $output, $retCode);
        @unlink("xml_diff.xml");

        if ($retCode != 0) {
            $result->diffState = "different";
            return $result;
        }

        $result->diffState = "ok";
        return $result;
    }
}
