all: both int-only krivka

both:
	php test.php  --jexamxml=./jexamxml.jar --int-script=../interpret.py --directory=tests/both --recursive > test-both.html

int-only:
	php test.php  --jexamxml=./jexamxml.jar --int-script=../interpret.py --directory=tests/interpret-only --recursive --int-only > test-int.html

krivka:
	php test.php  --jexamxml=./jexamxml.jar --int-script=../interpret.py --directory=tests/int-only --recursive --int-only > krivka.html

error:
	php test.php --parse-only --int-only --recursive

