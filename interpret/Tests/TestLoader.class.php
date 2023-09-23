<?php
if (!isset($TEST_ITEM)) include 'TestItem.class.php';

$TEST_LOADER = 1;

class TestsLoader
{
    /**
     * Funkce pro vyhledani testovacich souboru a jejich provereni.
     *
     * @param Arguments $config
     * @return TestItem[]
     */
    public static function findTests($config)
    {
        $tests = [];
        $files = self::scanDirectory($config, $config->directory);

        foreach ($files as $file) {
            $key = $file["dirname"] . DIRECTORY_SEPARATOR . $file["filename"];
            $extension = $file["extension"];

            if (!in_array($extension, ["src", "in", "out", "rc"])) continue;
            $test = key_exists($key, $tests) ? $tests[$key] : new TestItem($file["filename"], $file["dirname"]);

            switch ($extension) {
                case "src":
                    $test->srcExists = true;
                    break;
                case "in":
                    $test->inputExists = true;
                    break;
                case "out":
                    $test->outputExists = true;
                    break;
                case "rc":
                    $test->returnCodeExists = true;
                    break;
            }

            $tests[$key] = $test;
        }

        return $tests;
    }

    /**
     * Prohledavani adresare (s podporou rekurzivniho vyhledavani).
     *
     * @param Arguments $config
     * @param string $directory
     * @return (string[]|string)[]
     */
    private static function scanDirectory($config, $directory)
    {
        $files = [];

        $content = scandir($directory);
        foreach ($content as $item) {
            if ($item === "." && $item === ".") continue;
            $fullpath = $directory . DIRECTORY_SEPARATOR . $item;

            if (is_dir($fullpath)) {
                if ($config->recursive && $item !== "." && $item !== "..") {
                    array_push($files, ...self::scanDirectory($config, $fullpath));
                }
            } else {
                $files[] = pathinfo($fullpath);
            }
        }

        return $files;
    }
}
