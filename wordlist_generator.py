import multiprocessing
import sys
import time
from logging import exception

from math import ceil
from multiprocessing import Process, cpu_count, Manager, Queue
from os import cpu_count
from urllib.parse import  urlparse

import requests
from bs4 import BeautifulSoup
from urllib3.util import parse_url

bsparser="html.parser"

def extrahuj_slova(URL,fronta,verbose,pozice_dilu=1,pocet_dilu=1,maximum_stran=-1):
    def uloz_do_fronty(buffer):
        for text in buffer:
            slova = text.split()
            fronta.put(list(set(slova)))
        text_buffer.clear()
    prvniCastURL="https://"+parse_url(URL).netloc
    seznam_strana = 0
    predesly_nadpis = ""
    kol_pro_zapsani=5
    text_buffer = []
    try:
        # nacitani a ukladani textu dokud nenajede na posledni stranku
        while True:
            bezchyby=True
            if verbose:
                print(f"PID:{multiprocessing.current_process().pid} - page:{seznam_strana}")
            i = 0
            #nacte si odkazy na jednotlive články
            try:
                WikiSeznamHTML=BeautifulSoup(requests.get(URL).text,bsparser)
                seznam_stranek=WikiSeznamHTML.find(attrs={"class":"mw-allpages-chunk"}).find_all("a")
            except AttributeError:
                bezchyby=False
            if bezchyby:
                text_buffer = []
                omezeni_zhora=ceil(len(seznam_stranek) / pocet_dilu)
                konec_rozsahu=(pozice_dilu+1) *  omezeni_zhora
                zacatek_rozsahu=konec_rozsahu-omezeni_zhora
                if konec_rozsahu > len(seznam_stranek):
                    konec_rozsahu=len(seznam_stranek)

                stranky_URL = [""] * (konec_rozsahu-zacatek_rozsahu)

                #extrahuje odkazy ze seznamu
                j=0
                for i in range(zacatek_rozsahu,konec_rozsahu):
                    stranky_URL[j] = prvniCastURL+seznam_stranek[i].get('href')
                    j+=1
                #extrahuje text z jednotlivých stránek
                for i in range(len(stranky_URL)):
                    #print(str(i) + ":" + stranky_URL[i]) #debugging
                    try:
                        html=requests.get(stranky_URL[i]).text
                        html_parsed=BeautifulSoup(html,"html.parser")
                        nadpis=html_parsed.find(id='firstHeading').text
                    except AttributeError:
                        continue
                    if predesly_nadpis == nadpis:
                        continue
                    else:
                        text_buffer.append(html_parsed.body.get_text().strip())
                        predesly_nadpis=nadpis

            #prejde na dalsi stranku se seznamem
            URL_dalsi_stranka=WikiSeznamHTML.find(attrs={"class":"mw-allpages-nav"}).find_all("a")
            #print(URL_dalsi_stranka[-1].get('href'))
            #zkontroluje jestli se nenachazi na posledni strance nebo neprekrocil limit stran
            if (len(URL_dalsi_stranka) <= 1 < seznam_strana) or (seznam_strana >= maximum_stran != -1):
                # postprocessing
                uloz_do_fronty(text_buffer)
                break
            elif (seznam_strana+1)%kol_pro_zapsani==0: #zapise slova do spolecneho buferu
                # postprocessing
                uloz_do_fronty(text_buffer)
            URL= prvniCastURL+URL_dalsi_stranka[-1].get('href')#prejde na dalsi stranku
            seznam_strana += 1

    except KeyboardInterrupt:#v pripade SIGKILL ulozi text do fronty
        if verbose:
            print(f"ending PID:{multiprocessing.current_process().pid}")
        uloz_do_fronty(text_buffer)
    #radne ukonceni procesu



def cteni_queue(ukonceni,fronta,hlavni_buffer):
    try:
        while not ukonceni.value:
                while not fronta.empty():
                    hlavni_buffer.extend(fronta.get())
    except KeyboardInterrupt:
        while not ukonceni.value:
            while not fronta.empty():
                hlavni_buffer.extend(fronta.get())
    unikatni_slova=list(set(hlavni_buffer))
    hlavni_buffer[:]=unikatni_slova



def main():
    #zpracování argumentů z terminálu
    help=False
    ukecany=False
    pocet_CPU = cpu_count()
    dily = pocet_CPU * 2  # vypocte kolik processu bude bezet zaroven
    wp_kod=sys.argv[1]
    max_stran=-1
    if wp_kod.find("-") == 0:
        help = True
    if not help and len(sys.argv)>=3:
        for arg_pozice in range(2,len(sys.argv)):
            flag=sys.argv[arg_pozice]
            if flag.find("--")!=-1: #dlouhe argumenty
                if flag.find("help")!=-1:
                    help = True
                elif flag.find("processes")!=-1:
                    arg_hodnota=flag.find("=")
                    dily=int(flag[arg_hodnota+1:])
                elif flag.find("limit")!=-1:
                    arg_hodnota=flag.find("=")
                    max_stran=int(flag[arg_hodnota+1:])
            elif flag.find("-")!=-1: #kratke argumenty
                if flag.find("v")!=-1:
                    ukecany=True
    if help:
        print("""python3 wordlist_generator.py [WP] -flags
-v - verbose
--processes=N - number of prosesses (N) - sets how many processes will run at the same time. By default, the number of processes running is twice the number of CPU cores
--limit=N - maximum number of pages - how many Wikipedia pages the program will go through (if no limit is set, it will take all of them)
--help - shows this help page

WP - https://en.wikipedia.org/wiki/List_of_Wikipedias#Wikipedia_edition_codes""")
        return 0

    # nacte list wikipedia stranek a extrahuje URL pro dany WP kod
    url=""
    if ukecany:
        print("chosen WP:"+wp_kod)
    if wp_kod=="en":
        url="https://en.wikipedia.org/wiki/Special:Statistics"
    else:
        jazyk = BeautifulSoup(requests.get("https://en.wikipedia.org/wiki/List_of_Wikipedias").text,bsparser).find("a",string=wp_kod).parent.parent.next_sibling()
        if jazyk is None:
            print("code "+wp_kod+" doesnt exist")
            sys.exit()
        url=jazyk[0].get('href')
        if url.find("https:") == -1:
            print("code "+wp_kod+" doesnt exist")
            sys.exit()

    # presmeruje se na URL se seznamem clanku
    seznam_clanku=BeautifulSoup(requests.get(url).text,bsparser).find(attrs={"class":"mw-statistics-pages"}).find("a",href=True).get('href')
    zacatecni_URL="https://"+urlparse(url).netloc+seznam_clanku #prvni URL se seznamem

    #inicializace multiprocessingu ---------------
    fronta = multiprocessing.Queue()  # zde se slevaji vsechny stringy s procesu ze, ktereho se nakonce vytvori wordlist
    hlavni_buffer=multiprocessing.Manager().list()

    ukonceni=multiprocessing.Manager().Value("i",0)


    if ukecany:
        print(f"number of processes to start:{dily}")
    procesy=[""]*dily
    zpracovani_fronty=Process(target=cteni_queue, args=(ukonceni, fronta,hlavni_buffer))

    #vytvori a spusti procesy
    for i in range(len(procesy)):
        procesy[i]=Process(target=extrahuj_slova, args=(zacatecni_URL ,fronta,ukecany ,i, dily,max_stran))
    for i in range(len(procesy)):
        procesy[i].start()
        if ukecany:
            print(f"Process {i+1} started with PID:{procesy[i].pid}")
    zpracovani_fronty.start()
    try:
        print("world list processing has started")
        for i in range(len(procesy)):
            procesy[i].join()
        ukonceni.value = 1
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("ending script please wait")
        if ukecany:
            print("stoping processes")
        time.sleep(0.1)

        for i in range(len(procesy)):
            procesy[i].join()
        time.sleep(0.1)
        if ukecany:
            print("ending queue")
        ukonceni.value = 1
        zpracovani_fronty.join()
    if zpracovani_fronty.is_alive():
        time.sleep(2)
        zpracovani_fronty.terminate()
    # zapsani bufferu do souboru
    with open(wp_kod+"_wordlist.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(set(hlavni_buffer)))
        # zapise do souboru
    print("wordlist "+wp_kod+"_wordlist.txt was successfully created")


if __name__=='__main__':
    main()
