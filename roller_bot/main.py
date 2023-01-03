import os
from typing import Optional
from dotenv import load_dotenv
from roller_bot.clients.roller import RollerBot
from roller_bot.database import RollDatabase
from datetime import datetime
from roller_bot.items.dice import DiceRoll

from roller_bot.models.user import User
import logging


def dev():
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    db = RollDatabase(':memory:')
    session = db.session

    # Create users model
    user = User.new_user(1234, datetime.now())
    user2 = User.new_user(4321, datetime.now())

    # Add roll to the user
    user.add_roll(DiceRoll(base=6))
    user.add_roll(DiceRoll(base=5))

    user2.add_roll(DiceRoll(base=6))
    user2.add_roll(DiceRoll(base=6))
    user2.add_roll(DiceRoll(base=3))

    # Add user to the database
    session.add(user)
    session.add(user2)
    session.commit()

    # Query the user from the database
    user_query: Optional[User] = session.query(User).first()
    print(f"user: {user_query}")

    if user_query:
        print(f"rolls: {user_query.rolls}")
        print(f"total rolls: {user_query.total_rolls}")
        print(f"latest roll: {user_query.latest_roll}")

    # Query for the user with the highest total rolls
    total_user_query = (
        session.query(User)
        .order_by(User.total_rolls.desc())
        .first()
    )
    if total_user_query:
        print(f"totalUserQuery: {total_user_query.total_rolls}")


# Run the main bot function
def main(debug_mode: bool = False):
    print('Debug mode:', debug_mode)
    # enable sqlalchemy logging in debug mode
    db_path = 'rolls_v1.db'
    if debug_mode:
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        db_path = 'rolls_v1.db'

    # Load the environment variables from the .env file
    load_dotenv()

    # Start bot
    bot: RollerBot = RollerBot(
        command_prefix='!', db_path=db_path, debug_mode=debug_mode)

    # Run the discord bot
    token: str | None = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        raise ValueError('No token was found in the environment variables')
