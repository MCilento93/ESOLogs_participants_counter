import gspread

gc = gspread.service_account(filename=r'C:\Users\mario\OneDrive\esologs-counter\database\esologs-counter-39fdce6048e3.json')
sh = gc.open('esologs-counter') # spreadsheet
ws = sh.worksheet('rank') # worksheet

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