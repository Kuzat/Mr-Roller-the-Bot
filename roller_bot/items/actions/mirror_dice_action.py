from datetime import datetime, timedelta

import discord
from discord import ButtonStyle, Embed
from discord.ui import Button

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.items.actions.bonus_action import calculate_bonus
from roller_bot.models.item_data import ItemData
from roller_bot.models.roll import Roll
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage
from roller_bot.views.select_item_view import SelectItemView


async def use(item_data: ItemData, user: User, interaction: discord.Interaction, bot: DatabaseBot) -> None:
    item = item_data.item
    response = ResponseMessage(interaction, item.name, user=interaction.user)

    # Get the item from the user
    # noinspection PyTypeChecker
    user_owned_item = user.get_item_data(item_data.id)
    if not user_owned_item:
        response.send(f"You don't have a {item.name} in your inventory.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Check if we can roll
    if not user.can_roll():
        response.send(f"You already rolled a {user.latest_roll.base_value} today. Roll again tomorrow on {datetime.now().date() + timedelta(days=1)}.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Send the embed message describing the item
    info_embed = Embed(description=f"You rolled a {item.name}! You must select a user to mirror their previous roll.")
    info_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)

    # Make the positive button
    positive_button = Button(
            label="Mirror Roll",
            style=ButtonStyle.green,
    )

    async def positive_callback(callback_interaction: discord.Interaction, selected_user_id: int) -> None:
        callback_response = ResponseMessage(callback_interaction, item.name, user=callback_interaction.user)
        click_user = await UserVerificationBackend.verify_interaction_user(callback_interaction, bot)
        if click_user != user:
            await callback_interaction.response.send_message('You cannot use items for another user.', ephemeral=True, delete_after=60)
            return

        # Get the user to mirror
        user_to_mirror = bot.db.get_user(selected_user_id)
        if not user_to_mirror:
            await callback_interaction.response.send_message('That user does not exist.', ephemeral=True, delete_after=60)
            return

        # Get the last roll of the user to mirror
        last_roll = user_to_mirror.latest_roll
        if not last_roll:
            await callback_interaction.response.send_message('That user has not rolled yet.', ephemeral=True, delete_after=60)
            return

        # make a copy of the roll
        mirrored_roll = Roll(
                user_id=user.id,
                item_id=user_owned_item.id,
                roll_time=datetime.now(),
                base_value=last_roll.base_value,
                can_roll_again=False,
        )
        # remove health from the dice
        user_owned_item.health -= item.use_cost
        if user_owned_item.health <= 0:
            response.send(f"Your {item.name} broke and was removed from your inventory. You have {len(click_user.get_items(item.id))} left.")

        # Check if we got any bonuses
        bonus_values, bonus_embeds = calculate_bonus(user, mirrored_roll)
        mirrored_roll.bonus_values.extend(bonus_values)

        user.add_roll(mirrored_roll)
        bot.db.commit()

        response.send(f"You rolled a {mirrored_roll} with the {item.name} from {user_to_mirror.mention} latest roll. Your total is {user.total_rolls}.")
        await response.send_home_channel(bot, embeds=bonus_embeds)
        await callback_interaction.response.defer()

    select_user_view = SelectItemView(
            user,
            bot,
            SelectItemView.all_users_options(bot.db.get_all_users(), bot),
            positive_button,
            positive_callback,
            timeout=30,
            placeholder="Select a user to mirror their last roll.",
    )

    await interaction.response.send_message(embed=info_embed, view=select_user_view, ephemeral=True, delete_after=30)
