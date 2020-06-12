import logging
import traceback

import discord
from discord.ext import commands, menus

from objects import errors
import utils

log = logging.getLogger(__name__)


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Command errors
        if isinstance(error, commands.BadArgument):
            pass
        elif isinstance(error, commands.CommandInvokeError) \
                and isinstance(error.original, discord.HTTPException) \
                and error.original.code == 50013:
            pass
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(ctx.s("error.cooldown").format(error.retry_after))
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(ctx.s("error.missing_argument"))
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(ctx.s("error.no_dm"))
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(ctx.s("error.max_concurrency").format(error.number))
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(ctx.s("error.no_user_permission"))

        # Menu errors
        elif isinstance(error, menus.CannotAddReactions):
            await ctx.send(error)

        # Check errors
        elif isinstance(error, errors.BadArgumentErrorWithMessage):
            await ctx.send(error.message)
        elif isinstance(error, errors.FactionNotFoundError):
            await ctx.send(ctx.s("error.faction_not_found"))
        elif isinstance(error, errors.IdempotentActionError):
            try:
                f = discord.File("assets/y_tho.png", "y_tho.png")
                await ctx.send(ctx.s("error.why"), file=f)
            except IOError:
                await ctx.send(ctx.s("error.why"))
        elif isinstance(error, errors.NoAttachmentError):
            await ctx.send(ctx.s("error.no_attachment"))
        elif isinstance(error, errors.NoJpegsError):
            try:
                f = discord.File("assets/disdain_for_jpegs.gif", "disdain_for_jpegs.gif")
                await ctx.send(ctx.s("error.jpeg"), file=f)
            except IOError:
                await ctx.send(ctx.s("error.jpeg"))
        elif isinstance(error, errors.NoSelfPermissionError):
            await ctx.send(ctx.s("error.no_self_permission"))
        elif isinstance(error, errors.NoTemplatesError):
            if error.is_canvas_specific:
                await ctx.send(ctx.s("error.no_templates_for_canvas"))
            else:
                await ctx.send(ctx.s("error.no_templates"))
        elif isinstance(error, errors.NoUserPermissionError):
            await ctx.send(ctx.s("error.no_user_permission"))
        elif isinstance(error, errors.NotPngError):
            await ctx.send(ctx.s("error.not_png"))
        elif isinstance(error, errors.PilImageError):
            await ctx.send(ctx.s("error.bad_image"))
        elif isinstance(error, errors.TemplateHttpError):
            await ctx.send(ctx.s("error.cannot_fetch_template").format(error.template_name))
        elif isinstance(error, errors.TemplateNotFoundError):
            out = ctx.s("error.template_not_found").format(error.query)
            if error.matches != []:
                m = ctx.s("bot.or").format(", ".join(error.matches[:-1]), error.matches[-1]) if len(error.matches) > 1 else error.matches[0]
                out = "{} {}".format(out, ctx.s("error.did_you_mean").format(m))
            await ctx.send(out)
        elif isinstance(error, errors.UrlError):
            await ctx.send(ctx.s("error.non_discord_url"))
        elif isinstance(error, errors.HttpCanvasError):
            await ctx.send(ctx.s("error.http_canvas").format(utils.canvases.pretty_print[error.canvas]))
        elif isinstance(error, errors.HttpGeneralError):
            await ctx.send(ctx.s("error.http"))
        elif isinstance(error, errors.ColorError):
            await ctx.send(ctx.s("error.invalid_color"))
        elif isinstance(error, errors.TemplateTooLargeError):
            await ctx.send(ctx.s("canvas.dither_toolarge").format(error.limit))

        # Uncaught error
        else:
            name = ctx.command.qualified_name if ctx.command else "None"
            await utils.channel_log(
                self.bot, "An error occurred executing `{0}` in server **{1.name}** (ID: `{1.id}`):".format(name, ctx.guild))
            tb_text = "{}\n{}".format(error, ''.join(traceback.format_exception(None, error, error.__traceback__)))
            tb_text = [tb_text[i:i + 1500] for i in range(0, len(tb_text), 1500)]
            for chunk in tb_text:
                await utils.channel_log(self.bot, f"```{chunk}```")
            log.error("An error occurred executing '{}': {}\n{}".format(
                name, error, ''.join(traceback.format_exception(None, error, error.__traceback__))))
            await ctx.send(ctx.s("error.unknown"))


def setup(bot):
    bot.add_cog(Errors(bot))
