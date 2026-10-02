import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import time
from datetime import timedelta


# =========================================================
# DYNEX
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

CONFIG_FILE = "config.json"

EMOJIS = {
    "dynex": "<:Dynex:1555263060350996510>",
    "server": "<:Dynexserver:1555263062112604270>",
    "locked": "<:Dynexkilitli:1555263063366565918>",
    "settings": "<:Ayarlar:1555263064721334282>",
    "yes": "<:Dynexevet:1555263066235605023>",
    "wait": "<:Bekle:1555263067716198701>",
    "about": "<:Hakknda:1555263069318287464>",
    "loading": "<:Loading:1555263071151325184>",
    "unlock": "<:Dynexakkilit:1555263072988434493>",
    "alarm": "<:Alarm:1555263612426395739>",
    "developer": "<:Gelitirici:1555263614783463525>",
    "support": "<:Takviye:1555263624787005470>",
    "correct": "<:Doru:1555263630440923187>",
    "discord": "<:Discord:1555263704646557816>",
    "no": "<:Dynexhayir:1555265003727102134>",
}


DEFAULT_CONFIG = {
    "language": {},
    "servers": {},
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config()
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return DEFAULT_CONFIG.copy()

        data.setdefault("language", {})
        data.setdefault("servers", {})

        return data

    except Exception:
        return DEFAULT_CONFIG.copy()


CONFIG = load_config()


def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def get_guild_config(guild_id):
    guild_id = str(guild_id)

    if guild_id not in CONFIG["servers"]:
        CONFIG["servers"][guild_id] = {
            "ticket": {
                "category_id": None,
                "staff_role_id": None,
                "panel_channel_id": None,
                "panel_title": "Destek Talebi",
                "panel_description": "Destek almak için aşağıdaki butonu kullan.",
                "panel_image": None,
                "button_label": "Destek Talebi",
                "button_emoji": "🎫",
            },
            "welcome": {
                "channel_id": None,
                "title": "Hoş Geldin!",
                "description": "{user} sunucumuza hoş geldin!",
                "image": None,
                "dm_message": None,
            },
            "moderation": {
                "bad_words": [],
                "warning_limit": 3,
                "warning_action": "timeout",
                "timeout_duration": 10,
                "anti_link": False,
                "anti_spam": False,
                "log_channel_id": None,
            },
            "logs": {
                "channel_id": None,
                "delete": False,
                "edit": False,
                "join": False,
                "leave": False,
                "ban": False,
                "kick": False,
                "timeout": False,
            },
            "autorole": {
                "role_id": None,
            },
            "voice": {
                "channel_id": None,
                "join_message": "{user} ses kanalına katıldı.",
                "leave_message": "{user} ses kanalından ayrıldı.",
            },
            "giveaway": {
                "staff_role_id": None,
                "channel_id": None,
                "log_channel_id": None,
                "default_winners": 1,
                "default_duration": 10,
            },
            "dm": {
                "allowed_role_ids": [],
            },
            "games": {
                "number_channel_id": None,
                "word_channel_id": None,
                "number_target": 50,
                "words": [],
            },
        }

        save_config()

    return CONFIG["servers"][guild_id]


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="D.",
    intents=intents,
)


BOT_START_TIME = time.time()


# =========================================================
# HELPERS
# =========================================================

def guild_config(guild):
    return get_guild_config(guild.id)


def is_admin(interaction):
    return (
        interaction.guild
        and interaction.user
        and interaction.user.guild_permissions.administrator
    )


def parse_emoji(value, guild):
    if not value:
        return None

    value = str(value).strip()

    if value.startswith("<:") or value.startswith("<a:"):
        try:
            emoji = discord.PartialEmoji.from_str(value)
            if emoji.id:
                return emoji
        except Exception:
            return None

    if value.startswith(":") and value.endswith(":"):
        name = value[1:-1].strip()
        emoji = discord.utils.get(guild.emojis, name=name)
        if emoji:
            return emoji
        return None

    return value


def emoji_exists(value, guild):
    if not value:
        return True

    value = str(value).strip()

    if value.startswith(":") and value.endswith(":"):
        name = value[1:-1].strip()
        return discord.utils.get(guild.emojis, name=name) is not None

    if value.startswith("<:") or value.startswith("<a:"):
        try:
            emoji = discord.PartialEmoji.from_str(value)
            return emoji.id is not None
        except Exception:
            return False

    return True


def channel_mention(channel_id):
    if not channel_id:
        return "Ayarlanmadı"
    return f"<#{channel_id}>"


def role_mention(role_id):
    if not role_id:
        return "Ayarlanmadı"
    return f"<@&{role_id}>"


def format_uptime():
    seconds = int(time.time() - BOT_START_TIME)

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    result = []

    if days:
        result.append(f"{days} gün")
    if hours:
        result.append(f"{hours} saat")
    if minutes:
        result.append(f"{minutes} dakika")

    result.append(f"{seconds} saniye")

    return ", ".join(result)


async def send_log(guild, message):
    try:
        cfg = guild_config(guild)
        channel_id = cfg["logs"].get("channel_id")

        if not channel_id:
            channel_id = cfg["moderation"].get("log_channel_id")

        if not channel_id:
            return

        channel = guild.get_channel(channel_id)

        if channel:
            await channel.send(message)

    except Exception:
        pass


# =========================================================
# SETTINGS SELECT MENUS
# =========================================================

class SettingsMainSelect(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Ticket",
                description="Ticket sistemini ayarla.",
                emoji="🎫",
                value="ticket",
            ),
            discord.SelectOption(
                label="Karşılama",
                description="Hoş geldin sistemini ayarla.",
                emoji="👋",
                value="welcome",
            ),
            discord.SelectOption(
                label="Moderasyon",
                description="Moderasyon ayarlarını yönet.",
                emoji="🛡️",
                value="moderation",
            ),
            discord.SelectOption(
                label="Loglar",
                description="Log sistemini ayarla.",
                emoji="📋",
                value="logs",
            ),
            discord.SelectOption(
                label="Otorol",
                description="Otomatik rol sistemini ayarla.",
                emoji="🎭",
                value="autorole",
            ),
            discord.SelectOption(
                label="Ses",
                description="Ses kanalı bildirimlerini ayarla.",
                emoji="🔊",
                value="voice",
            ),
            discord.SelectOption(
                label="Çekiliş",
                description="Çekiliş ayarlarını yönet.",
                emoji="🎉",
                value="giveaway",
            ),
            discord.SelectOption(
                label="DM",
                description="Toplu DM yetkilerini ayarla.",
                emoji="✉️",
                value="dm",
            ),
            discord.SelectOption(
                label="Dil",
                description="Sunucu dilini değiştir.",
                emoji="🌐",
                value="language",
            ),
        ]

        super().__init__(
            placeholder="Bir ayar kategorisi seçin...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="dynex_settings_main",
        )

    async def callback(self, interaction):
        value = self.values[0]

        views = {
            "ticket": TicketSettingsView,
            "welcome": WelcomeSettingsView,
            "moderation": ModerationSettingsView,
            "logs": LogsSettingsView,
            "autorole": AutoroleSettingsView,
            "voice": VoiceSettingsView,
            "giveaway": GiveawaySettingsView,
            "dm": DMSettingsView,
            "language": LanguageSettingsView,
        }

        view_class = views.get(value)

        if not view_class:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Ayar bulunamadı.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            embed=view_class.create_embed(interaction.guild),
            view=view_class(),
        )


class SettingsMainView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(SettingsMainSelect())


# =========================================================
# TICKET SETTINGS
# =========================================================

class TicketCategorySelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Ticket kategorisini seçin...",
            channel_types=[discord.ChannelType.category],
            custom_id="dynex_ticket_category",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["ticket"]["category_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=TicketSettingsView.create_embed(interaction.guild),
            view=TicketSettingsView(),
        )


class TicketStaffRoleSelect(discord.ui.RoleSelect):

    def __init__(self):
        super().__init__(
            placeholder="Ticket yetkili rolünü seçin...",
            custom_id="dynex_ticket_staff_role",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["ticket"]["staff_role_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=TicketSettingsView.create_embed(interaction.guild),
            view=TicketSettingsView(),
        )


class TicketPanelChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Ticket panel kanalını seçin...",
            channel_types=[discord.ChannelType.text],
            custom_id="dynex_ticket_panel_channel",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["ticket"]["panel_channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=TicketSettingsView.create_embed(interaction.guild),
            view=TicketSettingsView(),
        )


class TicketTextModal(discord.ui.Modal, title="Ticket Panel Ayarları"):

    panel_title = discord.ui.TextInput(
        label="Panel başlığı",
        required=True,
        max_length=256,
    )

    panel_description = discord.ui.TextInput(
        label="Panel açıklaması",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000,
    )

    button_label = discord.ui.TextInput(
        label="Buton yazısı",
        required=True,
        max_length=80,
    )

    button_emoji = discord.ui.TextInput(
        label="Buton emojisi",
        placeholder="🎫 veya :dikkat: veya <:emoji:id>",
        required=False,
        max_length=100,
    )

    async def on_submit(self, interaction):
        cfg = guild_config(interaction.guild)

        emoji_value = self.button_emoji.value.strip()

        if emoji_value and not emoji_exists(emoji_value, interaction.guild):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu emoji sunucuda bulunamadı.",
                ephemeral=True,
            )
            return

        cfg["ticket"]["panel_title"] = self.panel_title.value
        cfg["ticket"]["panel_description"] = self.panel_description.value
        cfg["ticket"]["button_label"] = self.button_label.value
        cfg["ticket"]["button_emoji"] = emoji_value

        save_config()

        await interaction.response.edit_message(
            embed=TicketSettingsView.create_embed(interaction.guild),
            view=TicketSettingsView(),
        )


class TicketSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(TicketCategorySelect())
        self.add_item(TicketStaffRoleSelect())
        self.add_item(TicketPanelChannelSelect())

        edit_button = discord.ui.Button(
            label="Panel Yazılarını Düzenle",
            emoji="✏️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_ticket_text",
        )
        edit_button.callback = self.edit_text
        self.add_item(edit_button)

        back_button = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_ticket_back",
        )
        back_button.callback = self.back
        self.add_item(back_button)

    async def edit_text(self, interaction):
        await interaction.response.send_modal(TicketTextModal())

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["ticket"]

        embed = discord.Embed(
            title="🎫 Ticket Ayarları",
            description="Aşağıdaki menülerden Ticket sistemini ayarlayabilirsin.",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="Kategori",
            value=channel_mention(cfg.get("category_id")),
            inline=True,
        )

        embed.add_field(
            name="Yetkili Rolü",
            value=role_mention(cfg.get("staff_role_id")),
            inline=True,
        )

        embed.add_field(
            name="Panel Kanalı",
            value=channel_mention(cfg.get("panel_channel_id")),
            inline=True,
        )

        embed.add_field(
            name="Panel Başlığı",
            value=cfg.get("panel_title", "Destek Talebi"),
            inline=False,
        )

        return embed


# =========================================================
# WELCOME SETTINGS
# =========================================================

class WelcomeChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Karşılama kanalını seçin...",
            channel_types=[discord.ChannelType.text],
            custom_id="dynex_welcome_channel",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["welcome"]["channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=WelcomeSettingsView.create_embed(interaction.guild),
            view=WelcomeSettingsView(),
        )


class WelcomeModal(discord.ui.Modal, title="Karşılama Ayarları"):

    title_input = discord.ui.TextInput(
        label="Başlık",
        required=True,
        max_length=256,
    )

    description = discord.ui.TextInput(
        label="Mesaj",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000,
    )

    image = discord.ui.TextInput(
        label="Görsel URL",
        required=False,
        max_length=1000,
    )

    dm_message = discord.ui.TextInput(
        label="Özel mesaj",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=2000,
    )

    async def on_submit(self, interaction):
        cfg = guild_config(interaction.guild)

        cfg["welcome"]["title"] = self.title_input.value
        cfg["welcome"]["description"] = self.description.value
        cfg["welcome"]["image"] = self.image.value or None
        cfg["welcome"]["dm_message"] = self.dm_message.value or None

        save_config()

        await interaction.response.edit_message(
            embed=WelcomeSettingsView.create_embed(interaction.guild),
            view=WelcomeSettingsView(),
        )


class WelcomeSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(WelcomeChannelSelect())

        button = discord.ui.Button(
            label="Yazıları Düzenle",
            emoji="✏️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_welcome_edit",
        )
        button.callback = self.edit
        self.add_item(button)

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_welcome_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def edit(self, interaction):
        await interaction.response.send_modal(WelcomeModal())

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["welcome"]

        embed = discord.Embed(
            title="👋 Karşılama Ayarları",
            description="Karşılama sistemini buradan ayarlayabilirsin.",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Kanal",
            value=channel_mention(cfg.get("channel_id")),
            inline=True,
        )

        embed.add_field(
            name="Başlık",
            value=cfg.get("title", "Hoş Geldin!"),
            inline=False,
        )

        return embed


# =========================================================
# MODERATION SETTINGS
# =========================================================

class ModerationChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Moderasyon log kanalını seçin...",
            channel_types=[discord.ChannelType.text],
            custom_id="dynex_moderation_log",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["moderation"]["log_channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=ModerationSettingsView.create_embed(interaction.guild),
            view=ModerationSettingsView(),
        )


class ModerationActionSelect(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Timeout",
                value="timeout",
                emoji="⏱️",
            ),
            discord.SelectOption(
                label="Kick",
                value="kick",
                emoji="👢",
            ),
            discord.SelectOption(
                label="Ban",
                value="ban",
                emoji="🔨",
            ),
        ]

        super().__init__(
            placeholder="Uyarı sonrası işlemi seçin...",
            options=options,
            custom_id="dynex_moderation_action",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["moderation"]["warning_action"] = self.values[0]
        save_config()

        await interaction.response.edit_message(
            embed=ModerationSettingsView.create_embed(interaction.guild),
            view=ModerationSettingsView(),
        )


class ModerationToggleSelect(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Anti-Link Aç",
                value="link_on",
                emoji="🔗",
            ),
            discord.SelectOption(
                label="Anti-Link Kapat",
                value="link_off",
                emoji="🚫",
            ),
            discord.SelectOption(
                label="Anti-Spam Aç",
                value="spam_on",
                emoji="🛡️",
            ),
            discord.SelectOption(
                label="Anti-Spam Kapat",
                value="spam_off",
                emoji="❌",
            ),
        ]

        super().__init__(
            placeholder="Koruma ayarını seçin...",
            options=options,
            custom_id="dynex_moderation_toggle",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)["moderation"]

        value = self.values[0]

        if value == "link_on":
            cfg["anti_link"] = True
        elif value == "link_off":
            cfg["anti_link"] = False
        elif value == "spam_on":
            cfg["anti_spam"] = True
        elif value == "spam_off":
            cfg["anti_spam"] = False

        save_config()

        await interaction.response.edit_message(
            embed=ModerationSettingsView.create_embed(interaction.guild),
            view=ModerationSettingsView(),
        )


class BadWordsModal(discord.ui.Modal, title="Yasaklı Kelimeler"):

    words = discord.ui.TextInput(
        label="Kelimeler",
        placeholder="kelime1, kelime2, kelime3",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=2000,
    )

    async def on_submit(self, interaction):
        cfg = guild_config(interaction.guild)["moderation"]

        cfg["bad_words"] = [
            x.strip().lower()
            for x in self.words.value.split(",")
            if x.strip()
        ]

        save_config()

        await interaction.response.edit_message(
            embed=ModerationSettingsView.create_embed(interaction.guild),
            view=ModerationSettingsView(),
        )


class ModerationSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(ModerationChannelSelect())
        self.add_item(ModerationActionSelect())
        self.add_item(ModerationToggleSelect())

        bad_words = discord.ui.Button(
            label="Yasaklı Kelimeler",
            emoji="🚫",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_bad_words",
        )
        bad_words.callback = self.bad_words
        self.add_item(bad_words)

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_mod_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def bad_words(self, interaction):
        await interaction.response.send_modal(BadWordsModal())

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["moderation"]

        embed = discord.Embed(
            title="🛡️ Moderasyon Ayarları",
            description="Moderasyon sistemini buradan ayarlayabilirsin.",
            color=discord.Color.red(),
        )

        embed.add_field(
            name="Log Kanalı",
            value=channel_mention(cfg.get("log_channel_id")),
            inline=True,
        )

        embed.add_field(
            name="Uyarı İşlemi",
            value=cfg.get("warning_action", "timeout"),
            inline=True,
        )

        embed.add_field(
            name="Yasaklı Kelime Sayısı",
            value=str(len(cfg.get("bad_words", []))),
            inline=True,
        )

        embed.add_field(
            name="Anti-Link",
            value="Açık" if cfg.get("anti_link") else "Kapalı",
            inline=True,
        )

        embed.add_field(
            name="Anti-Spam",
            value="Açık" if cfg.get("anti_spam") else "Kapalı",
            inline=True,
        )

        return embed


# =========================================================
# LOG SETTINGS
# =========================================================

class LogsChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Log kanalını seçin...",
            channel_types=[discord.ChannelType.text],
            custom_id="dynex_logs_channel",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["logs"]["channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=LogsSettingsView.create_embed(interaction.guild),
            view=LogsSettingsView(),
        )


class LogsToggleSelect(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(label="Mesaj Silme", value="delete"),
            discord.SelectOption(label="Mesaj Düzenleme", value="edit"),
            discord.SelectOption(label="Üye Katılma", value="join"),
            discord.SelectOption(label="Üye Ayrılma", value="leave"),
            discord.SelectOption(label="Ban", value="ban"),
            discord.SelectOption(label="Kick", value="kick"),
            discord.SelectOption(label="Timeout", value="timeout"),
        ]

        super().__init__(
            placeholder="Açmak istediğin logu seç...",
            options=options,
            custom_id="dynex_logs_toggle",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)["logs"]
        key = self.values[0]
        cfg[key] = not cfg.get(key, False)
        save_config()

        await interaction.response.edit_message(
            embed=LogsSettingsView.create_embed(interaction.guild),
            view=LogsSettingsView(),
        )


class LogsSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(LogsChannelSelect())
        self.add_item(LogsToggleSelect())

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_logs_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["logs"]

        embed = discord.Embed(
            title="📋 Log Ayarları",
            description="Log kanalını seç ve kaydetmek istediğin olayları aç.",
            color=discord.Color.orange(),
        )

        embed.add_field(
            name="Log Kanalı",
            value=channel_mention(cfg.get("channel_id")),
            inline=False,
        )

        enabled = [
            name
            for key, name in [
                ("delete", "Mesaj Silme"),
                ("edit", "Mesaj Düzenleme"),
                ("join", "Üye Katılma"),
                ("leave", "Üye Ayrılma"),
                ("ban", "Ban"),
                ("kick", "Kick"),
                ("timeout", "Timeout"),
            ]
            if cfg.get(key)
        ]

        embed.add_field(
            name="Aktif Loglar",
            value=", ".join(enabled) if enabled else "Yok",
            inline=False,
        )

        return embed


# =========================================================
# AUTOROLE
# =========================================================

class AutoroleSelect(discord.ui.RoleSelect):

    def __init__(self):
        super().__init__(
            placeholder="Otorol seçin...",
            custom_id="dynex_autorole",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["autorole"]["role_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=AutoroleSettingsView.create_embed(interaction.guild),
            view=AutoroleSettingsView(),
        )


class AutoroleDisableButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Otorolü Kapat",
            emoji="❌",
            style=discord.ButtonStyle.danger,
            custom_id="dynex_autorole_disable",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["autorole"]["role_id"] = None
        save_config()

        await interaction.response.edit_message(
            embed=AutoroleSettingsView.create_embed(interaction.guild),
            view=AutoroleSettingsView(),
        )


class AutoroleSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(AutoroleSelect())
        self.add_item(AutoroleDisableButton())

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_autorole_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["autorole"]

        embed = discord.Embed(
            title="🎭 Otorol Ayarları",
            description="Sunucuya yeni katılan kişilere verilecek rolü seç.",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="Otorol",
            value=role_mention(cfg.get("role_id")),
            inline=False,
        )

        return embed


# =========================================================
# VOICE SETTINGS
# =========================================================

class VoiceChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Ses bildirim kanalını seçin...",
            channel_types=[discord.ChannelType.text],
            custom_id="dynex_voice_channel",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["voice"]["channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=VoiceSettingsView.create_embed(interaction.guild),
            view=VoiceSettingsView(),
        )


class VoiceModal(discord.ui.Modal, title="Ses Bildirimleri"):

    join_message = discord.ui.TextInput(
        label="Katılma mesajı",
        required=True,
        max_length=1000,
    )

    leave_message = discord.ui.TextInput(
        label="Ayrılma mesajı",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction):
        cfg = guild_config(interaction.guild)["voice"]

        cfg["join_message"] = self.join_message.value
        cfg["leave_message"] = self.leave_message.value

        save_config()

        await interaction.response.edit_message(
            embed=VoiceSettingsView.create_embed(interaction.guild),
            view=VoiceSettingsView(),
        )


class VoiceSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(VoiceChannelSelect())

        edit = discord.ui.Button(
            label="Mesajları Düzenle",
            emoji="✏️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_voice_edit",
        )
        edit.callback = self.edit
        self.add_item(edit)

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_voice_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def edit(self, interaction):
        await interaction.response.send_modal(VoiceModal())

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["voice"]

        embed = discord.Embed(
            title="🔊 Ses Ayarları",
            description="Ses kanalına giriş ve çıkış bildirimlerini ayarla.",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="Bildirim Kanalı",
            value=channel_mention(cfg.get("channel_id")),
            inline=False,
        )

        return embed


# =========================================================
# GIVEAWAY SETTINGS
# =========================================================

class GiveawayStaffRoleSelect(discord.ui.RoleSelect):

    def __init__(self):
        super().__init__(
            placeholder="Çekiliş yetkili rolünü seçin...",
            custom_id="dynex_giveaway_staff",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["giveaway"]["staff_role_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=GiveawaySettingsView.create_embed(interaction.guild),
            view=GiveawaySettingsView(),
        )


class GiveawayChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Çekiliş kanalını seçin...",
            channel_types=[discord.ChannelType.text],
            custom_id="dynex_giveaway_channel",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["giveaway"]["channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=GiveawaySettingsView.create_embed(interaction.guild),
            view=GiveawaySettingsView(),
        )


class GiveawayLogChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="Çekiliş log kanalını seçin...",
            channel_types=[discord.ChannelType.text],
            custom_id="dynex_giveaway_log",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)
        cfg["giveaway"]["log_channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=GiveawaySettingsView.create_embed(interaction.guild),
            view=GiveawaySettingsView(),
        )


class GiveawaySettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(GiveawayStaffRoleSelect())
        self.add_item(GiveawayChannelSelect())
        self.add_item(GiveawayLogChannelSelect())

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_giveaway_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["giveaway"]

        embed = discord.Embed(
            title="🎉 Çekiliş Ayarları",
            description="Çekiliş sistemi için rol ve kanalları seç.",
            color=discord.Color.gold(),
        )

        embed.add_field(
            name="Yetkili Rolü",
            value=role_mention(cfg.get("staff_role_id")),
            inline=True,
        )

        embed.add_field(
            name="Çekiliş Kanalı",
            value=channel_mention(cfg.get("channel_id")),
            inline=True,
        )

        embed.add_field(
            name="Log Kanalı",
            value=channel_mention(cfg.get("log_channel_id")),
            inline=True,
        )

        return embed


# =========================================================
# DM SETTINGS
# =========================================================

class DMAllowedRoleSelect(discord.ui.RoleSelect):

    def __init__(self):
        super().__init__(
            placeholder="DM kullanabilecek rolü seçin...",
            custom_id="dynex_dm_allowed_role",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)["dm"]

        role_id = self.values[0].id

        if role_id not in cfg["allowed_role_ids"]:
            cfg["allowed_role_ids"].append(role_id)

        save_config()

        await interaction.response.edit_message(
            embed=DMSettingsView.create_embed(interaction.guild),
            view=DMSettingsView(),
        )


class DMClearRolesButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Yetkileri Temizle",
            emoji="🗑️",
            style=discord.ButtonStyle.danger,
            custom_id="dynex_dm_clear",
        )

    async def callback(self, interaction):
        cfg = guild_config(interaction.guild)["dm"]
        cfg["allowed_role_ids"] = []

        save_config()

        await interaction.response.edit_message(
            embed=DMSettingsView.create_embed(interaction.guild),
            view=DMSettingsView(),
        )


class DMSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(DMAllowedRoleSelect())
        self.add_item(DMClearRolesButton())

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_dm_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        cfg = guild_config(guild)["dm"]

        roles = cfg.get("allowed_role_ids", [])

        if roles:
            role_text = "\n".join(role_mention(x) for x in roles)
        else:
            role_text = "Henüz rol seçilmedi."

        embed = discord.Embed(
            title="✉️ DM Ayarları",
            description="`/dm` komutunu kullanabilecek rolleri seç.",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="İzinli Roller",
            value=role_text,
            inline=False,
        )

        embed.add_field(
            name="Not",
            value="Sunucu yöneticileri her zaman `/dm` kullanabilir.",
            inline=False,
        )

        return embed


# =========================================================
# LANGUAGE SETTINGS
# =========================================================

class LanguageSelect(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Türkçe",
                value="tr",
                emoji="🇹🇷",
            ),
            discord.SelectOption(
                label="English",
                value="en",
                emoji="🇬🇧",
            ),
            discord.SelectOption(
                label="Azərbaycan",
                value="az",
                emoji="🇦🇿",
            ),
        ]

        super().__init__(
            placeholder="Bir dil seçin...",
            options=options,
            custom_id="dynex_language",
        )

    async def callback(self, interaction):
        CONFIG.setdefault("language", {})
        CONFIG["language"][str(interaction.guild.id)] = self.values[0]

        save_config()

        await interaction.response.edit_message(
            embed=LanguageSettingsView.create_embed(interaction.guild),
            view=LanguageSettingsView(),
        )


class LanguageSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(LanguageSelect())

        back = discord.ui.Button(
            label="Geri",
            emoji="↩️",
            style=discord.ButtonStyle.secondary,
            custom_id="dynex_language_back",
        )
        back.callback = self.back
        self.add_item(back)

    async def back(self, interaction):
        await interaction.response.edit_message(
            embed=SettingsEmbed.create(interaction.guild),
            view=SettingsMainView(),
        )

    @staticmethod
    def create_embed(guild):
        language = CONFIG.get("language", {}).get(str(guild.id), "tr")

        names = {
            "tr": "Türkçe 🇹🇷",
            "en": "English 🇬🇧",
            "az": "Azərbaycan 🇦🇿",
        }

        embed = discord.Embed(
            title="🌐 Dil Ayarları",
            description="Botun sunucu dilini seç.",
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="Mevcut Dil",
            value=names.get(language, "Türkçe 🇹🇷"),
            inline=False,
        )

        return embed


# =========================================================
# MAIN SETTINGS EMBED
# =========================================================

class SettingsEmbed:

    @staticmethod
    def create(guild):

        embed = discord.Embed(
            title=f"{EMOJIS['settings']} Dynex Ayarları",
            description=(
                "Aşağıdaki menüden değiştirmek istediğin ayarı seç.\n\n"
                "Seçim yaptığında ilgili ayar paneli açılır."
            ),
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="🎫 Ticket",
            value="Kategori, yetkili rolü ve panel kanalı.",
            inline=False,
        )

        embed.add_field(
            name="👋 Karşılama",
            value="Hoş geldin kanalı ve mesajları.",
            inline=False,
        )

        embed.add_field(
            name="🛡️ Moderasyon",
            value="Yasaklı kelimeler ve koruma sistemi.",
            inline=False,
        )

        embed.add_field(
            name="📋 Loglar",
            value="Sunucu olaylarının logları.",
            inline=False,
        )

        embed.add_field(
            name="🎭 Otorol",
            value="Yeni üyelere otomatik rol.",
            inline=False,
        )

        embed.add_field(
            name="🔊 Ses",
            value="Ses kanalı bildirimleri.",
            inline=False,
        )

        embed.add_field(
            name="🎉 Çekiliş",
            value="Çekiliş kanalları ve yetkileri.",
            inline=False,
        )

        embed.add_field(
            name="✉️ DM",
            value="Toplu DM kullanabilecek roller.",
            inline=False,
        )

        embed.add_field(
            name="🌐 Dil",
            value="Bot dilini değiştir.",
            inline=False,
        )

        return embed


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönetir.",
)
async def ayarlar(interaction: discord.Interaction):

    if not interaction.guild:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komut sadece sunucuda kullanılabilir.",
            ephemeral=True,
        )
        return

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarları sadece sunucu yöneticileri kullanabilir.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        embed=SettingsEmbed.create(interaction.guild),
        view=SettingsMainView(),
        ephemeral=True,
    )


# =========================================================
# /BOT
# =========================================================

@bot.tree.command(
    name="bot",
    description="Dynex bot bilgilerini gösterir.",
)
async def bot_info(interaction):

    embed = discord.Embed(
        title="Dynex Durum",
        color=discord.Color.from_rgb(0, 0, 0),
    )

    owner = None

    try:
        app = await bot.application_info()
        owner = app.owner
    except Exception:
        pass

    owner_text = owner.mention if owner else "Bilinmiyor"

    support_guild = bot.get_guild(1551647711332139098)

    if support_guild:
        support_members = support_guild.member_count
    else:
        support_members = "Bilinmiyor"

    embed.add_field(
        name="Sunucu Sayısı",
        value=str(len(bot.guilds)),
        inline=True,
    )

    embed.add_field(
        name="Destek Sunucusu Üye Sayısı",
        value=str(support_members),
        inline=True,
    )

    embed.add_field(
        name="Prefix",
        value="D.",
        inline=True,
    )

    embed.add_field(
        name="Slash Komutları",
        value="Aktif",
        inline=True,
    )

    embed.add_field(
        name="Aktif Kalma Süresi",
        value=format_uptime(),
        inline=True,
    )

    embed.add_field(
        name="Bot Sahibi",
        value=owner_text,
        inline=True,
    )

    embed.add_field(
        name="Destek Sunucusu",
        value="[Dynex Destek](https://discord.gg/2pFJwJNDR)",
        inline=False,
    )

    await interaction.response.send_message(
        embed=embed,
    )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Bot gecikmesini gösterir.",
)
async def ping(interaction):

    latency = round(bot.latency * 1000)

    if latency <= 80:
        status = "Mükemmel"
    elif latency <= 150:
        status = "İyi"
    elif latency <= 250:
        status = "Orta"
    elif latency <= 400:
        status = "Zayıf"
    else:
        status = "Berbat"

    embed = discord.Embed(
        title="Dynex Ping",
        description=f"**{latency}ms**\nDurum: **{status}**",
        color=discord.Color.blurple(),
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# /YARDIM
# =========================================================

class HelpSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Genel",
                value="general",
                emoji="🏠",
            ),
            discord.SelectOption(
                label="Moderasyon",
                value="moderation",
                emoji="🛡️",
            ),
            discord.SelectOption(
                label="Eğlence",
                value="fun",
                emoji="🎮",
            ),
            discord.SelectOption(
                label="Sunucu",
                value="server",
                emoji="🖥️",
            ),
            discord.SelectOption(
                label="Ayarlar",
                value="settings",
                emoji="⚙️",
            ),
        ]

        super().__init__(
            placeholder="Komut kategorisi seçin...",
            options=options,
            custom_id="dynex_help",
        )

    async def callback(self, interaction):

        data = {
            "general": (
                "`/bot`\n"
                "`/yardım`\n"
                "`/ping`\n"
                "`/kullanıcı`\n"
                "`/avatar`\n"
                "`/sunucu`\n"
                "`/roller`"
            ),
            "moderation": (
                "`/uyar`\n"
                "`/uyarılar`\n"
                "`/timeout`\n"
                "`/kick`\n"
                "`/ban`\n"
                "`/temizle`\n"
                "`/sil`\n"
                "`/kilitle`\n"
                "`/kilit-aç`\n"
                "`/yavaş-mod`"
            ),
            "fun": (
                "`/zar`\n"
                "`/yazı-tura`\n"
                "`/8ball`\n"
                "`/sayı-tahmin`\n"
                "`/sayı-oyunu-ayarla`\n"
                "`/sayı-oyunu-durdur`\n"
                "`/kelime-oyunu-ayarla`\n"
                "`/kelime-oyunu-durdur`"
            ),
            "server": (
                "`/sunucu`\n"
                "`/roller`\n"
                "`/ayarlar`\n"
                "`/dil`\n"
                "`/dm`"
            ),
            "settings": "`/ayarlar` → Ticket / Karşılama / Moderasyon / Loglar / Otorol / Ses / Çekiliş / DM / Dil",
        }

        embed = discord.Embed(
            title=f"{EMOJIS['dynex']} Dynex Yardım",
            description=data[self.values[0]],
            color=discord.Color.blurple(),
        )

        await interaction.response.edit_message(
            embed=embed,
            view=HelpView(),
        )


class HelpView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(HelpSelect())


@bot.tree.command(
    name="yardım",
    description="Dynex komutlarını gösterir.",
)
async def yardim(interaction):

    embed = discord.Embed(
        title=f"{EMOJIS['dynex']} Dynex Yardım",
        description="Bir kategori seç.",
        color=discord.Color.blurple(),
    )

    await interaction.response.send_message(
        embed=embed,
        view=HelpView(),
        ephemeral=True,
    )


# =========================================================
# BASIC COMMANDS
# =========================================================

@bot.tree.command(name="sunucu", description="Sunucu bilgilerini gösterir.")
async def sunucu(interaction):

    guild = interaction.guild

    embed = discord.Embed(
        title=f"{EMOJIS['server']} {guild.name}",
        color=discord.Color.blurple(),
    )

    embed.add_field(
        name="Üye Sayısı",
        value=str(guild.member_count),
        inline=True,
    )

    embed.add_field(
        name="Kanal Sayısı",
        value=str(len(guild.channels)),
        inline=True,
    )

    embed.add_field(
        name="Rol Sayısı",
        value=str(len(guild.roles)),
        inline=True,
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="kullanıcı", description="Kullanıcı bilgilerini gösterir.")
@app_commands.describe(kullanıcı="Bilgilerini görmek istediğin kullanıcı.")
async def kullanici(
    interaction,
    kullanıcı: discord.Member = None,
):

    kullanıcı = kullanıcı or interaction.user

    embed = discord.Embed(
        title="Kullanıcı Bilgileri",
        color=discord.Color.blurple(),
    )

    embed.set_thumbnail(url=kullanıcı.display_avatar.url)

    embed.add_field(
        name="Kullanıcı",
        value=kullanıcı.mention,
        inline=False,
    )

    embed.add_field(
        name="ID",
        value=str(kullanıcı.id),
        inline=True,
    )

    embed.add_field(
        name="Hesap",
        value=discord.utils.format_dt(kullanıcı.created_at, "F"),
        inline=False,
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="avatar", description="Kullanıcının avatarını gösterir.")
@app_commands.describe(kullanıcı="Avatarını görmek istediğin kullanıcı.")
async def avatar(
    interaction,
    kullanıcı: discord.Member = None,
):

    kullanıcı = kullanıcı or interaction.user

    embed = discord.Embed(
        title=f"{kullanıcı.display_name} Avatarı",
        color=discord.Color.blurple(),
    )

    embed.set_image(url=kullanıcı.display_avatar.url)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="roller", description="Sunucudaki rolleri gösterir.")
async def roller(interaction):

    roles = [
        role.mention
        for role in reversed(interaction.guild.roles)
        if role.name != "@everyone"
    ]

    text = "\n".join(roles)

    if len(text) > 4000:
        text = text[:3900] + "\n..."

    embed = discord.Embed(
        title="Sunucu Rolleri",
        description=text or "Rol bulunamadı.",
        color=discord.Color.blurple(),
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# FUN COMMANDS
# =========================================================

@bot.tree.command(name="zar", description="Zar atar.")
async def zar(interaction):

    number = random.randint(1, 6)

    await interaction.response.send_message(
        f"🎲 **{number}** geldi!"
    )


@bot.tree.command(name="yazı-tura", description="Yazı veya tura atar.")
async def yazi_tura(interaction):

    result = random.choice(["Yazı", "Tura"])

    await interaction.response.send_message(
        f"🪙 Sonuç: **{result}**"
    )


@bot.tree.command(name="8ball", description="8ball sorusuna cevap verir.")
@app_commands.describe(soru="Sorunu yaz.")
async def eightball(interaction, soru: str):

    answers = [
        "Evet.",
        "Hayır.",
        "Büyük ihtimalle.",
        "Sanmıyorum.",
        "Kesinlikle.",
        "Bunu zaman gösterecek.",
        "Şu an belli değil.",
    ]

    await interaction.response.send_message(
        f"🎱 **Soru:** {soru}\n**Cevap:** {random.choice(answers)}"
    )


@bot.tree.command(name="sayı-tahmin", description="1 ile 100 arasında sayı tahmin eder.")
async def sayi_tahmin(interaction):

    number = random.randint(1, 100)

    await interaction.response.send_message(
        f"🎯 Aklımdaki sayı **1 ile 100 arasında**.\n"
        f"Bu komutta rastgele tahminin: **{random.randint(1,100)}**\n"
        f"Gerçek sayı: **{number}**"
    )


# =========================================================
# DM SYSTEM
# =========================================================

def has_dm_permission(interaction):

    if is_admin(interaction):
        return True

    cfg = guild_config(interaction.guild)["dm"]
    allowed_roles = cfg.get("allowed_role_ids", [])

    user_role_ids = {role.id for role in interaction.user.roles}

    return bool(user_role_ids.intersection(allowed_roles))


class DMModal(discord.ui.Modal, title="Toplu DM Gönder"):

    title_input = discord.ui.TextInput(
        label="DM Başlığı",
        required=True,
        max_length=256,
    )

    message_input = discord.ui.TextInput(
        label="DM Mesajı",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000,
    )

    async def on_submit(self, interaction):

        target_role_id = getattr(
            interaction,
            "dynex_dm_target_role_id",
            None,
        )

        if not target_role_id:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Hedef rol bulunamadı.",
                ephemeral=True,
            )
            return

        role = interaction.guild.get_role(target_role_id)

        if not role:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu rol artık sunucuda bulunmuyor.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        success = 0
        failed = 0

        for member in role.members:

            if member.bot:
                continue

            try:
                embed = discord.Embed(
                    title=self.title_input.value,
                    description=self.message_input.value,
                    color=discord.Color.blurple(),
                )

                embed.set_footer(
                    text=f"{interaction.guild.name} • Dynex"
                )

                await member.send(embed=embed)
                success += 1

            except Exception:
                failed += 1

        await interaction.followup.send(
            f"{EMOJIS['yes']} DM gönderimi tamamlandı.\n\n"
            f"**Rol:** {role.mention}\n"
            f"**Başarılı:** {success}\n"
            f"**Başarısız:** {failed}",
            ephemeral=True,
        )


class DMRoleSelect(discord.ui.RoleSelect):

    def __init__(self):
        super().__init__(
            placeholder="DM gönderilecek rolü seçin...",
            custom_id="dynex_dm_target_role",
        )

    async def callback(self, interaction):

        if not has_dm_permission(interaction):
            await interaction.response.send_message(
                f"{EMOJIS['no']} `/dm` kullanma yetkin yok.",
                ephemeral=True,
            )
            return

        role = self.values[0]

        modal = DMModal()
        modal.dynex_dm_target_role_id = role.id

        await interaction.response.send_modal(modal)


class DMView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(DMRoleSelect())


@bot.tree.command(
    name="dm",
    description="Belirli bir role sahip kullanıcılara DM gönderir.",
)
async def dm(interaction):

    if not interaction.guild:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komut sadece sunucuda kullanılabilir.",
            ephemeral=True,
        )
        return

    if not has_dm_permission(interaction):
        await interaction.response.send_message(
            f"{EMOJIS['no']} `/dm` kullanma yetkin yok.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title="✉️ Toplu DM",
        description="DM gönderilecek rolü seç.",
        color=discord.Color.blurple(),
    )

    await interaction.response.send_message(
        embed=embed,
        view=DMView(),
        ephemeral=True,
    )


# =========================================================
# MODERATION
# =========================================================

@bot.tree.command(name="temizle", description="Mesajları siler.")
@app_commands.describe(miktar="Silinecek mesaj sayısı.")
async def temizle(interaction, miktar: app_commands.Range[int, 1, 100]):

    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Mesaj yönetme yetkin yok.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=miktar)

    await interaction.followup.send(
        f"{EMOJIS['yes']} **{len(deleted)}** mesaj silindi.",
        ephemeral=True,
    )


@bot.tree.command(name="sil", description="Belirtilen mesajı siler.")
@app_commands.describe(mesaj_id="Silinecek mesajın ID'si.")
async def sil(interaction, mesaj_id: str):

    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Yetkin yok.",
            ephemeral=True,
        )
        return

    try:
        message = await interaction.channel.fetch_message(int(mesaj_id))
        await message.delete()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Mesaj silindi.",
            ephemeral=True,
        )

    except Exception:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Mesaj bulunamadı.",
            ephemeral=True,
        )


@bot.tree.command(name="ban", description="Üyeyi yasaklar.")
@app_commands.describe(
    kullanıcı="Yasaklanacak kullanıcı.",
    sebep="Ban sebebi.",
)
async def ban(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi.",
):

    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Ban yetkin yok.",
            ephemeral=True,
        )
        return

    try:
        await kullanıcı.ban(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} yasaklandı."
        )

        await send_log(
            interaction.guild,
            f"🔨 {kullanıcı} banlandı.\nYetkili: {interaction.user.mention}\nSebep: {sebep}",
        )

    except Exception as e:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Ban işlemi başarısız: `{e}`",
            ephemeral=True,
        )


@bot.tree.command(name="kick", description="Üyeyi sunucudan atar.")
@app_commands.describe(
    kullanıcı="Atılacak kullanıcı.",
    sebep="Kick sebebi.",
)
async def kick(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi.",
):

    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kick yetkin yok.",
            ephemeral=True,
        )
        return

    try:
        await kullanıcı.kick(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} sunucudan atıldı."
        )

        await send_log(
            interaction.guild,
            f"👢 {kullanıcı} kicklendi.\nYetkili: {interaction.user.mention}\nSebep: {sebep}",
        )

    except Exception as e:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kick işlemi başarısız: `{e}`",
            ephemeral=True,
        )


@bot.tree.command(name="timeout", description="Üyeye timeout verir.")
@app_commands.describe(
    kullanıcı="Timeout verilecek kullanıcı.",
    dakika="Timeout süresi.",
    sebep="Sebep.",
)
async def timeout(
    interaction,
    kullanıcı: discord.Member,
    dakika: app_commands.Range[int, 1, 40320],
    sebep: str = "Sebep belirtilmedi.",
):

    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Timeout yetkin yok.",
            ephemeral=True,
        )
        return

    try:
        await kullanıcı.timeout(
            timedelta(minutes=dakika),
            reason=sebep,
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} **{dakika} dakika** timeout aldı."
        )

        await send_log(
            interaction.guild,
            f"⏱️ {kullanıcı} timeout aldı.\nYetkili: {interaction.user.mention}\nSüre: {dakika} dakika\nSebep: {sebep}",
        )

    except Exception as e:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Timeout başarısız: `{e}`",
            ephemeral=True,
        )


@bot.tree.command(name="uyar", description="Üyeyi uyarır.")
@app_commands.describe(
    kullanıcı="Uyarılacak kullanıcı.",
    sebep="Uyarı sebebi.",
)
async def uyar(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi.",
):

    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Yetkin yok.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"{EMOJIS['yes']} {kullanıcı.mention} uyarıldı.\n**Sebep:** {sebep}"
    )

    await send_log(
        interaction.guild,
        f"⚠️ {kullanıcı} uyarıldı.\nYetkili: {interaction.user.mention}\nSebep: {sebep}",
    )


@bot.tree.command(name="kilitle", description="Kanalı kilitler.")
async def kilitle(interaction):

    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kanal yönetme yetkin yok.",
            ephemeral=True,
        )
        return

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite,
    )

    await interaction.response.send_message(
        f"{EMOJIS['locked']} Kanal kilitlendi."
    )


@bot.tree.command(name="kilit-aç", description="Kanalın kilidini açar.")
async def kilit_ac(interaction):

    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kanal yönetme yetkin yok.",
            ephemeral=True,
        )
        return

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = True

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite,
    )

    await interaction.response.send_message(
        f"{EMOJIS['unlock']} Kanalın kilidi açıldı."
    )


@bot.tree.command(name="yavaş-mod", description="Kanal yavaş modunu ayarlar.")
@app_commands.describe(saniye="Yavaş mod süresi.")
async def yavas_mod(
    interaction,
    saniye: app_commands.Range[int, 0, 21600],
):

    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Yetkin yok.",
            ephemeral=True,
        )
        return

    await interaction.channel.edit(slowmode_delay=saniye)

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Yavaş mod **{saniye} saniye** olarak ayarlandı."
    )


# =========================================================
# DUYURU
# =========================================================

@bot.tree.command(name="duyuru", description="Duyuru gönderir.")
@app_commands.describe(
    başlık="Duyuru başlığı.",
    mesaj="Duyuru mesajı.",
)
async def duyuru(
    interaction,
    başlık: str,
    mesaj: str,
):

    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Yetkin yok.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title=başlık,
        description=mesaj,
        color=discord.Color.blurple(),
    )

    embed.set_footer(
        text=f"Duyuran: {interaction.user.display_name}"
    )

    await interaction.response.send_message(
        embed=embed,
    )


# =========================================================
# WELCOME + AUTOROLE
# =========================================================

@bot.event
async def on_member_join(member):

    cfg = guild_config(member.guild)

    role_id = cfg["autorole"].get("role_id")

    if role_id:
        role = member.guild.get_role(role_id)

        if role:
            try:
                await member.add_roles(role, reason="Dynex Otorol")
            except Exception:
                pass

    welcome = cfg["welcome"]

    channel_id = welcome.get("channel_id")

    if channel_id:
        channel = member.guild.get_channel(channel_id)

        if channel:
            try:
                description = welcome.get(
                    "description",
                    "{user} sunucumuza hoş geldin!",
                )

                description = description.replace(
                    "{user}",
                    member.mention,
                )

                embed = discord.Embed(
                    title=welcome.get(
                        "title",
                        "Hoş Geldin!",
                    ),
                    description=description,
                    color=discord.Color.green(),
                )

                if welcome.get("image"):
                    embed.set_image(
                        url=welcome["image"]
                    )

                await channel.send(
                    embed=embed
                )

            except Exception:
                pass

    dm_message = welcome.get("dm_message")

    if dm_message:
        try:
            await member.send(
                dm_message.replace(
                    "{user}",
                    member.mention,
                )
            )
        except Exception:
            pass


# =========================================================
# MESSAGE EVENTS
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.guild:

        cfg = guild_config(message.guild)

        # BAD WORDS
        bad_words = cfg["moderation"].get(
            "bad_words",
            [],
        )

        content_lower = message.content.lower()

        if bad_words:
            if any(word in content_lower for word in bad_words):

                try:
                    await message.delete()
                except Exception:
                    pass

                await send_log(
                    message.guild,
                    f"🚫 Yasaklı kelime nedeniyle mesaj silindi.\n"
                    f"Kullanıcı: {message.author.mention}\n"
                    f"Kanal: {message.channel.mention}",
                )

                return

        # ANTI LINK
        if cfg["moderation"].get("anti_link"):

            if (
                "http://" in content_lower
                or "https://" in content_lower
                or "discord.gg/" in content_lower
            ):

                if not message.author.guild_permissions.manage_messages:

                    try:
                        await message.delete()
                    except Exception:
                        pass

                    try:
                        await message.channel.send(
                            f"{EMOJIS['no']} {message.author.mention}, bu kanalda bağlantı paylaşamazsın.",
                            delete_after=5,
                        )
                    except Exception:
                        pass

                    return

    await bot.process_commands(message)


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()

        print(
            f"{len(synced)} slash komutu senkronize edildi."
        )

    except Exception as e:
        print(
            f"Slash komut senkronizasyon hatası: {e}"
        )

    print(
        f"Dynex giriş yaptı: {bot.user} ({bot.user.id})"
    )

    print(
        f"Sunucu sayısı: {len(bot.guilds)}"
    )


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction,
    error,
):

    print(
        f"/{interaction.command.name if interaction.command else 'bilinmeyen'} hatası: {repr(error)}"
    )

    try:

        if interaction.response.is_done():
            await interaction.followup.send(
                f"{EMOJIS['no']} Komut çalıştırılırken bir hata oluştu.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Komut çalıştırılırken bir hata oluştu.",
                ephemeral=True,
            )

    except Exception:
        pass


# =========================================================
# START
# =========================================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
