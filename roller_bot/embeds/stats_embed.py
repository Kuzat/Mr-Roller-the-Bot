from typing import Optional

import discord
from discord import Embed

from roller_bot.models.user import User


class StatsEmbed(Embed):
    def __init__(
            self,
            author: discord.User,
            user: User,
            position: Optional[int] = None,
    ):
        super().__init__(
                title=f'Stats',
                color=discord.Color.yellow(),
        )
        self.set_author(name=author.name, icon_url=author.avatar)

        self.add_field(
                name='Score',
                value=f'{user.total_rolls}',
        )
        self.add_field(
                name='Total Rolls',
                value=f'{len(user.rolls)}',
        )
        self.add_field(
                name='Average Roll',
                value=f'{user.average_rolls:.2f}',
        )

        if position is not None:
            pass
            # Resolve trophy emoji based on position
        else:
            self.set_thumbnail(url="https://em-content.zobj.net/thumbs/120/apple/325/trophy_1f3c6.png")
