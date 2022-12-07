import discord
from discord.ext import commands
import random
import sqlite3
import logging
from datetime import datetime, timedelta


class RollerBot:
  def __init__(self):
      # Create a new database if it does not exist
      self.conn = sqlite3.connect('rolls.db')
      self.c = self.conn.cursor()

      # Create a table for storing user rolls
      self.c.execute('''CREATE TABLE IF NOT EXISTS rolls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                roll INTEGER
              )''')

      # Save the changes to the database
      self.conn.commit()

  def __str__(self):
      return 'RollerBot'
  
  # Return a list of all users in the database that has not rolled on a given date
  def get_users_to_roll(self, date: str) -> list:
    self.c.execute('''SELECT DISTINCT user_id FROM rolls''')
    all_users = self.c.fetchall()

    self.c.execute('''SELECT DISTINCT user_id FROM rolls WHERE date=?''', (date,))
    rolled_users = self.c.fetchall()
    return [user for user in all_users if user not in rolled_users]

  # check if user has rolled a specific number on the given date
  def has_rolled(self, user_id: str, date: datetime.date, roll: int) -> bool:
    self.c.execute('''SELECT * FROM rolls WHERE user_id=? AND date=? AND roll=?''',
              (user_id, date, roll))
    return self.c.fetchone() is not None

  def roll(self, user_id: str, date = datetime.now().date()) -> int:
    # roll a random number between 1 and 6 and insert it into the database anbd return it
    roll = random.randint(1, 6)
    self.c.execute('''INSERT INTO rolls (user_id, date, roll) VALUES (?,?,?)''',
              (user_id, date, roll))
    self.conn.commit()

    return roll

  # get latest roll for given date
  def get_roll(self, user_id: str, date: datetime.date) -> int:
    self.c.execute('''SELECT roll FROM rolls WHERE user_id=? AND date=? ORDER BY id DESC LIMIT 1''',
              (user_id, date))

    # if the user has not rolled on the given date, return 0
    result = self.c.fetchone()
    if result is None:
      return 0
    return result[0]

  # get the total amount rolled b the user up to a given date
  def get_total(self, user_id: str, date: datetime.date) -> int:
    self.c.execute('''SELECT SUM(roll) FROM rolls WHERE user_id=? AND date<=?''',
              (user_id, date))
              
    # if the user has not rolled on the given date, return 0
    result = self.c.fetchone()
    if result is None:
      return 0
    return result[0]

  # get the longest streak of 6s rolled by the user up to a given date
  def get_longest_streak(self, user_id: str, date: datetime.date) -> int:
    # TODO: Fix this query to get the longest 6s streak for the user
    self.c.execute('''SELECT MAX(streak) FROM (SELECT user_id, date, roll, SUM(roll) OVER (PARTITION BY user_id ORDER BY date) AS streak FROM rolls) WHERE roll=6 AND date<=? AND user_id=?''',
              (date, user_id))
    
    # if the user has no streaks of 6s, return 0
    result = self.c.fetchone()
    if result is None:
      return 0
    return result[0]

  # delete roll for a given date for a user
  def delete_roll(self, user_id: str, date: datetime.date):
    self.c.execute('''DELETE FROM rolls WHERE user_id=? AND date=?''',
              (user_id, date))
    self.conn.commit()

# Set the logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)

rollerBot = RollerBot()

# Specify the intents that the bot will be able to access
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def today(ctx):
  users_not_rolled = rollerBot.get_users_to_roll(datetime.now().date())
  if len(users_not_rolled) == 0:
    await ctx.send('Everyone has rolled today! If you have not rolled before, roll with !roll.')
    return

  # TODO: Add a function to get user from id and print mention string

  user_mentions = [bot.get_user(int(user[0])) for user in users_not_rolled]
  await ctx.send(f'Users that have not rolled today: {", ".join(map(lambda x: x.mention, user_mentions))}')

@bot.command()
async def roll(ctx):
    user_id = str(ctx.message.author.id)

    # Check what the user has rolled today
    todays_roll = rollerBot.get_roll(user_id, datetime.now().date())

    logging.debug(f'Todays roll: {todays_roll} for user {user_id}')

    if todays_roll == 0 or todays_roll == 6:
      roll = rollerBot.roll(user_id, datetime.now().date())
      total = rollerBot.get_total(user_id, datetime.now().date())
      #longest_streak = rollerBot.get_longest_streak(user_id, datetime.now().date())
      if roll == 6:
        await ctx.send(f'You rolled a {roll}! You can roll again!')
      else:
        await ctx.send(f'You rolled a {roll}. Your total amount rolled is {total}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.')
    else:
      total = rollerBot.get_total(user_id, datetime.now().date())
      await ctx.send(f'You rolled a {todays_roll}. Your total amount rolled is {total}. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.')

bot.run('TOKEN')
