from typing import Optional

import discord
from discord import Embed

from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User


class TradeEmbed(Embed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item_data: ItemData,
            price: int,
            *,
            title: Optional[str] = None,
            description: Optional[str] = None,
            color: Optional[discord.Color] = None,
            author: Optional[discord.User] = None,
    ):
        super().__init__(
                title=title if title else 'Trade',
                description=description if description else
                f'{user.mention} wants to trade {item_data.item.name} to {other_user.mention} for {price} credits.',
                color=color if color else discord.Color.blue()
        )
        if author:
            self.set_author(name=author.display_name, icon_url=author.display_avatar)
        self.add_field(name='Seller', value=user.mention)
        self.add_field(name='Buyer', value=other_user.mention)
        self.add_field(name='Item', value=f'{item_data.item.name}')
        self.add_field(name='Price', value=f'{price} credits')
        self.add_field(name='Health', value=item_data.health)


class AcceptedTradeEmbed(TradeEmbed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item_data: ItemData,
            price: int,
            *,
            author: Optional[discord.User] = None,
    ) -> None:
        super().__init__(
                user,
                other_user,
                item_data,
                price,
                title="Trade - Accepted",
                description=f"{other_user.mention} accepted the trade with {user.mention}.",
                color=discord.Color.green(),
                author=author,
        )


class DeclinedTradeEmbed(TradeEmbed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item_data: ItemData,
            price: int,
            *,
            author: Optional[discord.User] = None,
    ) -> None:
        super().__init__(
                user,
                other_user,
                item_data,
                price,
                title="Trade - Declined",
                description=f"{other_user.mention} declined the trade with {user.mention}.",
                color=discord.Color.red(),
                author=author,
        )


class TimedOutTradeEmbed(TradeEmbed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item_data: ItemData,
            price: int,
            *,
            author: Optional[discord.User] = None,
    ) -> None:
        super().__init__(
                user,
                other_user,
                item_data,
                price,
                title="Trade - Timed out",
                description=f"The trade with {user.mention} has timed out.",
                color=discord.Color.red(),
                author=author,
        )
