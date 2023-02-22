# Implementačná dokumentácia k 1. úlohe do IPP 2022/2023
**Meno a priezvisko:** Matej Keznikl\
**Login:** xkezni01

## **Popis implementácie skriptu parse.php:**

Skript ako prvé skontroluje správnosť argumentov skriptu. V prípade, že bol zadaný nesprávny argument alebo bolo zadané väčšie množstvo argumentov ako jeden správny, ktorým je --help, skript vráti chybovú návratovú hodnotu 10.

Po kontrole argumentov začne skript načítať v cykle inštrukcie zo štandardného vstupu, ktoré sú následne spracovávané. V rámci cyklu sa ako prvé rozdelí vstup na jednotlivé indexy poľa. Následne sa odstránia komentáre a vykoná sa preusporiadanie poľa z dôvodu jeho možnej nelineárnosti a taktiež sa odstránia biele znaky. Prebehne kontrola prítomnosti hlavičky IPPcode23, v prípade chýbajúcej alebo nesprávnej hlavičky skript vráti chybovú návratovú hodnotu 21. 

Po výskyte hlavičky začne skript s overovaním korektnosti zápisu inštrukcií 
a taktiež s vytváraním XML reprezentácie kódu. Inštrukcie sú rozdelené do viacerých skupín podľa počtu a typu operandov tak, aby mohla byť použité príkazy switch a case na presné zaradenie inštrukcie zo vstupu do danej skupiny. V prípade, ak by bola na vstupe inštrukcia, ktorá nepatrí do ani jednej zo skupín, bude sa jednať o nesprávnu inštrukciu, pričom skript vráti chybovú návratovú hodnotu 22. V rámci danej skupiny je následne kontrolovaný počet parametrov funkciou check_arg_number(), typ operandov danej inštrukcie podľa daného typu operandu funkciami var_check() v prípade premennej, label_check() v prípade návestia, symb_check() v prípade symbolu a type_check() v prípade typu. V prípade akejkoľvek chyby v daných funkciách skript vráti chybovú návratovú hodnotu 23. Na koniec sa v rámci skupiny vygeneruje XML reprezentácia kódu použitím funkcie create_XML(), ktorá využíva knižnicu XMLWriter.

## **Popis jednotlivých funkcií:**
### **Funkcia create_XML**
#### **Vstupné parametre:** array $stream, int $operand_count, int $inst_number, ?string $type_1, ?string $type_2, ?string $type_3

Funkcia vytvára XML reprezentáciu kódu s pomocou knižnice XMLWriter, pričom v pripade, že aspoň jeden z trojice \$type_1, \$type_2, \$type_3 vykoná rozdelenie daného operandu na typ a hodnotu.

### **Funkcia check_op_number(**
#### **Vstupné parametre:** array $stream, int $operand_count

Funkcia overí počet operandov pre danú inštrukciu, pričom v prípade chyby zavolá funkciu syntax_err(), ktorá skript ukončí s návratovou hodnotou 23.

### **Funkcia var_check**
#### **Vstupné parametre:** string $token

Funkcia overí pomocou regulárneho výrazu, či $token je korektný zápis premennej. V prípade chyby zavolá funkciu syntax_err(), ktorá skript ukončí s návratovou hodnotou 23.

### **Funkcia label_check**
#### **Vstupné parametre:** string $token

Funkcia overí pomocou regulárneho výrazu, či $token je korektný zápis návestia. V prípade chyby zavolá funkciu syntax_err(), ktorá skript ukončí s návratovou hodnotou 23.

### **Funkcia symb_check**
#### **Vstupné parametre:** string $token

Funkcia overí pomocou regulárneho výrazu, či $token je korektný zápis symbolu, pričom symbol môže byť premenná alebo konštanta. V prípade chyby zavolá funkciu syntax_err(), ktorá skript ukončí s návratovou hodnotou 23.

### **Funkcia type_check**
#### **Vstupné parametre:** string $token

Funkcia overí pomocou regulárneho výrazu, či $token je korektný zápis typu. V prípade chyby zavolá funkciu syntax_err(), ktorá skript ukončí s návratovou hodnotou 23.

### **Funkcia arg_check**
#### **Vstupné parametre:**  int $argc,array $argv

Táto funkcia overí počet vstupných argumentov skriptu a taktiež ich korektný zápis, pričom je možný iba jeden
vstupný argument –help.
