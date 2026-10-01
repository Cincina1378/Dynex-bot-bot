import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime, timezone


# =========================================================
# TOKEN
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = "config.json"


# =========================================================
# INTENTS
# =========================================================

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True
INTENTS.voice_states = True


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
    "no": "<:Dynexhayir:1555265003727102134>"
}


# =========================================================
# DİLLER
# =========================================================

LANGUAGES = {
    "tr": "🇹🇷 Türkçe",
    "en": "🇬🇧 English",
    "az": "🇦🇿 Azərbaycan"
}


TEXTS = {

    "tr": {
        "language_title": "Dynex Dil Seçimi",
        "language_description": "Dynex'in kullanacağı dili seçin.",
        "language_changed": "Dil Türkçe olarak ayarlandı.",

        "ping_title": "Dynex Ping Durumu",
        "ping_description": "Dynex'in internet bağlantı durumu",
        "ping": "Ping",
        "excellent": "Mükemmel",
        "good": "İyi",
        "medium": "Orta",
        "weak": "Zayıf",
        "bad": "Berbat",

        "settings_title": "Dynex Ayarları",
        "settings_description": "Sunucu sistemlerini buradan yönetin.",

        "ticket": "Ticket",
        "logs": "Loglar",
        "welcome": "Hoş Geldin",
        "autorole": "Otorol",
        "moderation": "Moderasyon",

        "enabled": "Açık",
        "disabled": "Kapalı",

        "ticket_settings": "Ticket Ayarları",
        "logs_settings": "Log Ayarları",
        "welcome_settings": "Hoş Geldin Ayarları",
        "autorole_settings": "Otorol Ayarları",
        "moderation_settings": "Moderasyon Ayarları",

        "category": "Kategori",
        "role": "Yetkili Rolü",
        "panel_channel": "Panel Kanalı",
        "log_channel": "Log Kanalı",
        "welcome_channel": "Hoş Geldin Kanalı",
        "autorole_role": "Verilecek Rol",
        "message": "Mesaj",

        "select_category": "Kategori Seç",
        "select_role": "Rol Seç",
        "select_channel": "Kanal Seç",

        "ticket_saved": "Ticket ayarları kaydedildi.",
        "logs_saved": "Log ayarları kaydedildi.",
        "welcome_saved": "Hoş geldin ayarları kaydedildi.",
        "autorole_saved": "Otorol ayarları kaydedildi.",
        "moderation_saved": "Moderasyon ayarları kaydedildi.",

        "refresh": "Yenile",
        "reset": "Sıfırla",
        "back": "Geri",

        "ticket_open": "Ticket Aç",
        "ticket_close": "Ticket Kapat",
        "add_member": "Üye Ekle",

        "ticket_created": "Ticket oluşturuldu.",
        "ticket_closed": "Ticket kapatılıyor.",
        "ticket_disabled": "Ticket sistemi kapalı.",

        "problem": "Sorun",
        "problem_placeholder": "Sorununuzu yazın.",

        "member_id": "Üye ID",
        "member_id_placeholder": "Eklenecek üyenin Discord ID'si",
        "member_added": "Üye ticket'a eklendi.",
        "invalid_member": "Geçerli bir üye bulunamadı.",

        "permission": "Bu işlem için yetkiniz yok.",
        "reset_done": "Sunucu ayarları sıfırlandı.",

        "voice_title": "Ses Kanalı İstatistikleri",
        "voice_joined": "Katıldığı kanal",
        "voice_left": "Ayrıldığı kanal",
        "voice_duration": "Ses kanalında kalma süresi",
        "voice_members": "Çıkış anındaki üye sayısı",
        "voice_disable": "Ses Bildirimlerini Kapat",
        "voice_enable": "Ses Bildirimlerini Aç",
        "voice_disabled": "Ses bildirimleri kapatıldı.",
        "voice_enabled": "Ses bildirimleri açıldı."
    },

    "en": {
        "language_title": "Dynex Language Selection",
        "language_description": "Select the language Dynex should use.",
        "language_changed": "Language set to English.",

        "ping_title": "Dynex Ping Status",
        "ping_description": "Dynex internet connection status",
        "ping": "Ping",
        "excellent": "Excellent",
        "good": "Good",
        "medium": "Medium",
        "weak": "Weak",
        "bad": "Very Bad",

        "settings_title": "Dynex Settings",
        "settings_description": "Manage server systems here.",

        "ticket": "Ticket",
        "logs": "Logs",
        "welcome": "Welcome",
        "autorole": "Autorole",
        "moderation": "Moderation",

        "enabled": "Enabled",
        "disabled": "Disabled",

        "ticket_settings": "Ticket Settings",
        "logs_settings": "Log Settings",
        "welcome_settings": "Welcome Settings",
        "autorole_settings": "Autorole Settings",
        "moderation_settings": "Moderation Settings",

        "category": "Category",
        "role": "Staff Role",
        "panel_channel": "Panel Channel",
        "log_channel": "Log Channel",
        "welcome_channel": "Welcome Channel",
        "autorole_role": "Autorole",
        "message": "Message",

        "select_category": "Select Category",
        "select_role": "Select Role",
        "select_channel": "Select Channel",

        "ticket_saved": "Ticket settings saved.",
        "logs_saved": "Log settings saved.",
        "welcome_saved": "Welcome settings saved.",
        "autorole_saved": "Autorole settings saved.",
        "moderation_saved": "Moderation settings saved.",

        "refresh": "Refresh",
        "reset": "Reset",
        "back": "Back",

        "ticket_open": "Open Ticket",
        "ticket_close": "Close Ticket",
        "add_member": "Add Member",

        "ticket_created": "Ticket created.",
        "ticket_closed": "Closing ticket.",
        "ticket_disabled": "Ticket system is disabled.",

        "problem": "Problem",
        "problem_placeholder": "Describe your problem.",

        "member_id": "Member ID",
        "member_id_placeholder": "Discord ID of the member",
        "member_added": "Member added to the ticket.",
        "invalid_member": "No valid member was found.",

        "permission": "You do not have permission.",
        "reset_done": "Server settings reset.",

        "voice_title": "Voice Channel Statistics",
        "voice_joined": "Joined channel",
        "voice_left": "Left channel",
        "voice_duration": "Time spent in voice",
        "voice_members": "Members when leaving",
        "voice_disable": "Disable Voice Notifications",
        "voice_enable": "Enable Voice Notifications",
        "voice_disabled": "Voice notifications disabled.",
        "voice_enabled": "Voice notifications enabled."
    },

    "az": {
        "language_title": "Dynex Dil Seçimi",
        "language_description": "Dynex üçün dili seçin.",
        "language_changed": "Dil Azərbaycan dili olaraq təyin edildi.",

        "ping_title": "Dynex Ping Vəziyyəti",
        "ping_description": "Dynex internet bağlantı vəziyyəti",
        "ping": "Ping",
        "excellent": "Əla",
        "good": "Yaxşı",
        "medium": "Orta",
        "weak": "Zəif",
        "bad": "Çox Zəif",

        "settings_title": "Dynex Ayarları",
        "settings_description": "Server sistemlərini buradan idarə edin.",

        "ticket": "Ticket",
        "logs": "Loglar",
        "welcome": "Qarşılama",
        "autorole": "Avtorol",
        "moderation": "Moderasiya",

        "enabled": "Aktiv",
        "disabled": "Deaktiv",

        "ticket_settings": "Ticket Ayarları",
        "logs_settings": "Log Ayarları",
        "welcome_settings": "Qarşılama Ayarları",
        "autorole_settings": "Avtorol Ayarları",
        "moderation_settings": "Moderasiya Ayarları",

        "category": "Kateqoriya",
        "role": "Səlahiyyətli Rolu",
        "panel_channel": "Panel Kanalı",
        "log_channel": "Log Kanalı",
        "welcome_channel": "Qarşılama Kanalı",
        "autorole_role": "Veriləcək Rol",
        "message": "Mesaj",

        "select_category": "Kateqoriya Seç",
        "select_role": "Rol Seç",
        "select_channel": "Kanal Seç",

        "ticket_saved": "Ticket ayarları yadda saxlanıldı.",
        "logs_saved": "Log ayarları yadda saxlanıldı.",
        "welcome_saved": "Qarşılama ayarları yadda saxlanıldı.",
        "autorole_saved": "Avtorol ayarları yadda saxlanıldı.",
        "moderation_saved": "Moderasiya ayarları yadda saxlanıldı.",

        "refresh": "Yenilə",
        "reset": "Sıfırla",
        "back": "Geri",

        "ticket_open": "Ticket Aç",
        "ticket_close": "Ticketi Bağla",
        "add_member": "Üzv Əlavə Et",

        "ticket_created": "Ticket yaradıldı.",
        "ticket_closed": "Ticket bağlanır.",
        "ticket_disabled": "Ticket sistemi deaktivdir.",

        "problem": "Problem",
        "problem_placeholder": "Probleminizi yazın.",

        "member_id": "Üzv ID-si",
        "member_id_placeholder": "Üzvün Discord ID-si",
        "member_added": "Üzv ticketə əlavə edildi.",
        "invalid_member": "Etibarlı üzv tapılmadı.",

        "permission": "Bunu etmək üçün icazəniz yoxdur.",
        "reset_done": "Server ayarları sıfırlandı.",

        "voice_title": "Səs Kanalı Statistikası",
        "voice_joined": "Qoşulduğu kanal",
        "voice_left": "Ayrıldığı kanal",
        "voice_duration": "Səs kanalında qalma müddəti",
        "voice_members": "Çıxış zamanı üzv sayı",
        "voice_disable": "Səs bildirişlərini söndür",
        "voice_enable": "Səs bildirişlərini aktiv et",
        "voice_disabled": "Səs bildirişləri söndürüldü.",
        "voice_enabled": "Səs bildirişləri aktiv edildi."
    }
}


# =========================================================
# DEFAULT CONFIG
# =========================================================

DEFAULT_CONFIG = {
    "language": "tr",

    "ticket": {
        "enabled": True,
        "category": None,
        "role": None,
        "channel": None,
        "message": "Ticket açmak için aşağıdaki butona tıklayın."
    },

    "logs": {
        "enabled": False,
        "channel": None
    },

    "welcome": {
        "enabled": False,
        "channel": None,
        "message": "Hoş geldin {member}!"
    },

    "autorole": {
        "enabled": False,
        "role": None
    },

    "moderation": {
        "enabled": True
    }
}


configs = {}
user_settings = {}
voice_sessions = {}


# =========================================================
# VERİ
# =========================================================

def load_data():

    global configs
    global user_settings

    if not os.path.exists(CONFIG_FILE):
        return

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            configs = data.get(
                "configs",
                {}
            )

            user_settings = data.get(
                "user_settings",
                {}
            )

    except Exception:

        configs = {}
        user_settings = {}


def save_data():

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "configs": configs,
                "user_settings": user_settings
            },
            f,
            ensure_ascii=False,
            indent=4
        )


def get_config(guild_id):

    guild_id = str(guild_id)

    if guild_id not in configs:

        configs[guild_id] = json.loads(
            json.dumps(DEFAULT_CONFIG)
        )

        save_data()

    return configs[guild_id]


def get_language(guild_id):

    language = get_config(
        guild_id
    ).get(
        "language",
        "tr"
    )

    if language not in LANGUAGES:
        language = "tr"

    return language


def set_language(
    guild_id,
    language
):

    if language not in LANGUAGES:
        language = "tr"

    get_config(
        guild_id
    )["language"] = language

    save_data()


def t(
    language,
    key,
    **kwargs
):

    text = TEXTS.get(
        language,
        TEXTS["tr"]
    ).get(
        key,
        TEXTS["tr"].get(
            key,
            key
        )
    )

    try:
        return text.format(
            **kwargs
        )
    except Exception:
        return text


def get_voice_notifications(
    user_id
):

    return user_settings.get(
        str(user_id),
        {}
    ).get(
        "voice_notifications",
        True
    )


def set_voice_notifications(
    user_id,
    value
):

    user_id = str(user_id)

    if user_id not in user_settings:
        user_settings[user_id] = {}

    user_settings[user_id][
        "voice_notifications"
    ] = value

    save_data()


# =========================================================
# BOT
# =========================================================

class DynexBot(
    commands.Bot
):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=INTENTS
        )

    async def setup_hook(self):

        await self.tree.sync()


bot = DynexBot()


# =========================================================
# /DİL
# =========================================================

class LanguageSelect(
    discord.ui.Select
):

    def __init__(self):

        super().__init__(
            placeholder="Dil seçin / Select language",
            custom_id="dynex_language_select",
            options=[
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
                    label="Azərbaycan",
                    value="az",
                    emoji="🇦🇿"
                )
            ]
        )

    async def callback(
        self,
        interaction
    ):

        set_language(
            interaction.guild.id,
            self.values[0]
        )

        await interaction.response.send_message(
            f"{EMOJI['yes']} "
            + t(
                self.values[0],
                "language_changed"
            ),
            ephemeral=True
        )


class LanguageView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            LanguageSelect()
        )


@bot.tree.command(
    name="dil",
    description="Dynex dilini değiştir."
)
async def dil(
    interaction: discord.Interaction
):

    language = get_language(
        interaction.guild.id
    )

    embed = discord.Embed(
        title=(
            f"{EMOJI['dynex']} "
            + t(
                language,
                "language_title"
            )
        ),
        description=t(
            language,
            "language_description"
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun ping durumunu gösterir."
)
async def ping(
    interaction: discord.Interaction
):

    language = get_language(
        interaction.guild.id
    )

    latency = round(
        bot.latency * 1000
    )

    if latency <= 80:
        status = t(
            language,
            "excellent"
        )
        icon = EMOJI["correct"]

    elif latency <= 150:
        status = t(
            language,
            "good"
        )
        icon = EMOJI["yes"]

    elif latency <= 250:
        status = t(
            language,
            "medium"
        )
        icon = EMOJI["wait"]

    elif latency <= 400:
        status = t(
            language,
            "weak"
        )
        icon = EMOJI["alarm"]

    else:
        status = t(
            language,
            "bad"
        )
        icon = EMOJI["no"]

    embed = discord.Embed(
        title=(
            f"{EMOJI['dynex']} "
            + t(
                language,
                "ping_title"
            )
        ),
        description=t(
            language,
            "ping_description"
        ),
        color=discord.Color.from_rgb(
            0,
            0,
            0
        )
    )

    embed.add_field(
        name=t(
            language,
            "ping"
        ),
        value=(
            f"`{latency}ms`\n"
            f"{icon} **{status}**"
        ),
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# AYARLAR EMBED
# =========================================================

def settings_embed(
    guild_id
):

    language = get_language(
        guild_id
    )

    config = get_config(
        guild_id
    )

    def state(name):

        return (
            f"{EMOJI['yes']} "
            + t(language, "enabled")
            if config[name]["enabled"]
            else
            f"{EMOJI['no']} "
            + t(language, "disabled")
        )

    embed = discord.Embed(
        title=(
            f"{EMOJI['settings']} "
            + t(
                language,
                "settings_title"
            )
        ),
        description=t(
            language,
            "settings_description"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=f"{EMOJI['locked']} {t(language, 'ticket')}",
        value=state("ticket"),
        inline=True
    )

    embed.add_field(
        name=f"{EMOJI['about']} {t(language, 'logs')}",
        value=state("logs"),
        inline=True
    )

    embed.add_field(
        name=f"{EMOJI['server']} {t(language, 'welcome')}",
        value=state("welcome"),
        inline=True
    )

    embed.add_field(
        name=f"{EMOJI['correct']} {t(language, 'autorole')}",
        value=state("autorole"),
        inline=True
    )

    embed.add_field(
        name=f"{EMOJI['shield'] if 'shield' in EMOJI else EMOJI['dynex']} {t(language, 'moderation')}",
        value=state("moderation"),
        inline=True
    )

    return embed


# =========================================================
# TICKET AYARLARI
# =========================================================

class TicketSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="🎫 Aç/Kapat",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def toggle(
        self,
        interaction,
        button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["enabled"] = not config[
            "ticket"
        ]["enabled"]

        save_data()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="📁 Kategori",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def category(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Kategori seçmek için aşağıdaki menüyü kullan:",
            view=CategorySelectView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="👮 Rol",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def role(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Yetkili rolünü seç:",
            view=RoleSelectView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="📢 Kanal",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def channel(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Ticket panel kanalını seç:",
            view=ChannelSelectView(
                "ticket"
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="◀️ Geri",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=SettingsView()
        )


def ticket_settings_embed(
    guild_id
):

    language = get_language(
        guild_id
    )

    config = get_config(
        guild_id
    )["ticket"]

    embed = discord.Embed(
        title=(
            f"{EMOJI['locked']} "
            + t(
                language,
                "ticket_settings"
            )
        ),
        description=t(
            language,
            "ticket_description"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(
            language,
            "ticket_status"
        ),
        value=(
            f"{EMOJI['yes']} {t(language, 'enabled')}"
            if config["enabled"]
            else
            f"{EMOJI['no']} {t(language, 'disabled')}"
        ),
        inline=False
    )

    embed.add_field(
        name=t(language, "category"),
        value=(
            f"<#{config['category']}>"
            if config["category"]
            else "—"
        ),
        inline=True
    )

    embed.add_field(
        name=t(language, "role"),
        value=(
            f"<@&{config['role']}>"
            if config["role"]
            else "—"
        ),
        inline=True
    )

    embed.add_field(
        name=t(language, "panel_channel"),
        value=(
            f"<#{config['channel']}>"
            if config["channel"]
            else "—"
        ),
        inline=True
    )

    return embed


# =========================================================
# KATEGORİ SEÇİMİ
# =========================================================

class CategorySelect(
    discord.ui.ChannelSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Kategori seç",
            channel_types=[
                discord.ChannelType.category
            ],
            custom_id="dynex_category_select"
        )

    async def callback(
        self,
        interaction
    ):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["category"] = self.values[0].id

        save_data()

        await interaction.response.send_message(
            f"{EMOJI['yes']} Kategori kaydedildi.",
            ephemeral=True
        )


class CategorySelectView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            CategorySelect()
        )


# =========================================================
# ROL SEÇİMİ
# =========================================================

class RoleSelect(
    discord.ui.RoleSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Yetkili rolünü seç",
            custom_id="dynex_ticket_role_select"
        )

    async def callback(
        self,
        interaction
    ):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["role"] = self.values[0].id

        save_data()

        await interaction.response.send_message(
            f"{EMOJI['yes']} Yetkili rolü kaydedildi.",
            ephemeral=True
        )


class RoleSelectView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            RoleSelect()
        )


# =========================================================
# KANAL SEÇİMİ
# =========================================================

class ChannelSelect(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        target
    ):

        self.target = target

        super().__init__(
            placeholder="Kanal seç",
            channel_types=[
                discord.ChannelType.text
            ],
            custom_id=f"dynex_channel_select:{target}"
        )

    async def callback(
        self,
        interaction
    ):

        config = get_config(
            interaction.guild.id
        )

        channel_id = self.values[0].id

        if self.target == "ticket":

            config["ticket"]["channel"] = channel_id

        elif self.target == "logs":

            config["logs"]["channel"] = channel_id

        elif self.target == "welcome":

            config["welcome"]["channel"] = channel_id

        save_data()

        await interaction.response.send_message(
            f"{EMOJI['yes']} Kanal kaydedildi.",
            ephemeral=True
        )


class ChannelSelectView(
    discord.ui.View
):

    def __init__(
        self,
        target
    ):

        super().__init__(
            timeout=120
        )

        self.add_item(
            ChannelSelect(target)
        )


# =========================================================
# LOG AYARLARI
# =========================================================

def logs_settings_embed(
    guild_id
):

    language = get_language(
        guild_id
    )

    config = get_config(
        guild_id
    )["logs"]

    embed = discord.Embed(
        title=(
            f"{EMOJI['about']} "
            + t(
                language,
                "logs_settings"
            )
        ),
        description=t(
            language,
            "logs_description"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(language, "logs"),
        value=(
            f"{EMOJI['yes']} {t(language, 'enabled')}"
            if config["enabled"]
            else
            f"{EMOJI['no']} {t(language, 'disabled')}"
        )
    )

    embed.add_field(
        name=t(language, "log_channel"),
        value=(
            f"<#{config['channel']}>"
            if config["channel"]
            else "—"
        )
    )

    return embed


class LogsSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="📜 Aç/Kapat",
        style=discord.ButtonStyle.primary
    )
    async def toggle(
        self,
        interaction,
        button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["logs"]["enabled"] = not config[
            "logs"
        ]["enabled"]

        save_data()

        await interaction.response.edit_message(
            embed=logs_settings_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="📢 Kanal Seç",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Log kanalını seç:",
            view=ChannelSelectView(
                "logs"
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="◀️ Geri",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=SettingsView()
        )


# =========================================================
# WELCOME
# =========================================================

def welcome_settings_embed(
    guild_id
):

    language = get_language(
        guild_id
    )

    config = get_config(
        guild_id
    )["welcome"]

    embed = discord.Embed(
        title=(
            f"{EMOJI['server']} "
            + t(
                language,
                "welcome_settings"
            )
        ),
        description=t(
            language,
            "welcome_description"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(language, "welcome"),
        value=(
            f"{EMOJI['yes']} {t(language, 'enabled')}"
            if config["enabled"]
            else
            f"{EMOJI['no']} {t(language, 'disabled')}"
        )
    )

    embed.add_field(
        name=t(language, "welcome_channel"),
        value=(
            f"<#{config['channel']}>"
            if config["channel"]
            else "—"
        )
    )

    embed.add_field(
        name=t(language, "message"),
        value=config["message"],
        inline=False
    )

    return embed


class WelcomeMessageModal(
    discord.ui.Modal,
    title="Hoş Geldin Mesajı"
):

    message = discord.ui.TextInput(
        label="Mesaj",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(
        self,
        interaction
    ):

        config = get_config(
            interaction.guild.id
        )

        config["welcome"]["message"] = self.message.value

        save_data()

        await interaction.response.send_message(
            f"{EMOJI['yes']} Hoş geldin mesajı kaydedildi.",
            ephemeral=True
        )


class WelcomeSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="👋 Aç/Kapat",
        style=discord.ButtonStyle.primary
    )
    async def toggle(
        self,
        interaction,
        button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["welcome"]["enabled"] = not config[
            "welcome"
        ]["enabled"]

        save_data()

        await interaction.response.edit_message(
            embed=welcome_settings_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="📢 Kanal Seç",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Hoş geldin kanalını seç:",
            view=ChannelSelectView(
                "welcome"
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="✏️ Mesaj",
        style=discord.ButtonStyle.secondary
    )
    async def message(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            WelcomeMessageModal()
        )

    @discord.ui.button(
        label="◀️ Geri",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=SettingsView()
        )


# =========================================================
# OTOROL
# =========================================================

def autorole_settings_embed(
    guild_id
):

    language = get_language(
        guild_id
    )

    config = get_config(
        guild_id
    )["autorole"]

    embed = discord.Embed(
        title=(
            f"{EMOJI['correct']} "
            + t(
                language,
                "autorole_settings"
            )
        ),
        description=t(
            language,
            "autorole_description"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(language, "autorole"),
        value=(
            f"{EMOJI['yes']} {t(language, 'enabled')}"
            if config["enabled"]
            else
            f"{EMOJI['no']} {t(language, 'disabled')}"
        )
    )

    embed.add_field(
        name=t(language, "autorole_role"),
        value=(
            f"<@&{config['role']}>"
            if config["role"]
            else "—"
        )
    )

    return embed


class AutoroleSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="👤 Aç/Kapat",
        style=discord.ButtonStyle.primary
    )
    async def toggle(
        self,
        interaction,
        button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["autorole"]["enabled"] = not config[
            "autorole"
        ]["enabled"]

        save_data()

        await interaction.response.edit_message(
            embed=autorole_settings_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="🎭 Rol Seç",
        style=discord.ButtonStyle.secondary
    )
    async def role(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Otorolü seç:",
            view=AutoroleRoleView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="◀️ Geri",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=SettingsView()
        )


class AutoroleSelect(
    discord.ui.RoleSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Otorol seç",
            custom_id="dynex_autorole_select"
        )

    async def callback(
        self,
        interaction
    ):

        config = get_config(
            interaction.guild.id
        )

        config["autorole"]["role"] = self.values[0].id

        save_data()

        await interaction.response.send_message(
            f"{EMOJI['yes']} Otorol kaydedildi.",
            ephemeral=True
        )


class AutoroleRoleView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            AutoroleSelect()
        )


# =========================================================
# MODERASYON
# =========================================================

def moderation_settings_embed(
    guild_id
):

    language = get_language(
        guild_id
    )

    config = get_config(
        guild_id
    )["moderation"]

    embed = discord.Embed(
        title=(
            f"{EMOJI['alarm']} "
            + t(
                language,
                "moderation_settings"
            )
        ),
        description=t(
            language,
            "moderation_description"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(language, "moderation"),
        value=(
            f"{EMOJI['yes']} {t(language, 'enabled')}"
            if config["enabled"]
            else
            f"{EMOJI['no']} {t(language, 'disabled')}"
        )
    )

    return embed


class ModerationSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="🛡️ Aç/Kapat",
        style=discord.ButtonStyle.primary
    )
    async def toggle(
        self,
        interaction,
        button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["moderation"]["enabled"] = not config[
            "moderation"
        ]["enabled"]

        save_data()

        await interaction.response.edit_message(
            embed=moderation_settings_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="◀️ Geri",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=SettingsView()
        )


# =========================================================
# ANA AYARLAR MENÜSÜ
# =========================================================

class SettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="🎫 Ticket",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def ticket(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=ticket_settings_embed(
                interaction.guild.id
            ),
            view=TicketSettingsView()
        )

    @discord.ui.button(
        label="📜 Loglar",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def logs(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=logs_settings_embed(
                interaction.guild.id
            ),
            view=LogsSettingsView()
        )

    @discord.ui.button(
        label="👋 Hoş Geldin",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def welcome(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=welcome_settings_embed(
                interaction.guild.id
            ),
            view=WelcomeSettingsView()
        )

    @discord.ui.button(
        label="👤 Otorol",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def autorole(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=autorole_settings_embed(
                interaction.guild.id
            ),
            view=AutoroleSettingsView()
        )

    @discord.ui.button(
        label="🛡️ Moderasyon",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def moderation(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=moderation_settings_embed(
                interaction.guild.id
            ),
            view=ModerationSettingsView()
        )

    @discord.ui.button(
        label="🔄 Yenile",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def refresh(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="♻️ Sıfırla",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def reset(
        self,
        interaction,
        button
    ):

        configs[
            str(interaction.guild.id)
        ] = json.loads(
            json.dumps(DEFAULT_CONFIG)
        )

        save_data()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönet."
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def ayarlar(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        embed=settings_embed(
            interaction.guild.id
        ),
        view=SettingsView(),
        ephemeral=True
    )


@ayarlar.error
async def ayarlar_error(
    interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        await interaction.response.send_message(
            f"{EMOJI['no']} Bu komutu kullanmak için Yönetici yetkisine sahip olmalısınız.",
            ephemeral=True
        )


# =========================================================
# TICKET MODAL
# =========================================================

class TicketProblemModal(
    discord.ui.Modal,
    title="Ticket"
):

    problem = discord.ui.TextInput(
        label="Sorununuz",
        placeholder="Sorununuzu yazın.",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(
        self,
        interaction
    ):

        guild = interaction.guild
        config = get_config(
            guild.id
        )

        language = get_language(
            guild.id
        )

        ticket_config = config[
            "ticket"
        ]

        if not ticket_config[
            "enabled"
        ]:

            await interaction.response.send_message(
                f"{EMOJI['no']} "
                + t(
                    language,
                    "ticket_disabled"
                ),
                ephemeral=True
            )

            return

        category = None

        if ticket_config[
            "category"
        ]:

            category = guild.get_channel(
                ticket_config[
                    "category"
                ]
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
                    read_message_history=True,
                    manage_channels=True
                )
        }

        if ticket_config[
            "role"
        ]:

            role = guild.get_role(
                ticket_config[
                    "role"
                ]
            )

            if role:

                overwrites[
                    role
                ] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=(
                f"{EMOJI['locked']} "
                + t(
                    language,
                    "ticket"
                )
            ),
            description=(
                f"**{t(language, 'problem')}:**\n"
                f"{self.problem.value}"
            ),
            color=discord.Color.blurple()
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{EMOJI['yes']} "
            + t(
                language,
                "ticket_created"
            )
            + f" {channel.mention}",
            ephemeral=True
        )


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="🎫 Ticket Aç",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_ticket_open"
    )
    async def open_ticket(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            TicketProblemModal()
        )


class AddMemberModal(
    discord.ui.Modal,
    title="Üye Ekle"
):

    member_id = discord.ui.TextInput(
        label="Üye ID",
        placeholder="Discord ID",
        required=True
    )

    async def on_submit(
        self,
        interaction
    ):

        try:

            member_id = int(
                self.member_id.value
            )

            member = await interaction.guild.fetch_member(
                member_id
            )

        except Exception:

            await interaction.response.send_message(
                f"{EMOJI['no']} Geçerli bir üye bulunamadı.",
                ephemeral=True
            )

            return

        await interaction.channel.set_permissions(
            member,
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )

        await interaction.response.send_message(
            f"{EMOJI['yes']} {member.mention} ticket'a eklendi."
        )


class TicketCloseView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="🔒 Ticket Kapat",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_ticket_close"
    )
    async def close(
        self,
        interaction,
        button
    ):

        language = get_language(
            interaction.guild.id
        )

        await interaction.response.send_message(
            f"{EMOJI['locked']} "
            + t(
                language,
                "ticket_closed"
            )
        )

        await interaction.channel.delete()

    @discord.ui.button(
        label="👤 Üye Ekle",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_ticket_add_member"
    )
    async def add(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            AddMemberModal()
        )


# =========================================================
# HOŞ GELDİN / OTOROL
# =========================================================

@bot.event
async def on_member_join(
    member
):

    config = get_config(
        member.guild.id
    )

    autorole = config[
        "autorole"
    ]

    if autorole[
        "enabled"
    ] and autorole[
        "role"
    ]:

        role = member.guild.get_role(
            autorole[
                "role"
            ]
        )

        if role:

            try:
                await member.add_roles(
                    role
                )
            except Exception:
                pass

    welcome = config[
        "welcome"
    ]

    if welcome[
        "enabled"
    ] and welcome[
        "channel"
    ]:

        channel = member.guild.get_channel(
            welcome[
                "channel"
            ]
        )

        if channel:

            message = welcome[
                "message"
            ].replace(
                "{member}",
                member.mention
            )

            try:
                await channel.send(
                    message
                )
            except Exception:
                pass


# =========================================================
# SES BİLDİRİMİ
# =========================================================

class VoiceNotificationView(
    discord.ui.View
):

    def __init__(
        self,
        user_id
    ):

        super().__init__(
            timeout=None
        )

        enabled = get_voice_notifications(
            user_id
        )

        button = discord.ui.Button(
            label=(
                "🔕 Ses Bildirimlerini Kapat"
                if enabled
                else
                "🔔 Ses Bildirimlerini Aç"
            ),
            style=(
                discord.ButtonStyle.danger
                if enabled
                else
                discord.ButtonStyle.success
            ),
            custom_id=f"dynex_voice:{user_id}"
        )

        button.callback = self.toggle

        self.add_item(
            button
        )

        self.user_id = user_id

    async def toggle(
        self,
        interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                f"{EMOJI['no']} Bu buton size ait değil.",
                ephemeral=True
            )

            return

        current = get_voice_notifications(
            self.user_id
        )

        set_voice_notifications(
            self.user_id,
            not current
        )

        await interaction.response.send_message(
            (
                f"{EMOJI['yes']} "
                + (
                    "Ses bildirimleri açıldı."
                    if not current
                    else
                    "Ses bildirimleri kapatıldı."
                )
            ),
            ephemeral=True
        )


async def send_voice_statistics(
    member,
    before,
    after
):

    if not get_voice_notifications(
        member.id
    ):
        return

    start = voice_sessions.pop(
        member.id,
        None
    )

    if not start:
        return

    duration = (
        datetime.now(
            timezone.utc
        ) - start
    )

    seconds = int(
        duration.total_seconds()
    )

    minutes = seconds // 60
    seconds %= 60

    language = get_language(
        member.guild.id
    )

    embed = discord.Embed(
        title=(
            f"{EMOJI['dynex']} "
            + t(
                language,
                "voice_title"
            )
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(
            language,
            "voice_joined"
        ),
        value=before.channel.name,
        inline=False
    )

    embed.add_field(
        name=t(
            language,
            "voice_left"
        ),
        value=(
            after.channel.name
            if after.channel
            else "—"
        ),
        inline=False
    )

    embed.add_field(
        name=t(
            language,
            "voice_duration"
        ),
        value=f"{minutes} dk {seconds} sn",
        inline=False
    )

    try:

        await member.send(
            embed=embed,
            view=VoiceNotificationView(
                member.id
            )
        )

    except Exception:

        pass


@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if (
        before.channel is None
        and after.channel is not None
    ):

        voice_sessions[
            member.id
        ] = datetime.now(
            timezone.utc
        )

    elif (
        before.channel is not None
        and after.channel is None
    ):

        await send_voice_statistics(
            member,
            before,
            after
        )

    elif (
        before.channel
        and after.channel
        and before.channel.id != after.channel.id
    ):

        await send_voice_statistics(
            member,
            before,
            after
        )

        voice_sessions[
            member.id
        ] = datetime.now(
            timezone.utc
        )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(
        f"{bot.user} aktif."
    )

    try:

        bot.add_view(
            TicketPanelView()
        )

        bot.add_view(
            TicketCloseView()
        )

    except Exception:

        pass


# =========================================================
# BAŞLAT
# =========================================================

load_data()


if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )


bot.run(TOKEN)
