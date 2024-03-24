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
# Standard library imports
import sys, logging, configparser
from datetime import datetime
from pytz import timezone

# Project library imports
from esologs.esologs_parser import *
from esologs.url_scraper import *
from database.database import *

# Third-party library imports
import nextcord
from nextcord.ext import commands, tasks
from nextcord.ui.select import string


### GLOBALS
config = configparser.ConfigParser()
config.read('config.ini')

# Guild
DEVELOPER_ID = config['GUILD']['DEVELOPER_ID']
ADMIN_ID = config['GUILD']['ADMIN_ID']
LIST_OF_ADMINS = [DEVELOPER_ID,ADMIN_ID]
SERVER_ID = config['GUILD']['SERVER_ID']
CHANNEL_ID = config['GUILD']['CHANNEL_ID']
LINK_TO_CHANNEL = f"https://discord.com/channels/{SERVER_ID}/{CHANNEL_ID}"

# Timezone
TIMEZONE = timezone('Europe/Rome') # Set for logging
LOCAL_TIME_NOW = datetime.datetime.now(TIMEZONE).astimezone() # Get tz info for nextcord
TASK_LOOP_TIME = datetime.time(hour=5, minute=0, tzinfo=LOCAL_TIME_NOW.tzinfo)


### LOGGER
logger = logging.getLogger(__name__)
logging.Formatter.converter = lambda *args: datetime.datetime.now(tz=TIMEZONE).timetuple()
logging.basicConfig(filename='logs/logfile.log', 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s @%(name)-22s: %(message)s',
                    datefmt='%Y/%m/%d %H:%M')


### METHODS
# Core operations
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

def process_logs_in_db():
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

# Discord bot
intents = nextcord.Intents(messages=True, guilds=True)
intents.message_content = True
bot = commands.Bot(intents=intents)

async def has_permissions(interaction):
    permission_bool = False
    # Check if the bot has the necessary permissions in the channel
    if type(interaction.channel) == nextcord.PartialMessageable:
        permission_bool = False
    else:
        permission_bool = interaction.channel.permissions_for(interaction.guild.me).send_messages  # required authorization to send messages
    if permission_bool is False:
        await interaction.followup.send("🚫 I'm unable to send messages in this realm. Kindly ask the server's admin and ensure that the 'Send Messages' privilege is given to me and to my honored role in this channel ⚔️🏹")  # followup is webhook, so it can be sent
        return permission_bool  # bool
    
@bot.event
async def on_ready():
    num_logs = LogDataBase().num_logs
    print(f"{bot.user} bot is handling {num_logs} logs for Assassin's Souls")
    print('------------------------------------------------------------------')
    scheduled_message_routine.start()
    await bot.change_presence(activity=nextcord.CustomActivity(name=f"""Handling {num_logs} logs for the Assassin's Souls"""))

@bot.event
async def on_message(message):
    if message.guild.id == int(SERVER_ID) and message.channel.id == int(CHANNEL_ID) and message.author != bot.user:
        logger.info(f"{message.author} typed: {message.content}")
        urls = extract_esologs_urls_from_str(message.content)
        if urls:
            num_urls = len(urls)
            logger.info('Found valid urls, load_logs procedure started')
            for url in urls:
                log = Log(url)
                LogDataBase().append_log(   log.datetime_str,       # A - timestamp
                                            log.title,              # B - title
                                            log.owner,              # C - owner
                                            log.code,               # D - code
                                            log.url,                # E - url
                                            log.get_attendees().str)# I - attendees
            logs_worksheet_url = LogDataBase().url_to_worksheet
            await message.reply(f"""
Valid log(s) found! Thank you {message.author} 🙏🏻
I have updated the [logs-database]({logs_worksheet_url}) 💾
""",suppress_embeds=True)

@bot.slash_command(name='help', description="Get help on how I may help you")
async def help(interaction: nextcord.Interaction):
    await interaction.response.defer()
    logger.info(f'{interaction.user.name} invoked /help')
    await interaction.followup.send(f"""
👋 Greetings! I'm *{bot.user}* bot, here to account trials attendances in the guild analyzing [esologs.com](https://www.esologs.com/) urls!
Click [here](https://github.com/MCilento93/esologs-counter/blob/main/README.md) for my README 📜

**How I Help:**
I will keep track of all trials in the chat {LINK_TO_CHANNEL}.
**</show_rank:1221026522983436301>:** Use me to get the update rank of the community
**</process_logs:1221026519745429585>:** With this function I will calculate unprocessed logs (if any)

Stay ahead with the rank. Happy gaming! ⚔️👑🏹
""",suppress_embeds=True)

@bot.slash_command(name='show_rank',description='Print updated rank of the guild')
async def show_rank(interaction: nextcord.Interaction):
    await interaction.response.defer()
    logger.info(f'{interaction.user.name} invoked /show_rank')

    # Check Permissions
    permission_bool = await has_permissions(interaction)
    if permission_bool is False:
        return

    # Get table from database
    table_ascii = RankDataBase().get_ascii_table()
    rank_worksheet_url = RankDataBase().url_to_worksheet

    # Send reply
    if table_ascii:
        await interaction.followup.send(f"**Updated rank of the trials 🏆**```\n{table_ascii}\n```\n🧮 Click [here]({rank_worksheet_url}) for full table",suppress_embeds=True)
    else:
        logger.error('Empty *rank* database ... null data fetched in /show_rank slash command')
        await interaction.followup.send(f"🙇‍♀️ Rank is empty, check [database]({rank_worksheet_url}) and inform admins")

@bot.slash_command(name='process_logs',description='Calculate unprocessed logs from database')
async def process_logs(interaction: nextcord.Interaction):
    await interaction.response.defer()
    logger.info(f'{interaction.user.name} invoked /process_logs')

    # Check Permissions
    permission_bool = await has_permissions(interaction)
    if permission_bool is False:
        return

    # Update rank database
    if interaction.user.id in LIST_OF_ADMINS+[interaction.guild.owner_id]:
        message = f'  process_logs_in_db() starting ...'
        print(message)
        logger.info(message)
        process_logs_in_db()
        await interaction.followup.send(f"✅ Rank updated")
    else:
        await interaction.followup.send(f"🚫 You don't have permissions for update the rank")
        logger.error('  Something went wrong. Check logs')
    return

@tasks.loop(time=TASK_LOOP_TIME)
async def scheduled_message_routine():
    print('\nDaily routine for esologs-counter bot...')

    # Update presence
    num_logs = LogDataBase().num_logs
    await bot.change_presence(activity=nextcord.CustomActivity(name=f"""Handling {num_logs} logs for the Assassin's Souls"""))


### MAIN 
if __name__ == '__main__':

    args = sys.argv
    if len(args) == 1:
        print('No arguments given, run properly the software')
    # RUN PROCEDURE 1: analize locally the logs from local file (without saving results)
    elif args[1] == 'analyze_logs_from_file':
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
        process_logs_in_db()
        logger.info('*** END OF process_logs PROCEDURE')
    elif args[1] == 'discord':
    # RUN PROCEDURE 4: main with discord bot
        logger.info('')
        logger.info('*** RUN PROCEDURE: Discord bot')
        logger_discord = logging.getLogger('nextcord') # setup parallel log for nextcord
        logger_discord.setLevel(logging.CRITICAL)
        handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s @%(name)-23s: %(message)s',
                                               '%Y/%m/%d %H:%M'))
        logger_discord.addHandler(handler)
        bot.run(config['DISCORD']['TOKEN'])
        logger.info('*** END OF process_logs PROCEDURE')