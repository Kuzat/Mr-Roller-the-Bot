
from datetime import datetime
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from roller_bot.database import RollDatabase
from roller_bot.items.dice import Dice
from roller_bot.models.items import Items
from roller_bot.models.roll import Roll
from roller_bot.models.user import User


def migrate():
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    db = RollDatabase('rolls_migrated.db')
    session = db.session

    # Load old database data into new database
    old_engine = create_engine('sqlite:///rolls_old.db')
    Session = sessionmaker(bind=old_engine)
    old_session = Session()

    # Create users model
    # result = old_session.execute('SELECT * FROM rolls')

    # # print the results
    # for row in result:
    #     print(f"id: {row['id']}, user_id: {row['user_id']}, date: {row['date']}, roll: {row['roll']}")

    unique_users = old_session.execute('SELECT DISTINCT user_id FROM rolls')

    # print the results
    for row in unique_users:
        print(f"user_id: {row['user_id']}")
        # Create a user for each unique user_id
        user = User.new_user(row['user_id'], datetime.now())


        # Query all the rolls for the user order by id
        user_rolls = old_session.execute(f'SELECT * FROM rolls WHERE user_id = {row["user_id"]} ORDER BY id')
        # Then convert old rolls to new rolls and add them
        for row in user_rolls:
            print(f"id: {row['id']}, user_id: {row['user_id']}, date: {row['date']}, roll: {row['roll']}")
            roll_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            roll = Roll(id=row['id'], user_id=row['user_id'], date=roll_date, roll=row['roll'])
            user.rolls.append(roll)
        
        # Need to find date of first roll
        first_roll_date = user.rolls[0].date
        user.created_at = first_roll_date

        # Then add default item
        user.items[0].purchased_at = first_roll_date

        # Need to find sum of rolls
        user.roll_credit = user.total_rolls # type: ignore

        # Need to find streak of 6s
        longest_streak = 0
        current_streak = 0
        for roll in user.rolls:
            if roll.roll != 6:
                current_streak = 0
            else:
                current_streak += 1
            if current_streak > longest_streak:
                longest_streak = current_streak
        print(f"longest_streak: {longest_streak}")
        user.streak = longest_streak # type: ignore

        # Print user and rolls to verify
        print(f"user: {user}")
        print(f"rolls: {user.rolls}")

        # Add user to the database
        session.add(user)
        session.commit()


