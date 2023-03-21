import discord
from discord import Embed


class UseResultEmbed(Embed):
    def __init__(
            self,
            message: str,
            item_name: str,
            user: discord.User = None
    ):
        super().__init__(
                title=item_name,
                description=str(message),
                color=discord.Color.blue()
        )
        self.set_author(name=user.name, icon_url=user.display_avatar)  # TODO: Add image for items
