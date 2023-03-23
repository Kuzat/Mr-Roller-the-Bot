import discord

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.actions import box_action, daily_streak_token_action, dice_action, reroll_token_action
from roller_bot.items.dice.box.old_pizza_box import OldPizzaBox
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken
from roller_bot.items.tokens.reroll_token import RerollToken
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User


async def item_action(item_data: ItemData, user: User, interaction: discord.Interaction, bot: DatabaseBot) -> None:
    match item_data.item.id:
        case DailyStreakToken.id:
            await daily_streak_token_action.use(item_data, user, interaction)
        case RerollToken.id:
            await reroll_token_action.use(item_data, user, interaction)
        case OldPizzaBox.id:
            await box_action.use(item_data, user, interaction)
        case _:
            await dice_action.use(item_data, user, interaction, bot)