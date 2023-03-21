import discord

from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage


async def use(item_data: ItemData, user: User, interaction: discord.Interaction) -> ResponseMessage:
    item = item_data.item
    response = ResponseMessage(interaction, item.name, user=interaction.user)
    # Get item from user
    if user.has_item(item.id):
        response.send("You don't have a Reroll Token in your inventory.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Check if we already have a reroll active
    if user.can_roll_again:
        response.send("You already have a reroll active.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Remove the health from the item
    item_data.health -= item.use_cost

    # Set the user's can_roll_again to True
    user.can_roll_again = True

    # Check and remove the item if health is 0 or less
    if item.health <= 0:
        # remove quantity and reset health to start_health
        # noinspection PyTypeChecker
        user.remove_item(item_data.id)
        response.send("Your Reroll Token broke and was removed from your inventory. You can now roll again")
        return await response.send_interaction()

    response.send("You can now roll again")
    return await response.send_interaction()
