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
from esologs.esologs_parser import *
from esologs.url_scraper import *
from database.database import *
import time, sys, logging


### LOGGER
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/logfile.log', 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s @%(name)s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M')


### GLOBALS
INDENTATION = '  '


### METHODS
def analyze_logs_from_file(filepath):
    urls = extract_esologs_urls_from_local_file(filepath)
    for url in urls:
        logger.info(f'{INDENTATION}Analyzing {url}')
        log = Log(url)
        log.calculate_trials_closed()

def load_logs_from_file(filepath):
    # Store the log in the log database
    urls = extract_esologs_urls_from_local_file(filepath)
    for url in urls:
        logger.info(f'{INDENTATION}Analyzing {url}')
        log = Log(url)
        LogDataBase().append_log(log) # ADD HERE A CHECK ON CODE
        logger.info(f'{INDENTATION}{log.title} of {log.datetime_str} correctly loaded in *logs* worksheet ({log.url})')

def process_logs():
        # Get urls not processed yet
    urls = LogDataBase().get_unprocessed_logs()
    if urls == []:
        logger.info('All logs in the database have already been processed')
        return
    for url in urls:
        # Calculate logs information
        logger.info(f'{INDENTATION}Analyzing {url}')
        log = Log(url)
        log.calculate_trials_closed()
        for trial_closed in log.trials_closed.list:
        # Update RankDataBase
            rank_db=RankDataBase()
            rank_db.update(trial_closed.usernames_list_of_str,trial_closed.name,log.datetime_str)
            logger.info(f"{INDENTATION}{trial_closed.description} added to the *rank* database")
        # Update number of attendances
        rank_db.update_attendees(log.attendees.list_of_str)
        logger.info(f'{INDENTATION}Attendances number updated')
        # Update LogDataBase
        LogDataBase().mark_processed_log(log.code,log.status,log.trials_closed.str)
        logger.info(f'{INDENTATION}Processed and status of the log updated')


### MAIN 
if __name__ == '__main__':

    args = sys.argv
    # RUN PROCEDURE 1: analize locally the logs from local file (without saving results)
    if args[1] == 'analyze_logs_from_file':
        logger.info('*** RUN PROCEDURE: Analyze (only here) logs from local file')
        filepath = args[2]
        analyze_logs_from_file(filepath)
        logger.info('*** END OF analyze_logs_from_file PROCEDURE')
    # RUN PROCEDURE 2: load logs from local file to a remote database
    elif args[1] == 'load_logs_from_file':
        logger.info('*** RUN PROCEDURE: Load logs from local file')
        filepath = args[2]
        load_logs_from_file(filepath)
        logger.info('*** END OF load_logs_from_file PROCEDURE')
    # RUN PROCEDURE 3: analize remote logs and update rank database
    elif args[1] == 'process_logs':
        logger.info('*** RUN PROCEDURE: Process logs stored on the database')
        process_logs()
        logger.info('*** END OF process_logs PROCEDURE')