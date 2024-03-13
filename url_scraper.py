# -----------------------------------------------------------------------------
# Copyright (C) 2024 - M. Cilento
#
# Title: Esologs url extractor (string scraper)
# Date of creation: mar-2024
#
# Description:
#   This code simply extract links from string or from local file.
#   Run on the shell "python url_scraper.py path_to_txt.txt" to scrape urls on 
#   a  local txt.
#
# -----------------------------------------------------------------------------


### IMPORTING
import re, sys


### METHODS
def extract_esologs_urls_from_str(txt:str):
    pattern = r'https://www\.esologs\.com/reports/[a-zA-Z0-9]{16}'
    return re.findall(pattern, txt)

def extract_esologs_urls_from_local_file(filepath_to_txt):
    file = open(filepath_to_txt,"r",encoding='utf-8')
    content = file.read()
    file.close()
    return extract_esologs_urls_from_str(content)


### MAIN
if __name__ == '__main__':

#     # TEST 1: Scrape a string
#     txt = f"""
# vSS 17/01  https://www.esologs.com/reports/mk1PTjKqB8XF2Nap
# 27 gennaio 2024

# bloody🩸 — Ieri alle 22:32
# vCR+0 https://www.esologs.com/reports/BjqH3RPkhAcVZ8NY#boss=-2&difficulty=0
# """
#     urls = extract_esologs_urls_from_str(txt)
#     print(f"Urls from string: {urls}")
#     from esologs_parser import Log
#     for url in urls:
#         Log(url).calculate_list_winners()

    # TEST 2: Scrape a local file
    # urls = extract_esologs_urls_from_local_file()
    # print(f"Urls from local.txt: {urls}")

    # TEST 3: Scrape the corresponding esologs
    


    # TEST 4: from system arg
    args = sys.argv
    if len(args) > 1:
        print(f'Scraping local file: {args[1]}')
        print(extract_esologs_urls_from_local_file(args[1]))