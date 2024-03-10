
### IMPORTING
import re


### METHODS
def extract_esologs_urls_from_str(txt:str):
    pattern = r'https://www\.esologs\.com/reports/[a-zA-Z0-9]{16}'
    return re.findall(pattern, txt)

def extract_esologs_urls_from_local_file():
    file = open("local.txt","r",encoding='utf-8')
    content = file.read()
    file.close()
    return extract_esologs_urls_from_str(content)


### MAIN
if __name__ == '__main__':

    # TEST 1: Scrape a string
    txt = f"""
vSS 17/01  https://www.esologs.com/reports/mk1PTjKqB8XF2Nap
27 gennaio 2024

bloody🩸 — Ieri alle 22:32
vCR+0 https://www.esologs.com/reports/BjqH3RPkhAcVZ8NY#boss=-2&difficulty=0
"""
    urls = extract_esologs_urls_from_str(txt)
    print(f"Urls from string: {urls}")

    # TEST 2: Scrape a local file
    urls = extract_esologs_urls_from_local_file()
    print(f"Urls from local.txt: {urls}")

    # TEST 3: Scrape the corresponding esologs
    from esologs_parser import *
    for url in urls:
        Log(url).calculate_list_winners()