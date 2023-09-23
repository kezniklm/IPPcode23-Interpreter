<?php
$HTML_GENERATOR = 1;

/**
 * Generator vysledneho HTML reportu.
 */
class HTMLGenerator
{
    private static $title = "IPP 2020 Výsledky testů";

    /**
     * Provedeni vygenerovani reportu.
     *
     * @param TestResult[] $testResults Vysledky jednotlivych testu.
     * @param Arguments $config Konfigurace z prikazove radky.
     */
    public static function render($testResults, $config)
    {
        echo "<!DOCTYPE html><html>";

        self::renderHead();
        self::renderBody($testResults, $config);

        echo "</html>\n";
    }

    /**
     * Vygenerovani HTML hlavicky a stylu.
     */
    private static function renderHead()
    {
        echo "<head><title>" . self::$title . "</title><meta charset='utf-8' />";

        self::renderStyles();

        echo "</head>";
    }

    private static function renderStyles()
    {
        // Stranka
        echo "<style>* { margin: 0; padding: 0 }
body { box-sizing: border-box; font-family: \"Segoe UI\", Arial, \"Noto Sans\", sans-serif; background: whitesmoke; }";

        // Hlavicka
        echo "header { background: #343a40; display: grid; grid-template-columns: max-content auto; color: #f8f9fa }
header h1 { padding: 10px; padding-right: 15px; margin-right: 15px; font-weight: 100; border-right: 1px solid; }
header .created-at { display: flex; align-items: center; }";

        // Souhrny - konfigurace.
        echo ".summary-container { display: flex; justify-content: center; width: 100%; padding-top: 25px }
.summary-item { min-width: 550px; height: 300px; box-shadow: 10px 10px 50px -20px rgba(0,0,0,0.4); border-radius: 15px; }
.summary-item:not(:last-child) { margin-right: 20px; }
.sumamry-item-footer { font-size: 20px; padding: 10px; color: gray; border-top: 1px solid lightgray; }
.summary-item-content { height: 250px; color: rgba(0, 0, 0, 0.9); }
.summary-item-content ul { padding: 20px; padding-left: 40px; }
.summary-item-content li { padding-top: 5px; }";

        // Souhrny - testy.
        echo ".test-summary-grid { display: grid; grid-template-columns: 40% auto; padding: 20px; padding-left: 40px; height: 80%; }
.test-summary-grid h1 { font-size: 80px; font-weight: 300; height: 100%; display: flex; align-items: center; }
.test-summary-grid h1.bad, .test-result-status.failed { color: red; }
.test-summary-grid h1.middle { color: orange; }
.test-summary-grid h1.good, .test-result-status.success { color: green; }
.test-summary-grid div { display: flex; align-items: center; font-weight: 400; }
.test-summary-grid div table { width: 100%; }
.test-summary-grid div table tr td { font-size: 20px; }";

        // Tabulky.
        echo ".table-results { margin-left: auto; margin-right: auto; width: 70%; }
.table-results h1 { margin-top: 50px; margin-bottom: 20px; font-weight: 300; text-align: center; color: rgba(0, 0, 0, 0.7); font-size: 35px; }
.table-results-container { box-shadow: 10px 10px 50px -20px rgba(0, 0, 0, 0.4); border-radius: 15px; }";

        // Jednotlive testy.
        echo ".test-result { display: flex; border-bottom: 1px solid rgba(81, 85, 90, 0.1); padding: 10px; align-items: center; }
.test-result:last-child { border-bottom: none; margin-bottom: 20px; }
.test-result-order { border: 1px solid; border-radius: 50%; min-width: 32px; min-height: 32px; font-weight: bold; display: flex; justify-content: center; align-items: center; flex-shrink: 0; margin-right: 16px; }
.test-result-columns { display: flex; justify-content: space-between; width: 100%; align-items: center; }
.test-result-columns div { padding: 0px 5px; }
.test-result-columns div:first-child { width: 100%; }
.test-result-columns table { width: 60%; }
.test-result-columns table tr th { width: 180px; text-align: left; }
.test-result-status { font-weight: 400; }
.test-result-table-error-text td { padding-top: 10px; }
.test-result-table-error-text td pre { margin-top: 10px; }";

        echo "</style>";
    }

    /**
     * Vygenerovani tela stranky
     *
     * @param TestResult[] $testResults Vysledky jednotlivych testu.
     * @param Arguments $config Konfigurace z prikazove radky.
     */
    private static function renderBody($testResults, $config)
    {
        echo "<body>";

        self::renderHeader($testResults, $config);
        self::renderTestsTable($testResults);

        echo "</body>";
    }

    /**
     * Vygenerovani hlavicky stranky.
     *
     * @param TestResult[] $testResults Vysledky jednotlivych testu.
     * @param Arguments $config Konfigurace z prikazove radky.
     */
    private static function renderHeader($testResults, $config)
    {
        echo "<header><h1>" . self::$title . "</h1> <div class='created-at'>Vytvořeno:<br>" . date("d. m. Y H:i:s") . "</div></header>";
        self::renderSubheader($testResults, $config);
    }

    /**
     * Vygenerovani podhlavicky (prezentace konfigurace a souhrn testu).
     *
     * @param TestResult[] $testsResult Vysledky jednotlivych testu.
     * @param Arguments $config
     */
    private static function renderSubheader($testsResult, $config)
    {
        echo "<section class='summary-container'>";

        self::renderConfigCard($config);
        self::renderStatusCard($testsResult);

        echo "</section>";
    }

    /**
     * Vygenerovani karty s konfiguraci testu.
     *
     * @param Arguments $config
     */
    private static function renderConfigCard($config)
    {
        echo "<div class='summary-item'><div class='summary-item-content'><ul><li>Adresář: <b>" . $config->directory . "</b></li>";

        if ($config->recursive) echo "<li>Rekurzivní prohledávání</li>";
        if ($config->parseOnly) echo "<li>Pouze parse</li>";
        if ($config->intOnly) echo "<li>Pouze interpret</li>";

        echo "</ul></div><div class='sumamry-item-footer'>Konfigurace testů</div></div>";
    }

    /**
     * Vytenerovani souhrnu za vsechny testy.
     *
     * @param TestResult[] $testsResult
     */
    private static function renderStatusCard($testsResult)
    {
        list($success, $failed) = array_values(self::computeTestsSummary($testsResult));
        $total = $success + $failed;
        $percentage = $total == 0 ? 0 : round(($success / $total) * 100);
        $result_state = $percentage < 40 ? 'bad' : ($percentage >= 40 && $percentage < 80 ? 'middle' : 'good');

        echo "<div class='summary-item'><div class='summary-item-content'><div class='test-summary-grid'>";
        echo "<h1 class='$result_state'>$percentage%</h1><div><table>";

        echo "<tr><td>Úspěšných:</td><td>$success</td></tr><tr><td>Neúspěšných:</td><td>$failed</td></tr><tr><td>Celkem:</td><td>$total</td></tr>
</table></div></div></div><div class='sumamry-item-footer'>Souhrn testování</div></div>";
    }

    /**
     * Vypocet statistik uspesnosti testu.
     *
     * @param TestResult[] $testsResult
     */
    private static function computeTestsSummary($testsResult)
    {
        $result = [true => 0, false => 0];

        foreach ($testsResult as $test) {
            $result[$test->isOk()]++;
        }

        return $result;
    }

    /**
     * Vygenerovani tabulky s vysledky jednotlivych testu.
     *
     * @param TestResults[] $testResults
     */
    private static function renderTestsTable($testResults)
    {
        echo "<section class='table-results'><h1>Výsledky jednotlivých testů</h1><div class='table-results-container'>";

        $keys = array_keys($testResults);
        for ($i = 0; $i < count($keys); $i++) {
            $test = $testResults[$keys[$i]];
            $success = $test->isOk();

            echo "<div class='test-result'><div class='test-result-order'>" . ($i + 1) . "</div><div class='test-result-columns'>";
            echo "<div class='test-result-data'><table><tr><th>Sekce: </th><td>" . dirname($keys[$i]) . "</td></tr><tr><th>Test:</th><td>" . basename($keys[$i]) . "</td></tr>";

            if (!$success)
                echo "<tr class='test-result-table-error-text'><td colspan='2'>" . implode("<br>", $test->getMessage()) . "</td></tr>";

            echo "</table></div><h2 class='test-result-status " . ($success ? 'success' : 'failed') . "'>" . ($success ? 'Úspěch' : 'Selhalo') . "</h2></div></div>";
        }

        echo "</div></section>";
    }
}
