import discord
from discord import Embed


class BonusEmbed(Embed):
    def __init__(
            self,
            bonus_item_name: str,
            message: str,
    ):
        super().__init__(
                description=message,
                color=discord.Color.dark_green()
        )
        self.set_author(name=bonus_item_name)
