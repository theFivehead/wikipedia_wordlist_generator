# wikipedia wordlist generátor
[česká dokumentace](https://github.com/theFivehead/wikipedia_wordlist_generator/blob/main/README_cz.md)
## Description 
WWG uses selenium to generate a wordlist by reading a wikipedia page, writing out the words on the page, saving them and doing it over and over until it finishes and generates a worldlist from the accumulated words
## Installation
Selenium library is needed.
You can install it with this command.
`pip install selenium`
or in the script directory
`pip install -r requirements.txt`
## Usage
`python3 wordlist_generator.py [WP] -flags`
### flags:
-v - verbose\
-g - graphic - disable browser headless mode\
--processes=N - number of prosesses (N) - sets how many browsers will run at the same time. By default, the number of processes running is twice the number of CPU cores\
--limit=N - maximum number of pages (N) - how many pages of wikipedia the program will scan to (if there is no limit. It will scan all of them)\
--help - shows this help page
> WP - [link to wikipedia language codes](https://en.wikipedia.org/wiki/List_of_Wikipedias#Wikipedia_edition_codes)
## Examples
### wordlist from english wikipedia
`python3 wordlist_generator.py en`
### use 3 browsers (3 processess)
`python3 wordlist_generator.py en --processes=3`
### verbose and graphic
`python3 wordlist_generator.py en -gv`
### show help
`python3 wordlist_generator.py --help`
