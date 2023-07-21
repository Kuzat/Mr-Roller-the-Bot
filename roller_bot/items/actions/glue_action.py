from discord import ButtonStyle, Color, Embed, Interaction
from discord.ui import Button

from roller_bot.clients.backends.user_verification_backend import UserVerificationBackend
from roller_bot.clients.bots.database_bot import DatabaseBot
from roller_bot.models.item_data import ItemData
from roller_bot.models.user import User
from roller_bot.utils.discord import ResponseMessage
from roller_bot.views.select_item_view import SelectItemView


async def use(item_data: ItemData, user: User, interaction: Interaction, bot: DatabaseBot) -> None:
    item = item_data.item
    response = ResponseMessage(interaction, item.name, user=interaction.user)

    # Get item from user
    # noinspection PyTypeChecker
    user_owned_item = user.get_item_data(item_data.id)
    if not user_owned_item:
        response.send(f"You don't have a {item.name} in your inventory.")
        return await response.send_interaction(ephemeral=True, delete_after=60)

    # Send a glue embed and view message
    info_embed = Embed(description=f"You are about to use a {item.name}. {item.description}. Select a item to glue!")
    info_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)

    # Make positive button
    positive_button = Button(
            label="Glue Item 🔫",
            style=ButtonStyle.green,
    )

    async def positive_callback(callback_interaction: Interaction, selected_item_id: int) -> None:
        click_user = await UserVerificationBackend.verify_interaction_user(callback_interaction, bot)
        if click_user != user:
            await callback_interaction.response.send_message('You cannot use items for another user.', ephemeral=True, delete_after=60)
            return

        item_to_glue = click_user.get_item_data(selected_item_id)
        if not item_to_glue:
            await callback_interaction.response.send_message('That item does not exist in your inventory.', ephemeral=True, delete_after=60)
            return

        # Heal the item
        old_health = item_to_glue.health
        item_to_glue.health = min(item_to_glue.health + item.heal_amount, item_to_glue.item.start_health)

        # Remove the glue item
        # noinspection PyTypeChecker
        user.remove_item(user_owned_item.id)
        bot.db.commit()

        # Update the glue select view
        info_embed.description = f"You have glued a {item_to_glue.item.name} with a {item.name}. Health: {old_health} -> {item_to_glue.health}"
        info_embed.color = Color.green()
        await bot.home_channel.send(embed=info_embed)
        await callback_interaction.response.defer()

    # Get a view to select the item and use or cancel
    select_item_view = SelectItemView(
            user,
            bot,
            SelectItemView.stacked_user_items_options,
            positive_button,
            positive_callback,
            timeout=30,
    )

    await interaction.response.send_message(embed=info_embed, view=select_item_view, ephemeral=True, delete_after=30)
