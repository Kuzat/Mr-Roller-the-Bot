from typing import Optional

import discord
from discord import Embed

from roller_bot.models.user import User
from roller_bot.utils.assets_resolvers import AssetsResolvers, Trophies


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
            self.thumbnail_file = AssetsResolvers.resolve_trophy_asset(Trophies(position))
            self.set_thumbnail(url=f'attachment://{self.thumbnail_file.filename}')
        else:
            self.thumbnail_file = AssetsResolvers.resolve_trophy_asset(Trophies.first)
            self.set_thumbnail(url=f'attachment://{self.thumbnail_file.filename}')
