from typing import List, Optional, Protocol

import discord

from roller_bot.embeds.random_event_embed import RandomEventEmbed


class RandomEvent(Protocol):
    action_items: List[discord.ui.Item]
    event_timeout: int
    embed: RandomEventEmbed
    message: Optional[discord.Message]

    async def on_timeout(self) -> None:
        ...
