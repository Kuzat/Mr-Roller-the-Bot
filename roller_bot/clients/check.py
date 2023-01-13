from discord.ext import commands


class Check:
    @staticmethod
    def is_me():
        def predicate(ctx):
            return ctx.message.author.id == 119502664126955523

        return commands.check(predicate)

    @staticmethod
    def is_guild_owner():
        def predicate(ctx):
            return ctx.message.author.id == ctx.message.guild.owner.id

        return commands.check(predicate)

    @staticmethod
    def is_debug_mode(debug_mode: bool):
        return commands.check(lambda ctx: debug_mode)
