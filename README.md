# Mr roller the bot
This a discord bot that have a daily dice rolling game. Where you can roll a dice once a day and compete with your friends. It was partially written by a AI. 

## Instruction
To run the program you need to first install the dependencies using [poetry](https://python-poetry.org/): `poetry install`. 
You then need to add a `.env` file with the value `DISCORD_TOKEN` with you token from the [discord developer portal](https://discord.com/developers/applications).
You should then be able to run the bot using the command: `poetry run bot`

## After merge to deploy to ec2 server
1. ssh into the server
2. `cd Mr-Roller-the-Bot`
3. `kill $(ps -ef | grep '[r]oller_bot.main' | awk '{print $2}')`
4. `poetry run backup`
5. `git pull`
6. `poetry install`
7. `nohup poetry run bot &`


## TODO
- [ ] Fix the glue items
- [ ] Fix the mirror die
- [ ] Add an item that destroys all daily streak bonuses
- [ ] Add an new box
- [ ] New random event that adds the new box to the shop for a limited time
- [ ] New die that rolls a random number between 1 and 100 once based on your position in the leaderboard
- [ ] Add an item that makes random event more common for an interval
- [ ] Add a die also let you remove your roll value from another player
- [ ] Add a die that let you steal a random item from another player
- [ ] New item that let you half another players roll for the next day
