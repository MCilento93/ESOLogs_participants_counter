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
import re, sys, os


### GLOBALS
MODULE_DIR = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SW_DIR=os.path.dirname(MODULE_DIR)
LOGS_DIR=os.path.join(SW_DIR,'logs')
TXT_DIR=os.path.join(SW_DIR,'txt')


### METHODS
def extract_esologs_urls_from_str(txt:str):
    # pattern = r'https://www\.esologs\.com/reports/[a-zA-Z0-9]{16}'
    pattern = r'esologs\.com/reports/[a-zA-Z0-9]{16}'
    return ['https://www.'+a for a in re.findall(pattern, txt)]

def extract_esologs_urls_from_local_file(filepath_to_txt):
    file = open(filepath_to_txt,"r",encoding='utf-8')
    content = file.read()
    file.close()
    return extract_esologs_urls_from_str(content)


### MAIN
if __name__ == '__main__':

    # TEST 1: Scrape a string
    txt = f""" vSS 17/01  https://www.esologs.com/reports/mk1PTjKqB8XF2Nap
27 gennaio 2024 bloody🩸 — Ieri alle 22:32 
vCR+0 https://www.esologs.com/reports/BjqH3RPkhAcVZ8NY#boss=-2&difficulty=0"""
    urls = extract_esologs_urls_from_str(txt)
    print(f"Urls from string: {urls}")
    from esologs_parser import Log
    for url in urls:
        Log(url).calculate_list_winners()

    # TEST 2: Scrape a local file
    txtpath = os.path.join(TXT_DIR,'local.txt')
    urls = extract_esologs_urls_from_local_file(txtpath)
    print(f"Urls from local.txt: {urls}")