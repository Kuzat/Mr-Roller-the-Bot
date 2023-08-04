from roller_bot.items.models.dice import Dice

class CrackedD30Dice(Dice):
    def __init__(self):
        self.id = 10
        self.name = "Cracked D30 Dice"
        self.min_roll = 1
        self.max_roll = 30
        self.description = "A cracked D30 dice. It's a bit unreliable..."
        self.cost = 300
        self.sell_cost = 20
        self.start_health = 100
        self.use_cost = 10
        self.own_multiple = True
        self.buyable = False

    def roll_again(self, last_roll):
        # Override the roll_again method to implement the behavior of the cracked D30 dice
        return last_roll == self.max_roll