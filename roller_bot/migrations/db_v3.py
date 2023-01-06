from datetime import datetime
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from roller_bot.database import RollDatabase
from roller_bot.models.items import Items
from roller_bot.models.roll import Roll
from roller_bot.models.user import User


def migrate():
    """
    Migrate the database from version 2 to version 3
    New in v3:
    - Added the bonus table to the database
    - Added a relationship between the user and the bonus table
        - Should not need to do any migration for this

    :return:
    """
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    db = RollDatabase('rolls_v3.db')
    session = db.session

    # Load old database data into new database
    old_engine = create_engine('sqlite:///rolls_v2.db')
    Session = sessionmaker(bind=old_engine)
    old_session = Session()

    # Move old users to new users
    old_users = old_session.execute('SELECT * FROM users')

    for row in old_users:
        print(f"user: {row}")
        # Create a user for each unique user_id
        user = User(**row)
        user.created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S.%f')  # type: ignore
        print(user)
        # Add the users to the new database
        session.add(user)

    # Move old items
    old_items = old_session.execute('SELECT * FROM items')

    for row in old_items:
        print(f"item: {row}")
        # Create a user for each unique user_id
        item = Items(**row)
        item.purchased_at = datetime.strptime(row['purchased_at'], '%Y-%m-%d').date()  # type: ignore
        print(item)
        # Add the users to the new database
        session.add(item)

    # Move old rolls with default value for can_roll_again
    old_rolls = old_session.execute('SELECT * FROM rolls')

    for row in old_rolls:
        print(f"roll: {row}")
        # Create a user for each unique user_id
        roll = Roll(**row)
        roll.date = datetime.strptime(row['date'], '%Y-%m-%d').date()  # type: ignore
        print(roll)
        # Add the users to the new database
        session.add(roll)

    session.commit()
