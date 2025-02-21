# wikipedia wordlist generátor
[česká dokumentace](https://github.com/theFivehead/wikipedia_wordlist_generator/blob/main/README_cz.md)
## Description 
WWG uses selenium to generate a wordlist by reading a wikipedia page, writing out the words on the page, saving them and doing it over and over until it finishes and generates a worldlist from the accumulated words
## Instalace
Selenium library is needed.
You can install it with this command.
`pip install selenium`
or in the script directory
`pip install -r requirements.txt`
## Usage
`python3 wordlist_generator.py [WP] -flags`
### možnosti:
-v - verbose\
-g - graphic - disable browser headless mode\
--processes=N - počet procesů (N) - nastaví kolik prohlížečů pojede zároveň. V základu běží dvojnásobek počtu CPU jader\
--limit=N - maximalní počet stran (N) - do kolika stran wikipedie program pojede (pokud není nastavený limit vezme všechny)\
--help - zobrazí tuto stránku
> WP - [odkaz na jazykové kódy wikipedie](https://en.wikipedia.org/wiki/List_of_Wikipedias#Wikipedia_edition_codes)
## Příklady
### wordlist z české wikipedie
`python3 wordlist_generator.py cz`
### použíj 3 prohlížeče
`python3 wordlist_generator.py cz --processes=3`
### ukecaný a grafický
`python3 wordlist_generator.py en -gv`
### zobraz nápovědu
`python3 wordlist_generator.py --help`
