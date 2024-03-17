#  ESOlogs-counter
This project aims to develop a software infrastructure to handle the history of logs (retrieved by [esologs.com](https://www.esologs.com)) in a Elder Scrolls Online guild/community. In less words, its main purpose is to account for every user the number of trials closed succesfully. In this way, guild masters may have an useful tool to organize guild roles and check unactive users.

### Current architecture
The project is supposed to be implemented only for a local guild: large scale deployments are not planned yet. If you want to use this software for your guilds, clone the project and autenticate to your google sheet as reported [here](https://docs.gspread.org/en/latest/oauth2.html) following 'Service Account' procedure.

Its raw architecture is herebelow sketched:
* Routine that scrapes a local text file with copy-pasted chat messages containing esologs.com links:
```
:: If a txt holds the link, run in the project folder
python main.py from_local_file local.txt
```
* Google sheet database via [gspread](https://docs.gspread.org/en/latest/index.html) to store the output of the scrape
* A discord bot that constantly keeps an eye on the eso-logs discord chat for new logs to scrape

### Tips
It is highly recommended to store the console output when dealing with many historical logs.
```
:: To write on a file the console output, run
python main.py > output.txt
:: or even
python main.py from_local_file local.txt > output.txt
```
Console output can be really helpful when dealing with high number of logs, since google API has limited number of requests (60 requests/min) and the process may take a while.

### License
This repository is licensed under [MIT License](LICENSE) (c) 2024 GitHub, Inc.