import gspread
gc = gspread.service_account(filename='esologs-counter-39fdce6048e3.json')
sh = gc.open('esologs-counter') # spreadsheet
ws = sh.worksheet('rank') # worksheet

def print_ws():
    print(ws.get_all_records())
    
def add_new_username(username):
    ws.append_row([username])

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
        print(f'Fight {fight_name} not found in the database. Last pull kills not assigned.')
        return None

def update_counter(username,fight_name):
    row = find_username_row(username)
    col = find_fight_name_col(fight_name)
    current_counter = ws.cell(row, col).numeric_value
    if current_counter == None:
        current_counter = 0
    ws.update_cell(row, col, current_counter+1)