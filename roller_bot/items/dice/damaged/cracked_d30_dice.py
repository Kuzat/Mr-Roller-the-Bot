from roller_bot.items.models.dice import Dice

class CrackedD30Dice(Dice):
    id = 9
    name = "Cracked D30 Dice"
    min_roll = 1
    max_roll = 30
    description = "A cracked D30 dice. It's a bit unreliable..."
    cost = 300
    sell_cost = 20
    start_health = 100
    use_cost = 10
    own_multiple = True
    buyable = True

    def roll_again(self):
        # Override the roll_again method to implement the behavior of the cracked D30 dice
        pass