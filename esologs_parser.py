# -----------------------------------------------------------------------------
# Copyright (C) 2024 - M. Cilento
#
# Title: ESOlogs scraper by API V1
# Date of creation: mar-2024
#
# Readocs API V1
#   https://www.esologs.com/v1/docs/#!/Reports/reports_user_userName_get
#
# Examples of requests:
#   Zones (bosses id, see zones.json) 
#       https://www.esologs.com/v1/zones?api_key={API_KEY}
#   Classes 
#       https://www.esologs.com:443/v1/classes?api_key={API_KEY}
#   Fights (@users, kill last boss, difficulties)
#       https://www.esologs.com/v1/report/fights/AjDv37CYqFynXpGc?api_key={API_KEY} 
#
# -----------------------------------------------------------------------------


### IMPORTING
import os, requests, json, datetime, configparser
from bs4 import BeautifulSoup


### GLOBALS
config = configparser.ConfigParser()
config.read('config.ini')
API_KEY = config['ESOLOGS']['API_KEY']
VERBOSE = True


### CLASSES
class Boss:
  
    def __init__(self,zone):
        if   zone in ('Aetherian Archive','AA'):
            self.id   = 4
            self.name = 'The Mage'
        elif zone in ('Hel Ra Citadel','HRC'):
            self.id   = 8
            self.name = 'The Warrior'
        elif zone in ('Sanctum Ophidia','SO'):
            self.id   = 12
            self.name = 'The Serpent'
        elif zone in ('Maw of Lorkhaj','MOL'):
            self.id   = 15
            self.name = 'Rakkhat'
        elif zone in ('The Halls of Fabrication','HOF'):
            self.id   = 20
            self.name = 'Assembly General'
        elif zone in ('Asylum Sanctorium','AS'):
            self.id   = 23
            self.name = 'Saint Olms the Just'
        elif zone in ('Cloudrest','CR'):
            self.id   = 27
            self.name = "Z'Maja"
        elif zone in ('Sunspire','SS'):
            self.id   = 45
            self.name = 'Nahviintaas'
        elif zone in ("Kyne's Aegis",'KA'):
            self.id   = 48
            self.name = 'Lord Falgravn'
        elif zone in ('Rockgrove','RG'):
            self.id   = 51
            self.name = 'Xalvakka'
        elif zone in ('Dreadsail Reef','DSR'):
            self.id   = 54
            self.name = 'Tideborn Taleria'
        elif zone in ("Sanity's Edge",'SE'):
            self.id   = 57
            self.name = 'Ansuul the Tormentor'
        else:
            self.id   = None
            self.name = None
        
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
        elif name in ('The Halls of Fabrication','HOF'):
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
        else:
            self.is_valid = False
            self.name_short = None
            self.final_boss_id   = None
            self.name = None

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
            self.difficulty_suffix = 'HM'
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

    @property
    def summary(self):
        return f"@{self.difficulty_prefix}{self.zone.name_short}{self.difficulty_suffix} - {self.boss_name} (kill = {str(self.kill)})"

    @property
    def name(self):
        return f"{self.difficulty_prefix}{self.zone.name_short}{self.difficulty_suffix}"

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

class Log:
    
    def __init__(self,url):
        self.url = url    # complete url of the log 
        self.code = self.url.split('/')[-1] # code = final chunk of link
        self.request_url=f"https://www.esologs.com/v1/report/fights/{self.code}?api_key={API_KEY}"
        self.response = requests.get(self.request_url)
        if self.response.status_code == 200:
            self.is_valid = True
            self.json = self.response.json()
        else:
            self.is_valid = False
            self.json = None
        self.owner = self.get_owner()
        self.datetime = self.get_datetime()
        self.datetime_str = self.datetime.strftime('%Y/%m/%d')
        self.title = self.get_title()

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
        
    def get_last_pull_kills(self):
        if not self.is_valid:
            return []
        fights = self.json['fights']
        last_pull_kills = []
        if VERBOSE:
            print(f'\nAnalyzing fights for the log {self.url} ({self.datetime_str}):')
        for fight in fights:
            fight_obj = Fight(fight)
            if fight_obj.is_final_boss and fight_obj.kill: # compare boss id and if last pull
                last_pull_kills.append(fight_obj)
                if VERBOSE:
                    print(f'   Found successful last pull kill: {fight_obj.summary}')
        return last_pull_kills
    
    def get_human_friendlies(self):
        if not self.is_valid:
            return []
        friendlies = self.json['friendlies']
        human_friendlies = []
        if VERBOSE:
            print(f'\nAnalyzing friendlies for the log {self.url} ({self.datetime_str}):')
        for friend in friendlies:
            friend_obj = Friendly(friend)
            if friend_obj.is_human and not friend_obj.anonymous:
                human_friendlies.append(friend_obj)
                if VERBOSE:
                    print(f'   Found friend: {friend_obj.username}')
        return human_friendlies
    
    def calculate_list_winners(self):
        self.last_pull_kills = self.get_last_pull_kills()
        self.human_friendlies = self.get_human_friendlies()
        list_winners=[]
        print(f'\nCalculating winners (partecipants to a successful last pull kill) for the log {self.url} ({self.datetime_str}):')
        for fight in self.last_pull_kills:
            _humans = []
            for human in self.human_friendlies:
                if human.partecipated_to(fight.id):
                    _humans.append(human)
            list_winners.append({'description':f"{fight.name} by {', '.join([a.username for a in _humans])}",
                                 'fight':fight,
                                 'partipants':_humans,})
            print(f"   Summary: {list_winners[-1]['description']}")
        
        self.list_winners = list_winners
        if self.list_winners == []:
            print('   Not valid last pull kills found in this log')


### MAIN           
if __name__ == '__main__':
    
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
            
    log01 = Log('https://www.esologs.com/reports/1BNtTCKAa9HQhGyq')
    log01.calculate_list_winners()

    log02 = Log('https://www.esologs.com/reports/dZp6g1RhL3KTmJDt')
    log02.calculate_list_winners()

    log03 = Log('https://www.esologs.com/reports/2zt4PWF89A6qxcXn')
    log03.calculate_list_winners()