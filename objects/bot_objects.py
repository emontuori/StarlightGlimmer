import discord
from discord.ext import commands
from discord.utils import get as dget

from lang import en_US, pt_BR, tr_TR
from utils import canvases, config
from utils.database import Session, session_scope, Guild


class GlimContext(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.is_repeat = False
        self.is_autoscan = False
        self.is_default = False
        self.is_template = False

        # Create database session, we don't want to do this
        # inside before_invoke because it doesn't happen
        # before checks
        self.session = Session()

    langs = {
        'en-us': "English (US)",
        'pt-br': "Português (BR)",
        'tr-tr': "Türkçe (TR)",
    }

    @property
    def canvas(self):
        return self.session.query(Guild).get(self.guild.id).canvas

    @property
    def canvas_pretty(self):
        return canvases.pretty_print[self.canvas]

    @property
    def gprefix(self):
        guild = self.session.query(Guild).get(self.guild.id)
        if guild and guild.prefix:
            return guild.prefix
        return config.PREFIX

    @property
    def lang(self):
        return self.session.query(Guild).get(self.guild.id).language

    @staticmethod
    def get_from_guild(guild, str_id):
        with session_scope() as session:
            if isinstance(guild, discord.Guild):
                language = session.query(Guild).get(guild.id).language.lower()
            else:
                language = session.query(Guild).get(guild).language.lower()

        if language == "en-us":
            return en_US.STRINGS.get(str_id, None)
        if language == "pt-br":
            return pt_BR.STRINGS.get(str_id, None)
        if language == "tr-tr":
            return tr_TR.STRINGS.get(str_id, None)

    def s(self, str_id):
        language = self.lang.lower()
        if language == "en-us":
            return en_US.STRINGS.get(str_id, None)
        if language == "pt-br":
            return pt_BR.STRINGS.get(str_id, None)
        if language == "tr-tr":
            return tr_TR.STRINGS.get(str_id, None)

    async def invoke_default(self, cmd: str):
        default_canvas = self.canvas
        cmds = cmd.split('.')
        self.command = dget(self.bot.commands, name=cmds[0])
        self.view.index = 0
        self.view.preview = 0
        self.view.get_word()
        if len(cmds) > 1:
            for c in cmds[1:]:
                self.command = dget(self.command.commands, name=c)
                self.view.skip_ws()
                self.view.get_word()
        self.command = dget(self.command.commands, name=default_canvas)
        self.is_default = True
        if self.command is not None:
            await self.bot.invoke(self)
