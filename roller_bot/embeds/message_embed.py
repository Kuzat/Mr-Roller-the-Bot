from typing import Optional

import discord
from discord import Embed


class MessageEmbed(Embed):
    def __init__(
        self,
        author: Optional[discord.User],
        title: Optional[str],
        message: Optional[str],
    ):
        super().__init__(
            title=title, description=message, color=discord.Color.dark_blue()
        )
        if author:
            self.set_author(name=author.name, icon_url=author.avatar)
