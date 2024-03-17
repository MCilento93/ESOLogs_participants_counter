# -----------------------------------------------------------------------------
# Copyright (C) 2024 - M. Cilento
#
# Title: ESOlogs scraper by API V1
# Date of creation: mar-2024
#
# Readocs API V1:
#   https://www.esologs.com/v1/docs/#!/Reports/reports_user_userName_get
#
# Examples of requests:
#   - Zones (final boss id, name) (downloaded version: zones.json) 
#       https://www.esologs.com/v1/zones?api_key={API_KEY}
#   - Classes
#       https://www.esologs.com:443/v1/classes?api_key={API_KEY}
#   - Fights (@username, last pull kills, difficulties)
#       https://www.esologs.com/v1/report/fights/AjDv37CYqFynXpGc?api_key={API_KEY} 
#
# -----------------------------------------------------------------------------


### IMPORTING
from esologs_parser import *
from url_scraper import *
from database.database import *
import time, sys, logging


### LOGGER
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/logfile.log', 
                    level=logging.INFO,
                    format='%(asctime)s : %(levelname)s : %(name)s : %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')


### METHODS
def load_logs_from_local_file(filepath):
    # tb replace with only archiviation of logs, no processing
    urls = extract_esologs_urls_from_local_file(filepath)
    for url in urls:
        log = Log(url)
        log.calculate_list_winners()
        time.sleep(60) #30 s non ha funzionato
        for last_pull in log.list_winners:
            update_counter([a.username for a in last_pull['participants']],last_pull['fight'].name,log.datetime_str)


### MAIN 
if __name__ == '__main__':

    args = sys.argv
    # MODE 1: load logs from local file
    if args[1] == 'from_local_file':
        logger.debug('*** RUN PROCEDURE: Load logs from local file')
        filepath = args[2]
        # load_logs_from_local_file(filepath)