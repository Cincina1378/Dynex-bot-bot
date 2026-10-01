import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import copy
import re

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

E = {
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
# DİLLER
# =========================================================

LANGS = {
    "tr": "Türkçe",
    "en": "English",
    "az": "Azərbaycan"
}

T = {
    "tr": {
        "settings": "Dynex Ayarları",
        "settings_desc": "Sunucu sistemlerini buradan yönetin.",
        "ticket": "Ticket",
        "logs": "Loglar",
        "welcome": "Hoş Geldin",
        "autorole": "Otorol",
        "moderation": "Moderasyon",
        "refresh": "Yenile",
        "reset": "Sıfırla",
        "back": "Geri",
        "on": "Açık",
        "off": "Kapalı",

        "ticket_settings": "Ticket Ayarları",
        "ticket_message": "Ticket Mesajı",
        "ticket_image": "Ticket Resmi",
        "add_image": "Resim Ekle",
        "remove_image": "Resmi Kaldır",

        "staff_role": "Yetkili Rolü",
        "category": "Kategori",
        "panel_channel": "Panel Kanalı",

        "options": "Ticket Seçenekleri",
        "add_option": "Seçenek Ekle",
        "delete_option": "Seçenek Sil",
        "edit_option": "Seçenek Düzenle",
        "view_options": "Seçenekleri Gör",

        "save_send": "Kaydet ve Gönder",
        "enabled": "Ticket sistemi",
        "no_option": "Henüz seçenek eklenmedi.",

        "saved": "Ticket ayarları kaydedildi ve panel gönderildi.",
        "option_added": "Seçenek eklendi.",
        "option_deleted": "Seçenek silindi.",
        "option_edited": "Seçenek düzenlendi.",

        "choose_option": "Bir seçenek seçin.",
        "choose_channel": "Panel kanalını seçin.",
        "choose_role": "Yetkili rolünü seçin.",
        "choose_category": "Ticket kategorisini seçin.",

        "message_saved": "Ticket mesajı kaydedildi.",
        "image_saved": "Ticket resmi kaydedildi.",
        "image_removed": "Ticket resmi kaldırıldı.",

        "ticket_open": "Ticket Aç",
        "ticket_close": "Ticket Kapat",
        "add_member": "Üye Ekle",

        "problem": "Talep",
        "problem_placeholder": "Sorununuzu veya talebinizi yazın.",

        "ticket_created": "Ticket oluşturuldu.",
        "permission": "Bu işlem için yetkiniz yok.",

        "reset_done": "Ayarlar sıfırlandı.",

        "ping": "Ping",
        "ping_title": "Dynex Ping Durumu",

        "language": "Dil",
        "language_changed": "Dil değiştirildi.",

        "welcome_settings": "Hoş Geldin Ayarları",
        "logs_settings": "Log Ayarları",
        "autorole_settings": "Otorol Ayarları",
        "moderation_settings": "Moderasyon Ayarları",

        "select_channel": "Kanal Seç",
        "select_role": "Rol Seç",
        "select_category": "Kategori Seç",

        "welcome_message": "Hoş Geldin Mesajı",
        "edit_message": "Mesajı Düzenle",

        "voice": "Ses Bildirimleri"
    },

    "en": {
        "settings": "Dynex Settings",
        "settings_desc": "Manage server systems here.",
        "ticket": "Ticket",
        "logs": "Logs",
        "welcome": "Welcome",
        "autorole": "Autorole",
        "moderation": "Moderation",
        "refresh": "Refresh",
        "reset": "Reset",
        "back": "Back",
        "on": "Enabled",
        "off": "Disabled",

        "ticket_settings": "Ticket Settings",
        "ticket_message": "Ticket Message",
        "ticket_image": "Ticket Image",
        "add_image": "Add Image",
        "remove_image": "Remove Image",

        "staff_role": "Staff Role",
        "category": "Category",
        "panel_channel": "Panel Channel",

        "options": "Ticket Options",
        "add_option": "Add Option",
        "delete_option": "Delete Option",
        "edit_option": "Edit Option",
        "view_options": "View Options",

        "save_send": "Save & Send",
        "enabled": "Ticket system",
        "no_option": "No options added yet.",

        "saved": "Ticket settings saved and panel sent.",
        "option_added": "Option added.",
        "option_deleted": "Option deleted.",
        "option_edited": "Option edited.",

        "choose_option": "Choose an option.",
        "choose_channel": "Choose the panel channel.",
        "choose_role": "Choose the staff role.",
        "choose_category": "Choose the ticket category.",

        "message_saved": "Ticket message saved.",
        "image_saved": "Ticket image saved.",
        "image_removed": "Ticket image removed.",

        "ticket_open": "Open Ticket",
        "ticket_close": "Close Ticket",
        "add_member": "Add Member",

        "problem": "Request",
        "problem_placeholder": "Describe your problem or request.",

        "ticket_created": "Ticket created.",
        "permission": "You do not have permission.",

        "reset_done": "Settings reset.",

        "ping": "Ping",
        "ping_title": "Dynex Ping Status",

        "language": "Language",
        "language_changed": "Language changed.",

        "welcome_settings": "Welcome Settings",
        "logs_settings": "Log Settings",
        "autorole_settings": "Autorole Settings",
        "moderation_settings": "Moderation Settings",

        "select_channel": "Select Channel",
        "select_role": "Select Role",
        "select_category": "Select Category",

        "welcome_message": "Welcome Message",
        "edit_message": "Edit Message",

        "voice": "Voice Notifications"
    },

    "az": {
        "settings": "Dynex Ayarları",
        "settings_desc": "Server sistemlərini buradan idarə edin.",
        "ticket": "Ticket",
        "logs": "Loglar",
        "welcome": "Qarşılama",
        "autorole": "Avtorol",
        "moderation": "Moderasiya",
        "refresh": "Yenilə",
        "reset": "Sıfırla",
        "back": "Geri",
        "on": "Aktiv",
        "off": "Deaktiv",

        "ticket_settings": "Ticket Ayarları",
        "ticket_message": "Ticket Mesajı",
        "ticket_image": "Ticket Şəkli",
        "add_image": "Şəkil Əlavə Et",
        "remove_image": "Şəkli Sil",

        "staff_role": "Səlahiyyətli Rolu",
        "category": "Kateqoriya",
        "panel_channel": "Panel Kanalı",

        "options": "Ticket Seçimləri",
        "add_option": "Seçim Əlavə Et",
        "delete_option": "Seçim Sil",
        "edit_option": "Seçimi Dəyiş",
        "view_options": "Seçimləri Gör",

        "save_send": "Yadda Saxla və Göndər",
        "enabled": "Ticket sistemi",
        "no_option": "Hələ seçim əlavə edilməyib.",

        "saved": "Ticket ayarları yadda saxlanıldı və panel göndərildi.",
        "option_added": "Seçim əlavə edildi.",
        "option_deleted": "Seçim silindi.",
        "option_edited": "Seçim dəyişdirildi.",

        "choose_option": "Seçim edin.",
        "choose_channel": "Panel kanalını seçin.",
        "choose_role": "Səlahiyyətli rolunu seçin.",
        "choose_category": "Ticket kateqoriyasını seçin.",

        "message_saved": "Ticket mesajı yadda saxlanıldı.",
        "image_saved": "Ticket şəkli yadda saxlanıldı.",
        "image_removed": "Ticket şəkli silindi.",

        "ticket_open": "Ticket Aç",
        "ticket_close": "Ticket Bağla",
        "add_member": "Üzv Əlavə Et",

        "problem": "Müraciət",
        "problem_placeholder": "Probleminizi və ya müraciətinizi yazın.",

        "ticket_created": "Ticket yaradıldı.",
        "permission": "Bunun üçün icazəniz yoxdur.",

        "reset_done": "Ayarlar sıfırlandı.",

        "ping": "Ping",
        "ping_title": "Dynex Ping Vəziyyəti",

        "language": "Dil",
        "language_changed": "Dil dəyişdirildi.",

        "welcome_settings": "Qarşılama Ayarları",
        "logs_settings": "Log Ayarları",
        "autorole_settings": "Avtorol Ayarları",
        "moderation_settings": "Moderasiya Ayarları",

        "select_channel": "Kanal Seç",
        "select_role": "Rol Seç",
        "select_category": "Kateqoriya Seç",

        "welcome_message": "Qarşılama Mesajı",
        "edit_message": "Mesajı Dəyiş",

        "voice": "Səs Bildirişləri"
    }
}

# =========================================================
# DEFAULT CONFIG
# =========================================================

DEFAULT = {
    "language": "tr",

    "ticket": {
        "enabled": True,
        "category": None,
        "role": None,
        "channel": None,

        "message": "Destek talebi oluşturmak için aşağıdaki seçeneklerden birini seçin.",

        "image_url": None,

        "options": [
            {
                "name": "Şikayet",
                "button": "Şikayet",
                "emoji": "📝"
            },
            {
                "name": "Destek",
                "button": "Destek",
                "emoji": "🎫"
            }
        ]
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

# =========================================================
# DATA
# =========================================================

def load_data():
    global configs

    if not os.path.exists(CONFIG_FILE):
        configs = {}
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, dict) and "configs" in raw:
            raw = raw["configs"]

        if not isinstance(raw, dict):
            configs = {}
            return

        for guild_id, old_config in raw.items():

            config = copy.deepcopy(DEFAULT)

            if isinstance(old_config, dict):

                if old_config.get("language") in LANGS:
                    config["language"] = old_config["language"]

                for section in [
                    "ticket",
                    "logs",
                    "welcome",
                    "autorole",
                    "moderation"
                ]:
                    if isinstance(old_config.get(section), dict):
                        config[section].update(old_config[section])

            if not isinstance(config["ticket"].get("options"), list):
                config["ticket"]["options"] = copy.deepcopy(
                    DEFAULT["ticket"]["options"]
                )

            configs[str(guild_id)] = config

    except Exception:
        configs = {}


def save_data():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"configs": configs},
            f,
            ensure_ascii=False,
            indent=4
        )


def get_config(guild_id):
    guild_id = str(guild_id)

    if guild_id not in configs:
        configs[guild_id] = copy.deepcopy(DEFAULT)
        save_data()

    return configs[guild_id]


def get_lang(guild_id):
    language = get_config(guild_id).get("language", "tr")

    if language not in LANGS:
        language = "tr"

    return language


def text(guild_id, key):
    language = get_lang(guild_id)

    return T.get(
        language,
        T["tr"]
    ).get(
        key,
        T["tr"].get(key, key)
    )


def enabled_text(guild_id, value):
    return (
        f"{E['yes']} {text(guild_id, 'on')}"
        if value
        else
        f"{E['no']} {text(guild_id, 'off')}"
    )

# =========================================================
# BOT
# =========================================================

class DynexBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=INTENTS
        )

    async def setup_hook(self):
        await self.tree.sync()


bot = DynexBot()

# =========================================================
# LANGUAGE
# =========================================================

class LanguageSelect(discord.ui.Select):

    def __init__(self):
        super().__init__(
            placeholder="Türkçe / English / Azərbaycan",
            options=[
                discord.SelectOption(
                    label="Türkçe",
                    value="tr"
                ),
                discord.SelectOption(
                    label="English",
                    value="en"
                ),
                discord.SelectOption(
                    label="Azərbaycan",
                    value="az"
                )
            ]
        )

    async def callback(self, interaction):

        config = get_config(interaction.guild.id)

        config["language"] = self.values[0]

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {T[self.values[0]]['language_changed']}",
            ephemeral=True
        )


class LanguageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            LanguageSelect()
        )


@bot.tree.command(
    name="dil",
    description="Dynex dilini değiştir."
)
async def dil(interaction):

    embed = discord.Embed(
        title=f"{E['settings']} {text(interaction.guild.id, 'language')}",
        description="Türkçe / English / Azərbaycan",
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=LanguageView(),
        ephemeral=True
    )

# =========================================================
# PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Dynex ping durumunu gösterir."
)
async def ping(interaction):

    ms = round(bot.latency * 1000)

    if ms <= 80:
        icon = E["correct"]
    elif ms <= 150:
        icon = E["yes"]
    elif ms <= 250:
        icon = E["wait"]
    elif ms <= 400:
        icon = E["alarm"]
    else:
        icon = E["no"]

    embed = discord.Embed(
        title=f"{E['dynex']} {text(interaction.guild.id, 'ping_title')}",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=text(interaction.guild.id, "ping"),
        value=f"`{ms}ms` {icon}",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )

# =========================================================
# SETTINGS MAIN EMBED
# =========================================================

def settings_embed(guild_id):

    config = get_config(guild_id)

    embed = discord.Embed(
        title=f"{E['settings']} {text(guild_id, 'settings')}",
        description=text(guild_id, "settings_desc"),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=f"{E['locked']} {text(guild_id, 'ticket')}",
        value=enabled_text(
            guild_id,
            config["ticket"]["enabled"]
        ),
        inline=True
    )

    embed.add_field(
        name=f"{E['discord']} {text(guild_id, 'logs')}",
        value=enabled_text(
            guild_id,
            config["logs"]["enabled"]
        ),
        inline=True
    )

    embed.add_field(
        name=f"{E['yes']} {text(guild_id, 'welcome')}",
        value=enabled_text(
            guild_id,
            config["welcome"]["enabled"]
        ),
        inline=True
    )

    embed.add_field(
        name=f"{E['settings']} {text(guild_id, 'autorole')}",
        value=enabled_text(
            guild_id,
            config["autorole"]["enabled"]
        ),
        inline=True
    )

    embed.add_field(
        name=f"{E['shield'] if 'shield' in E else E['locked']} {text(guild_id, 'moderation')}",
        value=enabled_text(
            guild_id,
            config["moderation"]["enabled"]
        ),
        inline=True
    )

    return embed

# =========================================================
# TICKET EMBED
# =========================================================

def ticket_settings_embed(guild_id):

    config = get_config(guild_id)
    ticket = config["ticket"]

    embed = discord.Embed(
        title=f"{E['locked']} {text(guild_id, 'ticket_settings')}",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=text(guild_id, "enabled"),
        value=enabled_text(
            guild_id,
            ticket["enabled"]
        ),
        inline=False
    )

    embed.add_field(
        name=text(guild_id, "ticket_message"),
        value=ticket["message"][:1024],
        inline=False
    )

    embed.add_field(
        name=text(guild_id, "staff_role"),
        value=(
            f"<@&{ticket['role']}>"
            if ticket["role"]
            else "—"
        ),
        inline=True
    )

    embed.add_field(
        name=text(guild_id, "category"),
        value=(
            f"<#{ticket['category']}>"
            if ticket["category"]
            else "—"
        ),
        inline=True
    )

    embed.add_field(
        name=text(guild_id, "panel_channel"),
        value=(
            f"<#{ticket['channel']}>"
            if ticket["channel"]
            else "—"
        ),
        inline=True
    )

    image_value = (
        "Ayarlı"
        if ticket.get("image_url")
        else "Yok"
    )

    embed.add_field(
        name=text(guild_id, "ticket_image"),
        value=image_value,
        inline=True
    )

    options = ticket.get("options", [])

    if options:

        option_text = "\n".join(
            f"{o.get('emoji', '🎫')} **{o.get('name', 'Seçenek')}** → `{o.get('button', o.get('name', 'Seçenek'))}`"
            for o in options
        )

    else:
        option_text = text(
            guild_id,
            "no_option"
        )

    embed.add_field(
        name=text(guild_id, "options"),
        value=option_text[:1024],
        inline=False
    )

    return embed

# =========================================================
# TICKET MESSAGE MODAL
# =========================================================

class TicketMessageModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="Ticket Mesajı"
        )

        self.message_input = discord.ui.TextInput(
            label="Ticket mesajı",
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=True
        )

        self.add_item(
            self.message_input
        )

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["message"] = (
            self.message_input.value
        )

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'message_saved')}",
            ephemeral=True
        )

# =========================================================
# IMAGE MODAL
# =========================================================

class TicketImageModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="Ticket Resmi"
        )

        self.image_url = discord.ui.TextInput(
            label="Resim URL'si",
            placeholder="https://example.com/resim.png",
            max_length=1000,
            required=True
        )

        self.add_item(
            self.image_url
        )

    async def on_submit(self, interaction):

        url = self.image_url.value.strip()

        if not re.match(
            r"^https?://",
            url,
            re.IGNORECASE
        ):
            await interaction.response.send_message(
                f"{E['no']} Geçerli bir `http://` veya `https://` linki gir.",
                ephemeral=True
            )
            return

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["image_url"] = url

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'image_saved')}",
            ephemeral=True
        )

# =========================================================
# OPTION ADD MODAL
# =========================================================

class AddOptionModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="Seçenek Ekle"
        )

        self.name_input = discord.ui.TextInput(
            label="Seçenek adı",
            placeholder="Şikayet",
            max_length=60,
            required=True
        )

        self.button_input = discord.ui.TextInput(
            label="Buton yazısı",
            placeholder="Şikayet",
            max_length=60,
            required=True
        )

        self.emoji_input = discord.ui.TextInput(
            label="Buton emojisi",
            placeholder="📝",
            max_length=100,
            required=False
        )

        self.add_item(self.name_input)
        self.add_item(self.button_input)
        self.add_item(self.emoji_input)

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        options = config["ticket"]["options"]

        if len(options) >= 20:

            await interaction.response.send_message(
                f"{E['no']} En fazla 20 seçenek ekleyebilirsin.",
                ephemeral=True
            )

            return

        options.append(
            {
                "name": self.name_input.value,
                "button": self.button_input.value,
                "emoji": self.emoji_input.value or "🎫"
            }
        )

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'option_added')}",
            ephemeral=True
        )

# =========================================================
# OPTION EDIT MODAL
# =========================================================

class EditOptionModal(discord.ui.Modal):

    def __init__(self, index):

        super().__init__(
            title="Seçenek Düzenle"
        )

        self.index = index

        config = get_config(
            interaction_guild_placeholder()
        )

        # Alanlar callback içinde tekrar doldurulacak.
        self.name_input = discord.ui.TextInput(
            label="Seçenek adı",
            max_length=60
        )

        self.button_input = discord.ui.TextInput(
            label="Buton yazısı",
            max_length=60
        )

        self.emoji_input = discord.ui.TextInput(
            label="Buton emojisi",
            max_length=100,
            required=False
        )

        self.add_item(self.name_input)
        self.add_item(self.button_input)
        self.add_item(self.emoji_input)


def interaction_guild_placeholder():
    # Modal oluşturulurken guild bilgisi mevcut olmadığı için
    # sadece güvenli bir boş yapı döndürür.
    return "0"

# =========================================================
# FIXED EDIT MODAL
# =========================================================

class RealEditOptionModal(discord.ui.Modal):

    def __init__(self, guild_id, index):

        super().__init__(
            title="Seçenek Düzenle"
        )

        self.guild_id = guild_id
        self.index = index

        options = get_config(guild_id)["ticket"]["options"]

        current = options[index]

        self.name_input = discord.ui.TextInput(
            label="Seçenek adı",
            max_length=60,
            default=current.get("name", "")
        )

        self.button_input = discord.ui.TextInput(
            label="Buton yazısı",
            max_length=60,
            default=current.get("button", "")
        )

        self.emoji_input = discord.ui.TextInput(
            label="Buton emojisi",
            max_length=100,
            required=False,
            default=current.get("emoji", "")
        )

        self.add_item(self.name_input)
        self.add_item(self.button_input)
        self.add_item(self.emoji_input)

    async def on_submit(self, interaction):

        options = get_config(
            interaction.guild.id
        )["ticket"]["options"]

        if self.index >= len(options):

            await interaction.response.send_message(
                f"{E['no']} Seçenek bulunamadı.",
                ephemeral=True
            )

            return

        options[self.index] = {
            "name": self.name_input.value,
            "button": self.button_input.value,
            "emoji": self.emoji_input.value or "🎫"
        }

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'option_edited')}",
            ephemeral=True
        )

# =========================================================
# ROLE SELECT
# =========================================================

class TicketRoleSelect(discord.ui.RoleSelect):

    def __init__(self, guild_id):
        self.guild_id = guild_id

        super().__init__(
            placeholder=text(
                guild_id,
                "select_role"
            )
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["role"] = self.values[0].id

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'staff_role')} kaydedildi.",
            ephemeral=True
        )

# =========================================================
# CATEGORY SELECT
# =========================================================

class TicketCategorySelect(discord.ui.ChannelSelect):

    def __init__(self, guild_id):
        self.guild_id = guild_id

        super().__init__(
            placeholder=text(
                guild_id,
                "select_category"
            ),
            channel_types=[
                discord.ChannelType.category
            ]
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["category"] = self.values[0].id

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'category')} kaydedildi.",
            ephemeral=True
        )

# =========================================================
# PANEL CHANNEL SELECT
# =========================================================

class TicketPanelChannelSelect(discord.ui.ChannelSelect):

    def __init__(self, guild_id):
        self.guild_id = guild_id

        super().__init__(
            placeholder=text(
                guild_id,
                "select_channel"
            ),
            channel_types=[
                discord.ChannelType.text
            ]
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["channel"] = self.values[0].id

        save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'panel_channel')} kaydedildi.",
            ephemeral=True
        )

# =========================================================
# OPTION DELETE SELECT
# =========================================================

class OptionDeleteSelect(discord.ui.Select):

    def __init__(self, guild_id):

        self.guild_id = guild_id

        options = get_config(
            guild_id
        )["ticket"]["options"]

        select_options = []

        for index, option in enumerate(
            options[:25]
        ):

            select_options.append(
                discord.SelectOption(
                    label=option["name"][:100],
                    value=str(index),
                    emoji=option.get("emoji") or None
                )
            )

        super().__init__(
            placeholder=text(
                guild_id,
                "choose_option"
            ),
            options=select_options
        )

    async def callback(self, interaction):

        index = int(
            self.values[0]
        )

        options = get_config(
            interaction.guild.id
        )["ticket"]["options"]

        if index < len(options):

            options.pop(index)

            save_data()

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'option_deleted')}",
            ephemeral=True
        )

# =========================================================
# OPTION EDIT SELECT
# =========================================================

class OptionEditSelect(discord.ui.Select):

    def __init__(self, guild_id):

        self.guild_id = guild_id

        options = get_config(
            guild_id
        )["ticket"]["options"]

        select_options = []

        for index, option in enumerate(
            options[:25]
        ):

            select_options.append(
                discord.SelectOption(
                    label=option["name"][:100],
                    value=str(index),
                    emoji=option.get("emoji") or None
                )
            )

        super().__init__(
            placeholder=text(
                guild_id,
                "choose_option"
            ),
            options=select_options
        )

    async def callback(self, interaction):

        index = int(
            self.values[0]
        )

        options = get_config(
            interaction.guild.id
        )["ticket"]["options"]

        if index >= len(options):

            await interaction.response.send_message(
                f"{E['no']} Seçenek bulunamadı.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            RealEditOptionModal(
                interaction.guild.id,
                index
            )
        )

# =========================================================
# OPTION VIEWS
# =========================================================

class OptionDeleteView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(
            timeout=120
        )

        options = get_config(
            guild_id
        )["ticket"]["options"]

        if options:
            self.add_item(
                OptionDeleteSelect(guild_id)
            )


class OptionEditView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(
            timeout=120
        )

        options = get_config(
            guild_id
        )["ticket"]["options"]

        if options:
            self.add_item(
                OptionEditSelect(guild_id)
            )

# =========================================================
# TICKET SETTINGS VIEW
# =========================================================

class TicketSettingsView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=900
        )

    @discord.ui.button(
        label="Aç / Kapat",
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

        config["ticket"]["enabled"] = not config["ticket"]["enabled"]

        save_data()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(
                interaction.guild.id
            ),
            view=TicketSettingsView()
        )

    @discord.ui.button(
        label="Ticket Mesajı",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def message(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            TicketMessageModal()
        )

    @discord.ui.button(
        label="Resim Ekle",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def image(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            TicketImageModal()
        )

    @discord.ui.button(
        label="Resmi Kaldır",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def remove_image(
        self,
        interaction,
        button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["image_url"] = None

        save_data()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(
                interaction.guild.id
            ),
            view=TicketSettingsView()
        )

    @discord.ui.button(
        label="Yetkili Rolü",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def role(
        self,
        interaction,
        button
    ):

        view = discord.ui.View(
            timeout=120
        )

        view.add_item(
            TicketRoleSelect(
                interaction.guild.id
            )
        )

        await interaction.response.send_message(
            f"{E['settings']} {text(interaction.guild.id, 'choose_role')}",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Kategori",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def category(
        self,
        interaction,
        button
    ):

        view = discord.ui.View(
            timeout=120
        )

        view.add_item(
            TicketCategorySelect(
                interaction.guild.id
            )
        )

        await interaction.response.send_message(
            f"{E['settings']} {text(interaction.guild.id, 'choose_category')}",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Panel Kanalı",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def channel(
        self,
        interaction,
        button
    ):

        view = discord.ui.View(
            timeout=120
        )

        view.add_item(
            TicketPanelChannelSelect(
                interaction.guild.id
            )
        )

        await interaction.response.send_message(
            f"{E['settings']} {text(interaction.guild.id, 'choose_channel')}",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(
        label="Seçenek Ekle",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def add_option(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            AddOptionModal()
        )

    @discord.ui.button(
        label="Seçenek Sil",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def delete_option(
        self,
        interaction,
        button
    ):

        options = get_config(
            interaction.guild.id
        )["ticket"]["options"]

        if not options:

            await interaction.response.send_message(
                text(
                    interaction.guild.id,
                    "no_option"
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            text(
                interaction.guild.id,
                "choose_option"
            ),
            view=OptionDeleteView(
                interaction.guild.id
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Seçenek Düzenle",
        style=discord.ButtonStyle.secondary,
        row=3
    )
    async def edit_option(
        self,
        interaction,
        button
    ):

        options = get_config(
            interaction.guild.id
        )["ticket"]["options"]

        if not options:

            await interaction.response.send_message(
                text(
                    interaction.guild.id,
                    "no_option"
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            text(
                interaction.guild.id,
                "choose_option"
            ),
            view=OptionEditView(
                interaction.guild.id
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Seçenekleri Gör",
        style=discord.ButtonStyle.secondary,
        row=3
    )
    async def view_options(
        self,
        interaction,
        button
    ):

        options = get_config(
            interaction.guild.id
        )["ticket"]["options"]

        if not options:

            await interaction.response.send_message(
                text(
                    interaction.guild.id,
                    "no_option"
                ),
                ephemeral=True
            )

            return

        description = "\n".join(
            f"{o.get('emoji', '🎫')} **{o['name']}** → `{o['button']}`"
            for o in options
        )

        await interaction.response.send_message(
            description,
            ephemeral=True
        )

    @discord.ui.button(
        label="Kaydet ve Gönder",
        style=discord.ButtonStyle.success,
        row=4
    )
    async def save_send(
        self,
        interaction,
        button
    ):

        config = get_config(
            interaction.guild.id
        )

        ticket = config["ticket"]

        if not ticket["enabled"]:

            await interaction.response.send_message(
                f"{E['no']} Ticket sistemi kapalı.",
                ephemeral=True
            )

            return

        if not ticket["role"]:

            await interaction.response.send_message(
                f"{E['no']} Önce **Yetkili Rolü** seç.",
                ephemeral=True
            )

            return

        if not ticket["category"]:

            await interaction.response.send_message(
                f"{E['no']} Önce **Kategori** seç.",
                ephemeral=True
            )

            return

        if not ticket["channel"]:

            await interaction.response.send_message(
                f"{E['no']} Önce **Panel Kanalı** seç.",
                ephemeral=True
            )

            return

        if not ticket["options"]:

            await interaction.response.send_message(
                f"{E['no']} En az bir Ticket seçeneği ekle.",
                ephemeral=True
            )

            return

        channel = interaction.guild.get_channel(
            ticket["channel"]
        )

        if not channel:

            await interaction.response.send_message(
                f"{E['no']} Panel kanalı bulunamadı.",
                ephemeral=True
            )

            return

        try:

            await channel.send(
                embed=ticket_panel_embed(
                    interaction.guild.id
                ),
                view=TicketPanelView(
                    interaction.guild.id
                )
            )

        except Exception as error:

            await interaction.response.send_message(
                f"{E['no']} Panel gönderilemedi.\n`{error}`",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'saved')}",
            ephemeral=True
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.danger,
        row=4
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
# TICKET PANEL EMBED
# =========================================================

def ticket_panel_embed(guild_id):

    ticket = get_config(
        guild_id
    )["ticket"]

    embed = discord.Embed(
        title=f"{E['dynex']} Destek Talebi",
        description=ticket["message"],
        color=discord.Color.blurple()
    )

    image_url = ticket.get(
        "image_url"
    )

    if image_url:

        embed.set_image(
            url=image_url
        )

    return embed

# =========================================================
# TICKET PANEL BUTTONS
# =========================================================

class TicketPanelView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(
            timeout=None
        )

        options = get_config(
            guild_id
        )["ticket"]["options"]

        for index, option in enumerate(
            options[:20]
        ):

            button = discord.ui.Button(
                label=option["button"][:80],
                emoji=option.get("emoji") or None,
                style=discord.ButtonStyle.primary,
                custom_id=f"dynex_ticket_option_{index}"
            )

            async def callback(
                interaction,
                selected_index=index
            ):

                current_options = get_config(
                    interaction.guild.id
                )["ticket"]["options"]

                if selected_index >= len(current_options):

                    await interaction.response.send_message(
                        f"{E['no']} Bu seçenek artık mevcut değil.",
                        ephemeral=True
                    )

                    return

                option_name = current_options[
                    selected_index
                ]["name"]

                await interaction.response.send_modal(
                    TicketRequestModal(
                        option_name
                    )
                )

            button.callback = callback

            self.add_item(
                button
            )

# =========================================================
# TICKET REQUEST MODAL
# =========================================================

class TicketRequestModal(discord.ui.Modal):

    def __init__(self, option_name):

        super().__init__(
            title=option_name[:45]
        )

        self.option_name = option_name

        self.request = discord.ui.TextInput(
            label="Talebiniz",
            placeholder="Sorununuzu veya talebinizi yazın.",
            style=discord.TextStyle.paragraph,
            max_length=1500,
            required=True
        )

        self.add_item(
            self.request
        )

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        ticket = config["ticket"]

        category = (
            interaction.guild.get_channel(
                ticket["category"]
            )
            if ticket["category"]
            else None
        )

        overwrites = {
            interaction.guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
        }

        role = (
            interaction.guild.get_role(
                ticket["role"]
            )
            if ticket["role"]
            else None
        )

        if role:

            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        if interaction.guild.me:

            overwrites[interaction.guild.me] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True
            )

        safe_name = re.sub(
            r"[^a-zA-Z0-9ğüşöçıİĞÜŞÖÇ_-]",
            "-",
            self.option_name.lower()
        )

        safe_name = safe_name[:25].strip("-")

        username = re.sub(
            r"[^a-zA-Z0-9_-]",
            "-",
            interaction.user.name.lower()
        )[:25]

        channel_name = (
            f"{safe_name}-{username}"
            if safe_name
            else f"ticket-{username}"
        )

        try:

            channel = await interaction.guild.create_text_channel(
                channel_name[:95],
                category=category,
                overwrites=overwrites
            )

        except Exception as error:

            await interaction.response.send_message(
                f"{E['no']} Ticket oluşturulamadı.\n`{error}`",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=f"{E['locked']} {self.option_name}",
            description=(
                f"**{text(interaction.guild.id, 'problem')}:**\n"
                f"{self.request.value}\n\n"
                f"**Kullanıcı:** {interaction.user.mention}"
            ),
            color=discord.Color.blurple()
        )

        await channel.send(
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{E['yes']} {text(interaction.guild.id, 'ticket_created')} {channel.mention}",
            ephemeral=True
        )

# =========================================================
# TICKET CLOSE
# =========================================================

class TicketCloseView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Ticket Kapat",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_ticket_close"
    )
    async def close(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            f"{E['locked']} Ticket kapatılıyor..."
        )

        await interaction.channel.delete()

# =========================================================
# OTHER SETTINGS
# =========================================================

def other_settings_embed(
    guild_id,
    section
):

    config = get_config(
        guild_id
    )

    titles = {
        "logs": "logs_settings",
        "welcome": "welcome_settings",
        "autorole": "autorole_settings",
        "moderation": "moderation_settings"
    }

    embed = discord.Embed(
        title=f"{E['settings']} {text(guild_id, titles[section])}",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=text(guild_id, section),
        value=enabled_text(
            guild_id,
            config[section]["enabled"]
        )
    )

    if section in [
        "logs",
        "welcome"
    ]:

        embed.add_field(
            name="Kanal",
            value=(
                f"<#{config[section]['channel']}>"
                if config[section]["channel"]
                else "—"
            )
        )

    if section == "welcome":

        embed.add_field(
            name=text(guild_id, "welcome_message"),
            value=config["welcome"]["message"],
            inline=False
        )

    if section == "autorole":

        embed.add_field(
            name="Rol",
            value=(
                f"<@&{config['autorole']['role']}>"
                if config["autorole"]["role"]
                else "—"
            )
        )

    return embed

# =========================================================
# SIMPLE SETTINGS VIEW
# =========================================================

class SimpleSettingsView(discord.ui.View):

    def __init__(self, section):

        super().__init__(
            timeout=600
        )

        self.section = section

    @discord.ui.button(
        label="Aç / Kapat",
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

        config[self.section]["enabled"] = not config[
            self.section
        ]["enabled"]

        save_data()

        await interaction.response.edit_message(
            embed=other_settings_embed(
                interaction.guild.id,
                self.section
            ),
            view=self
        )

    @discord.ui.button(
        label="Geri",
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
# MAIN SETTINGS VIEW
# =========================================================

class SettingsView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=600
        )

    @discord.ui.button(
        label="Ticket",
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
        label="Loglar",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def logs(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=other_settings_embed(
                interaction.guild.id,
                "logs"
            ),
            view=SimpleSettingsView(
                "logs"
            )
        )

    @discord.ui.button(
        label="Hoş Geldin",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def welcome(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=other_settings_embed(
                interaction.guild.id,
                "welcome"
            ),
            view=SimpleSettingsView(
                "welcome"
            )
        )

    @discord.ui.button(
        label="Otorol",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def autorole(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=other_settings_embed(
                interaction.guild.id,
                "autorole"
            ),
            view=SimpleSettingsView(
                "autorole"
            )
        )

    @discord.ui.button(
        label="Moderasyon",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def moderation(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=other_settings_embed(
                interaction.guild.id,
                "moderation"
            ),
            view=SimpleSettingsView(
                "moderation"
            )
        )

    @discord.ui.button(
        label="Yenile",
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
            view=SettingsView()
        )

    @discord.ui.button(
        label="Sıfırla",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def reset(
        self,
        interaction,
        button
    ):

        configs[str(
            interaction.guild.id
        )] = copy.deepcopy(
            DEFAULT
        )

        save_data()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=SettingsView()
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

    if not interaction.response.is_done():

        await interaction.response.send_message(
            f"{E['no']} {text(interaction.guild.id, 'permission')}",
            ephemeral=True
        )

# =========================================================
# WELCOME + AUTOROLE
# =========================================================

@bot.event
async def on_member_join(member):

    config = get_config(
        member.guild.id
    )

    autorole = config["autorole"]

    if autorole["enabled"] and autorole["role"]:

        role = member.guild.get_role(
            autorole["role"]
        )

        if role:

            try:
                await member.add_roles(
                    role
                )
            except Exception:
                pass

    welcome = config["welcome"]

    if welcome["enabled"] and welcome["channel"]:

        channel = member.guild.get_channel(
            welcome["channel"]
        )

        if channel:

            try:

                message = welcome["message"].replace(
                    "{member}",
                    member.mention
                )

                await channel.send(
                    message
                )

            except Exception:
                pass

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
            TicketCloseView()
        )
    except Exception:
        pass

# =========================================================
# START
# =========================================================

load_data()

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
