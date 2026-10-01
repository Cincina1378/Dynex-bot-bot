import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
from datetime import datetime, timezone


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

CONFIG_FILE = "config.json"


DEFAULT_CONFIG = {
    "ticket_enabled": False,
    "ticket_category": None,
    "ticket_role": None,
    "ticket_title": "Destek Talebi",
    "ticket_description": "Destek almak için aşağıdaki butona tıklayın.",
    "ticket_message": "Ticketiniz başarıyla oluşturuldu.",

    "log_enabled": False,
    "log_channel": None,

    "welcome_enabled": False,
    "welcome_channel": None,
    "welcome_message": "Hoş geldin {user}!",

    "autorole_enabled": False,
    "autorole": None,

    "moderation_enabled": True
}


configs = {}
user_settings = {}
voice_sessions = {}


# =========================================================
# CONFIG
# =========================================================

def load_config():
    global configs, user_settings

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "guilds": {},
                    "users": {}
                },
                f,
                indent=4,
                ensure_ascii=False
            )

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        configs = data.get("guilds", {})

        raw_users = data.get("users", {})
        user_settings = {}

        for user_id, value in raw_users.items():

            # Eski sistem:
            # "123456": "tr"
            if isinstance(value, str):
                language = value if value in ("tr", "en") else "tr"

                user_settings[str(user_id)] = {
                    "language": language,
                    "voice_notifications": True
                }

            # Yeni sistem
            elif isinstance(value, dict):

                language = value.get(
                    "language",
                    "tr"
                )

                if language not in ("tr", "en"):
                    language = "tr"

                user_settings[str(user_id)] = {
                    "language": language,
                    "voice_notifications": value.get(
                        "voice_notifications",
                        True
                    )
                }

    except Exception:
        configs = {}
        user_settings = {}


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "guilds": configs,
                "users": user_settings
            },
            f,
            indent=4,
            ensure_ascii=False
        )


def get_config(guild_id):
    guild_id = str(guild_id)

    if guild_id not in configs:
        configs[guild_id] = DEFAULT_CONFIG.copy()
        save_config()

    changed = False

    for key, value in DEFAULT_CONFIG.items():

        if key not in configs[guild_id]:
            configs[guild_id][key] = value
            changed = True

    if changed:
        save_config()

    return configs[guild_id]


def get_user_settings(user_id):

    user_id = str(user_id)

    if user_id not in user_settings:
        user_settings[user_id] = {
            "language": "tr",
            "voice_notifications": True
        }
        save_config()

    data = user_settings[user_id]

    if "language" not in data:
        data["language"] = "tr"

    if data["language"] not in ("tr", "en"):
        data["language"] = "tr"

    if "voice_notifications" not in data:
        data["voice_notifications"] = True

    return data


def get_language(user_id):

    return get_user_settings(
        user_id
    )["language"]


def set_language(user_id, language):

    data = get_user_settings(
        user_id
    )

    data["language"] = language

    save_config()


def get_voice_notifications(user_id):

    return get_user_settings(
        user_id
    )["voice_notifications"]


def set_voice_notifications(user_id, enabled):

    data = get_user_settings(
        user_id
    )

    data["voice_notifications"] = enabled

    save_config()


def t(user_id, key, **kwargs):

    language = get_language(
        user_id
    )

    text = TEXTS[language].get(
        key,
        TEXTS["en"].get(key, key)
    )

    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass

    return text


load_config()


# =========================================================
# LANGUAGE TEXTS
# =========================================================

TEXTS = {

    "tr": {

        "language_title": "Dynex Dil Ayarları",
        "language_description": "Dynex'in kullanacağı dili seç.",
        "turkish": "Türkçe",
        "english": "English",

        "language_changed_tr":
            "Dynex dili **Türkçe** olarak ayarlandı.",

        "language_changed_en":
            "Dynex language has been changed to **English**.",

        "already_tr":
            "Zaten **Türkçe** kullanıyorsun.",

        "already_en":
            "You are already using **English**.",

        "no_permission":
            "Bu komutu kullanmak için Yönetici yetkisine sahip olmalısın.",

        "settings_title":
            "Dynex Ayarları",

        "settings_description":
            "Aşağıdaki butonlardan sunucunun sistemlerini yönetebilirsin.",

        "ticket": "Ticket",
        "log": "Log",
        "welcome": "Hoş Geldin",
        "autorole": "Otorol",
        "moderation": "Moderasyon",
        "refresh": "Yenile",
        "reset": "Sıfırla",

        "open": "Açık",
        "closed": "Kapalı",
        "not_set": "Ayarlanmadı",
        "category": "Kategori",
        "authorized_role": "Yetkili",
        "channel": "Kanal",
        "role": "Rol",
        "status": "Durum",

        "ticket_settings":
            "Ticket Sistemi Ayarları",

        "panel_title":
            "Panel başlığı",

        "panel_description":
            "Panel açıklaması",

        "category_id":
            "Ticket kategori ID",

        "role_id":
            "Ticket yetkili rol ID",

        "internal_message":
            "Ticket iç mesajı",

        "ticket_panel_created":
            "Ticket paneli oluşturuldu.",

        "invalid_category_role":
            "Kategori ve rol ID'si sayı olmalıdır.",

        "category_not_found":
            "Girilen kategori bulunamadı.",

        "role_not_found":
            "Girilen yetkili rolü bulunamadı.",

        "create_ticket":
            "Ticket Aç",

        "close_ticket":
            "Ticket Kapat",

        "add_member":
            "Üye Ekle",

        "create_ticket_title":
            "Ticket Oluştur",

        "problem":
            "Sorun",

        "problem_placeholder":
            "Sorununuzu buraya yazın...",

        "ticket_not_found":
            "Ticket kategorisi bulunamadı.",

        "ticket_role_not_found":
            "Ticket yetkili rolü bulunamadı.",

        "already_ticket":
            "Zaten açık bir ticketın var:",

        "ticket_created":
            "Ticket oluşturuldu:",

        "ticket_problem":
            "Ticketiniz sorun:",

        "ticket_closing":
            "Ticket 5 saniye içinde kapatılıyor.",

        "not_ticket":
            "Bu kanal bir ticket değil.",

        "owner_not_found":
            "Ticket sahibi bulunamadı.",

        "ticket_owner_or_staff":
            "Bu butonu sadece ticket sahibi veya ticket yetkilisi kullanabilir.",

        "add_member_title":
            "Ticket'a Üye Ekle",

        "member_id":
            "Üye ID",

        "member_id_placeholder":
            "Eklemek istediğin kullanıcının ID'si",

        "invalid_member_id":
            "Geçerli bir kullanıcı ID'si gir.",

        "member_not_found":
            "Bu kullanıcı sunucuda bulunamadı.",

        "member_added":
            "ticket'a eklendi.",

        "member_add_failed":
            "Kullanıcı ticket'a eklenemedi.",

        "log_settings":
            "Log Ayarları",

        "log_channel_id":
            "Log kanal ID",

        "invalid_channel":
            "Bu ID bir yazı kanalına ait değil.",

        "log_configured":
            "Log sistemi ayarlandı.",

        "welcome_settings":
            "Hoş Geldin Ayarları",

        "welcome_channel_id":
            "Hoş geldin kanal ID",

        "welcome_message":
            "Hoş geldin mesajı",

        "welcome_configured":
            "Hoş geldin sistemi ayarlandı.",

        "autorole_settings":
            "Otorol Ayarları",

        "autorole_id":
            "Otorol rol ID",

        "autorole_configured":
            "Otorol ayarlandı.",

        "reset_done":
            "Tüm ayarlar sıfırlandı.",

        "ping_title":
            "Dynex Ping durumu",

        "ping_description":
            "**Dynex**’in ping durumu",

        "voice_disable":
            "Ses Bildirimlerini Kapat",

        "voice_enable":
            "Ses Bildirimlerini Aç"
    },

    "en": {

        "language_title":
            "Dynex Language Settings",

        "language_description":
            "Choose the language Dynex will use.",

        "turkish":
            "Türkçe",

        "english":
            "English",

        "language_changed_tr":
            "Dynex dili **Türkçe** olarak ayarlandı.",

        "language_changed_en":
            "Dynex language has been changed to **English**.",

        "already_tr":
            "You are already using **Turkish**.",

        "already_en":
            "You are already using **English**.",

        "no_permission":
            "You need Administrator permission to use this command.",

        "settings_title":
            "Dynex Settings",

        "settings_description":
            "Manage your server systems using the buttons below.",

        "ticket":
            "Ticket",

        "log":
            "Log",

        "welcome":
            "Welcome",

        "autorole":
            "Autorole",

        "moderation":
            "Moderation",

        "refresh":
            "Refresh",

        "reset":
            "Reset",

        "open":
            "Enabled",

        "closed":
            "Disabled",

        "not_set":
            "Not set",

        "category":
            "Category",

        "authorized_role":
            "Authorized role",

        "channel":
            "Channel",

        "role":
            "Role",

        "status":
            "Status",

        "ticket_settings":
            "Ticket System Settings",

        "panel_title":
            "Panel title",

        "panel_description":
            "Panel description",

        "category_id":
            "Ticket category ID",

        "role_id":
            "Ticket staff role ID",

        "internal_message":
            "Ticket internal message",

        "ticket_panel_created":
            "Ticket panel created.",

        "invalid_category_role":
            "Category and role IDs must be numbers.",

        "category_not_found":
            "The specified category could not be found.",

        "role_not_found":
            "The specified staff role could not be found.",

        "create_ticket":
            "Open Ticket",

        "close_ticket":
            "Close Ticket",

        "add_member":
            "Add Member",

        "create_ticket_title":
            "Create Ticket",

        "problem":
            "Problem",

        "problem_placeholder":
            "Describe your problem...",

        "ticket_not_found":
            "The ticket category could not be found.",

        "ticket_role_not_found":
            "The ticket staff role could not be found.",

        "already_ticket":
            "You already have an open ticket:",

        "ticket_created":
            "Ticket created:",

        "ticket_problem":
            "Your ticket problem:",

        "ticket_closing":
            "The ticket will be closed in 5 seconds.",

        "not_ticket":
            "This channel is not a ticket.",

        "owner_not_found":
            "The ticket owner could not be found.",

        "ticket_owner_or_staff":
            "Only the ticket owner or ticket staff can use this button.",

        "add_member_title":
            "Add Member to Ticket",

        "member_id":
            "Member ID",

        "member_id_placeholder":
            "Enter the user's Discord ID",

        "invalid_member_id":
            "Enter a valid user ID.",

        "member_not_found":
            "This user could not be found in the server.",

        "member_added":
            "has been added to the ticket.",

        "member_add_failed":
            "The user could not be added to the ticket.",

        "log_settings":
            "Log Settings",

        "log_channel_id":
            "Log channel ID",

        "invalid_channel":
            "This ID is not a text channel.",

        "log_configured":
            "Log system configured.",

        "welcome_settings":
            "Welcome Settings",

        "welcome_channel_id":
            "Welcome channel ID",

        "welcome_message":
            "Welcome message",

        "welcome_configured":
            "Welcome system configured.",

        "autorole_settings":
            "Autorole Settings",

        "autorole_id":
            "Autorole role ID",

        "autorole_configured":
            "Autorole configured.",

        "reset_done":
            "All settings have been reset.",

        "ping_title":
            "Dynex Ping Status",

        "ping_description":
            "**Dynex**'s ping status",

        "voice_disable":
            "Disable Voice Notifications",

        "voice_enable":
            "Enable Voice Notifications"
    }
}


# =========================================================
# LANGUAGE SELECT
# =========================================================

class LanguageSelect(discord.ui.Select):

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
            )
        ]

        super().__init__(
            placeholder="Dil seç / Choose language",
            options=options,
            custom_id="dynex_language_select"
        )

    async def callback(self, interaction):

        new_language = self.values[0]
        current_language = get_language(
            interaction.user.id
        )

        if new_language == current_language:

            message = (
                TEXTS["tr"]["already_tr"]
                if new_language == "tr"
                else TEXTS["en"]["already_en"]
            )

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> {message}",
                ephemeral=True
            )

            return

        set_language(
            interaction.user.id,
            new_language
        )

        message = (
            TEXTS["tr"]["language_changed_tr"]
            if new_language == "tr"
            else TEXTS["en"]["language_changed_en"]
        )

        await interaction.response.edit_message(
            content=f"🌐 {message}",
            embed=None,
            view=None
        )


class LanguageView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=180
        )

        self.add_item(
            LanguageSelect()
        )


# =========================================================
# AYARLAR EMBED
# =========================================================

def settings_embed(guild, user_id):

    config = get_config(
        guild.id
    )

    ticket_category = (
        f"<#{config['ticket_category']}>"
        if config["ticket_category"]
        else t(user_id, "not_set")
    )

    ticket_role = (
        f"<@&{config['ticket_role']}>"
        if config["ticket_role"]
        else t(user_id, "not_set")
    )

    log_channel = (
        f"<#{config['log_channel']}>"
        if config["log_channel"]
        else t(user_id, "not_set")
    )

    welcome_channel = (
        f"<#{config['welcome_channel']}>"
        if config["welcome_channel"]
        else t(user_id, "not_set")
    )

    autorole = (
        f"<@&{config['autorole']}>"
        if config["autorole"]
        else t(user_id, "not_set")
    )

    enabled = t(user_id, "open")
    disabled = t(user_id, "closed")

    embed = discord.Embed(
        title=f"⚙️ {t(user_id, 'settings_title')}",
        description=t(
            user_id,
            "settings_description"
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name=f"🎫 {t(user_id, 'ticket')}",
        value=(
            f"{t(user_id, 'status')}: "
            f"**{enabled if config['ticket_enabled'] else disabled}**\n"
            f"{t(user_id, 'category')}: {ticket_category}\n"
            f"{t(user_id, 'authorized_role')}: {ticket_role}"
        ),
        inline=False
    )

    embed.add_field(
        name=f"📋 {t(user_id, 'log')}",
        value=(
            f"{t(user_id, 'status')}: "
            f"**{enabled if config['log_enabled'] else disabled}**\n"
            f"{t(user_id, 'channel')}: {log_channel}"
        ),
        inline=True
    )

    embed.add_field(
        name=f"👋 {t(user_id, 'welcome')}",
        value=(
            f"{t(user_id, 'status')}: "
            f"**{enabled if config['welcome_enabled'] else disabled}**\n"
            f"{t(user_id, 'channel')}: {welcome_channel}"
        ),
        inline=True
    )

    embed.add_field(
        name=f"🎭 {t(user_id, 'autorole')}",
        value=(
            f"{t(user_id, 'status')}: "
            f"**{enabled if config['autorole_enabled'] else disabled}**\n"
            f"{t(user_id, 'role')}: {autorole}"
        ),
        inline=True
    )

    embed.add_field(
        name=f"🛡️ {t(user_id, 'moderation')}",
        value=(
            f"{t(user_id, 'status')}: "
            f"**{enabled if config['moderation_enabled'] else disabled}**"
        ),
        inline=True
    )

    return embed


# =========================================================
# TICKET AYARLARI
# =========================================================

class TicketSettingsModal(discord.ui.Modal):

    def __init__(self, user_id):

        self.user_id = user_id

        language = get_language(
            user_id
        )

        super().__init__(
            title=TEXTS[language]["ticket_settings"]
        )

        self.title_input = discord.ui.TextInput(
            label=TEXTS[language]["panel_title"],
            placeholder="Destek Talebi",
            default="Destek Talebi",
            max_length=100
        )

        self.description_input = discord.ui.TextInput(
            label=TEXTS[language]["panel_description"],
            placeholder="Destek almak için butona tıklayın.",
            default="Destek almak için aşağıdaki butona tıklayın.",
            style=discord.TextStyle.paragraph,
            max_length=1000
        )

        self.category_input = discord.ui.TextInput(
            label=TEXTS[language]["category_id"],
            placeholder="Kategori ID'sini gir",
            required=True,
            max_length=30
        )

        self.role_input = discord.ui.TextInput(
            label=TEXTS[language]["role_id"],
            placeholder="Yetkili rolünün ID'sini gir",
            required=True,
            max_length=30
        )

        self.message_input = discord.ui.TextInput(
            label=TEXTS[language]["internal_message"],
            placeholder="Ticketiniz başarıyla oluşturuldu.",
            default="Ticketiniz başarıyla oluşturuldu.",
            style=discord.TextStyle.paragraph,
            max_length=1500
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.category_input)
        self.add_item(self.role_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:
            category_id = int(
                self.category_input.value
            )

            role_id = int(
                self.role_input.value
            )

        except Exception:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'invalid_category_role')}",
                ephemeral=True
            )

            return

        category = interaction.guild.get_channel(
            category_id
        )

        role = interaction.guild.get_role(
            role_id
        )

        if not isinstance(
            category,
            discord.CategoryChannel
        ):

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'category_not_found')}",
                ephemeral=True
            )

            return

        if not role:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'role_not_found')}",
                ephemeral=True
            )

            return

        config = get_config(
            guild_id
        )

        config["ticket_enabled"] = True
        config["ticket_category"] = category_id
        config["ticket_role"] = role_id
        config["ticket_title"] = self.title_input.value
        config["ticket_description"] = self.description_input.value
        config["ticket_message"] = self.message_input.value

        save_config()

        embed = discord.Embed(
            title=self.title_input.value,
            description=self.description_input.value,
            color=discord.Color.blue()
        )

        await interaction.channel.send(
            embed=embed,
            view=TicketPanelView(
                get_language(user_id)
            )
        )

        await interaction.response.send_message(
            f"<:Dynexevet:1555263066235605023> "
            f"{t(user_id, 'ticket_panel_created')}",
            ephemeral=True
        )


# =========================================================
# TICKET PROBLEM
# =========================================================

class TicketProblemModal(discord.ui.Modal):

    def __init__(self, user_id):

        language = get_language(
            user_id
        )

        super().__init__(
            title=TEXTS[language]["create_ticket_title"]
        )

        self.problem = discord.ui.TextInput(
            label=TEXTS[language]["problem"],
            placeholder=TEXTS[language]["problem_placeholder"],
            style=discord.TextStyle.paragraph,
            required=True,
            min_length=2,
            max_length=2000
        )

        self.add_item(
            self.problem
        )

    async def on_submit(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        config = get_config(
            guild_id
        )

        category = interaction.guild.get_channel(
            config.get("ticket_category")
        )

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not isinstance(
            category,
            discord.CategoryChannel
        ):

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'ticket_not_found')}",
                ephemeral=True
            )

            return

        if not role:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'ticket_role_not_found')}",
                ephemeral=True
            )

            return

        channel_name = (
            f"ticket-{interaction.user.name}"
            .lower()
            .replace(" ", "-")
        )

        existing = discord.utils.get(
            category.channels,
            name=channel_name
        )

        if existing:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'already_ticket')} "
                f"{existing.mention}",
                ephemeral=True
            )

            return

        overwrites = {

            interaction.guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                ),

            role:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_messages=True
                ),

            interaction.guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True,
                    manage_messages=True
                )
        }

        channel = await interaction.guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"dynex_ticket_owner:{interaction.user.id}"
        )

        embed = discord.Embed(
            title=f"🎫 {t(user_id, 'ticket')}",
            description=(
                f"{config.get('ticket_message')}\n\n"
                f"**{t(user_id, 'ticket_problem')}**\n"
                f"{self.problem.value}"
            ),
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"Ticket owner: {interaction.user}"
        )

        await channel.send(
            content=(
                f"{role.mention} | "
                f"{interaction.user.mention}"
            ),
            embed=embed,
            view=TicketCloseView(
                get_language(user_id)
            )
        )

        await interaction.response.send_message(
            f"<:Dynexevet:1555263066235605023> "
            f"{t(user_id, 'ticket_created')} "
            f"{channel.mention}",
            ephemeral=True
        )


# =========================================================
# ADD MEMBER
# =========================================================

class AddMemberModal(discord.ui.Modal):

    def __init__(self, user_id):

        language = get_language(
            user_id
        )

        super().__init__(
            title=TEXTS[language]["add_member_title"]
        )

        self.member_id = discord.ui.TextInput(
            label=TEXTS[language]["member_id"],
            placeholder=TEXTS[language]["member_id_placeholder"],
            required=True,
            max_length=30
        )

        self.add_item(
            self.member_id
        )

    async def on_submit(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        config = get_config(
            guild_id
        )

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not interaction.channel.topic:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'not_ticket')}",
                ephemeral=True
            )

            return

        try:
            owner_id = int(
                interaction.channel.topic.split(":")[1]
            )

        except Exception:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'owner_not_found')}",
                ephemeral=True
            )

            return

        is_owner = (
            interaction.user.id == owner_id
        )

        is_authorized = (
            role and role in interaction.user.roles
        )

        if not is_owner and not is_authorized:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'ticket_owner_or_staff')}",
                ephemeral=True
            )

            return

        try:
            member_id = int(
                self.member_id.value
            )

        except Exception:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'invalid_member_id')}",
                ephemeral=True
            )

            return

        member = interaction.guild.get_member(
            member_id
        )

        if not member:

            try:
                member = await interaction.guild.fetch_member(
                    member_id
                )
            except Exception:
                member = None

        if not member:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'member_not_found')}",
                ephemeral=True
            )

            return

        try:

            await interaction.channel.set_permissions(
                member,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )

        except Exception:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'member_add_failed')}",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"<:Dynexevet:1555263066235605023> "
            f"{member.mention} "
            f"{t(user_id, 'member_added')}"
        )


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(discord.ui.View):

    def __init__(self, language="tr"):

        super().__init__(
            timeout=None
        )

        self.language = language

        button = discord.ui.Button(
            label=TEXTS[language]["create_ticket"],
            emoji="🎫",
            style=discord.ButtonStyle.primary,
            custom_id="dynex_ticket_create"
        )

        button.callback = self.create_ticket
        self.add_item(button)

    async def create_ticket(self, interaction):

        await interaction.response.send_modal(
            TicketProblemModal(
                interaction.user.id
            )
        )


# =========================================================
# TICKET CLOSE VIEW
# =========================================================

class TicketCloseView(discord.ui.View):

    def __init__(self, language="tr"):

        super().__init__(
            timeout=None
        )

        self.language = language

        close_button = discord.ui.Button(
            label=TEXTS[language]["close_ticket"],
            emoji="🔒",
            style=discord.ButtonStyle.danger,
            custom_id="dynex_ticket_close"
        )

        add_button = discord.ui.Button(
            label=TEXTS[language]["add_member"],
            emoji="👤",
            style=discord.ButtonStyle.primary,
            custom_id="dynex_ticket_add_member"
        )

        close_button.callback = self.close_ticket
        add_button.callback = self.add_member

        self.add_item(close_button)
        self.add_item(add_button)

    async def close_ticket(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        config = get_config(
            guild_id
        )

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not interaction.channel.topic:

            await interaction.response.send_message(
                t(user_id, "not_ticket"),
                ephemeral=True
            )

            return

        try:
            owner_id = int(
                interaction.channel.topic.split(":")[1]
            )

        except Exception:

            await interaction.response.send_message(
                t(user_id, "owner_not_found"),
                ephemeral=True
            )

            return

        is_owner = (
            interaction.user.id == owner_id
        )

        is_authorized = (
            role and role in interaction.user.roles
        )

        if not is_owner and not is_authorized:

            await interaction.response.send_message(
                t(user_id, "ticket_owner_or_staff"),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"🔒 {t(user_id, 'ticket_closing')}"
        )

        await asyncio.sleep(5)

        try:
            await interaction.channel.delete(
                reason=f"Ticket closed by {interaction.user}"
            )
        except Exception:
            pass

    async def add_member(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        config = get_config(
            guild_id
        )

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not interaction.channel.topic:

            await interaction.response.send_message(
                t(user_id, "not_ticket"),
                ephemeral=True
            )

            return

        try:
            owner_id = int(
                interaction.channel.topic.split(":")[1]
            )

        except Exception:

            await interaction.response.send_message(
                t(user_id, "owner_not_found"),
                ephemeral=True
            )

            return

        is_owner = (
            interaction.user.id == owner_id
        )

        is_authorized = (
            role and role in interaction.user.roles
        )

        if not is_owner and not is_authorized:

            await interaction.response.send_message(
                t(user_id, "ticket_owner_or_staff"),
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            AddMemberModal(
                interaction.user.id
            )
        )


# =========================================================
# LOG
# =========================================================

class LogModal(discord.ui.Modal):

    def __init__(self, user_id):

        language = get_language(
            user_id
        )

        super().__init__(
            title=TEXTS[language]["log_settings"]
        )

        self.channel_id = discord.ui.TextInput(
            label=TEXTS[language]["log_channel_id"],
            placeholder="Enter channel ID",
            required=True,
            max_length=30
        )

        self.add_item(
            self.channel_id
        )

    async def on_submit(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:
            channel_id = int(
                self.channel_id.value
            )
        except Exception:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'invalid_channel')}",
                ephemeral=True
            )

            return

        channel = interaction.guild.get_channel(
            channel_id
        )

        if not isinstance(
            channel,
            discord.TextChannel
        ):

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'invalid_channel')}",
                ephemeral=True
            )

            return

        config = get_config(
            guild_id
        )

        config["log_enabled"] = True
        config["log_channel"] = channel_id

        save_config()

        await interaction.response.send_message(
            f"<:Dynexevet:1555263066235605023> "
            f"{t(user_id, 'log_configured')}",
            ephemeral=True
        )


# =========================================================
# WELCOME
# =========================================================

class WelcomeModal(discord.ui.Modal):

    def __init__(self, user_id):

        language = get_language(
            user_id
        )

        super().__init__(
            title=TEXTS[language]["welcome_settings"]
        )

        self.channel_id = discord.ui.TextInput(
            label=TEXTS[language]["welcome_channel_id"],
            placeholder="Enter channel ID",
            required=True,
            max_length=30
        )

        self.message = discord.ui.TextInput(
            label=TEXTS[language]["welcome_message"],
            placeholder="Hoş geldin {user}!",
            default="Hoş geldin {user}!",
            style=discord.TextStyle.paragraph,
            max_length=1000
        )

        self.add_item(self.channel_id)
        self.add_item(self.message)

    async def on_submit(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:
            channel_id = int(
                self.channel_id.value
            )
        except Exception:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'invalid_channel')}",
                ephemeral=True
            )

            return

        channel = interaction.guild.get_channel(
            channel_id
        )

        if not isinstance(
            channel,
            discord.TextChannel
        ):

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'invalid_channel')}",
                ephemeral=True
            )

            return

        config = get_config(
            guild_id
        )

        config["welcome_enabled"] = True
        config["welcome_channel"] = channel_id
        config["welcome_message"] = self.message.value

        save_config()

        await interaction.response.send_message(
            f"<:Dynexevet:1555263066235605023> "
            f"{t(user_id, 'welcome_configured')}",
            ephemeral=True
        )


# =========================================================
# AUTOROLE
# =========================================================

class AutoroleModal(discord.ui.Modal):

    def __init__(self, user_id):

        language = get_language(
            user_id
        )

        super().__init__(
            title=TEXTS[language]["autorole_settings"]
        )

        self.role_id = discord.ui.TextInput(
            label=TEXTS[language]["autorole_id"],
            placeholder="Enter role ID",
            required=True,
            max_length=30
        )

        self.add_item(
            self.role_id
        )

    async def on_submit(self, interaction):

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        try:
            role_id = int(
                self.role_id.value
            )
        except Exception:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'role_not_found')}",
                ephemeral=True
            )

            return

        role = interaction.guild.get_role(
            role_id
        )

        if not role:

            await interaction.response.send_message(
                f"<:Dynexhayir:1555265003727102134> "
                f"{t(user_id, 'role_not_found')}",
                ephemeral=True
            )

            return

        config = get_config(
            guild_id
        )

        config["autorole_enabled"] = True
        config["autorole"] = role_id

        save_config()

        await interaction.response.send_message(
            f"<:Dynexevet:1555263066235605023> "
            f"{t(user_id, 'autorole_configured')}",
            ephemeral=True
        )


# =========================================================
# AYARLAR VIEW
# =========================================================

class SettingsView(discord.ui.View):

    def __init__(self, user_id):

        super().__init__(
            timeout=300
        )

        language = get_language(
            user_id
        )

        self.add_item(
            self.make_button(
                TEXTS[language]["ticket"],
                "🎫",
                discord.ButtonStyle.primary,
                self.ticket
            )
        )

        self.add_item(
            self.make_button(
                TEXTS[language]["log"],
                "📋",
                discord.ButtonStyle.secondary,
                self.log
            )
        )

        self.add_item(
            self.make_button(
                TEXTS[language]["welcome"],
                "👋",
                discord.ButtonStyle.secondary,
                self.welcome
            )
        )

        self.add_item(
            self.make_button(
                TEXTS[language]["autorole"],
                "🎭",
                discord.ButtonStyle.secondary,
                self.autorole
            )
        )

        self.add_item(
            self.make_button(
                TEXTS[language]["moderation"],
                "🛡️",
                discord.ButtonStyle.secondary,
                self.moderation
            )
        )

        self.add_item(
            self.make_button(
                TEXTS[language]["refresh"],
                "🔄",
                discord.ButtonStyle.success,
                self.refresh,
                row=1
            )
        )

        self.add_item(
            self.make_button(
                TEXTS[language]["reset"],
                "🗑️",
                discord.ButtonStyle.danger,
                self.reset,
                row=1
            )
        )

    def make_button(
        self,
        label,
        emoji,
        style,
        callback,
        row=None
    ):

        button = discord.ui.Button(
            label=label,
            emoji=emoji,
            style=style,
            row=row
        )

        button.callback = callback

        return button

    async def ticket(self, interaction):

        await interaction.response.send_modal(
            TicketSettingsModal(
                interaction.user.id
            )
        )

    async def log(self, interaction):

        await interaction.response.send_modal(
            LogModal(
                interaction.user.id
            )
        )

    async def welcome(self, interaction):

        await interaction.response.send_modal(
            WelcomeModal(
                interaction.user.id
            )
        )

    async def autorole(self, interaction):

        await interaction.response.send_modal(
            AutoroleModal(
                interaction.user.id
            )
        )

    async def moderation(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["moderation_enabled"] = not config[
            "moderation_enabled"
        ]

        save_config()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild,
                interaction.user.id
            ),
            view=SettingsView(
                interaction.user.id
            )
        )

    async def refresh(self, interaction):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild,
                interaction.user.id
            ),
            view=SettingsView(
                interaction.user.id
            )
        )

    async def reset(self, interaction):

        configs[str(interaction.guild.id)] = (
            DEFAULT_CONFIG.copy()
        )

        save_config()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild,
                interaction.user.id
            ),
            view=SettingsView(
                interaction.user.id
            )
        )


# =========================================================
# /DİL
# =========================================================

@bot.tree.command(
    name="dil",
    description="Dynex dilini değiştir."
)
@app_commands.describe(
    dil="Kullanılacak dili seç."
)
@app_commands.choices(
    dil=[
        app_commands.Choice(
            name="Türkçe",
            value="tr"
        ),
        app_commands.Choice(
            name="English",
            value="en"
        )
    ]
)
async def dil(
    interaction,
    dil: app_commands.Choice[str]
):

    user_id = interaction.user.id

    current_language = get_language(
        user_id
    )

    if dil.value == current_language:

        message = (
            TEXTS["tr"]["already_tr"]
            if dil.value == "tr"
            else TEXTS["en"]["already_en"]
        )

        await interaction.response.send_message(
            f"<:Dynexhayir:1555265003727102134> {message}",
            ephemeral=True
        )

        return

    set_language(
        user_id,
        dil.value
    )

    message = (
        TEXTS["tr"]["language_changed_tr"]
        if dil.value == "tr"
        else TEXTS["en"]["language_changed_en"]
    )

    await interaction.response.send_message(
        f"🌐 {message}",
        ephemeral=True
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
async def ayarlar(interaction):

    await interaction.response.send_message(
        embed=settings_embed(
            interaction.guild,
            interaction.user.id
        ),
        view=SettingsView(
            interaction.user.id
        ),
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

        user_id = interaction.user.id

        if interaction.response.is_done():

            await interaction.followup.send(
                t(
                    user_id,
                    "no_permission"
                ),
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                t(
                    user_id,
                    "no_permission"
                ),
                ephemeral=True
            )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Dynex gecikmesini gösterir."
)
async def ping(interaction):

    latency = round(
        bot.latency * 1000
    )

    embed = discord.Embed(
        title=t(
            interaction.user.id,
            "ping_title"
        ),
        description=t(
            interaction.user.id,
            "ping_description"
        ),
        color=discord.Color.from_rgb(
            0,
            0,
            0
        )
    )

    embed.add_field(
        name="",
        value=f"`{latency}ms`",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# SES BİLDİRİMİ BUTONU
# =========================================================

class VoiceNotificationView(discord.ui.View):

    def __init__(
        self,
        user_id,
        enabled=None
    ):

        super().__init__(
            timeout=None
        )

        self.user_id = user_id

        if enabled is None:
            enabled = get_voice_notifications(
                user_id
            )

        language = get_language(
            user_id
        )

        if enabled:

            label = TEXTS[language][
                "voice_disable"
            ]

            emoji = "🔕"

        else:

            label = TEXTS[language][
                "voice_enable"
            ]

            emoji = "🔔"

        button = discord.ui.Button(
            label=label,
            emoji=emoji,
            style=(
                discord.ButtonStyle.danger
                if enabled
                else discord.ButtonStyle.success
            ),
            custom_id="dynex_voice_notifications"
        )

        button.callback = self.toggle
        self.add_item(button)

    async def toggle(self, interaction):

        user_id = interaction.user.id

        current = get_voice_notifications(
            user_id
        )

        new_state = not current

        set_voice_notifications(
            user_id,
            new_state
        )

        await interaction.response.edit_message(
            view=VoiceNotificationView(
                user_id,
                new_state
            )
        )


# =========================================================
# SES İSTATİSTİKLERİ
# =========================================================

async def send_voice_statistics(
    member,
    guild_name,
    duration_seconds,
    remaining_members,
    language
):

    if not get_voice_notifications(
        member.id
    ):
        return False

    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60

    if language == "tr":

        if hours > 0:

            duration_text = (
                f"{hours} saat "
                f"{minutes} dakika "
                f"{seconds} saniye"
            )

        elif minutes > 0:

            duration_text = (
                f"{minutes} dakika "
                f"{seconds} saniye"
            )

        else:

            duration_text = (
                f"{seconds} saniye"
            )

        message = (
            f"🔊 **{guild_name} adlı sunucunun ses istatikleri**\n\n"
            f"**Bugün {guild_name} adlı sunucuda sesli sohbete "
            f"katıldın. İşte istatiklerin:**\n\n"
            f"Sunucu adı: **{guild_name}**\n"
            f"Kaldığın süre: **{duration_text}**\n"
            f"Sen çıkınca sesli sohbete kalan üye sayısı: "
            f"**{remaining_members}**\n\n"
            f"**Dynex sizin sunucu dostunuz…**"
        )

    else:

        if hours > 0:

            duration_text = (
                f"{hours} hours "
                f"{minutes} minutes "
                f"{seconds} seconds"
            )

        elif minutes > 0:

            duration_text = (
                f"{minutes} minutes "
                f"{seconds} seconds"
            )

        else:

            duration_text = (
                f"{seconds} seconds"
            )

        message = (
            f"🔊 **{guild_name} voice statistics**\n\n"
            f"**Today you joined the voice chat on the "
            f"{guild_name} server. Here are your statistics:**\n\n"
            f"Server name: **{guild_name}**\n"
            f"Time spent: **{duration_text}**\n"
            f"Members remaining in voice after you left: "
            f"**{remaining_members}**\n\n"
            f"**Dynex is your server's friend…**"
        )

    try:

        dm = await member.create_dm()

        await dm.send(
            message,
            view=VoiceNotificationView(
                member.id,
                True
            )
        )

        return True

    except discord.Forbidden:

        print(
            f"DM kapalı: {member} ({member.id})"
        )

        return False

    except discord.HTTPException as e:

        print(
            f"DM HTTP hatası: {member} | {e}"
        )

        return False

    except Exception as e:

        print(
            f"DM gönderme hatası: {member} | {repr(e)}"
        )

        return False


# =========================================================
# VOICE STATE
# =========================================================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    # =====================================================
    # SES KANALINA GİRİŞ
    # =====================================================

    if (
        before.channel is None
        and after.channel is not None
    ):

        voice_sessions[
            (member.guild.id, member.id)
        ] = {
            "channel_id": after.channel.id,
            "started_at": datetime.now(
                timezone.utc
            )
        }

        return

    # =====================================================
    # SES KANALI DEĞİŞTİRME
    # =====================================================

    if (
        before.channel is not None
        and after.channel is not None
        and before.channel.id != after.channel.id
    ):

        key = (
            member.guild.id,
            member.id
        )

        voice_sessions[key] = {
            "channel_id": after.channel.id,
            "started_at": datetime.now(
                timezone.utc
            )
        }

        return

    # =====================================================
    # SESTEN ÇIKIŞ
    # =====================================================

    if (
        before.channel is not None
        and after.channel is None
    ):

        key = (
            member.guild.id,
            member.id
        )

        session = voice_sessions.pop(
            key,
            None
        )

        if not session:
            return

        started_at = session["started_at"]

        ended_at = datetime.now(
            timezone.utc
        )

        duration_seconds = int(
            (
                ended_at - started_at
            ).total_seconds()
        )

        if duration_seconds < 0:
            duration_seconds = 0

        remaining_members = len(
            before.channel.members
        )

        language = get_language(
            member.id
        )

        await send_voice_statistics(
            member=member,
            guild_name=member.guild.name,
            duration_seconds=duration_seconds,
            remaining_members=remaining_members,
            language=language
        )


# =========================================================
# MEMBER JOIN
# =========================================================

@bot.event
async def on_member_join(member):

    config = get_config(
        member.guild.id
    )

    # =====================================================
    # OTOROL
    # =====================================================

    if config.get(
        "autorole_enabled"
    ):

        role_id = config.get(
            "autorole"
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
                except Exception:
                    pass

    # =====================================================
    # HOŞ GELDİN
    # =====================================================

    if config.get(
        "welcome_enabled"
    ):

        channel_id = config.get(
            "welcome_channel"
        )

        if channel_id:

            channel = member.guild.get_channel(
                channel_id
            )

            if channel:

                message = config.get(
                    "welcome_message",
                    "Hoş geldin {user}!"
                )

                message = message.replace(
                    "{user}",
                    member.mention
                )

                try:
                    await channel.send(
                        message
                    )
                except Exception:
                    pass


# =========================================================
# READY
# =========================================================

views_added = False


@bot.event
async def on_ready():

    global views_added

    try:

        if not views_added:

            bot.add_view(
                TicketPanelView("tr")
            )

            bot.add_view(
                TicketCloseView("tr")
            )

            views_added = True

        synced = await bot.tree.sync()

        print(
            f"Dynex aktif: {bot.user}"
        )

        print(
            f"{len(synced)} slash komutu senkronize edildi."
        )

    except Exception as e:

        print(
            "READY HATASI:",
            repr(e)
        )


# =========================================================
# TOKEN
# =========================================================

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
