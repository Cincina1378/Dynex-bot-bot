import os
import json
import copy
import random
import asyncio
import time
from pathlib import Path
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# AYARLAR
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

CONFIG_FILE = Path("config.json")

SUPPORT_SERVER_ID = 1551647711332139098
SUPPORT_INVITE = "https://discord.gg/2pFJwJNDR"


# =========================================================
# DYNEX EMOJİLERİ
# =========================================================

EMOJI = {
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
    "boost": "<:Takviye:1555263624787005470>",
    "correct": "<:Doru:1555263630440923187>",
    "discord": "<:Discord:1555263704646557816>",
    "no": "<:Dynexhayir:1555265003727102134>",
}


# =========================================================
# VARSAYILAN SUNUCU AYARLARI
# =========================================================

DEFAULT_GUILD_CONFIG = {
    "ticket": {
        "category_id": None,
        "staff_role_id": None,
        "panel_channel_id": None,
        "panel_title": "Destek Talebi",
        "panel_description": "Destek almak için aşağıdaki butona bas.",
        "panel_image": None,
        "button_label": "Destek Talebi",
        "button_emoji": "🎫",
        "options": [],
    },

    "welcome": {
        "channel_id": None,
        "title": "Sunucumuza Hoş Geldin!",
        "description": "{member} sunucumuza katıldı.",
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
        "join_message": "{member} ses kanalına katıldı.",
        "leave_message": "{member} ses kanalından ayrıldı.",
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

    "language": "tr",

    "warnings": {},

    "games": {
        "number_channel_id": None,
        "number_target": 50,
        "number_current": 0,
        "number_started": False,

        "word_channel_id": None,
        "words": [],
        "word_current": None,
        "word_started": False,
    },
}


# =========================================================
# DİL SİSTEMİ
# =========================================================

LANGUAGES = {
    "tr": {
        "name": "Türkçe",

        "settings": "Dynex Ayarları",
        "settings_desc": "Sunucu ayarlarını buradan yönetebilirsin.",

        "language": "Sunucu Dili",
        "language_select": "Sunucuda Dynex'in kullanacağı dili seç.",

        "language_saved": "Sunucu dili Türkçe olarak ayarlandı.",
        "language_changed": "Dil değiştirildi.",

        "bot_status": "Dynex Durum",
        "server_count": "Sunucu sayısı",
        "support_server": "Destek sunucusu",
        "prefix": "Prefix",
        "uptime": "Çalışma süresi",
        "owner": "Bot sahibi",

        "help": "Yardım",
        "ping": "Ping",
        "user": "Kullanıcı",
        "avatar": "Avatar",
        "server": "Sunucu",
        "roles": "Roller",

        "success": "Başarılı",
        "error": "Hata",
        "no_permission": "Bu komutu kullanmak için yetkin yok.",
        "not_found": "Bulunamadı.",
        "back": "Geri",

        "ticket": "Ticket",
        "welcome": "Karşılama",
        "moderation": "Moderasyon",
        "logs": "Loglar",
        "autorole": "Otorol",
        "voice": "Ses",
        "giveaway": "Çekiliş",
        "dm": "DM",
    },

    "en": {
        "name": "English",

        "settings": "Dynex Settings",
        "settings_desc": "Manage the server settings here.",

        "language": "Server Language",
        "language_select": "Choose the language Dynex will use on this server.",

        "language_saved": "Server language has been set to English.",
        "language_changed": "Language changed.",

        "bot_status": "Dynex Status",
        "server_count": "Server count",
        "support_server": "Support server",
        "prefix": "Prefix",
        "uptime": "Uptime",
        "owner": "Bot owner",

        "help": "Help",
        "ping": "Ping",
        "user": "User",
        "avatar": "Avatar",
        "server": "Server",
        "roles": "Roles",

        "success": "Success",
        "error": "Error",
        "no_permission": "You do not have permission to use this command.",
        "not_found": "Not found.",
        "back": "Back",

        "ticket": "Ticket",
        "welcome": "Welcome",
        "moderation": "Moderation",
        "logs": "Logs",
        "autorole": "Auto Role",
        "voice": "Voice",
        "giveaway": "Giveaway",
        "dm": "DM",
    },

    "az": {
        "name": "Azərbaycan dili",

        "settings": "Dynex Ayarları",
        "settings_desc": "Server ayarlarını buradan idarə et.",

        "language": "Server Dili",
        "language_select": "Dynex-in bu serverdə istifadə edəcəyi dili seç.",

        "language_saved": "Server dili Azərbaycan dili olaraq təyin edildi.",
        "language_changed": "Dil dəyişdirildi.",

        "bot_status": "Dynex Vəziyyəti",
        "server_count": "Server sayı",
        "support_server": "Dəstək serveri",
        "prefix": "Prefix",
        "uptime": "İşləmə müddəti",
        "owner": "Bot sahibi",

        "help": "Kömək",
        "ping": "Ping",
        "user": "İstifadəçi",
        "avatar": "Avatar",
        "server": "Server",
        "roles": "Rollar",

        "success": "Uğurlu",
        "error": "Xəta",
        "no_permission": "Bu əmrdən istifadə etmək üçün icazən yoxdur.",
        "not_found": "Tapılmadı.",
        "back": "Geri",

        "ticket": "Ticket",
        "welcome": "Qarşılama",
        "moderation": "Moderasiya",
        "logs": "Loglar",
        "autorole": "Avtorol",
        "voice": "Səs",
        "giveaway": "Çəkiliş",
        "dm": "DM",
    },
}


# =========================================================
# CONFIG
# =========================================================

def deep_merge(target, defaults):
    for key, value in defaults.items():

        if isinstance(value, dict):

            if not isinstance(target.get(key), dict):
                target[key] = {}

            deep_merge(target[key], value)

        elif key not in target:
            target[key] = copy.deepcopy(value)


def load_config():

    if not CONFIG_FILE.exists():
        return {}

    try:
        data = json.loads(
            CONFIG_FILE.read_text(encoding="utf-8")
        )

        if not isinstance(data, dict):
            return {}

        return data

    except Exception:
        return {}


CONFIG = load_config()


def save_config():

    CONFIG_FILE.write_text(
        json.dumps(
            CONFIG,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def get_guild_config(guild_id):

    guild_id = str(guild_id)

    if guild_id not in CONFIG:
        CONFIG[guild_id] = copy.deepcopy(
            DEFAULT_GUILD_CONFIG
        )

    else:
        if not isinstance(CONFIG[guild_id], dict):
            CONFIG[guild_id] = copy.deepcopy(
                DEFAULT_GUILD_CONFIG
            )

        deep_merge(
            CONFIG[guild_id],
            DEFAULT_GUILD_CONFIG
        )

    language = CONFIG[guild_id].get(
        "language",
        "tr"
    )

    if language not in LANGUAGES:
        CONFIG[guild_id]["language"] = "tr"

    return CONFIG[guild_id]


def get_language(guild):

    config = get_guild_config(guild.id)

    language = config.get(
        "language",
        "tr"
    )

    if language not in LANGUAGES:
        language = "tr"

    return language


def t(guild, key, **kwargs):

    language = get_language(guild)

    value = LANGUAGES[language].get(
        key,
        LANGUAGES["tr"].get(key, key)
    )

    try:
        return value.format(**kwargs)
    except Exception:
        return value


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()

intents.members = True
intents.message_content = True
intents.presences = True


bot = commands.Bot(
    command_prefix="D.",
    intents=intents
)


START_TIME = time.time()
SYNC_DONE = False


# =========================================================
# YARDIMCI
# =========================================================

def black_color():

    return discord.Color.from_rgb(
        0,
        0,
        0
    )


def uptime_text():

    seconds = int(
        time.time() - START_TIME
    )

    days, seconds = divmod(
        seconds,
        86400
    )

    hours, seconds = divmod(
        seconds,
        3600
    )

    minutes, seconds = divmod(
        seconds,
        60
    )

    parts = []

    if days:
        parts.append(f"{days}g")

    if hours:
        parts.append(f"{hours}s")

    if minutes:
        parts.append(f"{minutes}d")

    parts.append(f"{seconds}sn")

    return " ".join(parts)


def parse_emoji(value, guild):

    if not value:
        return None

    value = str(value).strip()

    if value.startswith("<:") or value.startswith("<a:"):

        try:
            return discord.PartialEmoji.from_str(
                value
            )

        except Exception:
            return None

    if value.startswith(":") and value.endswith(":"):

        name = value[1:-1].strip()

        return discord.utils.get(
            guild.emojis,
            name=name
        )

    return value


async def send_log(
    guild,
    setting,
    title,
    description
):

    config = get_guild_config(
        guild.id
    )

    logs = config["logs"]

    if not logs.get(setting):
        return

    channel_id = logs.get(
        "channel_id"
    )

    if not channel_id:
        return

    channel = guild.get_channel(
        channel_id
    )

    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=black_color(),
        timestamp=discord.utils.utcnow()
    )

    try:
        await channel.send(
            embed=embed
        )

    except discord.HTTPException:
        pass


# =========================================================
# AYARLAR EMBED
# =========================================================

def settings_embed(guild):

    config = get_guild_config(
        guild.id
    )

    language = config["language"]

    embed = discord.Embed(
        title=f"{EMOJI['settings']} {t(guild, 'settings')}",
        description=t(
            guild,
            "settings_desc"
        ),
        color=black_color()
    )

    embed.add_field(
        name=t(guild, "language"),
        value=LANGUAGES[
            language
        ]["name"],
        inline=False
    )

    return embed


def language_embed(guild):

    language = get_language(
        guild
    )

    embed = discord.Embed(
        title=f"{EMOJI['settings']} {t(guild, 'language')}",
        description=(
            f"{t(guild, 'language_select')}\n\n"
            f"**{LANGUAGES[language]['name']}**"
        ),
        color=black_color()
    )

    return embed


# =========================================================
# AYARLAR - GERİ
# =========================================================

class SettingsBackButton(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Geri",
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild
            ),
            view=SettingsView()
        )


# =========================================================
# DİL SELECT
# =========================================================

class LanguageSelect(
    discord.ui.Select
):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Türkçe",
                value="tr",
                emoji="🇹🇷"
            ),

            discord.SelectOption(
                label="English",
                value="en",
                emoji="🇬🇧"
            ),

            discord.SelectOption(
                label="Azərbaycan dili",
                value="az",
                emoji="🇦🇿"
            ),

        ]

        super().__init__(
            placeholder="Dil / Language",
            options=options
        )

    async def callback(
        self,
        interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                t(
                    interaction.guild,
                    "no_permission"
                ),
                ephemeral=True
            )

            return

        selected = self.values[0]

        config = get_guild_config(
            interaction.guild.id
        )

        config["language"] = selected

        save_config()

        await interaction.response.edit_message(
            embed=language_embed(
                interaction.guild
            ),
            view=LanguageView()
        )


class LanguageView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=180
        )

        self.add_item(
            LanguageSelect()
        )

        self.add_item(
            SettingsBackButton()
        )


# =========================================================
# AYARLAR ANA SELECT
# =========================================================

class SettingsSelect(
    discord.ui.Select
):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Ticket",
                value="ticket",
                emoji="🎫"
            ),

            discord.SelectOption(
                label="Welcome",
                value="welcome",
                emoji="👋"
            ),

            discord.SelectOption(
                label="Moderation",
                value="moderation",
                emoji="🛡️"
            ),

            discord.SelectOption(
                label="Logs",
                value="logs",
                emoji="📜"
            ),

            discord.SelectOption(
                label="Autorole",
                value="autorole",
                emoji="🎭"
            ),

            discord.SelectOption(
                label="Voice",
                value="voice",
                emoji="🔊"
            ),

            discord.SelectOption(
                label="Giveaway",
                value="giveaway",
                emoji="🎉"
            ),

            discord.SelectOption(
                label="DM",
                value="dm",
                emoji="✉️"
            ),

            discord.SelectOption(
                label="Language",
                value="language",
                emoji="🌐"
            ),

        ]

        super().__init__(
            placeholder="Kategori seç",
            options=options
        )

    async def callback(
        self,
        interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                t(
                    interaction.guild,
                    "no_permission"
                ),
                ephemeral=True
            )

            return

        selected = self.values[0]

        if selected == "language":

            await interaction.response.edit_message(
                embed=language_embed(
                    interaction.guild
                ),
                view=LanguageView()
            )

            return

        await interaction.response.edit_message(
            embed=category_embed(
                interaction.guild,
                selected
            ),
            view=CategoryView(selected)
        )


class SettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=180
        )

        self.add_item(
            SettingsSelect()
        )


# =========================================================
# KATEGORİ EMBED
# =========================================================

def category_embed(
    guild,
    category
):

    config = get_guild_config(
        guild.id
    )

    names = {

        "ticket": "ticket",
        "welcome": "welcome",
        "moderation": "moderation",
        "logs": "logs",
        "autorole": "autorole",
        "voice": "voice",
        "giveaway": "giveaway",
        "dm": "dm",

    }

    embed = discord.Embed(
        title=(
            f"{EMOJI['settings']} "
            f"{t(guild, names.get(category, category))}"
        ),
        color=black_color()
    )

    data = config.get(
        category,
        {}
    )

    embed.description = (
        "```json\n"
        + json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )[:3500]
        + "\n```"
    )

    return embed


class CategoryView(
    discord.ui.View
):

    def __init__(
        self,
        category
    ):

        super().__init__(
            timeout=180
        )

        self.category = category

        self.add_item(
            SettingsBackButton()
        )


# =========================================================
# /BOT
# =========================================================

@bot.tree.command(
    name="bot",
    description="Bot durumunu gösterir"
)
async def bot_status(
    interaction: discord.Interaction
):

    if not interaction.guild:
        return

    # ÖNEMLİ:
    # Sunucu sayısı sadece botun gerçek guild cache'inden alınır.
    server_count = len(
        bot.guilds
    )

    embed = discord.Embed(
        title=(
            f"{EMOJI['dynex']} "
            f"{t(interaction.guild, 'bot_status')}"
        ),
        color=black_color()
    )

    owner_text = "Bilinmiyor"

    try:

        owner = bot.application.owner

        if owner:
            owner_text = owner.mention

    except Exception:
        pass

    support_guild = bot.get_guild(
        SUPPORT_SERVER_ID
    )

    if support_guild:

        support_members = str(
            support_guild.member_count
        )

    else:

        support_members = "Bilinmiyor"

    embed.add_field(
        name=t(
            interaction.guild,
            "server_count"
        ),
        value=str(server_count),
        inline=True
    )

    embed.add_field(
        name=t(
            interaction.guild,
            "support_server"
        ),
        value=(
            f"{support_members}\n"
            f"{SUPPORT_INVITE}"
        ),
        inline=True
    )

    embed.add_field(
        name=t(
            interaction.guild,
            "prefix"
        ),
        value="D.",
        inline=True
    )

    embed.add_field(
        name=t(
            interaction.guild,
            "uptime"
        ),
        value=uptime_text(),
        inline=True
    )

    embed.add_field(
        name=t(
            interaction.guild,
            "owner"
        ),
        value=owner_text,
        inline=True
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /DİL
# =========================================================

@bot.tree.command(
    name="dil",
    description="Sunucunun bot dilini ayarla"
)
@app_commands.default_permissions(
    administrator=True
)
async def dil(
    interaction: discord.Interaction
):

    if not interaction.guild:
        return

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            t(
                interaction.guild,
                "no_permission"
            ),
            ephemeral=True
        )

        return

    await interaction.response.send_message(
        embed=language_embed(
            interaction.guild
        ),
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Sunucu ayarlarını yönet"
)
@app_commands.default_permissions(
    administrator=True
)
async def ayarlar(
    interaction: discord.Interaction
):

    if not interaction.guild:
        return

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            t(
                interaction.guild,
                "no_permission"
            ),
            ephemeral=True
        )

        return

    await interaction.response.send_message(
        embed=settings_embed(
            interaction.guild
        ),
        view=SettingsView(),
        ephemeral=True
    )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Bot gecikmesini gösterir"
)
async def ping(
    interaction: discord.Interaction
):

    ping_ms = round(
        bot.latency * 1000
    )

    await interaction.response.send_message(
        f"{EMOJI['dynex']} **Ping:** `{ping_ms}ms`"
    )


# =========================================================
# /YARDIM
# =========================================================

@bot.tree.command(
    name="yardim",
    description="Komutları gösterir"
)
async def yardim(
    interaction: discord.Interaction
):

    guild = interaction.guild

    embed = discord.Embed(
        title=(
            f"{EMOJI['about']} "
            f"{t(guild, 'help')}"
        ),
        color=black_color()
    )

    embed.add_field(
        name="Genel",
        value=(
            "`/bot` `/yardim` `/ping` "
            "`/kullanici` `/avatar` "
            "`/sunucu` `/roller`"
        ),
        inline=False
    )

    embed.add_field(
        name="Moderasyon",
        value=(
            "`/uyar` `/uyarilar` "
            "`/uyari-sifirla` `/timeout` "
            "`/kick` `/ban` `/temizle` "
            "`/kilitle` `/kilit-ac` `/yavas-mod` "
            "`/duyuru`"
        ),
        inline=False
    )

    embed.add_field(
        name="Eğlence",
        value=(
            "`/zar` `/yazi-tura` "
            "`/8ball` `/sayi-tahmin`"
        ),
        inline=False
    )

    embed.add_field(
        name="Sistem",
        value=(
            "`/ayarlar` `/dil` `/dm` "
            "`/ticket-panel`"
        ),
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# =========================================================
# /SUNUCU
# =========================================================

@bot.tree.command(
    name="sunucu",
    description="Sunucu bilgilerini göster"
)
async def sunucu(
    interaction: discord.Interaction
):

    guild = interaction.guild

    embed = discord.Embed(
        title=(
            f"{EMOJI['server']} "
            f"{t(guild, 'server')}"
        ),
        color=black_color()
    )

    embed.add_field(
        name="Ad",
        value=guild.name,
        inline=True
    )

    embed.add_field(
        name="ID",
        value=str(guild.id),
        inline=True
    )

    embed.add_field(
        name="Üye",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="Kanal",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="Rol",
        value=str(len(guild.roles)),
        inline=True
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /ROLLER
# =========================================================

@bot.tree.command(
    name="roller",
    description="Sunucu rollerini göster"
)
async def roller(
    interaction: discord.Interaction
):

    guild = interaction.guild

    role_text = "\n".join(
        f"`{role.id}` — {role.name}"
        for role in guild.roles[-50:]
    )

    embed = discord.Embed(
        title=t(guild, "roles"),
        description=role_text,
        color=black_color()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# =========================================================
# /KULLANICI
# =========================================================

@bot.tree.command(
    name="kullanici",
    description="Kullanıcı bilgilerini göster"
)
@app_commands.describe(
    kullanici="Kullanıcı"
)
async def kullanici(
    interaction: discord.Interaction,
    kullanici: discord.Member = None
):

    user = kullanici or interaction.user

    embed = discord.Embed(
        title=t(
            interaction.guild,
            "user"
        ),
        color=black_color()
    )

    embed.set_thumbnail(
        url=user.display_avatar.url
    )

    embed.add_field(
        name="ID",
        value=str(user.id)
    )

    embed.add_field(
        name="Hesap oluşturulma",
        value=discord.utils.format_dt(
            user.created_at,
            "F"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /AVATAR
# =========================================================

@bot.tree.command(
    name="avatar",
    description="Kullanıcının avatarını göster"
)
@app_commands.describe(
    kullanici="Kullanıcı"
)
async def avatar(
    interaction: discord.Interaction,
    kullanici: discord.Member = None
):

    user = kullanici or interaction.user

    embed = discord.Embed(
        color=black_color()
    )

    embed.set_image(
        url=user.display_avatar.url
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# ZAR
# =========================================================

@bot.tree.command(
    name="zar",
    description="Zar at"
)
async def zar(
    interaction: discord.Interaction
):

    result = random.randint(
        1,
        6
    )

    await interaction.response.send_message(
        f"🎲 **{result}**"
    )


# =========================================================
# YAZI TURA
# =========================================================

@bot.tree.command(
    name="yazi-tura",
    description="Yazı veya tura at"
)
async def yazi_tura(
    interaction: discord.Interaction
):

    result = random.choice(
        [
            "Yazı",
            "Tura"
        ]
    )

    await interaction.response.send_message(
        f"🪙 **{result}**"
    )


# =========================================================
# 8BALL
# =========================================================

@bot.tree.command(
    name="8ball",
    description="8ball"
)
@app_commands.describe(
    soru="Sorun"
)
async def eightball(
    interaction: discord.Interaction,
    soru: str
):

    answers = [
        "Evet.",
        "Hayır.",
        "Kesinlikle.",
        "Belki.",
        "Bilinmiyor.",
        "Büyük ihtimalle."
    ]

    await interaction.response.send_message(
        f"🎱 {random.choice(answers)}"
    )


# =========================================================
# SAYI TAHMİN
# =========================================================

@bot.tree.command(
    name="sayi-tahmin",
    description="1-100 arasında sayı tahmin et"
)
async def sayi_tahmin(
    interaction: discord.Interaction
):

    number = random.randint(
        1,
        100
    )

    await interaction.response.send_message(
        "🎯 1-100 arasında bir sayı tuttum. "
        "30 saniye içinde kanala tahminini yaz."
    )

    def check(message):

        return (
            message.author.id == interaction.user.id
            and message.channel.id == interaction.channel.id
            and message.content.isdigit()
        )

    try:

        message = await bot.wait_for(
            "message",
            timeout=30,
            check=check
        )

        guess = int(
            message.content
        )

        if guess == number:

            await message.reply(
                f"{EMOJI['correct']} Doğru tahmin!"
            )

        elif guess < number:

            await message.reply(
                "📈 Daha büyük."
            )

        else:

            await message.reply(
                "📉 Daha küçük."
            )

    except asyncio.TimeoutError:

        pass


# =========================================================
# MODERASYON KONTROL
# =========================================================

async def moderation_check(
    interaction,
    permission
):

    if not getattr(
        interaction.user.guild_permissions,
        permission,
        False
    ):

        await interaction.response.send_message(
            t(
                interaction.guild,
                "no_permission"
            ),
            ephemeral=True
        )

        return False

    return True


# =========================================================
# TEMİZLE
# =========================================================

@bot.tree.command(
    name="temizle",
    description="Mesajları temizle"
)
@app_commands.describe(
    miktar="Silinecek mesaj sayısı"
)
async def temizle(
    interaction: discord.Interaction,
    miktar: app_commands.Range[int, 1, 100]
):

    if not await moderation_check(
        interaction,
        "manage_messages"
    ):
        return

    await interaction.response.defer(
        ephemeral=True
    )

    deleted = await interaction.channel.purge(
        limit=miktar
    )

    await interaction.followup.send(
        f"{EMOJI['yes']} `{len(deleted)}` mesaj silindi.",
        ephemeral=True
    )


# =========================================================
# KICK
# =========================================================

@bot.tree.command(
    name="kick",
    description="Üyeyi sunucudan at"
)
@app_commands.describe(
    uye="Üye",
    sebep="Sebep"
)
async def kick(
    interaction: discord.Interaction,
    uye: discord.Member,
    sebep: str = "Belirtilmedi"
):

    if not await moderation_check(
        interaction,
        "kick_members"
    ):
        return

    await uye.kick(
        reason=sebep
    )

    await interaction.response.send_message(
        f"{EMOJI['yes']} {uye.mention} sunucudan atıldı."
    )

    await send_log(
        interaction.guild,
        "kick",
        "Kick",
        f"{uye.mention}\nSebep: {sebep}"
    )


# =========================================================
# BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Üyeyi yasakla"
)
@app_commands.describe(
    uye="Üye",
    sebep="Sebep"
)
async def ban(
    interaction: discord.Interaction,
    uye: discord.Member,
    sebep: str = "Belirtilmedi"
):

    if not await moderation_check(
        interaction,
        "ban_members"
    ):
        return

    await uye.ban(
        reason=sebep
    )

    await interaction.response.send_message(
        f"{EMOJI['yes']} {uye.mention} yasaklandı."
    )

    await send_log(
        interaction.guild,
        "ban",
        "Ban",
        f"{uye.mention}\nSebep: {sebep}"
    )


# =========================================================
# TIMEOUT
# =========================================================

@bot.tree.command(
    name="timeout",
    description="Üyeye timeout uygula"
)
@app_commands.describe(
    uye="Üye",
    dakika="Dakika"
)
async def timeout(
    interaction: discord.Interaction,
    uye: discord.Member,
    dakika: app_commands.Range[int, 1, 10080]
):

    if not await moderation_check(
        interaction,
        "moderate_members"
    ):
        return

    await uye.timeout(
        discord.utils.utcnow()
        + timedelta(minutes=dakika)
    )

    await interaction.response.send_message(
        f"{EMOJI['yes']} {uye.mention} "
        f"`{dakika}` dakika timeout aldı."
    )

    await send_log(
        interaction.guild,
        "timeout",
        "Timeout",
        f"{uye.mention}\nSüre: {dakika} dakika"
    )


# =========================================================
# UYAR
# =========================================================

@bot.tree.command(
    name="uyar",
    description="Üyeyi uyar"
)
@app_commands.describe(
    uye="Üye",
    sebep="Sebep"
)
async def uyar(
    interaction: discord.Interaction,
    uye: discord.Member,
    sebep: str = "Belirtilmedi"
):

    if not await moderation_check(
        interaction,
        "moderate_members"
    ):
        return

    config = get_guild_config(
        interaction.guild.id
    )

    warnings = config["warnings"].setdefault(
        str(uye.id),
        []
    )

    warnings.append(
        {
            "reason": sebep,
            "by": interaction.user.id,
            "time": int(time.time())
        }
    )

    save_config()

    await interaction.response.send_message(
        f"⚠️ {uye.mention} uyarıldı.\n"
        f"Toplam uyarı: `{len(warnings)}`"
    )


# =========================================================
# UYARILAR
# =========================================================

@bot.tree.command(
    name="uyarilar",
    description="Üyenin uyarılarını göster"
)
@app_commands.describe(
    uye="Üye"
)
async def uyarilar(
    interaction: discord.Interaction,
    uye: discord.Member = None
):

    user = uye or interaction.user

    warnings = get_guild_config(
        interaction.guild.id
    )["warnings"].get(
        str(user.id),
        []
    )

    if not warnings:

        await interaction.response.send_message(
            f"{user.mention} için uyarı bulunmuyor.",
            ephemeral=True
        )

        return

    lines = []

    for index, warning in enumerate(
        warnings,
        1
    ):

        lines.append(
            f"**{index}.** "
            f"{warning.get('reason', 'Belirtilmedi')}"
        )

    await interaction.response.send_message(
        "\n".join(lines),
        ephemeral=True
    )


# =========================================================
# UYARI SIFIRLA
# =========================================================

@bot.tree.command(
    name="uyari-sifirla",
    description="Üyenin uyarılarını sıfırla"
)
@app_commands.describe(
    uye="Üye"
)
async def uyarı_sifirla(
    interaction: discord.Interaction,
    uye: discord.Member
):

    if not await moderation_check(
        interaction,
        "moderate_members"
    ):
        return

    config = get_guild_config(
        interaction.guild.id
    )

    config["warnings"].pop(
        str(uye.id),
        None
    )

    save_config()

    await interaction.response.send_message(
        f"{EMOJI['yes']} {uye.mention} uyarıları sıfırlandı."
    )


# =========================================================
# KİLİTLE
# =========================================================

@bot.tree.command(
    name="kilitle",
    description="Kanalı kilitle"
)
async def kilitle(
    interaction: discord.Interaction
):

    if not await moderation_check(
        interaction,
        "manage_channels"
    ):
        return

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        send_messages=False
    )

    await interaction.response.send_message(
        f"{EMOJI['locked']} Kanal kilitlendi."
    )


# =========================================================
# KİLİT AÇ
# =========================================================

@bot.tree.command(
    name="kilit-ac",
    description="Kanal kilidini aç"
)
async def kilit_ac(
    interaction: discord.Interaction
):

    if not await moderation_check(
        interaction,
        "manage_channels"
    ):
        return

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        send_messages=None
    )

    await interaction.response.send_message(
        f"{EMOJI['unlock']} Kanal kilidi açıldı."
    )


# =========================================================
# YAVAŞ MOD
# =========================================================

@bot.tree.command(
    name="yavas-mod",
    description="Yavaş modu ayarla"
)
@app_commands.describe(
    saniye="0 = kapalı"
)
async def yavas_mod(
    interaction: discord.Interaction,
    saniye: app_commands.Range[int, 0, 21600]
):

    if not await moderation_check(
        interaction,
        "manage_channels"
    ):
        return

    await interaction.channel.edit(
        slowmode_delay=saniye
    )

    await interaction.response.send_message(
        f"{EMOJI['yes']} Yavaş mod: `{saniye}` saniye."
    )


# =========================================================
# DUYURU
# =========================================================

@bot.tree.command(
    name="duyuru",
    description="Duyuru gönder"
)
@app_commands.describe(
    mesaj="Duyuru mesajı"
)
async def duyuru(
    interaction: discord.Interaction,
    mesaj: str
):

    if not await moderation_check(
        interaction,
        "manage_messages"
    ):
        return

    embed = discord.Embed(
        title="📢 Duyuru",
        description=mesaj,
        color=black_color()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# TICKET - KAPAT
# =========================================================

class TicketCloseView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Ticket Kapat",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_ticket_close"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.channel.name.startswith(
            "ticket-"
        ):
            return

        await interaction.response.send_message(
            "Ticket kapatılıyor..."
        )

        await asyncio.sleep(
            1
        )

        try:
            await interaction.channel.delete()
        except discord.HTTPException:
            pass


# =========================================================
# TICKET - AÇ
# =========================================================

class TicketOpenView(
    discord.ui.View
):

    def __init__(
        self,
        guild=None
    ):

        super().__init__(
            timeout=None
        )

        config = None

        if guild:

            config = get_guild_config(
                guild.id
            )["ticket"]

        button = discord.ui.Button(
            label=(
                config.get(
                    "button_label"
                )
                if config
                else "Destek Talebi"
            ) or "Destek Talebi",

            style=discord.ButtonStyle.primary,

            custom_id="dynex_ticket_open"
        )

        if guild and config:

            emoji = parse_emoji(
                config.get(
                    "button_emoji"
                ),
                guild
            )

            if emoji:

                button.emoji = emoji

        button.callback = self.open_ticket

        self.add_item(
            button
        )

    async def open_ticket(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        config = get_guild_config(
            guild.id
        )["ticket"]

        # Aynı kişinin açık ticketini kontrol et

        for channel in guild.text_channels:

            if channel.topic == (
                f"ticket-owner:{interaction.user.id}"
            ):

                await interaction.response.send_message(
                    f"{EMOJI['no']} Zaten açık ticketin var: "
                    f"{channel.mention}",
                    ephemeral=True
                )

                return

        category = None

        if config.get(
            "category_id"
        ):

            category = guild.get_channel(
                config["category_id"]
            )

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True
                )
        }

        staff_role_id = config.get(
            "staff_role_id"
        )

        if staff_role_id:

            staff_role = guild.get_role(
                staff_role_id
            )

            if staff_role:

                overwrites[staff_role] = (
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True
                    )
                )

        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}"[:90],
            category=category,
            overwrites=overwrites,
            topic=(
                f"ticket-owner:"
                f"{interaction.user.id}"
            )
        )

        await channel.send(
            f"{interaction.user.mention} ticket oluşturuldu.",
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{EMOJI['yes']} Ticket oluşturuldu: "
            f"{channel.mention}",
            ephemeral=True
        )


# =========================================================
# TICKET PANEL
# =========================================================

@bot.tree.command(
    name="ticket-panel",
    description="Ticket paneli gönder"
)
async def ticket_panel(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.manage_guild:

        await interaction.response.send_message(
            t(
                interaction.guild,
                "no_permission"
            ),
            ephemeral=True
        )

        return

    config = get_guild_config(
        interaction.guild.id
    )["ticket"]

    channel = interaction.channel

    if config.get(
        "panel_channel_id"
    ):

        configured_channel = interaction.guild.get_channel(
            config["panel_channel_id"]
        )

        if configured_channel:

            channel = configured_channel

    embed = discord.Embed(
        title=config.get(
            "panel_title"
        ) or "Destek Talebi",

        description=config.get(
            "panel_description"
        ) or "Destek almak için butona bas.",

        color=black_color()
    )

    if config.get(
        "panel_image"
    ):

        embed.set_image(
            url=config["panel_image"]
        )

    await channel.send(
        embed=embed,
        view=TicketOpenView(
            interaction.guild
        )
    )

    await interaction.response.send_message(
        f"{EMOJI['yes']} Ticket paneli gönderildi.",
        ephemeral=True
    )


# =========================================================
# TOPLU DM
# =========================================================

@bot.tree.command(
    name="dm",
    description="Bir role toplu DM gönder"
)
@app_commands.describe(
    rol="Hedef rol"
)
async def dm(
    interaction: discord.Interaction,
    rol: discord.Role
):

    config = get_guild_config(
        interaction.guild.id
    )

    allowed_roles = config["dm"].get(
        "allowed_role_ids",
        []
    )

    has_access = (
        interaction.user.guild_permissions.administrator
        or any(
            role.id in allowed_roles
            for role in interaction.user.roles
        )
    )

    if not has_access:

        await interaction.response.send_message(
            t(
                interaction.guild,
                "no_permission"
            ),
            ephemeral=True
        )

        return

    class DMModal(
        discord.ui.Modal,
        title="Toplu DM"
    ):

        baslik = discord.ui.TextInput(
            label="Başlık",
            max_length=100
        )

        mesaj = discord.ui.TextInput(
            label="Mesaj",
            style=discord.TextStyle.paragraph,
            max_length=2000
        )

        async def on_submit(
            self,
            modal_interaction
        ):

            await modal_interaction.response.send_message(
                "DM gönderimi başladı.",
                ephemeral=True
            )

            sent = 0

            for member in rol.members:

                if member.bot:
                    continue

                try:

                    await member.send(
                        f"**{self.baslik.value}**\n\n"
                        f"{self.mesaj.value}"
                    )

                    sent += 1

                except discord.HTTPException:
                    pass

                await asyncio.sleep(
                    0.15
                )

            try:

                await modal_interaction.followup.send(
                    f"{EMOJI['yes']} "
                    f"{sent} kişiye gönderildi.",
                    ephemeral=True
                )

            except discord.HTTPException:
                pass

    await interaction.response.send_modal(
        DMModal()
    )


# =========================================================
# KARŞILAMA
# =========================================================

@bot.event
async def on_member_join(
    member: discord.Member
):

    config = get_guild_config(
        member.guild.id
    )

    welcome = config["welcome"]

    channel = None

    if welcome.get(
        "channel_id"
    ):

        channel = member.guild.get_channel(
            welcome["channel_id"]
        )

    if channel:

        description = welcome[
            "description"
        ].format(
            member=member.mention
        )

        embed = discord.Embed(
            title=welcome["title"],
            description=description,
            color=black_color()
        )

        if welcome.get(
            "image"
        ):

            embed.set_image(
                url=welcome["image"]
            )

        try:

            await channel.send(
                embed=embed
            )

        except discord.HTTPException:
            pass

    if welcome.get(
        "dm_message"
    ):

        try:

            await member.send(
                welcome[
                    "dm_message"
                ].format(
                    member=member.mention,
                    guild=member.guild.name
                )
            )

        except discord.HTTPException:
            pass

    role_id = config["autorole"].get(
        "role_id"
    )

    if role_id:

        role = member.guild.get_role(
            role_id
        )

        if role:

            try:

                await member.add_roles(
                    role
                )

            except discord.HTTPException:
                pass

    await send_log(
        member.guild,
        "join",
        "Üye katıldı",
        member.mention
    )


# =========================================================
# ÜYE AYRILDI
# =========================================================

@bot.event
async def on_member_remove(
    member
):

    await send_log(
        member.guild,
        "leave",
        "Üye ayrıldı",
        member.mention
    )


# =========================================================
# MESAJ SİLİNDİ
# =========================================================

@bot.event
async def on_message_delete(
    message
):

    if not message.guild:
        return

    if message.author.bot:
        return

    await send_log(
        message.guild,
        "delete",
        "Mesaj silindi",
        (
            f"{message.author.mention}\n"
            f"{message.content[:1000]}"
        )
    )


# =========================================================
# MESAJ DÜZENLENDİ
# =========================================================

@bot.event
async def on_message_edit(
    before,
    after
):

    if not before.guild:
        return

    if before.author.bot:
        return

    if before.content == after.content:
        return

    await send_log(
        before.guild,
        "edit",
        "Mesaj düzenlendi",
        (
            f"{before.author.mention}\n\n"
            f"Önce:\n{before.content[:500]}\n\n"
            f"Sonra:\n{after.content[:500]}"
        )
    )


# =========================================================
# SES
# =========================================================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if before.channel == after.channel:
        return

    config = get_guild_config(
        member.guild.id
    )

    voice_config = config["voice"]

    channel_id = voice_config.get(
        "channel_id"
    )

    if not channel_id:
        return

    channel = member.guild.get_channel(
        channel_id
    )

    if not channel:
        return

    if after.channel:

        message = voice_config[
            "join_message"
        ]

        voice_channel = after.channel

    else:

        message = voice_config[
            "leave_message"
        ]

        voice_channel = before.channel

    message = message.format(
        member=member.mention,
        channel=voice_channel.mention
        if voice_channel else ""
    )

    try:

        await channel.send(
            message
        )

    except discord.HTTPException:
        pass


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    global SYNC_DONE

    if not SYNC_DONE:

        try:

            await bot.tree.sync()

            SYNC_DONE = True

            print(
                f"Slash komutları senkronlandı."
            )

        except Exception as error:

            print(
                f"Slash sync hatası: {error}"
            )

    print(
        f"BOT AKTİF: {bot.user}"
    )

    print(
        f"GERÇEK SUNUCU SAYISI: {len(bot.guilds)}"
    )


# =========================================================
# PERSISTENT VIEWS
# =========================================================

async def setup_persistent_views():

    bot.add_view(
        TicketCloseView()
    )

    bot.add_view(
        TicketOpenView()
    )


# =========================================================
# STARTUP
# =========================================================

async def main():

    if not TOKEN:

        raise RuntimeError(
            "DISCORD_TOKEN ortam değişkeni bulunamadı."
        )

    await setup_persistent_views()

    await bot.start(
        TOKEN
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
