
from datetime import datetime
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from roller_bot.database import RollDatabase
from roller_bot.models.item_data import ItemData
from roller_bot.models.roll import Roll
from roller_bot.models.user import User


def migrate():
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    db = RollDatabase('rolls_v1.db')
    session = db.session

    # Load old database data into new database
    old_engine = create_engine('sqlite:///rolls_v0.db')
    Session = sessionmaker(bind=old_engine)
    old_session = Session()

    # Move old users to new users
    old_users = old_session.execute('SELECT * FROM users')

    for row in old_users:
        print(f"user: {row}")
        # Create a user for each unique user_id
        user = User(**row)
        user.created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S.%f') # type: ignore
        print(user)
        # Add the users to the new database
        session.add(user)

    # Move old items
    old_items = old_session.execute('SELECT * FROM items')

    for row in old_items:
        print(f"item: {row}")
        # Create a user for each unique user_id
        item = ItemData(**row)
        item.purchased_at = datetime.strptime(row['purchased_at'], '%Y-%m-%d').date() # type: ignore
        print(item)
        # Add the users to the new database
        session.add(item)

    # Move old rolls with default value for can_roll_again
    old_rolls = old_session.execute('SELECT * FROM rolls')

    for row in old_rolls:
        print(f"roll: {row}")
        # Create a user for each unique user_id
        roll = Roll(**row)
        roll.can_roll_again = False # type: ignore
        roll.date = datetime.strptime(row['date'], '%Y-%m-%d').date() # type: ignore
        print(roll)
        # Add the users to the new database
        session.add(roll)

    session.commit()
