import multiprocessing
import sys
import time
import argparse
from math import ceil
from multiprocessing import Process, cpu_count, Manager, Queue
from os import cpu_count
from selenium import webdriver
from sys import argv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.firefox.options import Options




def extrahuj_slova(URL,nastaveni,fronta,verbose,pozice_dilu=1,pocet_dilu=1,maximum_stran=-1):
    driver=webdriver.Firefox(options=nastaveni)
    driver.get(URL)
    seznam_strana = 0
    predesly_nadpis = ""
    kol_pro_zapsani=5
    # nacitani a ukladani textu dokud nenajede na posledni stranku
    while True:
        if verbose:
            print(f"PID:{multiprocessing.current_process().pid} - page:{seznam_strana}")
        i = 0
        URL_seznam = driver.current_url
        seznam_stranek = driver.find_element(By.CLASS_NAME, "mw-allpages-chunk").find_elements(By.TAG_NAME, "a")
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
            stranky_URL[j] = seznam_stranek[i].get_attribute("href")
            j+=1
        #extrahuje text z jednotlivých stránek
        for i in range(len(stranky_URL)):
            #print(str(i) + ":" + stranky_URL[i])
            driver.get(stranky_URL[i])
            nadpis=driver.find_element(By.ID,"firstHeading").text
            if predesly_nadpis == nadpis:
                continue
            else:
                text_buffer.append(driver.find_element(By.ID, "bodyContent").text)
                predesly_nadpis=nadpis
        driver.get(URL_seznam)

        #prejde na dalsi stranku se seznamem
        dalsi_stranka = driver.find_element(By.CLASS_NAME, "mw-allpages-nav").find_elements(By.TAG_NAME, "a")
        dalsi_stranka[-1].click()
        if len(driver.find_element(By.CLASS_NAME, "mw-allpages-nav").find_elements(By.TAG_NAME, "a"))<=1 or (seznam_strana >= maximum_stran !=-1):
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

        seznam_strana += 1
    #radne ukonceni procesu
    driver.quit()



def cteni_queue(ukonceni,fronta,hlavni_buffer):
    while not ukonceni.value:
        while not fronta.empty():
            hlavni_buffer.extend(fronta.get())
    unikatni_slova=list(set(hlavni_buffer))
    hlavni_buffer[:]=unikatni_slova



def main():
    #zpracování argumentů z terminálu
    help=False
    ukecany=False
    headless=True
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
                if flag.find("g")!=-1:
                    headless=False
    if help:
        print("""wordlist_generator.py [WP] -možnosti
        -v - ukecaný
        -g - grafický - vypne headless mode prohlížeče a zobrazí je na obrazovku
        --processes=N - počet procesů - nastaví kolik prohlížečů pojede zároveň. V základu běží dvojnásobek počtu CPU jader
        --limit=N - maximální počet stran - do kolika stran wikipedie program pojede (pokud není nastavený limit, vezme všechny)
        --help - zobrazí tuto stránku

        WP - [odkaz na jazykové kódy wikipedie](https://en.wikipedia.org/wiki/List_of_Wikipedias#Wikipedia_edition_codes)
        """)
        return 0

    #nastavi driver
    nastaveni=Options()
    nastaveni.add_argument("--width=1024")
    nastaveni.add_argument("--height=720")
    if headless:
        nastaveni.add_argument("--headless")
    driver = webdriver.Firefox(options=nastaveni)

    # nacte list wikipedia stranek
    driver.get("https://en.wikipedia.org/wiki/List_of_Wikipedias")
    jazyk = driver.find_element(By.XPATH, "//*[text()='" + wp_kod + "']")
    url = driver.find_element(locate_with(By.TAG_NAME, "a").straight_right_of(jazyk))

    driver.get(url.get_attribute("href"))
    # presmeruje se na URL se seznamem stranek
    driver.get(
        driver.find_element(By.CLASS_NAME, "mw-statistics-pages").find_element(By.TAG_NAME, "a").get_attribute("href"))
    time.sleep(1)
    zacatecni_URL = driver.current_url
    driver.quit()
    if ukecany:
        print(f"first page URL:{zacatecni_URL}")
    #inicializace multiprocessingu ---------------
    fronta = multiprocessing.Queue()  # zde se slevaji vsechny stringy s procesu ze, ktereho se nakonce vytvori wordlist
    hlavni_buffer=multiprocessing.Manager().list()
    pocet_CPU=cpu_count()
    ukonceni=multiprocessing.Manager().Value("i",0)
    dily=pocet_CPU*2 #vypocte kolik prohlizecu bude bezet zaroven
    if ukecany:
        print(f"number of browsers to open:{dily}")
    procesy=[""]*dily
    zpracovani_fronty=Process(target=cteni_queue, args=(ukonceni, fronta,hlavni_buffer))
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

    ukonceni.value=1
    time.sleep(0.5)
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
