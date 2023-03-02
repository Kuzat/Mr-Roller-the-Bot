import discord
from discord import Embed

from roller_bot.items.models.item import Item


class UseResultEmbed(Embed):
    def __init__(
            self,
            message: str,
            item: Item,
            user: discord.User = None
    ):
        super().__init__(
                title=item.name,
                description=str(message),
                color=discord.Color.blue()
        )
        self.set_author(name=user.name, icon_url=user.display_avatar)  # TODO: Add image for items
        # self.add_field(name="User", value=user_mention, inline=False)
