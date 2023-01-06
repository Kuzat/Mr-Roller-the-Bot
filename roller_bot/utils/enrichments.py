from roller_bot.models.user import User

from discord.ext import commands


def add_discord_mention(bot: commands.Bot, user: User) -> User:
    discord_user = bot.get_user(user.id)
    if discord_user is None:
        return user

    user.mention = discord_user.mention
    return user
