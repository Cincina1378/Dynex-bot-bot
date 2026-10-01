import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import copy
import secrets
import re
import asyncio
from datetime import timedelta


# =========================================================
# DYNEX
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = "config.json"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


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
    "support": "<:Takviye:1555263624787005470>",
    "correct": "<:Doru:1555263630440923187>",
    "discord": "<:Discord:1555263704646557816>",
    "no": "<:Dynexhayir:1555265003727102134>",
}


# =========================================================
# DİLLER
# =========================================================

LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
    "az": "Azərbaycan dili"
}

TEXT = {
    "tr": {
        "settings": "Dynex Ayarları",
        "saved": "Ayarlar kaydedildi.",
        "permission": "Bu ayarı değiştirmek için Yönetici yetkisine sahip olmalısın.",
        "reset": "Ayarlar sıfırlandı.",
        "ticket": "Ticket",
        "welcome": "Hoş Geldiniz",
        "moderation": "Moderasyon",
        "logs": "Loglar",
        "autorole": "Otorol",
        "voice": "Ses Bildirimleri",
        "language": "Dil",
        "panel_sent": "Ticket paneli gönderildi.",
        "panel_missing": "Önce ticket panel kanalını seçmelisin.",
        "category_missing": "Önce ticket kategorisini seçmelisin.",
        "option_missing": "Ticket seçeneği bulunamadı.",
        "ticket_created": "Ticket oluşturuldu.",
        "ticket_closed": "Ticket kapatıldı.",
        "emoji_missing": "Bu emoji sunucuda bulunamadı.",
        "too_many_options": "En fazla 20 ticket seçeneği ekleyebilirsin.",
        "language_changed": "Dil değiştirildi.",
    },
    "en": {
        "settings": "Dynex Settings",
        "saved": "Settings saved.",
        "permission": "You need Administrator permission.",
        "reset": "Settings reset.",
        "ticket": "Ticket",
        "welcome": "Welcome",
        "moderation": "Moderation",
        "logs": "Logs",
        "autorole": "Auto Role",
        "voice": "Voice Notifications",
        "language": "Language",
        "panel_sent": "Ticket panel sent.",
        "panel_missing": "Select the ticket panel channel first.",
        "category_missing": "Select the ticket category first.",
        "option_missing": "Ticket option not found.",
        "ticket_created": "Ticket created.",
        "ticket_closed": "Ticket closed.",
        "emoji_missing": "This emoji was not found in the server.",
        "too_many_options": "You can add up to 20 ticket options.",
        "language_changed": "Language changed.",
    },
    "az": {
        "settings": "Dynex Ayarları",
        "saved": "Ayarlar yadda saxlanıldı.",
        "permission": "Bunu dəyişmək üçün Administrator icazən olmalıdır.",
        "reset": "Ayarlar sıfırlandı.",
        "ticket": "Ticket",
        "welcome": "Xoş Gəlmisiniz",
        "moderation": "Moderasiya",
        "logs": "Loglar",
        "autorole": "Avtomatik Rol",
        "voice": "Səs Bildirişləri",
        "language": "Dil",
        "panel_sent": "Ticket paneli göndərildi.",
        "panel_missing": "Əvvəlcə ticket panel kanalını seç.",
        "category_missing": "Əvvəlcə ticket kateqoriyasını seç.",
        "option_missing": "Ticket seçimi tapılmadı.",
        "ticket_created": "Ticket yaradıldı.",
        "ticket_closed": "Ticket bağlandı.",
        "emoji_missing": "Bu emoji serverdə tapılmadı.",
        "too_many_options": "Maksimum 20 ticket seçimi əlavə edə bilərsən.",
        "language_changed": "Dil dəyişdirildi.",
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
        "message": "Destek talebi oluşturmak için aşağıdaki seçeneklerden birini seçin.",
        "title": "Destek Merkezi",
        "description": "Size yardımcı olabilmemiz için aşağıdaki seçeneklerden birini seçin.",
        "color": "5865F2",
        "image_url": None,
        "thumbnail_url": None,
        "options": [
            {
                "id": "destek",
                "name": "Destek",
                "button": "Destek",
                "emoji": "🎫"
            },
            {
                "id": "sikayet",
                "name": "Şikayet",
                "button": "Şikayet",
                "emoji": "📝"
            }
        ]
    },

    "welcome": {
        "enabled": False,
        "channel": None,
        "message": "Hoş geldin {member}! {server} sunucusuna katıldın.",
        "title": "Hoş Geldin!",
        "description": "Sunucumuza katıldığın için teşekkürler.",
        "color": "57F287",
        "image_url": None,
        "thumbnail_url": None,
        "show_member": True,
        "show_username": True,
        "show_id": False,
        "show_server": True,
        "show_member_count": True,
        "show_join_number": True,
        "dm_enabled": False,
        "dm_message": "Merhaba {member}, {server} sunucusuna hoş geldin!"
    },

    "moderation": {
        "enabled": True,
        "anti_spam": True,
        "anti_link": False,
        "bad_words": False,
        "bad_words_list": [],
        "max_warnings": 3,
        "warning_action": "timeout",
        "timeout_minutes": 10,
        "delete_after": 0
    },

    "logs": {
        "enabled": False,
        "channel": None,
        "message_delete": True,
        "message_edit": True,
        "member_join": True,
        "member_leave": True,
        "ban": True,
        "kick": True,
        "timeout": True
    },

    "autorole": {
        "enabled": False,
        "role": None
    },

    "voice": {
        "enabled": False,
        "channel": None,
        "join_message": "{member} ses kanalına katıldı.",
        "leave_message": "{member} ses kanalından ayrıldı."
    }
}


# =========================================================
# CONFIG SİSTEMİ
# =========================================================

configs = {}


def merge_config(default, current):
    result = copy.deepcopy(default)

    if not isinstance(current, dict):
        return result

    for key, value in current.items():

        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value

    return result


def load_configs():
    global configs

    if not os.path.exists(CONFIG_FILE):
        configs = {}
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        configs = {}

        for guild_id, config in data.items():
            configs[guild_id] = merge_config(
                DEFAULT_CONFIG,
                config
            )

    except Exception as error:
        print("Config yükleme hatası:", error)
        configs = {}


def save_configs():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(
                configs,
                file,
                ensure_ascii=False,
                indent=4
            )
    except Exception as error:
        print("Config kayıt hatası:", error)


def get_config(guild_id):
    guild_id = str(guild_id)

    if guild_id not in configs:
        configs[guild_id] = copy.deepcopy(DEFAULT_CONFIG)

    configs[guild_id] = merge_config(
        DEFAULT_CONFIG,
        configs[guild_id]
    )

    return configs[guild_id]


def reset_config(guild_id):
    configs[str(guild_id)] = copy.deepcopy(DEFAULT_CONFIG)
    save_configs()


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def get_lang(guild_id):
    config = get_config(guild_id)
    language = config.get("language", "tr")

    if language not in LANGUAGES:
        language = "tr"

    return language


def tr(guild_id, key):
    language = get_lang(guild_id)
    return TEXT[language].get(key, key)


def parse_bool(value, default=False):
    if value is None:
        return default

    value = str(value).strip().lower()

    if value in [
        "true",
        "1",
        "evet",
        "yes",
        "on",
        "açık",
        "acik"
    ]:
        return True

    if value in [
        "false",
        "0",
        "hayır",
        "hayir",
        "no",
        "off",
        "kapalı",
        "kapali"
    ]:
        return False

    return default


def parse_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def parse_color(value, default=0x5865F2):
    if not value:
        return default

    value = str(value).strip()

    if value.startswith("#"):
        value = value[1:]

    try:
        result = int(value, 16)

        if 0 <= result <= 0xFFFFFF:
            return result

    except Exception:
        pass

    return default


def replace_variables(text, member):
    if not text:
        return ""

    guild = member.guild

    replacements = {
        "{member}": member.mention,
        "{username}": member.name,
        "{server}": guild.name,
        "{member_count}": str(guild.member_count),
        "{id}": str(member.id)
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    return text


def is_admin(interaction):
    return (
        interaction.guild
        and interaction.user.guild_permissions.administrator
    )


async def admin_required(interaction):
    if is_admin(interaction):
        return True

    await interaction.response.send_message(
        f"{E['no']} {tr(interaction.guild.id, 'permission')}",
        ephemeral=True
    )

    return False


# =========================================================
# EMOJİ SİSTEMİ
# =========================================================

def parse_emoji(value, guild):
    """
    Desteklenenler:

    🎫
    ⚠️
    :dikkat:
    :uyari:
    :destek:
    <:Dynex:1555263060350996510>
    <a:animasyonlu:123456789>
    """

    if not value:
        return None

    value = str(value).strip()

    if not value:
        return None

    # <:isim:id>
    if value.startswith("<:") or value.startswith("<a:"):
        try:
            emoji = discord.PartialEmoji.from_str(value)

            if emoji.id:
                return emoji

        except Exception:
            return None

    # :isim:
    if value.startswith(":") and value.endswith(":"):

        emoji_name = value[1:-1].strip()

        # Sunucudaki BÜTÜN emojiler arasında arar.
        emoji = discord.utils.get(
            guild.emojis,
            name=emoji_name
        )

        if emoji:
            return emoji

        return None

    # Unicode / klavye emojisi
    return value


def emoji_exists(value, guild):
    if not value:
        return True

    value = str(value).strip()

    if value.startswith(":") and value.endswith(":"):

        emoji_name = value[1:-1].strip()

        return discord.utils.get(
            guild.emojis,
            name=emoji_name
        ) is not None

    if value.startswith("<:") or value.startswith("<a:"):

        try:
            emoji = discord.PartialEmoji.from_str(value)
            return emoji.id is not None
        except Exception:
            return False

    return True


# =========================================================
# LOG
# =========================================================

async def send_log(guild, title, description):
    config = get_config(guild.id)
    log_config = config["logs"]

    if not log_config.get("enabled"):
        return

    channel_id = log_config.get("channel")

    if not channel_id:
        return

    channel = guild.get_channel(int(channel_id))

    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow()
    )

    try:
        await channel.send(embed=embed)
    except Exception:
        pass


# =========================================================
# /AYARLAR
# =========================================================

class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_settings_ticket"
    )
    async def ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            TicketSettingsModal()
        )

    @discord.ui.button(
        label="Hoş Geldiniz",
        emoji="👋",
        style=discord.ButtonStyle.success,
        custom_id="dynex_settings_welcome"
    )
    async def welcome(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            WelcomeSettingsModal()
        )

    @discord.ui.button(
        label="Moderasyon",
        emoji="🛡️",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_settings_moderation"
    )
    async def moderation(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            ModerationSettingsModal()
        )

    @discord.ui.button(
        label="Loglar",
        emoji="📋",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_settings_logs"
    )
    async def logs(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            LogsSettingsModal()
        )

    @discord.ui.button(
        label="Otorol",
        emoji="🔧",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_settings_autorole"
    )
    async def autorole(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            AutoroleSettingsModal()
        )


class SettingsView2(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Ses Bildirimleri",
        emoji="🔊",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_settings_voice"
    )
    async def voice(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            VoiceSettingsModal()
        )

    @discord.ui.button(
        label="Ayarları Sıfırla",
        emoji="♻️",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_settings_reset"
    )
    async def reset(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await admin_required(interaction):
            return

        reset_config(interaction.guild.id)

        await interaction.response.send_message(
            f"{E['yes']} {tr(interaction.guild.id, 'reset')}",
            ephemeral=True
        )


# =========================================================
# TICKET AYARLARI
# =========================================================

class TicketSettingsModal(
    discord.ui.Modal,
    title="🎫 Ticket Ayarları"
):

    enabled = discord.ui.TextInput(
        label="Ticket sistemi",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    title_text = discord.ui.TextInput(
        label="Başlık",
        placeholder="Destek Merkezi",
        required=False,
        max_length=256
    )

    description = discord.ui.TextInput(
        label="Açıklama",
        placeholder="Ticket panel açıklaması",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    message = discord.ui.TextInput(
        label="Ticket mesajı",
        placeholder="Panelde gösterilecek mesaj",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    image_url = discord.ui.TextInput(
        label="Resim URL",
        placeholder="Boş bırakabilirsin",
        required=False,
        max_length=1000
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(interaction.guild.id)
        ticket = config["ticket"]

        ticket["enabled"] = parse_bool(
            self.enabled.value,
            ticket["enabled"]
        )

        if self.title_text.value:
            ticket["title"] = self.title_text.value

        if self.description.value:
            ticket["description"] = self.description.value

        if self.message.value:
            ticket["message"] = self.message.value

        ticket["image_url"] = (
            self.image_url.value.strip()
            if self.image_url.value.strip()
            else None
        )

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} {tr(interaction.guild.id, 'saved')}\n\n"
            "🎫 Yetkili rolü, kategori ve panel kanalını aşağıdan seçebilirsin.",
            view=TicketSelectorsView(),
            ephemeral=True
        )


# =========================================================
# TICKET SEÇİCİLERİ
# =========================================================

class TicketSelectorsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(TicketRoleSelect())
        self.add_item(TicketCategorySelect())
        self.add_item(TicketPanelChannelSelect())


class TicketRoleSelect(discord.ui.RoleSelect):

    def __init__(self):
        super().__init__(
            placeholder="🎫 Ticket yetkili rolünü seç",
            min_values=0,
            max_values=1,
            custom_id="dynex_ticket_role"
        )

    async def callback(self, interaction):

        config = get_config(interaction.guild.id)

        if self.values:
            config["ticket"]["role"] = str(
                self.values[0].id
            )
        else:
            config["ticket"]["role"] = None

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Ticket yetkili rolü kaydedildi.",
            ephemeral=True
        )


class TicketCategorySelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="📁 Ticket kategorisini seç",
            channel_types=[discord.ChannelType.category],
            min_values=0,
            max_values=1,
            custom_id="dynex_ticket_category"
        )

    async def callback(self, interaction):

        config = get_config(interaction.guild.id)

        if self.values:
            config["ticket"]["category"] = str(
                self.values[0].id
            )
        else:
            config["ticket"]["category"] = None

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Ticket kategorisi kaydedildi.",
            ephemeral=True
        )


class TicketPanelChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):
        super().__init__(
            placeholder="📢 Ticket panel kanalını seç",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=1,
            custom_id="dynex_ticket_panel_channel"
        )

    async def callback(self, interaction):

        config = get_config(interaction.guild.id)

        if self.values:
            config["ticket"]["channel"] = str(
                self.values[0].id
            )
        else:
            config["ticket"]["channel"] = None

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Ticket panel kanalı kaydedildi.",
            ephemeral=True
        )


# =========================================================
# TICKET YÖNETİMİ
# =========================================================

class TicketManagementView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Seçenek Ekle",
        emoji="➕",
        style=discord.ButtonStyle.success
    )
    async def add_option(
        self,
        interaction,
        button
    ):

        if not await admin_required(interaction):
            return

        config = get_config(interaction.guild.id)

        if len(config["ticket"]["options"]) >= 20:

            await interaction.response.send_message(
                f"{E['no']} {tr(interaction.guild.id, 'too_many_options')}",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            AddTicketOptionModal()
        )

    @discord.ui.button(
        label="Seçenek Sil",
        emoji="🗑️",
        style=discord.ButtonStyle.danger
    )
    async def delete_option(
        self,
        interaction,
        button
    ):

        if not await admin_required(interaction):
            return

        config = get_config(interaction.guild.id)

        if not config["ticket"]["options"]:

            await interaction.response.send_message(
                "Silinecek seçenek yok.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            "Silmek istediğin seçeneği seç:",
            view=DeleteTicketOptionView(
                interaction.guild.id
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Seçenek Düzenle",
        emoji="✏️",
        style=discord.ButtonStyle.primary
    )
    async def edit_option(
        self,
        interaction,
        button
    ):

        if not await admin_required(interaction):
            return

        config = get_config(interaction.guild.id)

        if not config["ticket"]["options"]:

            await interaction.response.send_message(
                "Düzenlenecek seçenek yok.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            "Düzenlemek istediğin seçeneği seç:",
            view=EditTicketOptionView(
                interaction.guild.id
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Seçenekleri Gör",
        emoji="📋",
        style=discord.ButtonStyle.secondary
    )
    async def show_options(
        self,
        interaction,
        button
    ):

        config = get_config(interaction.guild.id)
        options = config["ticket"]["options"]

        if not options:
            text = "Henüz ticket seçeneği yok."

        else:
            lines = []

            for option in options:

                emoji = option.get("emoji", "")

                lines.append(
                    f"{emoji} **{option['name']}** "
                    f"→ `{option['button']}`"
                )

            text = "\n".join(lines)

        await interaction.response.send_message(
            text,
            ephemeral=True
        )

    @discord.ui.button(
        label="Paneli Gönder",
        emoji="📨",
        style=discord.ButtonStyle.primary
    )
    async def send_panel(
        self,
        interaction,
        button
    ):

        if not await admin_required(interaction):
            return

        await send_ticket_panel(interaction)


async def send_ticket_panel(interaction):

    config = get_config(interaction.guild.id)
    ticket = config["ticket"]

    channel_id = ticket.get("channel")

    if not channel_id:

        await interaction.response.send_message(
            f"{E['no']} {tr(interaction.guild.id, 'panel_missing')}",
            ephemeral=True
        )

        return

    channel = interaction.guild.get_channel(
        int(channel_id)
    )

    if not channel:

        await interaction.response.send_message(
            f"{E['no']} Panel kanalı bulunamadı.",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        title=ticket.get("title", "Destek Merkezi"),
        description=(
            ticket.get("description", "")
            + "\n\n"
            + ticket.get("message", "")
        ),
        color=parse_color(
            ticket.get("color"),
            0x5865F2
        )
    )

    if ticket.get("image_url"):
        embed.set_image(
            url=ticket["image_url"]
        )

    if ticket.get("thumbnail_url"):
        embed.set_thumbnail(
            url=ticket["thumbnail_url"]
        )

    view = TicketPanelView(
        interaction.guild.id
    )

    try:

        await channel.send(
            embed=embed,
            view=view
        )

    except Exception as error:

        await interaction.response.send_message(
            f"{E['no']} Panel gönderilemedi.\n`{error}`",
            ephemeral=True
        )

        return

    await interaction.response.send_message(
        f"{E['yes']} {tr(interaction.guild.id, 'panel_sent')}",
        ephemeral=True
    )


# =========================================================
# TICKET SEÇENEK EKLE
# =========================================================

class AddTicketOptionModal(
    discord.ui.Modal,
    title="🎫 Ticket Seçeneği Ekle"
):

    name = discord.ui.TextInput(
        label="Seçenek adı",
        placeholder="Örn: Şikayet",
        max_length=80
    )

    button_text = discord.ui.TextInput(
        label="Buton yazısı",
        placeholder="Örn: Şikayet Oluştur",
        max_length=80
    )

    emoji = discord.ui.TextInput(
        label="Emoji",
        placeholder="🎫 veya :dikkat: veya <:isim:id>",
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        emoji_value = self.emoji.value.strip()

        if emoji_value:

            if not emoji_exists(
                emoji_value,
                interaction.guild
            ):

                await interaction.response.send_message(
                    f"{E['no']} {tr(interaction.guild.id, 'emoji_missing')}",
                    ephemeral=True
                )

                return

        config = get_config(interaction.guild.id)

        if len(config["ticket"]["options"]) >= 20:

            await interaction.response.send_message(
                f"{E['no']} {tr(interaction.guild.id, 'too_many_options')}",
                ephemeral=True
            )

            return

        option_id = secrets.token_hex(4)

        config["ticket"]["options"].append({
            "id": option_id,
            "name": self.name.value,
            "button": self.button_text.value,
            "emoji": emoji_value
        })

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Ticket seçeneği eklendi.",
            ephemeral=True
        )


# =========================================================
# TICKET SEÇENEK SİL
# =========================================================

class DeleteTicketOptionView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(timeout=120)

        config = get_config(guild_id)

        options = config["ticket"]["options"]

        choices = []

        for option in options[:25]:

            choices.append(
                discord.SelectOption(
                    label=option["name"][:100],
                    value=option["id"],
                    emoji=(
                        parse_emoji(
                            option.get("emoji"),
                            discord.utils.get(
                                bot.guilds,
                                id=guild_id
                            )
                        )
                        if option.get("emoji")
                        else None
                    )
                )
            )

        select = discord.ui.Select(
            placeholder="Silinecek ticket seçeneğini seç",
            options=choices,
            custom_id="dynex_delete_ticket_option"
        )

        async def callback(interaction):

            config = get_config(
                interaction.guild.id
            )

            option_id = select.values[0]

            before = len(
                config["ticket"]["options"]
            )

            config["ticket"]["options"] = [
                option
                for option in config["ticket"]["options"]
                if option["id"] != option_id
            ]

            if len(config["ticket"]["options"]) == before:

                await interaction.response.send_message(
                    f"{E['no']} {tr(interaction.guild.id, 'option_missing')}",
                    ephemeral=True
                )

                return

            save_configs()

            await interaction.response.send_message(
                f"{E['yes']} Ticket seçeneği silindi.",
                ephemeral=True
            )

        select.callback = callback
        self.add_item(select)


# =========================================================
# TICKET SEÇENEK DÜZENLE
# =========================================================

class EditTicketOptionView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(timeout=120)

        config = get_config(guild_id)

        options = config["ticket"]["options"]

        choices = []

        for option in options[:25]:

            choices.append(
                discord.SelectOption(
                    label=option["name"][:100],
                    value=option["id"]
                )
            )

        select = discord.ui.Select(
            placeholder="Düzenlenecek seçeneği seç",
            options=choices,
            custom_id="dynex_edit_ticket_option"
        )

        async def callback(interaction):

            option_id = select.values[0]

            await interaction.response.send_modal(
                EditTicketOptionModal(
                    option_id
                )
            )

        select.callback = callback
        self.add_item(select)


class EditTicketOptionModal(
    discord.ui.Modal,
    title="🎫 Ticket Seçeneğini Düzenle"
):

    def __init__(self, option_id):

        super().__init__()

        self.option_id = option_id

        config = get_config(
            0
        )

        # Alanlar aşağıda varsayılan boş bırakılır.
        self.name = discord.ui.TextInput(
            label="Yeni seçenek adı",
            required=False,
            max_length=80
        )

        self.button_text = discord.ui.TextInput(
            label="Yeni buton yazısı",
            required=False,
            max_length=80
        )

        self.emoji = discord.ui.TextInput(
            label="Yeni emoji",
            placeholder="🎫 / :emoji: / <:isim:id>",
            required=False,
            max_length=100
        )

        self.add_item(self.name)
        self.add_item(self.button_text)
        self.add_item(self.emoji)

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(
            interaction.guild.id
        )

        option = next(
            (
                item
                for item in config["ticket"]["options"]
                if item["id"] == self.option_id
            ),
            None
        )

        if not option:

            await interaction.response.send_message(
                f"{E['no']} {tr(interaction.guild.id, 'option_missing')}",
                ephemeral=True
            )

            return

        if self.name.value:
            option["name"] = self.name.value

        if self.button_text.value:
            option["button"] = self.button_text.value

        if self.emoji.value:

            if not emoji_exists(
                self.emoji.value,
                interaction.guild
            ):

                await interaction.response.send_message(
                    f"{E['no']} {tr(interaction.guild.id, 'emoji_missing')}",
                    ephemeral=True
                )

                return

            option["emoji"] = self.emoji.value

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Ticket seçeneği düzenlendi.",
            ephemeral=True
        )


# =========================================================
# TICKET PANELİ
# =========================================================

class TicketPanelView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(timeout=None)

        config = get_config(guild_id)

        options = config["ticket"]["options"]

        for option in options[:20]:

            emoji = parse_emoji(
                option.get("emoji"),
                discord.utils.get(
                    bot.guilds,
                    id=guild_id
                )
            )

            button = discord.ui.Button(
                label=option["button"][:80],
                style=discord.ButtonStyle.primary,
                emoji=emoji,
                custom_id=f"dynex_ticket:{option['id']}"
            )

            async def callback(
                interaction,
                option_id=option["id"]
            ):

                config = get_config(
                    interaction.guild.id
                )

                selected = next(
                    (
                        item
                        for item in config["ticket"]["options"]
                        if item["id"] == option_id
                    ),
                    None
                )

                if not selected:

                    await interaction.response.send_message(
                        f"{E['no']} {tr(interaction.guild.id, 'option_missing')}",
                        ephemeral=True
                    )

                    return

                await interaction.response.send_modal(
                    TicketRequestModal(
                        option_id,
                        selected["name"]
                    )
                )

            button.callback = callback
            self.add_item(button)


# =========================================================
# TICKET TALEP MODALI
# =========================================================

class TicketRequestModal(
    discord.ui.Modal
):

    def __init__(self, option_id, option_name):

        super().__init__(
            title=f"🎫 {option_name[:40]}"
        )

        self.option_id = option_id
        self.option_name = option_name

        self.request = discord.ui.TextInput(
            label="Talebiniz",
            placeholder="Ne hakkında yardım istiyorsunuz?",
            style=discord.TextStyle.paragraph,
            max_length=2000
        )

        self.add_item(self.request)

    async def on_submit(self, interaction):

        guild = interaction.guild

        config = get_config(guild.id)
        ticket = config["ticket"]

        category_id = ticket.get("category")

        if not category_id:

            await interaction.response.send_message(
                f"{E['no']} {tr(guild.id, 'category_missing')}",
                ephemeral=True
            )

            return

        category = guild.get_channel(
            int(category_id)
        )

        if not category:

            await interaction.response.send_message(
                f"{E['no']} {tr(guild.id, 'category_missing')}",
                ephemeral=True
            )

            return

        staff_role = None

        if ticket.get("role"):

            staff_role = guild.get_role(
                int(ticket["role"])
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }

        if staff_role:

            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        safe_name = re.sub(
            r"[^a-zA-Z0-9\-]",
            "-",
            self.option_name.lower()
        )

        safe_name = safe_name[:25]

        channel_name = (
            f"{safe_name}-"
            f"{interaction.user.name.lower()}"
        )

        channel_name = re.sub(
            r"[^a-zA-Z0-9\-]",
            "-",
            channel_name
        )[:90]

        try:

            channel = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites,
                topic=(
                    f"Dynex Ticket | "
                    f"{self.option_name} | "
                    f"{interaction.user.id}"
                )
            )

        except Exception as error:

            await interaction.response.send_message(
                f"{E['no']} Ticket oluşturulamadı.\n`{error}`",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=f"🎫 {self.option_name}",
            description=(
                f"**Ticket sahibi:** {interaction.user.mention}\n\n"
                f"**Talep:**\n{self.request.value}"
            ),
            color=0x5865F2
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{E['yes']} {tr(guild.id, 'ticket_created')}\n"
            f"{channel.mention}",
            ephemeral=True
        )


# =========================================================
# TICKET KAPAT
# =========================================================

class TicketCloseView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ticket Kapat",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_ticket_close"
    )
    async def close_ticket(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            f"{E['wait']} Ticket kapatılıyor...",
            ephemeral=True
        )

        await asyncio.sleep(1)

        try:
            await interaction.channel.delete(
                reason=f"Ticket kapatıldı: {interaction.user}"
            )
        except Exception:
            pass


# =========================================================
# HOŞ GELDİNİZ AYARLARI
# =========================================================

class WelcomeSettingsModal(
    discord.ui.Modal,
    title="👋 Hoş Geldiniz Ayarları"
):

    enabled = discord.ui.TextInput(
        label="Hoş geldin sistemi",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    message = discord.ui.TextInput(
        label="Hoş geldin mesajı",
        placeholder="{member} {server} {member_count}",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1000
    )

    title_text = discord.ui.TextInput(
        label="Embed başlığı",
        required=False,
        max_length=256
    )

    description = discord.ui.TextInput(
        label="Embed açıklaması",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    color = discord.ui.TextInput(
        label="Embed rengi",
        placeholder="5865F2 veya #5865F2",
        required=False,
        max_length=20
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(
            interaction.guild.id
        )

        welcome = config["welcome"]

        welcome["enabled"] = parse_bool(
            self.enabled.value,
            welcome["enabled"]
        )

        if self.message.value:
            welcome["message"] = self.message.value

        if self.title_text.value:
            welcome["title"] = self.title_text.value

        if self.description.value:
            welcome["description"] = self.description.value

        if self.color.value:
            welcome["color"] = self.color.value

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Hoş geldiniz ayarları kaydedildi.\n\n"
            "📢 Hoş geldin kanalını aşağıdan seçebilirsin.",
            view=WelcomeChannelView(),
            ephemeral=True
        )


class WelcomeChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(
            WelcomeChannelSelect()
        )


class WelcomeChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):

        super().__init__(
            placeholder="📢 Hoş geldin kanalını seç",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=1,
            custom_id="dynex_welcome_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        if self.values:
            config["welcome"]["channel"] = str(
                self.values[0].id
            )
        else:
            config["welcome"]["channel"] = None

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Hoş geldin kanalı kaydedildi.",
            ephemeral=True
        )


# =========================================================
# MODERASYON AYARLARI
# =========================================================

class ModerationSettingsModal(
    discord.ui.Modal,
    title="🛡️ Moderasyon Ayarları"
):

    enabled = discord.ui.TextInput(
        label="Moderasyon",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    anti_spam = discord.ui.TextInput(
        label="Anti-Spam",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    anti_link = discord.ui.TextInput(
        label="Anti-Link",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    bad_words = discord.ui.TextInput(
        label="Küfür filtresi",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    bad_words_list = discord.ui.TextInput(
        label="Yasaklı kelimeler",
        placeholder="kelime1, kelime2, kelime3",
        required=False,
        max_length=1000
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(
            interaction.guild.id
        )

        moderation = config["moderation"]

        moderation["enabled"] = parse_bool(
            self.enabled.value,
            moderation["enabled"]
        )

        moderation["anti_spam"] = parse_bool(
            self.anti_spam.value,
            moderation["anti_spam"]
        )

        moderation["anti_link"] = parse_bool(
            self.anti_link.value,
            moderation["anti_link"]
        )

        moderation["bad_words"] = parse_bool(
            self.bad_words.value,
            moderation["bad_words"]
        )

        if self.bad_words_list.value:

            moderation["bad_words_list"] = [
                word.strip().lower()
                for word in self.bad_words_list.value.split(",")
                if word.strip()
            ]

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Moderasyon ayarları kaydedildi.\n\n"
            "⚙️ Ceza ve süre ayarları için aşağıdaki butona bas.",
            view=ModerationAdvancedView(),
            ephemeral=True
        )


class ModerationAdvancedView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Ceza Ayarları",
        emoji="⚙️",
        style=discord.ButtonStyle.primary
    )
    async def punishment(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            ModerationPunishmentModal()
        )


class ModerationPunishmentModal(
    discord.ui.Modal,
    title="🛡️ Moderasyon Ceza Ayarları"
):

    max_warnings = discord.ui.TextInput(
        label="Maksimum uyarı",
        placeholder="3",
        required=False,
        max_length=5
    )

    warning_action = discord.ui.TextInput(
        label="Uyarı sonrası işlem",
        placeholder="timeout / kick / ban",
        required=False,
        max_length=20
    )

    timeout_minutes = discord.ui.TextInput(
        label="Timeout süresi",
        placeholder="10",
        required=False,
        max_length=10
    )

    delete_after = discord.ui.TextInput(
        label="Mesaj silme süresi",
        placeholder="0 = kapalı",
        required=False,
        max_length=10
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(
            interaction.guild.id
        )

        moderation = config["moderation"]

        if self.max_warnings.value:
            moderation["max_warnings"] = parse_int(
                self.max_warnings.value,
                moderation["max_warnings"]
            )

        if self.warning_action.value:
            moderation["warning_action"] = (
                self.warning_action.value.strip().lower()
            )

        if self.timeout_minutes.value:
            moderation["timeout_minutes"] = parse_int(
                self.timeout_minutes.value,
                moderation["timeout_minutes"]
            )

        if self.delete_after.value:
            moderation["delete_after"] = parse_int(
                self.delete_after.value,
                moderation["delete_after"]
            )

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Moderasyon ceza ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# LOG AYARLARI
# =========================================================

class LogsSettingsModal(
    discord.ui.Modal,
    title="📋 Log Ayarları"
):

    enabled = discord.ui.TextInput(
        label="Log sistemi",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    message_delete = discord.ui.TextInput(
        label="Mesaj silme logu",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    message_edit = discord.ui.TextInput(
        label="Mesaj düzenleme logu",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    member_join = discord.ui.TextInput(
        label="Üye giriş logu",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    member_leave = discord.ui.TextInput(
        label="Üye ayrılma logu",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(
            interaction.guild.id
        )

        logs = config["logs"]

        logs["enabled"] = parse_bool(
            self.enabled.value,
            logs["enabled"]
        )

        logs["message_delete"] = parse_bool(
            self.message_delete.value,
            logs["message_delete"]
        )

        logs["message_edit"] = parse_bool(
            self.message_edit.value,
            logs["message_edit"]
        )

        logs["member_join"] = parse_bool(
            self.member_join.value,
            logs["member_join"]
        )

        logs["member_leave"] = parse_bool(
            self.member_leave.value,
            logs["member_leave"]
        )

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Log ayarları kaydedildi.\n\n"
            "📋 Log kanalını aşağıdan seçebilirsin.",
            view=LogChannelView(),
            ephemeral=True
        )


class LogChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(
            LogChannelSelect()
        )


class LogChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):

        super().__init__(
            placeholder="📋 Log kanalını seç",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=1,
            custom_id="dynex_log_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        if self.values:
            config["logs"]["channel"] = str(
                self.values[0].id
            )
        else:
            config["logs"]["channel"] = None

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Log kanalı kaydedildi.",
            ephemeral=True
        )


# =========================================================
# OTOROL
# =========================================================

class AutoroleSettingsModal(
    discord.ui.Modal,
    title="🔧 Otorol Ayarları"
):

    enabled = discord.ui.TextInput(
        label="Otorol sistemi",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(
            interaction.guild.id
        )

        config["autorole"]["enabled"] = parse_bool(
            self.enabled.value,
            config["autorole"]["enabled"]
        )

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Otorol ayarları kaydedildi.\n\n"
            "🔧 Verilecek rolü aşağıdan seç.",
            view=AutoroleRoleView(),
            ephemeral=True
        )


class AutoroleRoleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(
            AutoroleSelect()
        )


class AutoroleSelect(discord.ui.RoleSelect):

    def __init__(self):

        super().__init__(
            placeholder="🔧 Otorolü seç",
            min_values=0,
            max_values=1,
            custom_id="dynex_autorole"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        if self.values:
            config["autorole"]["role"] = str(
                self.values[0].id
            )
        else:
            config["autorole"]["role"] = None

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Otorol kaydedildi.",
            ephemeral=True
        )


# =========================================================
# SES BİLDİRİMLERİ
# =========================================================

class VoiceSettingsModal(
    discord.ui.Modal,
    title="🔊 Ses Bildirimleri"
):

    enabled = discord.ui.TextInput(
        label="Ses bildirimleri",
        placeholder="Açık / Kapalı",
        required=False,
        max_length=10
    )

    join_message = discord.ui.TextInput(
        label="Katılma mesajı",
        placeholder="{member} ses kanalına katıldı.",
        required=False,
        max_length=500
    )

    leave_message = discord.ui.TextInput(
        label="Ayrılma mesajı",
        placeholder="{member} ses kanalından ayrıldı.",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction):

        if not await admin_required(interaction):
            return

        config = get_config(
            interaction.guild.id
        )

        voice = config["voice"]

        voice["enabled"] = parse_bool(
            self.enabled.value,
            voice["enabled"]
        )

        if self.join_message.value:
            voice["join_message"] = self.join_message.value

        if self.leave_message.value:
            voice["leave_message"] = self.leave_message.value

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Ses bildirimleri kaydedildi.\n\n"
            "🔊 Bildirim kanalını aşağıdan seç.",
            view=VoiceChannelView(),
            ephemeral=True
        )


class VoiceChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

        self.add_item(
            VoiceChannelSelect()
        )


class VoiceChannelSelect(discord.ui.ChannelSelect):

    def __init__(self):

        super().__init__(
            placeholder="🔊 Ses bildirim kanalını seç",
            channel_types=[discord.ChannelType.text],
            min_values=0,
            max_values=1,
            custom_id="dynex_voice_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        if self.values:
            config["voice"]["channel"] = str(
                self.values[0].id
            )
        else:
            config["voice"]["channel"] = None

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} Ses bildirim kanalı kaydedildi.",
            ephemeral=True
        )


# =========================================================
# DİL
# =========================================================

class LanguageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.select(
        placeholder="🌐 Dil seç",
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
                label="Azərbaycan dili",
                value="az",
                emoji="🇦🇿"
            )
        ]
    )
    async def select_language(
        self,
        interaction,
        select
    ):

        config = get_config(
            interaction.guild.id
        )

        config["language"] = select.values[0]

        save_configs()

        await interaction.response.send_message(
            f"{E['yes']} {TEXT[select.values[0]]['language_changed']}",
            ephemeral=True
        )


# =========================================================
# /DİL
# =========================================================

@bot.tree.command(
    name="dil",
    description="Dynex botunun dilini değiştir"
)
@app_commands.describe(
    dil="Botun kullanacağı dil"
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
        ),
        app_commands.Choice(
            name="Azərbaycan dili",
            value="az"
        )
    ]
)
async def dil(
    interaction: discord.Interaction,
    dil: app_commands.Choice[str]
):

    if not await admin_required(interaction):
        return

    config = get_config(
        interaction.guild.id
    )

    config["language"] = dil.value

    save_configs()

    await interaction.response.send_message(
        f"{E['yes']} {TEXT[dil.value]['language_changed']}",
        ephemeral=True
    )


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönet"
)
async def ayarlar(interaction: discord.Interaction):

    if not await admin_required(interaction):
        return

    config = get_config(
        interaction.guild.id
    )

    embed = discord.Embed(
        title=f"{E['settings']} Dynex Ayarları",
        description=(
            "Aşağıdaki bölümlerden birine basarak "
            "ayarlarını açabilirsin.\n\n"
            "🎫 Ticket\n"
            "👋 Hoş Geldiniz\n"
            "🛡️ Moderasyon\n"
            "📋 Loglar\n"
            "🔧 Otorol\n"
            "🔊 Ses Bildirimleri\n"
            "🌐 Dil"
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(),
        ephemeral=True
    )

    await interaction.followup.send(
        view=SettingsView2(),
        ephemeral=True
    )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun ping durumunu göster"
)
async def ping(interaction):

    latency = round(
        bot.latency * 1000
    )

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
        title="Dynex Botunun Ping(internet) Durumu",
        description=(
            f"**Ping:** `{latency}ms`\n"
            f"**Durum:** {status}"
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Bir kullanıcıyı yasaklar"
)
@app_commands.describe(
    kullanici="Yasaklanacak kullanıcı",
    sebep="Yasaklama sebebi"
)
async def ban(
    interaction,
    kullanici: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):

    if not await admin_required(interaction):
        return

    try:

        await kullanici.ban(
            reason=sebep
        )

        await interaction.response.send_message(
            f"{E['yes']} {kullanici.mention} yasaklandı.\n"
            f"**Sebep:** {sebep}"
        )

        await send_log(
            interaction.guild,
            "🔨 Kullanıcı Yasaklandı",
            f"{kullanici.mention}\nSebep: {sebep}"
        )

    except Exception as error:

        await interaction.response.send_message(
            f"{E['no']} İşlem başarısız.\n`{error}`",
            ephemeral=True
        )


# =========================================================
# /KICK
# =========================================================

@bot.tree.command(
    name="kick",
    description="Bir kullanıcıyı sunucudan atar"
)
@app_commands.describe(
    kullanici="Atılacak kullanıcı",
    sebep="Atılma sebebi"
)
async def kick(
    interaction,
    kullanici: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):

    if not await admin_required(interaction):
        return

    try:

        await kullanici.kick(
            reason=sebep
        )

        await interaction.response.send_message(
            f"{E['yes']} {kullanici.mention} sunucudan atıldı.\n"
            f"**Sebep:** {sebep}"
        )

        await send_log(
            interaction.guild,
            "👢 Kullanıcı Atıldı",
            f"{kullanici.mention}\nSebep: {sebep}"
        )

    except Exception as error:

        await interaction.response.send_message(
            f"{E['no']} İşlem başarısız.\n`{error}`",
            ephemeral=True
        )


# =========================================================
# /TIMEOUT
# =========================================================

@bot.tree.command(
    name="timeout",
    description="Kullanıcıya timeout verir"
)
@app_commands.describe(
    kullanici="Timeout verilecek kullanıcı",
    dakika="Dakika",
    sebep="Sebep"
)
async def timeout(
    interaction,
    kullanici: discord.Member,
    dakika: int,
    sebep: str = "Sebep belirtilmedi."
):

    if not await admin_required(interaction):
        return

    if dakika < 1:
        dakika = 1

    if dakika > 40320:
        dakika = 40320

    try:

        await kullanici.timeout(
            timedelta(minutes=dakika),
            reason=sebep
        )

        await interaction.response.send_message(
            f"{E['yes']} {kullanici.mention} "
            f"`{dakika}` dakika timeout aldı."
        )

        await send_log(
            interaction.guild,
            "⏱️ Timeout",
            f"{kullanici.mention}\n"
            f"Süre: {dakika} dakika\n"
            f"Sebep: {sebep}"
        )

    except Exception as error:

        await interaction.response.send_message(
            f"{E['no']} İşlem başarısız.\n`{error}`",
            ephemeral=True
        )


# =========================================================
# MESAJ SİLME
# =========================================================

@bot.event
async def on_message_delete(message):

    if not message.guild:
        return

    config = get_config(
        message.guild.id
    )

    if not config["logs"].get("message_delete"):
        return

    content = message.content or "Mesaj içeriği yok."

    await send_log(
        message.guild,
        "🗑️ Mesaj Silindi",
        f"**Kullanıcı:** {message.author.mention}\n"
        f"**Kanal:** {message.channel.mention}\n"
        f"**İçerik:** {content[:1500]}"
    )


# =========================================================
# MESAJ DÜZENLEME
# =========================================================

@bot.event
async def on_message_edit(before, after):

    if not before.guild:
        return

    if before.content == after.content:
        return

    config = get_config(
        before.guild.id
    )

    if not config["logs"].get("message_edit"):
        return

    await send_log(
        before.guild,
        "✏️ Mesaj Düzenlendi",
        f"**Kullanıcı:** {before.author.mention}\n"
        f"**Kanal:** {before.channel.mention}\n\n"
        f"**Eski:** {before.content[:700]}\n"
        f"**Yeni:** {after.content[:700]}"
    )

    await bot.process_commands(after)


# =========================================================
# ÜYE GİRİŞ
# =========================================================

@bot.event
async def on_member_join(member):

    config = get_config(
        member.guild.id
    )

    welcome = config["welcome"]

    # Otorol
    autorole = config["autorole"]

    if autorole.get("enabled") and autorole.get("role"):

        role = member.guild.get_role(
            int(autorole["role"])
        )

        if role:

            try:
                await member.add_roles(
                    role,
                    reason="Dynex Otorol"
                )
            except Exception:
                pass

    # Hoş geldin
    if welcome.get("enabled") and welcome.get("channel"):

        channel = member.guild.get_channel(
            int(welcome["channel"])
        )

        if channel:

            description = replace_variables(
                welcome.get("description", ""),
                member
            )

            message = replace_variables(
                welcome.get("message", ""),
                member
            )

            embed = discord.Embed(
                title=welcome.get(
                    "title",
                    "Hoş Geldin!"
                ),
                description=(
                    description
                    + "\n\n"
                    + message
                ),
                color=parse_color(
                    welcome.get("color"),
                    0x57F287
                )
            )

            if welcome.get("show_member"):
                embed.add_field(
                    name="👤 Kullanıcı",
                    value=member.mention,
                    inline=True
                )

            if welcome.get("show_username"):
                embed.add_field(
                    name="İsim",
                    value=member.name,
                    inline=True
                )

            if welcome.get("show_id"):
                embed.add_field(
                    name="ID",
                    value=str(member.id),
                    inline=True
                )

            if welcome.get("show_server"):
                embed.add_field(
                    name="Sunucu",
                    value=member.guild.name,
                    inline=True
                )

            if welcome.get("show_member_count"):
                embed.add_field(
                    name="Üye Sayısı",
                    value=str(member.guild.member_count),
                    inline=True
                )

            if welcome.get("show_join_number"):
                embed.add_field(
                    name="Katılan Sırası",
                    value=str(member.guild.member_count),
                    inline=True
                )

            if welcome.get("image_url"):
                embed.set_image(
                    url=welcome["image_url"]
                )

            if welcome.get("thumbnail_url"):
                embed.set_thumbnail(
                    url=welcome["thumbnail_url"]
                )

            try:
                await channel.send(
                    embed=embed
                )
            except Exception:
                pass

    # DM
    if welcome.get("dm_enabled"):

        dm_message = replace_variables(
            welcome.get("dm_message", ""),
            member
        )

        try:
            await member.send(
                dm_message
            )
        except Exception:
            pass


# =========================================================
# ÜYE AYRILMA
# =========================================================

@bot.event
async def on_member_remove(member):

    config = get_config(
        member.guild.id
    )

    if not config["logs"].get("member_leave"):
        return

    await send_log(
        member.guild,
        "👋 Üye Ayrıldı",
        f"{member.mention} sunucudan ayrıldı."
    )


# =========================================================
# SES DURUMU
# =========================================================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if before.channel == after.channel:
        return

    config = get_config(
        member.guild.id
    )

    voice = config["voice"]

    if not voice.get("enabled"):
        return

    channel_id = voice.get("channel")

    if not channel_id:
        return

    text_channel = member.guild.get_channel(
        int(channel_id)
    )

    if not text_channel:
        return

    if after.channel and not before.channel:

        message = replace_variables(
            voice.get("join_message", ""),
            member
        )

        await text_channel.send(
            message
        )

    elif before.channel and not after.channel:

        message = replace_variables(
            voice.get("leave_message", ""),
            member
        )

        await text_channel.send(
            message
        )


# =========================================================
# BASİT ANTI-LINK
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not message.guild:
        await bot.process_commands(message)
        return

    config = get_config(
        message.guild.id
    )

    moderation = config["moderation"]

    if moderation.get("enabled"):

        # Anti-link
        if moderation.get("anti_link"):

            link_pattern = r"(https?://|www\.)"

            if re.search(
                link_pattern,
                message.content,
                re.IGNORECASE
            ):

                if not message.author.guild_permissions.manage_messages:

                    try:
                        await message.delete()
                    except Exception:
                        pass

                    try:
                        await message.channel.send(
                            f"{E['no']} {message.author.mention} "
                            "Link göndermek yasaktır.",
                            delete_after=5
                        )
                    except Exception:
                        pass

                    await bot.process_commands(message)
                    return

        # Küfür filtresi
        if moderation.get("bad_words"):

            content = message.content.lower()

            words = moderation.get(
                "bad_words_list",
                []
            )

            found = any(
                word.lower() in content
                for word in words
                if word
            )

            if found:

                if not message.author.guild_permissions.manage_messages:

                    try:
                        await message.delete()
                    except Exception:
                        pass

                    try:
                        await message.channel.send(
                            f"{E['no']} {message.author.mention} "
                            "Bu mesaj filtre tarafından engellendi.",
                            delete_after=5
                        )
                    except Exception:
                        pass

                    await bot.process_commands(message)
                    return

    await bot.process_commands(message)


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(
        f"Bot aktif: {bot.user} "
        f"(ID: {bot.user.id})"
    )

    try:
        synced = await bot.tree.sync()

        print(
            f"{len(synced)} slash komut senkronize edildi."
        )

    except Exception as error:
        print(
            "Slash komut senkronizasyon hatası:",
            error
        )


# =========================================================
# BAŞLAT
# =========================================================

load_configs()

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
