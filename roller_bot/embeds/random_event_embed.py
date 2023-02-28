from datetime import datetime

import discord
from discord import Embed


class RandomEventEmbed(Embed):

    def __init__(self, random_event_name: str, random_event_description: str):
        super().__init__(
                description=random_event_description,

                colour=discord.Colour.orange(),

        )
        self.set_author(name=random_event_name)
        self.set_footer(text=f"Event started at {datetime.now().strftime('%H:%M:%S')}")
