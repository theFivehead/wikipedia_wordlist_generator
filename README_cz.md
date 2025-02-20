# wikipedia wordlist generátor
## Popis
WWG používá selenium pro vygenerování wordlistu tak, že načte stránku z wikipedie výpiše slova na stránce uloží si je a tak to dělá pořád do kola dokud se neukončí a z nahromaděných slov vygeneruje worldlist
## Instalace
Je nutné stáhnout knihovnu selenium
`pip install selenium`
nebo v adresáři skriptu
`pip install -r requirements.txt`
## Použití
`python3 wordlist_generator.py [WP] -možnosti`
### možnosti:
-v - ukecaný\
-g - grafický - vypne headless mode prohližeče a zobrazí je na obrazovku\
--processes=N - počet procesů (N) - nastaví kolik prohlížečů pojede zároveň. V základu běží dvojnásobek počtu CPU jader\
--limit=N - maximalní počet stran (N) - do kolika stran wikipedie program pojede (pokud není nastavený limit vezme všechny)\
--help - zobrazí tuto stránku
> WP - [odkaz na jazykové kódy wikipedie](https://en.wikipedia.org/wiki/List_of_Wikipedias#Wikipedia_edition_codes)
## Příklady
### wordlist z české wikipedie
`python3 wordlist_generator.py cz`
### použíj 3 prohlížeče
`python3 wordlist_generator.py cz --processes=3`
### zobraz nápovědu
`python3 wordlist_generator.py --help`
