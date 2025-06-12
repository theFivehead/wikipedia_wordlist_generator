import multiprocessing
import sys
import time

from math import ceil
from multiprocessing import Process, cpu_count
from os import cpu_count
from urllib.parse import  urlparse

import requests
from bs4 import BeautifulSoup
from urllib3.util import parse_url

bsparser="html.parser"

def extrahuj_slova(URL,fronta,verbose,pozice_dilu=1,pocet_dilu=1,maximum_stran=-1):
    try:
        prvniCastURL="https://"+parse_url(URL).netloc
        seznam_strana = 0
        predesly_nadpis = ""
        kol_pro_zapsani=5
        # nacitani a ukladani textu dokud nenajede na posledni stranku
        while True:
            if verbose:
                print(f"PID:{multiprocessing.current_process().pid} - page:{seznam_strana}")
            i = 0
            #nacte si odkazy na jednotlive články
            WikiSeznamHTML=BeautifulSoup(requests.get(URL).text,bsparser)
            seznam_stranek=WikiSeznamHTML.find(attrs={"class":"mw-allpages-chunk"}).find_all("a")

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
                html=requests.get(stranky_URL[i]).text
                html_parsed=BeautifulSoup(html,"html.parser")
                nadpis=html_parsed.find(id='firstHeading').text
                if predesly_nadpis == nadpis:
                    continue
                else:
                    text_buffer.append(html_parsed.body.get_text().strip())
                    predesly_nadpis=nadpis


            #prejde na dalsi stranku se seznamem
            URL_dalsi_stranka=WikiSeznamHTML.find(attrs={"class":"mw-allpages-nav"}).find_all("a")
            print(URL_dalsi_stranka[-1].get('href'))
            print(len(URL_dalsi_stranka))
            print(len(URL_dalsi_stranka) <= 1 < seznam_strana)
            print(seznam_strana >= maximum_stran != -1)
            #zkontroluje jestli se nenachazi na posledni strance nebo neprekrocil limit stran
            if (len(URL_dalsi_stranka) <= 1 < seznam_strana) or (seznam_strana >= maximum_stran != -1):
                # postprocessing
                for text in text_buffer:
                    slova = text.split()
                    fronta.put(list(set(slova)))
                text_buffer.clear()
                break
            elif (seznam_strana+1)%kol_pro_zapsani==0: #zapise slova do spolecneho buferu
                # postprocessing
                for text in text_buffer:
                    slova = text.split(text)
                    fronta.put(list(set(slova)))
                text_buffer.clear()

            URL= prvniCastURL+URL_dalsi_stranka[-1].get('href')#prejde na dalsi stranku
            print("URL: "+URL)

            seznam_strana += 1
    except KeyboardInterrupt:
        if verbose:
            print(f"ending PID:{multiprocessing.current_process().pid}")
        for text in text_buffer:
            slova = text.split()
            fronta.put(list(set(slova)))
        text_buffer.clear()
        return 1
    #radne ukonceni procesu



def cteni_queue(ukonceni,fronta,hlavni_buffer):

    while not ukonceni.value:
        try:
            while not fronta.empty():
                hlavni_buffer.extend(fronta.get())
        except KeyboardInterrupt:
            print("stop")
            ukonceni.value=1
    unikatni_slova=list(set(hlavni_buffer))
    hlavni_buffer[:]=unikatni_slova



def main():
    #zpracování argumentů z terminálu
    help=False
    ukecany=False
    headless=True
    pocet_CPU = cpu_count()
    dily = pocet_CPU * 2  # vypocte kolik prohlizecu bude bezet zaroven
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
                if flag.find("processes"):
                    arg_hodnota=flag.find("=")
                    dily=int(flag[arg_hodnota+1:])
                if flag.find("limit"):
                    arg_hodnota=flag.find("=")
                    max_stran=int(flag[arg_hodnota+1:])
            elif flag.find("-")!=-1: #kratke argumenty
                if flag.find("v")!=-1:
                    ukecany=True
    if help:
        print("""wordlist_generator.py [WP] -možnosti
        -v - ukecaný
        --processes=N - počet procesů - nastaví kolik prohlížečů pojede zároveň. V základu běží dvojnásobek počtu CPU jader
        --limit=N - maximální počet stran - do kolika stran wikipedie program pojede (pokud není nastavený limit, vezme všechny)
        --help - zobrazí tuto stránku

        WP - [odkaz na jazykové kódy wikipedie](https://en.wikipedia.org/wiki/List_of_Wikipedias#Wikipedia_edition_codes)
        """)
        return 0



    # nacte list wikipedia stranek a extrahuje URL pro dany WP kod
    print(wp_kod)
    jazyk = BeautifulSoup(requests.get("https://en.wikipedia.org/wiki/List_of_Wikipedias").text,bsparser).find("a",string=wp_kod).parent.parent.next_sibling()
    print(jazyk)

    if jazyk is None:
        print("code "+wp_kod+" doesnt exist")
        sys.exit()
    url=jazyk[0].get('href')
    print(url)
    if url.find("https:") == -1:
        print("code "+wp_kod+" doesnt exist")
        sys.exit()

    #driver.get(url.get_attribute("href"))
    requests.get(url)
    # presmeruje se na URL se seznamem clanku
    r=requests.get(url)
    seznam_clanku=BeautifulSoup(r.text,bsparser).find(attrs={"class":"mw-statistics-pages"}).find("a",href=True).get('href')
    print(seznam_clanku)

    zacatecni_URL="https://"+urlparse(url).netloc+seznam_clanku #prvni URL se seznamem
    print(zacatecni_URL)


    if ukecany:
        print(f"first page URL:{zacatecni_URL}")
    #inicializace multiprocessingu ---------------
    fronta = multiprocessing.Queue()  # zde se slevaji vsechny stringy s procesu ze, ktereho se nakonce vytvori wordlist
    hlavni_buffer=multiprocessing.Manager().list()

    ukonceni=multiprocessing.Manager().Value("i",0)


    if ukecany:
        print(f"number of processes to start:{dily}")
    procesy=[""]*dily
    zpracovani_fronty=Process(target=cteni_queue, args=(ukonceni, fronta,hlavni_buffer))
    try:
        #vytvori a spusti procesy
        for i in range(len(procesy)):
            procesy[i]=Process(target=extrahuj_slova, args=(zacatecni_URL,nastaveni ,fronta,ukecany ,i, dily,max_stran))
        for i in range(len(procesy)):
            procesy[i].start()
            if ukecany:
                print(f"Process {i+1} started with PID:{procesy[i].pid}")
        zpracovani_fronty.start()
        print("world list processing has started")
        for i in range(len(procesy)):
            procesy[i].join()
        ukonceni.value = 1
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("ending script please wait")
        ukonceni.value = 1
        time.sleep(0.5)
        for i in range(len(procesy)):
            procesy[i].join()
    if zpracovani_fronty.is_alive():
        time.sleep(2)
        zpracovani_fronty.terminate()
    # zapsani bufferu do souboru
    with open(wp_kod+"_wordlist.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(set(hlavni_buffer)))
        # zapise do souboru
    print("wordlist "+wp_kod+"_wordlist.txt successfully created")


if __name__=='__main__':
    main()
