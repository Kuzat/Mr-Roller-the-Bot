from typing import Any, Callable, Coroutine, List, Optional

import discord

from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User


class ItemOption(discord.SelectOption):
    def __init__(
            self,
            item_data: ItemData,
            label: Optional[str] = None,
            value: Optional[str] = None,
            emoji: Optional[discord.PartialEmoji] = None,
            description: Optional[str] = None,
            default: bool = False,
    ):
        super().__init__(
                label=label if label else item_data.item.name,
                value=value if value else str(item_data.id),
                emoji=emoji,
                description=description,
                default=default,
        )


class UserOption(discord.SelectOption):
    def __init__(
            self,
            user: User,
            label: Optional[str] = None,
            value: Optional[str] = None,
            emoji: Optional[discord.PartialEmoji] = None,
            description: Optional[str] = None,
            default: bool = False,
    ):
        super().__init__(
                label=label if label else user.id,
                value=value if value else user.id,
                emoji=emoji,
                description=description,
                default=default,
        )


class ItemSelect(discord.ui.Select):

    def __init__(
            self,
            item_options: List[ItemOption | UserOption],
            select_callback: Callable[[discord.Interaction, discord.ui.Select], Coroutine[Any, Any, None]],
            placeholder: Optional[str] = None,
            disabled: bool = False,
    ):
        super().__init__(
                placeholder=placeholder,
                options=item_options,
                disabled=disabled,
        )
        self.select_callback = select_callback

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.select_callback(interaction, self)
