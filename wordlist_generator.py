import time
from itertools import dropwhile
import threading
import selenium
from selenium import webdriver
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with

driver=webdriver.Firefox()

#z terminalu nacte argumenty
wp_kod="cs" #kod wikipedie

#nacte list wikipedia stranek
driver.get("https://en.wikipedia.org/wiki/List_of_Wikipedias")
jazyk = driver.find_element(By.XPATH, "//*[text()='"+wp_kod+"']")
url=driver.find_element(locate_with(By.TAG_NAME,"a").straight_right_of(jazyk))

driver.get(url.get_attribute("href"))
#presmeruje se na URL se seznamem stranek
driver.get(driver.find_element(By.CLASS_NAME,"mw-statistics-pages").find_element(By.TAG_NAME,"a").get_attribute("href"))
time.sleep(1)

driver.find_element(By.CLASS_NAME, "mw-allpages-nav").find_element(By.TAG_NAME, "a").click()

driver.get("https://cs.wikipedia.org/wiki/Speci%C3%A1ln%C3%AD:V%C5%A1echny_str%C3%A1nky?from=&to=&namespace=0")
#nacitani a ukladani textu dokud nenajede na posledni stranku
start = time.time()
seznam_strana=0
predesly_nadpis=""

while True:
    print(seznam_strana)
    i = 0
    URL_seznam = driver.current_url
    seznam_stranek = driver.find_element(By.CLASS_NAME, "mw-allpages-body").find_elements(By.TAG_NAME, "a")
    stranky_URL = [""] * len(seznam_stranek)
    text_buffer = []
    processed_buffer = []
    #extrahuje odkazy ze seznamu
    for stranka in seznam_stranek:
        stranky_URL[i] = stranka.get_attribute("href")
        i += 1

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
    if len(driver.find_element(By.CLASS_NAME, "mw-allpages-nav").find_elements(By.TAG_NAME, "a"))<=1:
        break
    seznam_strana += 1
stop = time.time()

print("cas "+str(stop-start))


#postprocessing
for text in text_buffer:
    slova=text.split()
    processed_buffer.extend(slova)



#zapsani bufferu do souboru
with open("file.txt", "w",encoding='utf-8') as f:
    f.write("\n".join(list(set(processed_buffer))))#zapise do souboru
text_buffer.clear()

time.sleep(10)
driver.quit()