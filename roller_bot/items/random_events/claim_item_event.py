from datetime import datetime
from typing import Optional

import discord

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.embeds.random_event_embed import RandomEventEmbed
from roller_bot.items.models.item import Item
from roller_bot.items.tokens.daily_streak_token import DailyStreakToken
from roller_bot.items.tokens.reroll_token import RerollToken
from roller_bot.items.utils import item_from_id
from roller_bot.models.items import Items
from roller_bot.utils.random_lists import WeightedRandomItemsList, WeightedItem


class ClaimItemEventCreator:
    def __init__(self, bot: DatabaseBot):
        self.bot = bot
        self.random_items_list = WeightedRandomItemsList(
                items=[
                    WeightedItem(item=RerollToken(), weight=10),
                    WeightedItem(item=DailyStreakToken(), weight=1),
                ]

        )

    def create(self) -> 'ClaimItemEvent':
        event_item = self.random_items_list.get_random_item()

        return ClaimItemEvent(event_item, self.bot)


class ClaimItemEvent:
    action_items: list[discord.ui.Item]
    event_timeout: int
    embed: RandomEventEmbed
    message: Optional[discord.Message]

    def __init__(self, event_item: Item, bot: DatabaseBot):
        self.bot = bot
        self.item = event_item
        self.event_timeout = 900

        # Might be different buttons for different events and should be defined by the event definition
        # for now we just have a single hardcoded button for the claim item event
        self.claim_button = discord.ui.Button(label="Claim", style=discord.ButtonStyle.green, emoji="🎁")
        self.claim_button.callback = self.claim_item

        self.trash_button = discord.ui.Button(label="Trash", style=discord.ButtonStyle.red, emoji="🗑️")
        self.trash_button.callback = self.trash_item

        self.action_items = [self.claim_button, self.trash_button]

        self.claimed_user = None
        self.message = None

        self.embed = RandomEventEmbed(
                random_event_name="Random Item Spawn",
                random_event_description=f"A {self.item.name} has spawned in the channel! Quickly claim it before someone else does!"
        )

    async def on_timeout(self) -> None:
        if self.message is None:
            raise Exception(f'View: {self} has no message to edit at timeout.')

        if self.claimed_user is not None:
            # If the item has been claimed, we don't need to do anything
            return

        random_event_embed = self.message.embeds[0]
        random_event_embed.description = f'Item spawn of {self.item.name} vanished before anyone could claim it. ⚰️⏱️'
        random_event_embed.set_footer(text=f'{random_event_embed.footer.text} and event ended at {datetime.now().strftime("%H:%M:%S")}')
        await self.message.edit(embed=random_event_embed, view=None)

    async def trash_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        # Check if the item has already been claimed
        if self.claimed_user is not None:
            if user != self.claimed_user:
                return await interaction.response.send_message('This item has already been claimed.', ephemeral=True, delete_after=60)

        # lock the item to the user
        self.claimed_user = user

        random_event_embed = interaction.message.embeds[0]
        random_event_embed.description = f'Item spawn of {self.item.name} was trashed by {user.mention}! 🗑️📦'
        random_event_embed.set_footer(text=f'{random_event_embed.footer.text} and event ended at {datetime.now().strftime("%H:%M:%S")}')
        await interaction.message.edit(embed=random_event_embed, view=None)

    async def claim_item(self, interaction: discord.Interaction) -> None:
        user = await UserVerificationBackend.verify_interaction_user(interaction, self.bot)

        # Check if the item has already been claimed
        if self.claimed_user is not None:
            if user != self.claimed_user:
                return await interaction.response.send_message('This item has already been claimed.', ephemeral=True, delete_after=60)

        # lock the item to the user
        self.claimed_user = user

        item = item_from_id(self.item.id)
        if item is None:
            await interaction.response.send_message('That item does not exist.', ephemeral=True, delete_after=60)
            return

        # Check that the item is able to be owned multiple times
        if not item.own_multiple:
            await interaction.response.send_message('You cannot own multiple of that item.', ephemeral=True, delete_after=60)
            return

        # Check again that the item is not claimed by another user
        if self.claimed_user != user:
            await interaction.response.send_message('This item has already been claimed.', ephemeral=True, delete_after=60)
            return

        # Get the user's owned item
        user_owned_item = user.get_item(item.id)
        # Add the item to the user's inventory
        if not user_owned_item:
            user.items.append(
                    Items(
                            item_id=item.id, user_id=user.id,
                            quantity=1, purchased_at=datetime.now()
                    )
            )
        elif item.own_multiple and user_owned_item:
            # If they can own multiple of the same item, increment the quantity
            user_owned_item.quantity += 1
        else:
            raise Exception(f'Could not add or increase item quantity for item {item.id} for user {user.id}')

        # Commit the changes to the database
        self.bot.db.commit()

        # Update the message
        random_event_embed = interaction.message.embeds[0]
        random_event_embed.description = f'Item spawn of {item.name} claimed by {user.mention}! 🎉🎁'
        random_event_embed.set_footer(text=f'{random_event_embed.footer.text} and event ended at {datetime.now().strftime("%H:%M:%S")}')
        await interaction.message.edit(embed=random_event_embed, view=None)
