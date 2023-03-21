from typing import Optional

import discord
from discord import Embed

from roller_bot.items.models.item import Item
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User


class TradeEmbed(Embed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item: Item,
            quantity: int,
            price: int,
            *,
            title: Optional[str] = None,
            description: Optional[str] = None,
            color: Optional[discord.Color] = None,
            author: Optional[discord.User] = None,
            trade_item: Optional[ItemData] = None,
    ):
        super().__init__(
                title=title if title else 'Trade',
                description=description if description else
                f'{user.mention} wants to trade {quantity} {item.name} to {other_user.mention} for {price}  credits.',
                color=color if color else discord.Color.blue()
        )
        if author:
            self.set_author(name=author.display_name, icon_url=author.display_avatar)
        self.add_field(name='Seller', value=user.mention)
        self.add_field(name='Buyer', value=other_user.mention)
        self.add_field(name='Item', value=f'{quantity} {item.name}')
        self.add_field(name='Price', value=f'{price} credits')
        if trade_item:
            self.add_field(name='Health', value=trade_item.health)


class AcceptedTradeEmbed(TradeEmbed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item: Item,
            quantity: int,
            price: int,
            *,
            author: Optional[discord.User] = None,
            trade_item: Optional[ItemData] = None
    ) -> None:
        super().__init__(
                user,
                other_user,
                item,
                quantity,
                price,
                title="Trade - Accepted",
                description=f"{other_user.mention} accepted the trade with {user.mention}.",
                color=discord.Color.green(),
                author=author,
                trade_item=trade_item
        )


class DeclinedTradeEmbed(TradeEmbed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item: Item,
            quantity: int,
            price: int,
            *,
            author: Optional[discord.User] = None,
            trade_item: Optional[ItemData] = None
    ) -> None:
        super().__init__(
                user,
                other_user,
                item,
                quantity,
                price,
                title="Trade - Declined",
                description=f"{other_user.mention} declined the trade with {user.mention}.",
                color=discord.Color.red(),
                author=author,
                trade_item=trade_item
        )


class TimedOutTradeEmbed(TradeEmbed):
    def __init__(
            self,
            user: User,
            other_user: User,
            item: Item,
            quantity: int,
            price: int,
            *,
            author: Optional[discord.User] = None,
            trade_item: Optional[ItemData] = None
    ) -> None:
        super().__init__(
                user,
                other_user,
                item,
                quantity,
                price,
                title="Trade - Timed out",
                description=f"The trade with {user.mention} has timed out.",
                color=discord.Color.red(),
                author=author,
                trade_item=trade_item
        )
