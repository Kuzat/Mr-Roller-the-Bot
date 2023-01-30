import discord
from discord import Embed

from roller_bot.items.models.item import Item


class UserInfoEmbed(Embed):
    def __init__(
            self,
            author: discord.User,
            message: str,
    ):
        super().__init__(
                title=message,
                color=discord.Color.blue()
        )
        self.set_author(name=author.name, icon_url=author.avatar)
