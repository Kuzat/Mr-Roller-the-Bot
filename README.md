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
- [x] Fix the glue items - Box 2
- [ ] Fix the mirror die - Shop limited
- [ ] Add an item that destroys all of a type of Bonus - Shop limited
- [ ] New damaged die that rolls a random number between 1 and 100 once based on your position in the leaderboard - Box 2
- [ ] Add a damaged die that let you steal a random item from another player if you hit the reroll - box 2
- [ ] New damaged die that roll between -6 and +30 - Box 3 
- [ ] New damaged d25 dice that roll between 1 and 25 - Box 3
- [ ] New item that let you half another players roll for the next day - box 3
- [ ] Add an item that makes random event more common for an interval - Box 3
- [ ] New item that gives you a bonus to roll twice a day - Box 3
- [ ] New random event that adds a new item to the shop for a limited time
- [ ] New random event TODO
- [ ] Add a damaged die also let you remove your roll value from another player
- [ ] new random event that lets you start a limited tournament where everyone roll a 1 to 100 dice twice, the pot is split between the top 3. Every player that enter contribute to the pot depending on their position in the leaderboard. 
