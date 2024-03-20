# -----------------------------------------------------------------------------
# Copyright (C) 2024 - M. Cilento
#
# Title: Main esologs-counter
# Date of creation: mar-2024
#
# Description:
#   Main for multiple commands. Default run: discord-bot layer.
#
# -----------------------------------------------------------------------------


### IMPORTING
from esologs.esologs_parser import *
from esologs.url_scraper import *
from database.database import *
import sys, logging


### LOGGER
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/logfile.log', 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s @%(name)-22s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M')


### METHODS
def analyze_logs_from_file(filepath):
    # Analyze only url logs stored on a local file
    urls = extract_esologs_urls_from_local_file(filepath)
    for url in urls:
        log = Log(url)
        log.calculate_trials_closed()

def load_logs_from_file(filepath):
    # Store the log in the log database
    urls = extract_esologs_urls_from_local_file(filepath)
    for url in urls:
        log = Log(url)
        LogDataBase().append_log(   log.datetime_str,       # A - timestamp
                                    log.title,              # B - title
                                    log.owner,              # C - owner
                                    log.code,               # D - code
                                    log.url,                # E - url
                                    log.get_attendees().str)# I - attendees

def process_logs():
    # Get urls not processed yet
    urls = LogDataBase().get_unprocessed_logs()
    if urls == []:
        logger.info('All logs in the database have already been processed')
        return
    for url in urls:
    # Calculate logs information
        log = Log(url)
        log.calculate_trials_closed()
        for trial_closed in log.trials_closed.list:
    # Update RankDataBase
            rank_db=RankDataBase()
            rank_db.update(trial_closed.usernames_list_of_str,trial_closed.name,log.datetime_str)
    # Update number of attendances
        rank_db.update_attendees(log.attendees.list_of_str)
    # Update LogDataBase
        LogDataBase().mark_processed_log(log.url,log.status,log.trials_closed.str)


### MAIN 
if __name__ == '__main__':

    args = sys.argv
    # RUN PROCEDURE 1: analize locally the logs from local file (without saving results)
    if args[1] == 'analyze_logs_from_file':
        logger.info('')
        logger.info('*** RUN PROCEDURE: Analyze (only here) logs from local file')
        filepath = args[2]
        analyze_logs_from_file(filepath)
        logger.info('*** END OF analyze_logs_from_file PROCEDURE')
    # RUN PROCEDURE 2: load logs from local file to a remote database
    elif args[1] == 'load_logs_from_file':
        logger.info('')
        logger.info('*** RUN PROCEDURE: Load logs from local file')
        filepath = args[2]
        load_logs_from_file(filepath)
        logger.info('*** END OF load_logs_from_file PROCEDURE')
    # RUN PROCEDURE 3: analize remote logs and update rank database
    elif args[1] == 'process_logs':
        logger.info('')
        logger.info('*** RUN PROCEDURE: Process logs stored on the database')
        process_logs()
        logger.info('*** END OF process_logs PROCEDURE')