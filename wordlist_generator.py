import multiprocessing
import time
import argparse
from math import ceil
from multiprocessing import Process, cpu_count, Manager, Queue
from os import cpu_count
from selenium import webdriver
from sys import argv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with




def extrahuj_slova(URL,fronta,pozice_dilu=1,pocet_dilu=1):
    driver=webdriver.Firefox()
    driver.get(URL)
    seznam_strana = 0
    predesly_nadpis = ""
    kol_pro_zapsani=5
    # nacitani a ukladani textu dokud nenajede na posledni stranku
    while True:
        print(seznam_strana)
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
            print(str(i) + ":" + stranky_URL[i])
            driver.get(stranky_URL[i])
            nadpis=driver.find_element(By.ID,"firstHeading").text
            if predesly_nadpis == nadpis:
                continue
            else:
                # print(driver.find_element(By.ID, "bodyContent").text)
                text_buffer.append(driver.find_element(By.ID, "bodyContent").text)
                predesly_nadpis=nadpis
        driver.get(URL_seznam)

        #prejde na dalsi stranku se seznamem
        dalsi_stranka = driver.find_element(By.CLASS_NAME, "mw-allpages-nav").find_elements(By.TAG_NAME, "a")
        dalsi_stranka[-1].click()
        if len(driver.find_element(By.CLASS_NAME, "mw-allpages-nav").find_elements(By.TAG_NAME, "a"))<=1 or seznam_strana >=5:
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
        #print(ukonceni.value)
        while not fronta.empty():
            hlavni_buffer.extend(fronta.get())
    unikatni_slova=list(set(hlavni_buffer))
    hlavni_buffer[:]=unikatni_slova



def main():
    #zpracování argumentů z terminálu

    driver = webdriver.Firefox()
    # z terminalu nacte argumenty
    wp_kod = "cs"  # kod wikipedie

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
    #zahaji nekolik threadu
    start = time.time()
    #inicializace multiprocessingu ---------------
    fronta = multiprocessing.Queue()  # zde se slevaji vsechny stringy s procesu ze, ktereho se nakonce vytvori wordlist
    hlavni_buffer=multiprocessing.Manager().list()
    pocet_CPU=cpu_count()
    ukonceni=multiprocessing.Manager().Value("i",0)
    print(pocet_CPU)
    dily=pocet_CPU*2
    procesy=[""]*dily
    zpracovani_fronty=Process(target=cteni_queue, args=(ukonceni, fronta,hlavni_buffer))
    for i in range(len(procesy)):
        procesy[i]=Process(target=extrahuj_slova, args=(zacatecni_URL, fronta, i, dily))
    for i in range(len(procesy)):
        procesy[i].start()
    zpracovani_fronty.start()
    for i in range(len(procesy)):
        procesy[i].join()

    ukonceni.value=1
    time.sleep(2)
    if zpracovani_fronty.is_alive():
        zpracovani_fronty.terminate()
    print("Konecny cas je:"+str(time.time()-start)+"s")
    # zapsani bufferu do souboru
    with open("file.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(set(hlavni_buffer)))
        # zapise do souboru
    time.sleep(10)







if __name__=='__main__':
    main()




'''





'''
