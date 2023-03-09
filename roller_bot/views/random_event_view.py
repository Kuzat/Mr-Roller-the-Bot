from typing import Protocol

import discord
from discord.ui import View


class RandomEventData(Protocol):
    action_items: list[discord.ui.Item]
    event_timeout: int

    async def on_timeout(self) -> None:
        ...


class RandomEventView(View):
    def __init__(self, random_event_data: RandomEventData):
        super().__init__()
        # Add all action button to the view
        for action_item in random_event_data.action_items:
            self.add_item(action_item)

        self.timeout = random_event_data.event_timeout
        self.on_timeout = random_event_data.on_timeout
