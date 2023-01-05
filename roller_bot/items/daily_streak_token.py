from datetime import datetime, timedelta

from roller_bot.items.item import Item
from roller_bot.models.bonus import Bonus
from roller_bot.models.pydantic.bonus_value import BonusValue
from roller_bot.models.user import User


class DailyStreakToken(Item):
    id = 5

    def __init__(self):
        super().__init__()
        self.name: str = "Daily Streak Token"
        self.description: str = ("A token that gives a bonus as long as you keep your daily rolling streak going. Starts at +1 and goes up to +3."
                                 "The token will break if you miss a day.")
        self.cost: int = 0
        self.start_health: int = 100
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

        # Bonus parameters
        self.max_bonus_value: int = 3
        self.start_bonus_value: int = 0

    def __repr__(self) -> str:
        return f'DailyStreakToken(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'

    def bonus(self, user: User) -> BonusValue:
        """
        Calculate the bonus value for the user and if it is still active or need to be changed.

        :param user: a user
        :return: the bonus value
        """
        today = datetime.now().date()
        # Get the bonus from the user
        bonus = user.bonuses.get(self.id)
        if bonus is None:
            return BonusValue(value=0, active=False, message="You don't have a Daily Streak Token bonus active.")

        # Check if we lost the streak
        # Check that they have not a roll from yesterday, and it is not the first day of the bonus
        if bonus.started_at != datetime.now().date() and user.get_roll_on_date(today - timedelta(days=1)) is None:
            # Remove the bonus from the user
            user.bonuses.pop(self.id)
            return BonusValue(value=0, active=False, message="You missed a day and your Daily Streak Token bonus has ended.")

        # Update the bonus value
        bonus.bonus_value = min((today - bonus.started_at).days, self.max_bonus_value)

        # Return the bonus value
        return BonusValue(value=bonus.bonus_value, active=True, message=f"You have a {bonus.bonus_value} bonus from your Daily Streak Token.")

    def use(self, user: User) -> str:
        # Get item from user
        item = user.get_item(self.id)
        if item is None:
            return f"You don't have a {self.name} in your inventory."

        # Check if we already have a streak bonus active
        if user.bonuses.get(item.id):
            return f"You already have a {self.name} bonus active."

        # Add the bonus to the user
        daily_bonus = Bonus(
                user_id=user.id,
                item_id=item.id,
                bonus_value=self.start_bonus_value,
                started_at=datetime.now().date(),
        )
        user.bonuses[daily_bonus.item_id] = daily_bonus

        # Remove the health from the item
        item.health -= self.use_cost

        # Check and remove the item if health is 0 or less
        if item.health <= 0:
            # remove quantity and reset health to start_health
            item.quantity -= 1
            item.health = self.start_health
            return f"Your {self.name} broke and was removed from your inventory. You will now get a bonus as long as you keep your daily rolling streak going."

        return "You will now get a bonus as long as you keep your daily rolling streak going."
