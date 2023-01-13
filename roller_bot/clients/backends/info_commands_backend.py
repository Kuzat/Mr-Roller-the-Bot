from datetime import date, timedelta
from typing import List

import discord

from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.user import User
from roller_bot.utils.enrichments import add_discord_mention


class InfoCommandsBackend:

    @staticmethod
    async def rolls(interaction: discord.Interaction, rolls_date: date, bot: DatabaseBot) -> None:
        users: List[User] = bot.db.get_all_users()

        message = f'Users that rolled on {rolls_date}:\n'

        # Get the rolls for each user rolls_date
        for user in users:
            user = add_discord_mention(bot, user)
            user_rolls = user.get_all_rolls(rolls_date)
            if len(user_rolls) == 0:
                date_not_rolled = (
                    'today' if rolls_date == date.today() else
                    'yesterday' if rolls_date == date.today() - timedelta(days=1) else
                    rolls_date.strftime('%d-%m-%Y')
                )
                message += f'{user.mention} has not rolled {date_not_rolled}.'
            else:
                rolls_string = '\n'.join(map(lambda x: str(x), user_rolls))
                message += f'{user.mention} rolled: ```\n{rolls_string}\n```'

        await interaction.response.send_message(message, ephemeral=True)
