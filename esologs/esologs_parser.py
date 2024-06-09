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
import os, requests, json, datetime, configparser, logging, sys
from bs4 import BeautifulSoup


### GLOBALS
# Directories
MODULE_DIR = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SW_DIR=os.path.dirname(MODULE_DIR)
LOGS_DIR=os.path.join(SW_DIR,'logs')
                              
# Config file
config = configparser.ConfigParser()
config.read(os.path.join(SW_DIR,'config.ini'))

# ESOlogs
API_KEY = config['ESOLOGS']['API_KEY']
VERBOSE = True

# Logging
logger = logging.getLogger(__name__)


### CLASSES
class SpecialList:
    def __init__(self,_list: list):
        self.list = _list
    
    def __str__(self) -> str:
        return ', '.join(self.list_of_str)
    
    def __len__(self) -> int:
        return len(self.list)
    
    @property
    def str(self):
        return str(self)

    @property
    def num(self):
        return len(self)
    
    @property
    def list_of_str(self):
        return [str(a) for a in self.list]

class Zone:

    @staticmethod
    def get_zone_json(api_call=False):
        if api_call:
            # API call to retrieve information on all zones
            url = f'https://www.esologs.com/v1/zones?api_key={API_KEY}'
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        else:
            # to avoid API call
            f = open('zones.json')
            zones = json.load(f)
            f.close()
            return zones

    @staticmethod
    def scrape_zone_json():
        zone_json = Zone.get_zone_json()
        scrape_result = []
        for zone in zone_json:
            name = zone['name']
            encounters = zone['encounters']
            final_boss_id = encounters[-1]['id']
            final_boss_name = encounters[-1]['name']
            scrape_result.append({'name':name,
                                 'final_boss_id':final_boss_id,
                                 'final_boss_name':final_boss_name})
        return scrape_result
        
    def __init__(self,name):
        self.is_valid = True
        self.name = name                # string name of the zone (complete or abbreviated)
        if   name in ('Aetherian Archive','AA'):
            self.name_short = 'AA'
            self.final_boss_id   = 4
            self.final_boss_name = 'The Mage'
        elif name in ('Hel Ra Citadel','HRC'):
            self.name_short = 'HRC'
            self.final_boss_id   = 8
            self.final_boss_name = 'The Warrior'
        elif name in ('Sanctum Ophidia','SO'):
            self.name_short = 'SO'
            self.final_boss_id   = 12
            self.final_boss_name = 'The Serpent'
        elif name in ('Maw of Lorkhaj','MOL'):
            self.name_short = 'MOL'
            self.final_boss_id   = 15
            self.final_boss_name = 'Rakkhat'
        elif name in ('Halls of Fabrication','HOF','The Halls of Fabrication'):
            self.name_short = 'HOF'
            self.final_boss_id   = 20
            self.final_boss_name = 'Assembly General'
        elif name in ('Asylum Sanctorium','AS'):
            self.name_short = 'AS'
            self.final_boss_id   = 23
            self.final_boss_name = 'Saint Olms the Just'
        elif name in ('Cloudrest','CR'):
            self.name_short = 'CR'
            self.final_boss_id   = 27
            self.final_boss_name = "Z'Maja"
        elif name in ('Sunspire','SS'):
            self.name_short = 'SS'
            self.final_boss_id   = 45
            self.final_boss_name = 'Nahviintaas'
        elif name in ("Kyne's Aegis",'KA'):
            self.name_short = 'KA'
            self.final_boss_id   = 48
            self.final_boss_name = 'Lord Falgravn'
        elif name in ('Rockgrove','RG'):
            self.name_short = 'RG'
            self.final_boss_id   = 51
            self.final_boss_name = 'Xalvakka'
        elif name in ('Dreadsail Reef','DSR'):
            self.name_short = 'DSR'
            self.final_boss_id   = 54
            self.final_boss_name = 'Tideborn Taleria'
        elif name in ("Sanity's Edge",'SE'):
            self.name_short = 'SE'
            self.final_boss_id   = 57
            self.final_boss_name = 'Ansuul the Tormentor'
        elif name in ("Lucent Citadel",'LC'):
            self.name_short = 'LC'
            self.final_boss_id   = 60
            self.final_boss_name = 'Xoryn'
        else:
            self.is_valid = False
            self.name_short = None
            self.final_boss_id   = None
            self.name = 'n/a'

    def __str__(self) -> str:
        return self.name
    
    def check_if_final_boss(self,boss_id):
        if boss_id == self.final_boss_id:
            return True
        else:
            return False
        
class Fight:

    def __init__(self,fight_dict):
        if fight_dict.get('difficulty'): # is a boss
            self.type = 'boss'
            self.id = fight_dict['id']
            self.boss_id = fight_dict['boss']
            self.boss_name = fight_dict['name']
            self.zone = Zone(fight_dict['zoneName'])
            self.kill = fight_dict['kill']
            self.difficulty_id = fight_dict['difficulty']
            self.assign_difficulty()
        else:
            self.type = 'trash' # trash pull
    
    def __str__(self) -> str:
        return self.name
    
    @property   
    def is_final_boss(self):
        if self.type == 'boss':
            if self.boss_id == self.zone.final_boss_id:
                return True
            else:
                return False
        else:
            return False

    def assign_difficulty(self):
        if self.difficulty_id == 120:
            self.difficulty = 'Normal'
            self.difficulty_prefix = 'n'
            self.difficulty_suffix = ''
        elif self.difficulty_id == 121:
            self.difficulty = 'Veteran'
            self.difficulty_prefix = 'v'
            self.difficulty_suffix = ''
        elif self.difficulty_id == 122:
            self.difficulty = 'Hard Mode'
            self.difficulty_prefix = 'v'
            self.difficulty_suffix = ' HM'
        elif self.difficulty_id == 123:
            self.difficulty = 'Veteran+1'
            self.difficulty_prefix = 'v'
            self.difficulty_suffix= '+1'
        elif self.difficulty_id == 124:
            self.difficulty = 'Veteran+2'
            self.difficulty_prefix = 'v'
            self.difficulty_suffix = '+2'
        elif self.difficulty_id == 125:
            self.difficulty = 'Veteran+3'
            self.difficulty_prefix = 'v'
            self.difficulty_suffix = '+3'
        else:
            pass

    @property
    def name(self):
        if self.type == 'boss':
            return f"{self.difficulty_prefix}{self.zone.name_short}{self.difficulty_suffix}"
        else:
            return 'trash-pull'
        
    @property
    def summary(self):
        if self.type == 'boss':
            return self.name+f" - {self.boss_name} (kill = {str(self.kill)})"
        else:
            return 'trash-pull'

class Friendly:

    def __init__(self,friend_dict):
        _type = friend_dict['type']
        if _type in ['DragonKnight','Arcanist','Templar',
                     'Nightblade','Sorcerer','Warden',
                     'Necromancer']: # see classes request via API V1
            self.is_human = True
            self.dict = friend_dict
            self.class_ = _type
            self.anonymous = friend_dict['anonymous']
            self.username = friend_dict['displayName']
            self.fights = self.get_fights_id()
        else:
            self.is_human = False

    def __str__(self):
        if self.is_human:
            return self.username
        else:
            return 'not-human'
    
    def get_fights_id(self):
        list_fights_id = []
        for fight in self.dict['fights']:
            list_fights_id.append(fight['id'])
        return list_fights_id
    
    def partecipated_to(self,fight_id):
        if self.is_human and fight_id in self.fights:
            return True
        else:
            return False  

class TrialClosed:

    def __init__(self,fight:Fight,winners:SpecialList):
        self.fight = fight
        self.winners = winners

    def __str__(self) -> str:
        return self.name
    
    @property
    def description(self):
        return f"{self.fight.name} by {self.winners.str}"
    
    @property
    def name(self):
        return self.fight.name
    
    @property
    def usernames_str(self):
        return self.winners.str
    
    @property
    def usernames_list_of_str(self):
        return self.winners.list_of_str

class APIError(Exception):
    # Esologs API error, or too many requests (3600/h allowed)
    pass

class Log:
    
    def __init__(self,url):
        """
        Log Status (visible from logs db):
           - NOT ASSIGNET YET    : when created, not visible outside the class herebelow
           - VALID LOG           : log with valid information
           - API ERROR           : error with esologs api call, retry
           - CONNECTION ERORR    : in case of connection lost during the api-call
           - X TC                : indicating the number of trial closed
           - NO TC               : no trial closed in the log
        """
        self.url = url    # complete url of the log 
        self.code = self.url.split('/')[-1] # code = final chunk of link
        self.request_url=f"https://www.esologs.com/v1/report/fights/{self.code}?api_key={API_KEY}"
        self.status = 'NOT ASSIGNET YET'
        logger.info(f'Analyzing url {self.url}') 
        try:
            self.response = requests.get(self.request_url)
            if self.response.status_code == 200:
                self.is_valid = True
                self.status = 'VALID LOG'
                self.json = self.response.json()
                logger.debug('  Request done with success')
            else:
                raise APIError('Request done, but the log is not valid')
        except APIError:
            logger.critical('  Request done, but the log is not valid (API erorr, status code != 200)')
            self.set_invalid_prop()
            self.status = 'API ERROR'
            return
        except requests.exceptions.ConnectionError:
            logger.critical('  Connection erorr, please retry')
            self.set_invalid_prop()
            self.status = 'CONNECTION ERORR'
            return
        self.owner = self.get_owner()
        self.datetime = self.get_datetime()
        self.datetime_str = self.datetime.strftime('%Y/%m/%d')
        self.title = self.get_title()
        logger.info(f'  Valid log enterd: {self.title} ({self.datetime_str})')
    
    def set_invalid_prop(self):
        self.is_valid = False
        self.json = None
        self.datetime_str = 'n/a'

    def get_datetime(self):
        if self.is_valid:
            start_UNIX = self.json['start'] # getting only the start time
            return datetime.datetime.fromtimestamp(int(start_UNIX)/1000) # datetime

    def get_title(self):
        if self.is_valid:
            return self.json['title']
            
    def get_owner(self):
        if self.is_valid:
            return self.json['owner']

    def get_attendees(self):
        if not self.is_valid:
            return SpecialList([])
        friendlies = self.json['friendlies']
        attendees = []
        logger.info(f'- Analyzing friendlies')
        for friend in friendlies:
            friend_obj = Friendly(friend)
            if friend_obj.is_human and not friend_obj.anonymous:
                attendees.append(friend_obj)
                logger.info(f'  Found attendee (human-friend): {friend_obj.username}')
        if attendees == []:
            logger.warning(f'  No attendees found.')
        return SpecialList(attendees)
    
    def calculate_trials_closed(self):
        
        # Inizialization
        logger.info(f'Analyzing trials closed')
        if not self.is_valid:
            self.attendees = SpecialList([])
            self.trials_closed = SpecialList([])
            logger.warning(f'  Log not valid, no fights found.')
            return
        
        # Get attendees
        self.attendees = self.get_attendees()

        # Get fights
        _fights = self.json['fights']
        fights = [Fight(fight) for fight in _fights]

        # Cross the data
        trials_closed = []
        logger.info(f'- Analyzing fights:')
        for fight in fights:
            winners = []
            if fight.is_final_boss and fight.kill: # compare boss id and if last pull
                for attendee in self.attendees.list:
                    if attendee.partecipated_to(fight.id):
                        winners.append(attendee)
                trial_closed = TrialClosed(fight,SpecialList(winners))
                trials_closed.append(trial_closed)
                logger.info(f'  Found last pull kill: {trial_closed.description}')
        self.trials_closed = SpecialList(trials_closed)

        # Update status
        if self.trials_closed.list:
            self.status = f'{len(self.trials_closed.list)} TC'
        else:
            logger.warning(f'  No fights found.')
            self.status = 'NO TC'


### MAIN           
if __name__ == '__main__':

    # Setting up logging for test phase
    logpath=os.path.join(LOGS_DIR,'logfile_esolgos.log')
    logging.basicConfig(filename=logpath, 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s @%(name)-8s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M')
    logger.info('')
    logger.info('*** Run script esologs_parser.py')

    # TEST 1: Get information on final trial bosses
    print('Comparing zones information:')
    zones_json = Zone.scrape_zone_json() # current values from ESOlogs
    for zone in zones_json:
        name = zone['name']
        zone_obj = Zone(name)            # zones under analysis
        try:
            print(f"   @{name} ({zone_obj.name_short}) the final boss is {zone_obj.final_boss_name} (id = {zone_obj.final_boss_id})")
        except:
            print(f'   This zone will not be analyzed: {zone}')
        
    # TEST 2: Open log & calculate winners
    # no. 2 pull CR     https://www.esologs.com/reports/1BNtTCKAa9HQhGyq
    # no. 1 pull SS     https://www.esologs.com/reports/dZp6g1RhL3KTmJDt
    # no. 0 pull MOL    https://www.esologs.com/reports/2zt4PWF89A6qxcXn

    url01 = 'https://www.esologs.com/reports/1BNtTCKAa9HQhGyq'
    log01 = Log(url01)
    log01.calculate_trials_closed()

    url02 = 'https://www.esologs.com/reports/dZp6g1RhL3KTmJDt'
    log02 = Log(url02)
    log02.calculate_trials_closed()

    url03 = 'https://www.esologs.com/reports/2zt4PWF89A6qxcXn' 
    log03 = Log(url03)
    log03.calculate_trials_closed()

    url04 = 'not_a_valid_url' 
    log04 = Log(url04)
    log04.calculate_trials_closed()