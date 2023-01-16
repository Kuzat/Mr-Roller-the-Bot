import discord
from discord import Embed

from roller_bot.utils.discord import ResponseMessage


class UseResultEmbed(Embed):
    def __init__(
            self,
            message: ResponseMessage,
            author: discord.User,
    ):
        super().__init__(
                title="Result",
                description=str(message),
                color=discord.Color.gold()
        )
        self.set_author(name=author.display_name, icon_url=author.display_avatar)

