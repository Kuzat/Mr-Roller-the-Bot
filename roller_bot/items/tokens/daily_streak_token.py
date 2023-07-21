from roller_bot.items.models.bonus import Bonus


class DailyStreakToken(Bonus):
    id = 5

    def __init__(self):
        super().__init__()
        self.name: str = "Daily Streak Token"
        self.description: str = ("A token that gives a bonus as long as you keep your daily rolling streak going. Starts at +1 and goes up to +3."
                                 "The token will break if you miss a day.")
        self.cost: int = 0
        self.sell_cost: int = 5
        self.start_health: int = 100
        self.use_cost: int = 100

        self.own_multiple: bool = True
        self.buyable: bool = False

        # Bonus parameters
        self.max_bonus_value: int = 3
        self.start_bonus_value: int = 0

    def __repr__(self) -> str:
        return f'DailyStreakToken(id={self.id}, name={self.name}, description={self.description}, cost={self.cost})'
