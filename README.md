# wikipedia wordlist generator
## Description 
WWG uses requests and BeautifulSoup2 to generate a wordlist by reading a wikipedia page, extracting words out of the page, saving them and doing it over and over until it finishes and generates a worldlist from the accumulated words
## Installation
To install needed libraries use this command:
`pip install -r requirements.txt`
## Usage
`python3 wordlist_generator.py [WP] -flags`
### flags:
-v - verbose\
--processes=N - number of prosesses (N) - sets how many processes will run at the same time. By default, the number of processes running is twice the number of CPU cores\
--limit=N - maximum number of pages (N) - how many pages of wikipedia the program will scan to (if there is no limit. It will scan all of them)\
--help - shows this help page
> WP - [link to wikipedia language codes](https://en.wikipedia.org/wiki/List_of_Wikipedias#Wikipedia_edition_codes)
## Examples
### wordlist from english wikipedia
`python3 wordlist_generator.py en`
### use 3 processess
`python3 wordlist_generator.py en --processes=3`
### verbose
`python3 wordlist_generator.py en -v`
### show help
`python3 wordlist_generator.py --help`
