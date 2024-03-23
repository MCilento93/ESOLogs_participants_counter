
### IMPORTING
import os, configparser, logging
import gspread, backoff
import pandas as pd
from gspread import Cell
from table2ascii import table2ascii as t2a, PresetStyle
logger = logging.getLogger(__name__)


### GLOBALS
# Directories
MODULE_DIR = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SW_DIR=os.path.dirname(MODULE_DIR)
LOGS_DIR=os.path.join(SW_DIR,'logs')
GOOGLE_KEY_DIR = os.path.join(MODULE_DIR,'esologs-counter-39fdce6048e3.json')
                              
# Config file
config = configparser.ConfigParser()
config.read(os.path.join(SW_DIR,'config.ini'))

# Backoff algorithm
GOOGLE_API_REFRESH_TIME = 60                    # s
MAX_BACKOFF_TIME = GOOGLE_API_REFRESH_TIME+1    # s - with margins

# Google sheet
SPREADSHEET_NAME = 'esologs-counter-R01'


### METHODS
@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def find_row_by_val(ws,value,in_column=1):
    # get row number finding by value in a given column
    cell = ws.find(value,in_column=in_column)
    if cell:
        return cell.row
    else:
        return None

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def find_col_by_val(ws,value,in_row=1):
    # get col number finding by value in a given row
    cell = ws.find(value,in_row=in_row)
    if cell:
        return cell.col
    else:
        return None

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def get_numeric_value(ws,row,col):
    # get numeric value in a cell
    value = ws.cell(row, col)
    if value.numeric_value:
        return value.numeric_value
    else:
        return 0

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def set_value(ws,row,col,value):
    ws.update_cell(row, col, value)

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def append_row(ws,first_col_value):
    row_num = len(ws.col_values(1))
    ws.insert_row([first_col_value],index=row_num+1) # add to first column

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def append_col(ws,header):
    col_num = len(ws.row_values(1))
    ws.insert_cols([[header]],col=col_num+1)  # header set in first row

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def print_worksheet(ws):
    print(get_in_batch(ws))

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def get_in_batch(ws):
    try:
        return ws.get_all_records() # va in errore se trova un alcune colonne di header vuote
    except gspread.exceptions.GSpreadException:
        logger.error(f'Header in "{ws.title}" worksheet has some holes or there are duplicate trial names. Check the header.')

@backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
def set_in_batch(ws,cells:list):
    ws.update_cells(cells)
    logger.info(f'  "{ws.title}" worksheet updated on {len(cells)} cells')


### CLASSES
    
class UserInfo:
    def __init__(self,row,col,value) -> None:
        self.row = row
        self.col = col
        self.value = value

class RankDataBase:

    def __init__(self):
        self.gc = gspread.service_account(filename=GOOGLE_KEY_DIR)
        self.sh = self.gc.open(SPREADSHEET_NAME) # spreadsheet
        self.ws = self.sh.worksheet('rank') # worksheet

    @property
    def url_to_worksheet(self):
        return self.ws.url
    
    def find_username_row(self,username,or_insert=False):
        row = find_row_by_val(self.ws,username)
        if row==None and or_insert:
            append_row(self.ws,username)          
            logger.info(f'Added new user to the *{self.ws.title}* worksheet: {username}')
            row = find_row_by_val(self.ws,username)
        return row
    
    def find_trial_col(self,trial_name,or_insert=False):
        col = find_col_by_val(self.ws,trial_name)
        if col==None and or_insert:
            append_col(self.ws,trial_name)          
            logger.info(f'Added new trial to the *{self.ws.title}* worksheet: {trial_name}')
            col = find_row_by_val(self.ws,trial_name)
        return col

    def start_up_procedure(self):
        set_value(self.ws,2,1,value="This row has been intentionally left empty")
        logger.warning('  Dumb value added in *rank* db as username to sustain update procedure')

    def slow_update(self,usernames:list,trial_name,time_str):
        logger.warning(f'Slow update procedure started ({trial_name} of {time_str})')
        col = self.find_trial_col(trial_name,or_insert=True)
        for username in usernames:
            row = self.find_username_row(username,or_insert=True)
            current_counter = get_numeric_value(self.ws,row,col)
            set_value(self.ws,row,col,current_counter+1)
            set_value(self.ws,row,2,time_str)
            logger.info(f'+1 @{trial_name} for {username}')

    def get_ascii_table(self):
        values = get_in_batch(self.ws)
        # Startup for an empty worksheet
        if values == []:
            return None

        # Open pandas dataframe to locate elements
        df = pd.DataFrame.from_dict(values)
        df = df[df['attendances']!='']                                              # remove blank row
        df.sort_values(by=['attendances'],ascending=False, inplace=True)            # sort by attendances
        df_subset = df[['username','attendances','n','v','v HM+1+2+3']][0:10]       # up to 10th on the leaderboard
        df_subset['Pos.'] = df_subset.reset_index().index + 1                       # Add rank position
        df_subset = df_subset[['Pos.','username','attendances','n','v','v HM+1+2+3']]# Change column order
        # df_subset.set_index('Pos.',inplace=True)
        # df_subset.to_markdown(tablefmt="grid")                                    # intresting alternative with the module 'tabulate'
        header = df_subset.columns.tolist()
        body = df_subset.values.tolist()
        output = t2a(
            header=header,
            body=body,
            style=PresetStyle.thin_compact
        )
        return output

    def update(self,usernames:list,trial_name,time_str):
        logger.info(f'*rank* db - update procedure started ({trial_name} of {time_str})')
        cells = [] # to update
        values = get_in_batch(self.ws)

        # Startup for an empty worksheet
        if values == []:
            self.start_up_procedure()
            values = get_in_batch(self.ws)
            
        # Open pandas dataframe to locate elements
        df = pd.DataFrame.from_dict(values)
        df.set_index('username',inplace=True)
        num_of_users = df.index.size
        last_user_row = num_of_users+1
        last_trial_col = df.columns.size+1
        flag_add_trial = False

        # Detect column of the trial
        if trial_name not in df.columns.values:
            col = last_trial_col+1
            cells.append(Cell(row=1, col=col, value=trial_name))
            flag_add_trial=True
            df[trial_name]=''
        else:
            col = df.columns.get_loc(trial_name)+2 

        # Search usernames
        for username in usernames:
            if username in df.index:
                row = df.index.get_loc(username)+2 
                value = df.loc[username,trial_name]
                if isinstance(value,int):
                    cells.append(Cell(row=row, col=col, value=value+1)) # update trial
                else:
                    cells.append(Cell(row=row, col=col, value=1)) # update trial
                cells.append(Cell(row=row, col=2, value=time_str)) # update time-last-log
            else:
                row = last_user_row+1
                cells.append(Cell(row=row, col=1, value=username)) # update username  
                cells.append(Cell(row=row, col=col, value=1)) # update trial
                cells.append(Cell(row=row, col=2, value=time_str)) # update time-last-log
                last_user_row = last_user_row + 1 

        # Update worksheet
        set_in_batch(self.ws,cells)
        if flag_add_trial:
            logger.info(f'  New column with trial {trial_name} added')
        logger.info(f"{trial_name} succesfully added to the *rank* database")

    def update_attendees(self,usernames_list_of_str):

        # To be executed after the .update method so that users are already defined
        cells = [] # to update
        values = get_in_batch(self.ws)

        # Open pandas dataframe to locate elements
        df = pd.DataFrame.from_dict(values)
        df.set_index('username',inplace=True)
        col = 3 # column with attendee count
        attendee_label = 'attendances'

        # Search usernames
        for username in usernames_list_of_str:
            if username in df.index:
                row = df.index.get_loc(username)+2 
                value = df.loc[username,attendee_label]
                if isinstance(value,int):
                    cells.append(Cell(row=row, col=col, value=value+1)) # update trial
                else:
                    cells.append(Cell(row=row, col=col, value=1)) # update trial

        # Update worksheet
        set_in_batch(self.ws,cells)
        logger.info(f'  Attendances number updated in *rank* db')

class LogDataBase:

    def __init__(self):
        self.gc = gspread.service_account(filename=GOOGLE_KEY_DIR)
        self.sh = self.gc.open(SPREADSHEET_NAME) # spreadsheet
        self.ws = self.sh.worksheet('logs') # worksheet
    
    @property
    def url_to_worksheet(self):
        return self.ws.url
    
    @backoff.on_exception(backoff.expo,gspread.exceptions.APIError,max_time=MAX_BACKOFF_TIME,logger=logger)
    def append_log(self, strftime, title, owner, code, url, attendees_str):
        row = find_row_by_val(self.ws,url,in_column=5) # in case of duplicate, skip
        if row == None:
            body=[  strftime,       # A - timestamp
                    title,          # B - title
                    owner,          # C - owner
                    code,           # D - code
                    url,            # E - url
                    'N',            # F - processed
                    '',             # G - status
                    '',             # H - trials closed
                    attendees_str]  # I - attendees
            self.ws.append_row(body, table_range="A1:I1")
            logger.info(f'  {title} of {strftime} correctly loaded in *logs* worksheet ({url})')

    def start_up_procedure(self):
        set_value(self.ws,2,1,value="This row has been intentionally left empty")
        logger.warning('Dumb value added to *log* database for startup procedure')

    def get_unprocessed_logs(self):
        values = get_in_batch(self.ws)
        if values == []:
            self.start_up_procedure()
            return []
        df = pd.DataFrame.from_dict(values)
        return df['url'].where(df['processed'] == 'N').dropna().to_list()
    
    def mark_processed_log(self,url,status,trials_closed_str):
        row = find_row_by_val(self.ws,url,in_column=5)
        set_value(self.ws,row,col=6,value='Y')                  # set processed
        set_value(self.ws,row,col=7,value=status)               # set status
        set_value(self.ws,row,col=8,value=trials_closed_str)    # update name of trial closed
        logger.info(f'Processed and status of the log updated for {trials_closed_str}')

    
### TESTs
def test1__slow_update():
    logger.info(' * Test 1 started')
    r = RankDataBase()
    username_list = ['a','b','c','d','e','f','g','h','i','j','mata']
    trial_list=['nAA','vAA','vAA HM','vHRC','nAA','nAA','vHRC','vHRC','vHRC','vHRC']
    import time
    start = time.time()
    for trial in trial_list:
        r.slow_update(username_list,trial,'1-1-1070')
    end = time.time()
    logger.info(f'Test 1 completed in {end-start}s')

def test2__update():
    logger.info(' * Test 2 started')
    r = RankDataBase()
    username_list = ['a','b','c','d','e','f','g','h','i','j','mata']
    trial_list=['nAA','vAA','vAA HM','vHRC','nAA','nAA','vHRC','vHRC','vHRC','vHRC','trialU41']
    import time
    start = time.time()
    for trial in trial_list:
        r.update(username_list,trial,'1-1-1070')
    end = time.time()
    logger.info(f'Test 2 completed in {end-start}s')

def test3__log_update():
    pass

### MAIN
if __name__ == '__main__':
    
    # Setting up logging for test phase
    logpath=os.path.join(LOGS_DIR,'logfile_database.log')
    logging.basicConfig(filename=logpath, 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s @%(name)s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M')
    logger.info('*** Run script database.py')
    # test2__update()
    # test1__slow_update()
    ws = RankDataBase().ws