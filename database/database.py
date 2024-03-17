
### IMPORTING
import gspread, backoff
import os, configparser, logging
logger = logging.getLogger(__name__)


### GLOBALS
MODULE_DIR = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SW_DIR=os.path.dirname(MODULE_DIR)
LOGS_DIR=os.path.join(SW_DIR,'logs')
config = configparser.ConfigParser()
config.read(os.path.join(SW_DIR,'config.ini'))


### METHODS


gc = gspread.service_account(filename=r'C:\Users\mario\OneDrive\esologs-counter\database\esologs-counter-39fdce6048e3.json')


sh = gc.open('esologs-counter-R01') # spreadsheet
ws = sh.worksheet('rank') # worksheet



def get_all_table(ws):
    return ws.get_all_records() # va in errore se trova un alcune colonne di header vuote

def update_cells(ws):
    cells = []
    cells.append(Cell(row=300, col=1, value='Row-1 -- Col-1'))
    cells.append(Cell(row=1, col=50, value='nuova col'))
    ws.update_cells(cells)

import backoff
@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=80)
def main():
    logger.info('avviata la funzione')
    try:
        for i in range(0,500):
            ws.update_cell(1, 1, i)
    except:
        logger.error('errore, va in backoff ')
    






def print_ws():
    print(ws.get_all_records())
    
def add_new_username(username):
    ws.append_row([username])

def add_new_trial(trial):
    col_num = len(ws.row_values(1))
    ws.insert_cols([[trial]],col=col_num+1)
    # ws.update_cell(1,col_num+1,trial)

def find_username_row(username):
    cell = ws.find(username,in_column=1) # return a cel element
    if cell:
        return cell.row
    else:
        add_new_username(username)
        print(f'Added new user to the database: {username}')
        return find_username_row(username)

def find_fight_name_col(fight_name):
    cell = ws.find(fight_name,in_row=1) # return a cel element
    if cell:
        return cell.col
    else:
        add_new_trial(fight_name)
        return ws.find(fight_name,in_row=1).col
        print(f'Fight {fight_name} not found in the database. Added {fight_name}.')
        return None

def update_counter(usernames,fight_name,time_str):
    col = find_fight_name_col(fight_name)
    if col is None:
        print(f'Column name {fight_name} not found')
        return
    for username in usernames:
        row = find_username_row(username)
        current_counter = ws.cell(row, col).numeric_value
        if current_counter == None:
            current_counter = 0
        ws.update_cell(row, col, current_counter+1)
        ws.update_cell(row,2,time_str)


if __name__ == '__main__':

    # Setting up logging for test phase
    logpath=os.path.join(LOGS_DIR,'logfile_database.log')
    logging.basicConfig(filename=logpath, 
                    level=logging.INFO,
                    format='%(asctime)s : %(levelname)s : %(name)s : %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')
    logger.info('prova sa')