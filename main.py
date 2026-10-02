import os
import json
import asyncio
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# TEMEL
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = Path("config.json")

PREFIX = "D."
SUPPORT_SERVER_ID = 1551647711332139098

START_TIME = datetime.now(timezone.utc)

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN bulunamadı.")


# =========================================================
# EMOJİLER
# =========================================================

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


# =========================================================
# VARSAYILAN CONFIG
# =========================================================

DEFAULT_CONFIG = {
    "language": "tr",

    "ticket": {
        "category_id": None,
        "role_id": None,
        "panel_channel_id": None,
        "panel_title": "Destek Talebi",
        "panel_description": "Destek almak için aşağıdaki seçeneklerden birini seç.",
        "panel_image": "",
        "options": []
    },

    "welcome": {
        "channel_id": None,
        "title": "Hoş Geldin!",
        "description": "{user}, sunucumuza hoş geldin!",
        "image": "",
        "thumbnail": "",
        "dm_enabled": False,
        "dm_message": ""
    },

    "autorole": {
        "role_id": None
    },

    "moderation": {
        "bad_words": [],
        "max_warnings": 3,
        "warning_action": "timeout",
        "timeout_minutes": 10,
        "anti_link": False,
        "anti_spam": False,
        "log_channel_id": None
    },

    "logs": {
        "channel_id": None,
        "message_delete": True,
        "message_edit": True,
        "member_join": True,
        "member_leave": True,
        "ban": True,
        "kick": True,
        "timeout": True
    },

    "voice": {
        "channel_id": None,
        "join_message": "{user} ses kanalına katıldı.",
        "leave_message": "{user} ses kanalından ayrıldı."
    },

    "giveaway": {
        "staff_role_id": None,
        "channel_id": None,
        "log_channel_id": None,
        "default_winners": 1,
        "default_duration": 10
    },

    "warnings": {}
}


# =========================================================
# CONFIG
# =========================================================

def copy_default():
    return json.loads(
        json.dumps(DEFAULT_CONFIG)
    )


def load_config():
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)
    except Exception:
        return {}


configs = load_config()


def merge(old, default):
    if isinstance(default, dict):
        result = {}

        for key, value in default.items():
            if key in old:
                result[key] = merge(
                    old[key],
                    value
                )
            else:
                result[key] = json.loads(
                    json.dumps(value)
                )

        for key, value in old.items():
            if key not in result:
                result[key] = value

        return result

    return old


def save_configs():
    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            configs,
            f,
            ensure_ascii=False,
            indent=4
        )


def get_config(guild_id):
    gid = str(guild_id)

    if gid not in configs:
        configs[gid] = copy_default()
    else:
        configs[gid] = merge(
            configs[gid],
            DEFAULT_CONFIG
        )

    # Eski Destek + Şikayet seçeneklerini temizle
    options = configs[gid]["ticket"].get(
        "options",
        []
    )

    if len(options) == 2:
        names = {
            str(x.get("name", "")).lower()
            for x in options
            if isinstance(x, dict)
        }

        if names == {"destek", "şikayet"}:
            configs[gid]["ticket"]["options"] = []

    save_configs()

    return configs[gid]


# =========================================================
# YARDIMCILAR
# =========================================================

def uptime_text():
    seconds = int(
        (
            datetime.now(timezone.utc)
            - START_TIME
        ).total_seconds()
    )

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    parts = []

    if days:
        parts.append(f"{days} gün")

    if hours:
        parts.append(f"{hours} saat")

    if minutes:
        parts.append(f"{minutes} dakika")

    if seconds or not parts:
        parts.append(f"{seconds} saniye")

    return " ".join(parts)


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

        emoji = discord.utils.get(
            guild.emojis,
            name=name
        )

        return emoji

    return value


def emoji_exists(value, guild):
    if not value:
        return True

    value = str(value).strip()

    if value.startswith(":") and value.endswith(":"):
        name = value[1:-1].strip()

        return discord.utils.get(
            guild.emojis,
            name=name
        ) is not None

    if value.startswith("<:") or value.startswith("<a:"):
        try:
            return (
                discord.PartialEmoji.from_str(
                    value
                ).id is not None
            )
        except Exception:
            return False

    return True


async def admin_only(interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Yönetici yetkin bulunmuyor.",
            ephemeral=True
        )
        return False

    return True


async def send_log(
    guild,
    text,
    log_type
):
    config = get_config(guild.id)

    if not config["logs"].get(
        log_type,
        False
    ):
        return

    channel_id = config["logs"].get(
        "channel_id"
    )

    if not channel_id:
        return

    channel = guild.get_channel(
        channel_id
    )

    if channel:
        try:
            await channel.send(text)
        except Exception:
            pass


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.voice_states = True


class DynexBot(commands.Bot):

    async def setup_hook(self):
        self.add_view(
            TicketCloseView()
        )

        try:
            await self.tree.sync()
            print("Slash komutları senkronize edildi.")
        except Exception as e:
            print(
                "Slash sync hatası:",
                repr(e)
            )


bot = DynexBot(
    command_prefix=PREFIX,
    intents=intents
)


# =========================================================
# TICKET KAPAT
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
    async def close(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            f"{EMOJIS['locked']} Ticket kapatılıyor."
        )

        await asyncio.sleep(3)

        try:
            await interaction.channel.delete()
        except Exception:
            pass


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(
    discord.ui.View
):

    def __init__(self, guild):
        super().__init__(
            timeout=None
        )

        config = get_config(
            guild.id
        )

        for option in config["ticket"]["options"]:

            option_id = option.get(
                "id"
            )

            label = (
                option.get("button")
                or option.get("name")
                or "Ticket"
            )

            emoji = parse_emoji(
                option.get("emoji"),
                guild
            )

            button = discord.ui.Button(
                label=label[:80],
                style=discord.ButtonStyle.primary,
                custom_id=f"dynex_ticket_{option_id}",
                emoji=emoji
            )

            async def callback(
                interaction,
                option_id=option_id
            ):
                await self.create_ticket(
                    interaction,
                    option_id
                )

            button.callback = callback

            self.add_item(button)

    async def create_ticket(
        self,
        interaction,
        option_id
    ):
        guild = interaction.guild
        config = get_config(
            guild.id
        )

        option = next(
            (
                x for x
                in config["ticket"]["options"]
                if x.get("id") == option_id
            ),
            None
        )

        if not option:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Ticket seçeneği bulunamadı.",
                ephemeral=True
            )
            return

        existing = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{interaction.user.id}"
        )

        if existing:
            await interaction.response.send_message(
                f"{EMOJIS['wait']} Zaten açık ticketın var: "
                f"{existing.mention}",
                ephemeral=True
            )
            return

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
                )
        }

        role = None

        if config["ticket"]["role_id"]:
            role = guild.get_role(
                config["ticket"]["role_id"]
            )

            if role:
                overwrites[role] = (
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True
                    )
                )

        category = None

        if config["ticket"]["category_id"]:
            category = guild.get_channel(
                config["ticket"]["category_id"]
            )

        try:
            channel = await guild.create_text_channel(
                f"ticket-{interaction.user.id}",
                category=category,
                overwrites=overwrites
            )
        except Exception:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Ticket oluşturulamadı.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=option.get(
                "name",
                "Ticket"
            ),
            description=(
                f"{interaction.user.mention}, ticketın oluşturuldu.\n\n"
                "Yetkililer seninle ilgilenecektir."
            ),
            color=discord.Color.blurple()
        )

        await channel.send(
            content=(
                role.mention
                if role
                else None
            ),
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket oluşturuldu: "
            f"{channel.mention}",
            ephemeral=True
        )


# =========================================================
# AYARLAR ANA MENÜ
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
                label="Karşılama",
                value="welcome",
                emoji="👋"
            ),
            discord.SelectOption(
                label="Moderasyon",
                value="moderation",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="Log",
                value="logs",
                emoji="📜"
            ),
            discord.SelectOption(
                label="Oto Rol",
                value="autorole",
                emoji="🎭"
            ),
            discord.SelectOption(
                label="Ses",
                value="voice",
                emoji="🔊"
            ),
            discord.SelectOption(
                label="Çekiliş",
                value="giveaway",
                emoji="🎉"
            )
        ]

        super().__init__(
            placeholder="Bir ayar kategorisi seç...",
            options=options
        )

    async def callback(
        self,
        interaction
    ):
        value = self.values[0]

        views = {
            "ticket": (
                "🎫 **Ticket Ayarları**",
                TicketSettingsView()
            ),
            "welcome": (
                "👋 **Karşılama Ayarları**",
                WelcomeSettingsView()
            ),
            "moderation": (
                "🛡️ **Moderasyon Ayarları**",
                ModerationSettingsView()
            ),
            "logs": (
                "📜 **Log Ayarları**",
                LogsSettingsView()
            ),
            "autorole": (
                "🎭 **Oto Rol Ayarları**",
                AutoroleSettingsView()
            ),
            "voice": (
                "🔊 **Ses Ayarları**",
                VoiceSettingsView()
            ),
            "giveaway": (
                "🎉 **Çekiliş Ayarları**",
                GiveawaySettingsView()
            )
        }

        text, view = views[value]

        await interaction.response.edit_message(
            content=text,
            embed=None,
            view=view
        )


class SettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

        self.add_item(
            SettingsSelect()
        )


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
        label="Kategori",
        style=discord.ButtonStyle.secondary
    )
    async def category(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Ticket kategorisini seç:",
            view=TicketCategoryView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Yetkili Rolü",
        style=discord.ButtonStyle.secondary
    )
    async def role(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Ticket yetkili rolünü seç:",
            view=TicketRoleView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Panel Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Panel kanalını seç:",
            view=TicketChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Panel Bilgileri",
        style=discord.ButtonStyle.primary
    )
    async def info(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            TicketPanelModal()
        )

    @discord.ui.button(
        label="Seçenekler",
        style=discord.ButtonStyle.success
    )
    async def options(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Ticket Seçenekleri**",
            view=TicketOptionsView()
        )

    @discord.ui.button(
        label="Paneli Gönder",
        style=discord.ButtonStyle.success
    )
    async def send_panel(
        self,
        interaction,
        button
    ):
        config = get_config(
            interaction.guild.id
        )

        if not config["ticket"]["panel_channel_id"]:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Panel kanalı ayarlanmamış.",
                ephemeral=True
            )
            return

        if not config["ticket"]["options"]:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Önce ticket seçeneği ekle.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(
            config["ticket"]["panel_channel_id"]
        )

        if not channel:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Panel kanalı bulunamadı.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=config["ticket"]["panel_title"],
            description=config["ticket"]["panel_description"],
            color=discord.Color.blurple()
        )

        if config["ticket"]["panel_image"]:
            embed.set_image(
                url=config["ticket"]["panel_image"]
            )

        await channel.send(
            embed=embed,
            view=TicketPanelView(
                interaction.guild
            )
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket paneli gönderildi.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class TicketCategoryView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.category
            ],
            placeholder="Kategori seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["category_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Kategori ayarlandı.",
            ephemeral=True
        )


class TicketRoleView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.RoleSelect(
            placeholder="Yetkili rolü seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        role = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["role_id"] = role.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Yetkili rolü ayarlandı.",
            ephemeral=True
        )


class TicketChannelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.text
            ],
            placeholder="Panel kanalı seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["panel_channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Panel kanalı ayarlandı.",
            ephemeral=True
        )


class TicketPanelModal(
    discord.ui.Modal,
    title="Ticket Paneli"
):

    panel_title = discord.ui.TextInput(
        label="Panel başlığı",
        default="Destek Talebi",
        max_length=100
    )

    description = discord.ui.TextInput(
        label="Panel açıklaması",
        style=discord.TextStyle.paragraph,
        default="Destek almak için aşağıdaki seçeneklerden birini seç.",
        max_length=1000
    )

    image = discord.ui.TextInput(
        label="Görsel URL",
        required=False
    )

    async def on_submit(
        self,
        interaction
    ):
        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["panel_title"] = str(
            self.panel_title
        )

        config["ticket"]["panel_description"] = str(
            self.description
        )

        config["ticket"]["panel_image"] = str(
            self.image
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket paneli kaydedildi.",
            ephemeral=True
        )


# =========================================================
# TICKET SEÇENEKLERİ
# =========================================================

class TicketOptionsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Seçenek Ekle",
        style=discord.ButtonStyle.success
    )
    async def add(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            AddTicketOptionModal()
        )

    @discord.ui.button(
        label="Seçenekleri Gör",
        style=discord.ButtonStyle.secondary
    )
    async def show(
        self,
        interaction,
        button
    ):
        config = get_config(
            interaction.guild.id
        )

        options = config["ticket"]["options"]

        if not options:
            await interaction.response.send_message(
                "Henüz ticket seçeneği eklenmemiş.",
                ephemeral=True
            )
            return

        text = []

        for i, option in enumerate(
            options,
            1
        ):
            text.append(
                f"**{i}. {option.get('name')}** "
                f"| Buton: `{option.get('button')}` "
                f"| Emoji: `{option.get('emoji') or 'Yok'}`"
            )

        await interaction.response.send_message(
            "\n".join(text),
            ephemeral=True
        )

    @discord.ui.button(
        label="Seçenek Sil",
        style=discord.ButtonStyle.danger
    )
    async def delete(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            DeleteTicketOptionModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Ticket Ayarları**",
            view=TicketSettingsView()
        )


class AddTicketOptionModal(
    discord.ui.Modal,
    title="Ticket Seçeneği Ekle"
):

    name = discord.ui.TextInput(
        label="Seçenek adı",
        placeholder="Örneğin Destek",
        max_length=50
    )

    button_name = discord.ui.TextInput(
        label="Buton yazısı",
        placeholder="Örneğin Destek",
        max_length=50
    )

    emoji = discord.ui.TextInput(
        label="Emoji",
        placeholder="🎫 veya :emoji: veya <:isim:id>",
        required=False,
        max_length=100
    )

    async def on_submit(
        self,
        interaction
    ):
        if not emoji_exists(
            str(self.emoji),
            interaction.guild
        ):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Emoji bulunamadı.",
                ephemeral=True
            )
            return

        config = get_config(
            interaction.guild.id
        )

        option_id = (
            str(self.name)
            .lower()
            .replace(" ", "_")
        )

        option_id = "".join(
            x for x in option_id
            if x.isalnum() or x == "_"
        )

        if not option_id:
            option_id = (
                f"ticket_"
                f"{len(config['ticket']['options']) + 1}"
            )

        ids = {
            x.get("id")
            for x in config["ticket"]["options"]
        }

        base = option_id
        count = 2

        while option_id in ids:
            option_id = (
                f"{base}_{count}"
            )
            count += 1

        config["ticket"]["options"].append({
            "id": option_id,
            "name": str(self.name),
            "button": str(self.button_name),
            "emoji": str(self.emoji)
        })

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket seçeneği eklendi.",
            ephemeral=True
        )


class DeleteTicketOptionModal(
    discord.ui.Modal,
    title="Ticket Seçeneği Sil"
):

    option = discord.ui.TextInput(
        label="Seçenek adı",
        placeholder="Silinecek seçenek"
    )

    async def on_submit(
        self,
        interaction
    ):
        config = get_config(
            interaction.guild.id
        )

        target = str(
            self.option
        ).lower()

        old = config["ticket"]["options"]

        new = [
            x for x in old
            if str(
                x.get("name", "")
            ).lower() != target
            and str(
                x.get("id", "")
            ).lower() != target
        ]

        if len(new) == len(old):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Seçenek bulunamadı.",
                ephemeral=True
            )
            return

        config["ticket"]["options"] = new

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket seçeneği silindi.",
            ephemeral=True
        )


# =========================================================
# KARŞILAMA
# =========================================================

class WelcomeSettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Kanal",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Karşılama kanalını seç:",
            view=WelcomeChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Mesaj",
        style=discord.ButtonStyle.primary
    )
    async def message(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            WelcomeModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class WelcomeChannelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.text
            ],
            placeholder="Karşılama kanalı seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["welcome"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Karşılama kanalı ayarlandı.",
            ephemeral=True
        )


class WelcomeModal(
    discord.ui.Modal,
    title="Karşılama Ayarları"
):

    title_text = discord.ui.TextInput(
        label="Başlık",
        default="Hoş Geldin!",
        max_length=100
    )

    description = discord.ui.TextInput(
        label="Açıklama",
        default="{user}, sunucumuza hoş geldin!",
        max_length=1000
    )

    image = discord.ui.TextInput(
        label="Görsel URL",
        required=False
    )

    dm = discord.ui.TextInput(
        label="DM mesajı",
        required=False,
        max_length=1000
    )

    async def on_submit(
        self,
        interaction
    ):
        config = get_config(
            interaction.guild.id
        )

        config["welcome"]["title"] = str(
            self.title_text
        )

        config["welcome"]["description"] = str(
            self.description
        )

        config["welcome"]["image"] = str(
            self.image
        )

        dm = str(self.dm)

        config["welcome"]["dm_enabled"] = bool(
            dm
        )

        config["welcome"]["dm_message"] = dm

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Karşılama ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# OTOROL
# =========================================================

class AutoroleSettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Rol Seç",
        style=discord.ButtonStyle.success
    )
    async def role(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Oto rolü seç:",
            view=AutoroleRoleView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class AutoroleRoleView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.RoleSelect(
            placeholder="Oto rolü seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        role = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["autorole"]["role_id"] = role.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Oto rol ayarlandı.",
            ephemeral=True
        )


# =========================================================
# MODERASYON
# =========================================================

class ModerationSettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Ayarlar",
        style=discord.ButtonStyle.primary
    )
    async def settings(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            ModerationModal()
        )

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Moderasyon log kanalını seç:",
            view=ModerationChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class ModerationChannelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.text
            ],
            placeholder="Log kanalı seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["moderation"]["log_channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Moderasyon log kanalı ayarlandı.",
            ephemeral=True
        )


class ModerationModal(
    discord.ui.Modal,
    title="Moderasyon Ayarları"
):

    bad_words = discord.ui.TextInput(
        label="Yasaklı kelimeler",
        placeholder="kelime1, kelime2",
        required=False
    )

    max_warnings = discord.ui.TextInput(
        label="Uyarı limiti",
        default="3",
        max_length=2
    )

    timeout_minutes = discord.ui.TextInput(
        label="Timeout süresi",
        default="10",
        max_length=5
    )

    anti_link = discord.ui.TextInput(
        label="Anti-link",
        default="kapalı"
    )

    anti_spam = discord.ui.TextInput(
        label="Anti-spam",
        default="kapalı"
    )

    async def on_submit(
        self,
        interaction
    ):
        config = get_config(
            interaction.guild.id
        )

        try:
            max_warnings = max(
                1,
                int(str(self.max_warnings))
            )
        except Exception:
            max_warnings = 3

        try:
            timeout_minutes = max(
                1,
                int(str(self.timeout_minutes))
            )
        except Exception:
            timeout_minutes = 10

        enabled = [
            "açık",
            "acik",
            "evet",
            "on",
            "true"
        ]

        config["moderation"]["bad_words"] = [
            x.strip()
            for x in str(
                self.bad_words
            ).split(",")
            if x.strip()
        ]

        config["moderation"]["max_warnings"] = (
            max_warnings
        )

        config["moderation"]["timeout_minutes"] = (
            timeout_minutes
        )

        config["moderation"]["anti_link"] = (
            str(self.anti_link).lower()
            in enabled
        )

        config["moderation"]["anti_spam"] = (
            str(self.anti_spam).lower()
            in enabled
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Moderasyon ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# LOG
# =========================================================

class LogsSettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Log kanalını seç:",
            view=LogsChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Log Türleri",
        style=discord.ButtonStyle.primary
    )
    async def types(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            LogsModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class LogsChannelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.text
            ],
            placeholder="Log kanalı seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["logs"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Log kanalı ayarlandı.",
            ephemeral=True
        )


class LogsModal(
    discord.ui.Modal,
    title="Log Ayarları"
):

    delete = discord.ui.TextInput(
        label="Mesaj silme",
        default="açık"
    )

    edit = discord.ui.TextInput(
        label="Mesaj düzenleme",
        default="açık"
    )

    members = discord.ui.TextInput(
        label="Üye giriş/çıkış",
        default="açık"
    )

    moderation = discord.ui.TextInput(
        label="Ban/Kick/Timeout",
        default="açık"
    )

    async def on_submit(
        self,
        interaction
    ):
        config = get_config(
            interaction.guild.id
        )

        def enabled(value):
            return str(value).lower() in [
                "açık",
                "acik",
                "evet",
                "on",
                "true"
            ]

        config["logs"]["message_delete"] = (
            enabled(self.delete)
        )

        config["logs"]["message_edit"] = (
            enabled(self.edit)
        )

        config["logs"]["member_join"] = (
            enabled(self.members)
        )

        config["logs"]["member_leave"] = (
            enabled(self.members)
        )

        config["logs"]["ban"] = (
            enabled(self.moderation)
        )

        config["logs"]["kick"] = (
            enabled(self.moderation)
        )

        config["logs"]["timeout"] = (
            enabled(self.moderation)
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Log ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# SES
# =========================================================

class VoiceSettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Kanal",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Ses bildirim kanalını seç:",
            view=VoiceChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Mesajlar",
        style=discord.ButtonStyle.primary
    )
    async def messages(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            VoiceModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class VoiceChannelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.text
            ],
            placeholder="Bildirim kanalı seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["voice"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ses kanalı ayarlandı.",
            ephemeral=True
        )


class VoiceModal(
    discord.ui.Modal,
    title="Ses Mesajları"
):

    join = discord.ui.TextInput(
        label="Giriş mesajı",
        default="{user} ses kanalına katıldı."
    )

    leave = discord.ui.TextInput(
        label="Çıkış mesajı",
        default="{user} ses kanalından ayrıldı."
    )

    async def on_submit(
        self,
        interaction
    ):
        config = get_config(
            interaction.guild.id
        )

        config["voice"]["join_message"] = str(
            self.join
        )

        config["voice"]["leave_message"] = str(
            self.leave
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ses mesajları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# ÇEKİLİŞ AYARLARI
# =========================================================

class GiveawaySettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Yetkili Rolü",
        style=discord.ButtonStyle.secondary
    )
    async def role(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Çekiliş yetkili rolünü seç:",
            view=GiveawayRoleView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Çekiliş Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def channel(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Çekiliş kanalını seç:",
            view=GiveawayChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def log(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Çekiliş log kanalını seç:",
            view=GiveawayLogChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Varsayılanlar",
        style=discord.ButtonStyle.primary
    )
    async def defaults(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            GiveawayModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(
        self,
        interaction,
        button
    ):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class GiveawayRoleView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.RoleSelect(
            placeholder="Çekiliş yetkili rolünü seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        role = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["giveaway"]["staff_role_id"] = role.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş yetkili rolü ayarlandı.",
            ephemeral=True
        )


class GiveawayChannelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.text
            ],
            placeholder="Çekiliş kanalı seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["giveaway"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş kanalı ayarlandı.",
            ephemeral=True
        )


class GiveawayLogChannelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.ChannelSelect(
            channel_types=[
                discord.ChannelType.text
            ],
            placeholder="Çekiliş log kanalı seç..."
        )

        select.callback = self.callback

        self.add_item(select)

    async def callback(
        self,
        interaction
    ):
        channel = self.children[0].values[0]

        config = get_config(
            interaction.guild.id
        )

        config["giveaway"]["log_channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş log kanalı ayarlandı.",
            ephemeral=True
        )


class GiveawayModal(
    discord.ui.Modal,
    title="Çekiliş Varsayılanları"
):

    winners = discord.ui.TextInput(
        label="Kazanan sayısı",
        default="1"
    )

    duration = discord.ui.TextInput(
        label="Süre (dakika)",
        default="10"
    )

    async def on_submit(
        self,
        interaction
    ):
        config = get_config(
            interaction.guild.id
        )

        try:
            winners = max(
                1,
                int(str(self.winners))
            )
        except Exception:
            winners = 1

        try:
            duration = max(
                1,
                min(
                    40,
                    int(str(self.duration))
                )
            )
        except Exception:
            duration = 10

        config["giveaway"]["default_winners"] = (
            winners
        )

        config["giveaway"]["default_duration"] = (
            duration
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# ÇEKİLİŞ
# =========================================================

active_giveaways = {}


class GiveawayView(
    discord.ui.View
):

    def __init__(
        self,
        giveaway_id
    ):
        super().__init__(
            timeout=None
        )

        self.giveaway_id = giveaway_id

    @discord.ui.button(
        label="Çekilişe Katıl",
        style=discord.ButtonStyle.success,
        custom_id="dynex_giveaway_join"
    )
    async def join(
        self,
        interaction,
        button
    ):
        giveaway = active_giveaways.get(
            self.giveaway_id
        )

        if not giveaway:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Çekiliş aktif değil.",
                ephemeral=True
            )
            return

        user_id = interaction.user.id

        if user_id in giveaway["participants"]:
            giveaway["participants"].remove(
                user_id
            )

            await interaction.response.send_message(
                "Çekilişten ayrıldın.",
                ephemeral=True
            )

        else:
            giveaway["participants"].add(
                user_id
            )

            await interaction.response.send_message(
                f"{EMOJIS['yes']} Çekilişe katıldın!",
                ephemeral=True
            )


async def finish_giveaway(
    giveaway_id
):
    giveaway = active_giveaways.get(
        giveaway_id
    )

    if not giveaway:
        return

    await asyncio.sleep(
        giveaway["duration"]
    )

    giveaway = active_giveaways.get(
        giveaway_id
    )

    if not giveaway:
        return

    guild = bot.get_guild(
        giveaway["guild_id"]
    )

    if not guild:
        return

    channel = guild.get_channel(
        giveaway["channel_id"]
    )

    if not channel:
        return

    participants = list(
        giveaway["participants"]
    )

    if not participants:
        await channel.send(
            f"{EMOJIS['no']} Çekiliş bitti fakat katılımcı yok."
        )

        active_giveaways.pop(
            giveaway_id,
            None
        )

        return

    count = min(
        giveaway["winners"],
        len(participants)
    )

    winners = random.sample(
        participants,
        count
    )

    mentions = " ".join(
        f"<@{x}>"
        for x in winners
    )

    embed = discord.Embed(
        title="🎉 Çekiliş Bitti!",
        description=(
            f"**Ödül:** {giveaway['prize']}\n\n"
            f"**Kazananlar:** {mentions}"
        ),
        color=discord.Color.green()
    )

    await channel.send(
        content=mentions,
        embed=embed
    )

    active_giveaways.pop(
        giveaway_id,
        None
    )


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönet."
)
@app_commands.default_permissions(
    administrator=True
)
async def settings_command(
    interaction
):
    if not await admin_only(
        interaction
    ):
        return

    await interaction.response.send_message(
        f"{EMOJIS['settings']} **Dynex Ayarları**\n"
        "Aşağıdan bir kategori seç.",
        view=SettingsView(),
        ephemeral=True
    )


# =========================================================
# /DİL
# =========================================================

class LanguageView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=120
        )

        select = discord.ui.Select(
            placeholder="Dil seç...",
            options=[
                discord.SelectOption(
                    label="Türkçe",
                    value="tr"
                ),
                discord.SelectOption(
                    label="English",
                    value="en"
                )
            ]
        )

        async def callback(
            interaction
        ):
            config = get_config(
                interaction.guild.id
            )

            config["language"] = (
                select.values[0]
            )

            save_configs()

            await interaction.response.send_message(
                f"{EMOJIS['yes']} Dil ayarlandı.",
                ephemeral=True
            )

        select.callback = callback

        self.add_item(select)


@bot.tree.command(
    name="dil",
    description="Dynex dilini değiştir."
)
async def language_command(
    interaction
):
    if not await admin_only(
        interaction
    ):
        return

    await interaction.response.send_message(
        "Dil seç:",
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# /BOT
# =========================================================
@bot.tree.command(
    name="bot",
    description="Dynex botunun durumunu gösterir."
)
async def bot_status(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title="Dynex Durum",
            color=discord.Color.black()
        )

        # Bot sahibi
        try:
            app_info = await bot.application_info()
            owner = app_info.owner
            owner_text = owner.mention if owner else "Bilinmiyor"
        except Exception as e:
            print("Bot sahibi hatası:", repr(e))
            owner_text = "Bilinmiyor"

        # Destek sunucusu
        try:
            support_guild = bot.get_guild(1551647711332139098)

            if support_guild is not None:
                support_members = support_guild.member_count
                if support_members is None:
                    support_members = len(support_guild.members)
            else:
                support_members = "Bilinmiyor"
        except Exception as e:
            print("Destek sunucusu hatası:", repr(e))
            support_members = "Bilinmiyor"

        # Aktif kalma süresi
        try:
            uptime = uptime_text()
        except Exception as e:
            print("Uptime hatası:", repr(e))
            uptime = "Bilinmiyor"

        embed.description = (
            f"**Sunucu sayısı:** `{len(bot.guilds)}`\n\n"
            f"**Destek sunucusu üye sayısı:** `{support_members}`\n\n"
            f"**Prefix yani . Komut:** `D.`\n\n"
            f"**Aktif kalma süresi:** `{uptime}`\n\n"
            f"**Bot sahibi:** {owner_text}"
        )

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print("/bot KOMUT HATASI:", repr(e))

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Bot durumu gösterilirken bir hata oluştu.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ Bot durumu gösterilirken bir hata oluştu.",
                ephemeral=True
            )

# =========================================================
# /YARDIM
# =========================================================

class HelpView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=180
        )

        select = discord.ui.Select(
            placeholder="Bir kategori seç...",
            options=[
                discord.SelectOption(
                    label="Genel",
                    value="general",
                    emoji="📌"
                ),
                discord.SelectOption(
                    label="Moderasyon",
                    value="moderation",
                    emoji="🛡️"
                ),
                discord.SelectOption(
                    label="Ticket",
                    value="ticket",
                    emoji="🎫"
                ),
                discord.SelectOption(
                    label="Çekiliş",
                    value="giveaway",
                    emoji="🎉"
                ),
                discord.SelectOption(
                    label="Sunucu",
                    value="server",
                    emoji="🏠"
                )
            ]
        )

        async def callback(
            interaction
        ):
            value = select.values[0]

            if value == "general":
                text = (
                    "`/bot` — Bot durumunu gösterir.\n"
                    "`/ping` — Ping durumunu gösterir.\n"
                    "`/kullanıcı` — Kullanıcı bilgisi.\n"
                    "`/avatar` — Avatar gösterir.\n"
                    "`/sunucu` — Sunucu bilgisi.\n"
                    "`/roller` — Rolleri gösterir."
                )

            elif value == "moderation":
                text = (
                    "`/ban` — Kullanıcıyı yasaklar.\n"
                    "`/kick` — Kullanıcıyı atar.\n"
                    "`/timeout` — Timeout verir.\n"
                    "`/uyar` — Kullanıcıyı uyarır.\n"
                    "`/uyarılar` — Uyarıları gösterir.\n"
                    "`/temizle` — Mesajları siler."
                )

            elif value == "ticket":
                text = (
                    "`/ayarlar` → Ticket\n\n"
                    "Kategori, yetkili rolü, panel kanalı "
                    "ve ticket seçeneklerini ayarlayabilirsin."
                )

            elif value == "giveaway":
                text = (
                    "`/çekiliş` — Çekiliş başlatır.\n"
                    "`/çekiliş-bitir` — Çekilişi bitirir.\n\n"
                    "Yetkili rolü ve kanallar `/ayarlar` "
                    "üzerinden ayarlanır."
                )

            else:
                text = (
                    "`/sunucu` — Sunucu bilgileri.\n"
                    "`/roller` — Sunucu rolleri.\n"
                    "`/ayarlar` — Sunucu ayarları.\n"
                    "`/dil` — Bot dili."
                )

            embed = discord.Embed(
                title="Dynex Yardım",
                description=text,
                color=discord.Color.blurple()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=self
            )

        select.callback = callback

        self.add_item(select)


@bot.tree.command(
    name="yardım",
    description="Dynex komut yardımını gösterir."
)
async def help_command(
    interaction
):
    embed = discord.Embed(
        title="Dynex Yardım",
        description=(
            "Görmek istediğin komut kategorisini seç."
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=HelpView()
    )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Dynex bağlantı durumunu gösterir."
)
async def ping(
    interaction
):
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
            f"**Durum:** `{status}`"
        ),
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /SUNUCU
# =========================================================

@bot.tree.command(
    name="sunucu",
    description="Sunucu bilgilerini gösterir."
)
async def server_info(
    interaction
):
    guild = interaction.guild

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Sunucu ID",
        value=f"`{guild.id}`",
        inline=False
    )

    embed.add_field(
        name="Üye",
        value=f"`{guild.member_count}`",
        inline=True
    )

    embed.add_field(
        name="Kanal",
        value=f"`{len(guild.channels)}`",
        inline=True
    )

    embed.add_field(
        name="Rol",
        value=f"`{len(guild.roles)}`",
        inline=True
    )

    if guild.icon:
        embed.set_thumbnail(
            url=guild.icon.url
        )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /KULLANICI
# =========================================================

@bot.tree.command(
    name="kullanıcı",
    description="Kullanıcı bilgilerini gösterir."
)
@app_commands.describe(
    kullanıcı="Bilgileri gösterilecek kullanıcı."
)
async def user_info(
    interaction,
    kullanıcı: discord.Member = None
):
    user = kullanıcı or interaction.user

    embed = discord.Embed(
        title="Kullanıcı Bilgileri",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=user.display_avatar.url
    )

    embed.add_field(
        name="Kullanıcı",
        value=user.mention,
        inline=False
    )

    embed.add_field(
        name="ID",
        value=f"`{user.id}`",
        inline=False
    )

    embed.add_field(
        name="Hesap oluşturulma",
        value=discord.utils.format_dt(
            user.created_at,
            "F"
        ),
        inline=False
    )

    if user.joined_at:
        embed.add_field(
            name="Sunucuya katılma",
            value=discord.utils.format_dt(
                user.joined_at,
                "F"
            ),
            inline=False
        )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /AVATAR
# =========================================================

@bot.tree.command(
    name="avatar",
    description="Kullanıcının avatarını gösterir."
)
@app_commands.describe(
    kullanıcı="Avatarı gösterilecek kullanıcı."
)
async def avatar(
    interaction,
    kullanıcı: discord.User = None
):
    user = kullanıcı or interaction.user

    embed = discord.Embed(
        title=f"{user.display_name} Avatarı",
        color=discord.Color.blurple()
    )

    embed.set_image(
        url=user.display_avatar.url
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /ROLLER
# =========================================================

@bot.tree.command(
    name="roller",
    description="Sunucudaki rolleri listeler."
)
async def roles_command(
    interaction
):
    roles = [
        role
        for role in interaction.guild.roles
        if role != interaction.guild.default_role
    ]

    roles.reverse()

    if not roles:
        await interaction.response.send_message(
            "Sunucuda rol yok."
        )
        return

    text = "\n".join(
        f"{role.mention} — `{role.id}`"
        for role in roles[:50]
    )

    embed = discord.Embed(
        title="Sunucu Rolleri",
        description=text,
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /TEMİZLE
# =========================================================

@bot.tree.command(
    name="temizle",
    description="Mesajları siler."
)
@app_commands.describe(
    miktar="1-100 arası mesaj."
)
async def clear(
    interaction,
    miktar: app_commands.Range[
        int,
        1,
        100
    ]
):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Mesaj yönetme yetkin yok.",
            ephemeral=True
        )
        return

    await interaction.response.defer(
        ephemeral=True
    )

    deleted = await interaction.channel.purge(
        limit=miktar
    )

    await interaction.followup.send(
        f"{EMOJIS['yes']} `{len(deleted)}` mesaj silindi.",
        ephemeral=True
    )


# =========================================================
# /BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Kullanıcıyı yasaklar."
)
@app_commands.describe(
    kullanıcı="Yasaklanacak kullanıcı.",
    sebep="Sebep."
)
async def ban_command(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Ban yetkin yok.",
            ephemeral=True
        )
        return

    try:
        await kullanıcı.ban(
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} yasaklandı.\n"
            f"**Sebep:** {sebep}"
        )

        await send_log(
            interaction.guild,
            f"🔨 {kullanıcı} banlandı.\n"
            f"Sebep: {sebep}",
            "ban"
        )

    except Exception as e:
        print(
            "Ban hatası:",
            repr(e)
        )

        await interaction.response.send_message(
            f"{EMOJIS['no']} Kullanıcı banlanamadı.",
            ephemeral=True
        )


# =========================================================
# /KICK
# =========================================================

@bot.tree.command(
    name="kick",
    description="Kullanıcıyı sunucudan atar."
)
@app_commands.describe(
    kullanıcı="Atılacak kullanıcı.",
    sebep="Sebep."
)
async def kick_command(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kick yetkin yok.",
            ephemeral=True
        )
        return

    try:
        await kullanıcı.kick(
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} atıldı.\n"
            f"**Sebep:** {sebep}"
        )

        await send_log(
            interaction.guild,
            f"👢 {kullanıcı} kicklendi.\n"
            f"Sebep: {sebep}",
            "kick"
        )

    except Exception as e:
        print(
            "Kick hatası:",
            repr(e)
        )

        await interaction.response.send_message(
            f"{EMOJIS['no']} Kullanıcı kicklenemedi.",
            ephemeral=True
        )


# =========================================================
# /TIMEOUT
# =========================================================

@bot.tree.command(
    name="timeout",
    description="Kullanıcıya timeout verir."
)
@app_commands.describe(
    kullanıcı="Timeout verilecek kullanıcı.",
    dakika="Timeout süresi.",
    sebep="Sebep."
)
async def timeout_command(
    interaction,
    kullanıcı: discord.Member,
    dakika: app_commands.Range[
        int,
        1,
        40320
    ],
    sebep: str = "Sebep belirtilmedi."
):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Timeout yetkin yok.",
            ephemeral=True
        )
        return

    try:
        await kullanıcı.timeout(
            timedelta(
                minutes=dakika
            ),
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} "
            f"`{dakika}` dakika timeout aldı."
        )

        await send_log(
            interaction.guild,
            f"⏱️ {kullanıcı} timeout aldı.\n"
            f"Süre: {dakika} dakika\n"
            f"Sebep: {sebep}",
            "timeout"
        )

    except Exception as e:
        print(
            "Timeout hatası:",
            repr(e)
        )

        await interaction.response.send_message(
            f"{EMOJIS['no']} Timeout verilemedi.",
            ephemeral=True
        )


# =========================================================
# /UYAR
# =========================================================

@bot.tree.command(
    name="uyar",
    description="Kullanıcıya uyarı verir."
)
@app_commands.describe(
    kullanıcı="Uyarılacak kullanıcı.",
    sebep="Uyarı sebebi."
)
async def warn_command(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu işlem için yetkin yok.",
            ephemeral=True
        )
        return

    config = get_config(
        interaction.guild.id
    )

    uid = str(
        kullanıcı.id
    )

    if uid not in config["warnings"]:
        config["warnings"][uid] = []

    config["warnings"][uid].append({
        "reason": sebep,
        "moderator": interaction.user.id,
        "time": datetime.now(
            timezone.utc
        ).isoformat()
    })

    save_configs()

    count = len(
        config["warnings"][uid]
    )

    limit = config["moderation"]["max_warnings"]

    await interaction.response.send_message(
        f"{EMOJIS['yes']} {kullanıcı.mention} uyarıldı.\n"
        f"**Sebep:** {sebep}\n"
        f"**Uyarı:** `{count}/{limit}`"
    )

    if count >= limit:
        try:
            await kullanıcı.timeout(
                timedelta(
                    minutes=config["moderation"]["timeout_minutes"]
                ),
                reason="Uyarı limiti doldu."
            )
        except Exception:
            pass


# =========================================================
# /UYARILAR
# =========================================================

@bot.tree.command(
    name="uyarılar",
    description="Kullanıcının uyarılarını gösterir."
)
@app_commands.describe(
    kullanıcı="Kullanıcı."
)
async def warnings_command(
    interaction,
    kullanıcı: discord.Member = None
):
    user = kullanıcı or interaction.user

    config = get_config(
        interaction.guild.id
    )

    warnings = config["warnings"].get(
        str(user.id),
        []
    )

    if not warnings:
        await interaction.response.send_message(
            f"{EMOJIS['correct']} Uyarı bulunmuyor.",
            ephemeral=True
        )
        return

    text = []

    for i, warning in enumerate(
        warnings[-10:],
        1
    ):
        text.append(
            f"**{i}.** {warning['reason']}"
        )

    embed = discord.Embed(
        title=f"{user.display_name} Uyarıları",
        description="\n".join(text),
        color=discord.Color.orange()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /ÇEKİLİŞ
# =========================================================

@bot.tree.command(
    name="çekiliş",
    description="Çekiliş başlatır."
)
@app_commands.describe(
    ödül="Çekiliş ödülü.",
    kazanan="Kazanan sayısı.",
    süre="Süre, dakika."
)
async def giveaway_command(
    interaction,
    ödül: str,
    kazanan: app_commands.Range[
        int,
        1,
        20
    ],
    süre: app_commands.Range[
        int,
        1,
        40
    ]
):
    config = get_config(
        interaction.guild.id
    )

    role_id = config["giveaway"]["staff_role_id"]

    if role_id:
        role = interaction.guild.get_role(
            role_id
        )

        if role and role not in interaction.user.roles:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu komut için "
                f"{role.mention} rolü gerekiyor.",
                ephemeral=True
            )
            return

    elif not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Çekiliş yetkili rolü ayarlanmamış.",
            ephemeral=True
        )
        return

    channel = interaction.channel

    if config["giveaway"]["channel_id"]:
        selected = interaction.guild.get_channel(
            config["giveaway"]["channel_id"]
        )

        if selected:
            channel = selected

    giveaway_id = (
        f"{interaction.guild.id}-"
        f"{channel.id}-"
        f"{int(datetime.now().timestamp())}"
    )

    active_giveaways[giveaway_id] = {
        "guild_id": interaction.guild.id,
        "channel_id": channel.id,
        "prize": ödül,
        "winners": kazanan,
        "duration": süre * 60,
        "participants": set()
    }

    embed = discord.Embed(
        title="🎉 Çekiliş",
        description=(
            f"**Ödül:** {ödül}\n"
            f"**Kazanan:** {kazanan}\n"
            f"**Süre:** {süre} dakika\n\n"
            "Katılmak için aşağıdaki butona bas."
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Çekiliş oluşturuldu.",
        ephemeral=True
    )

    await channel.send(
        embed=embed,
        view=GiveawayView(
            giveaway_id
        )
    )

    asyncio.create_task(
        finish_giveaway(
            giveaway_id
        )
    )


# =========================================================
# /ÇEKİLİŞ-BİTİR
# =========================================================

@bot.tree.command(
    name="çekiliş-bitir",
    description="Aktif çekilişi bitirir."
)
async def giveaway_end(
    interaction
):
    config = get_config(
        interaction.guild.id
    )

    role_id = config["giveaway"]["staff_role_id"]

    if role_id:
        role = interaction.guild.get_role(
            role_id
        )

        if role and role not in interaction.user.roles:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Çekiliş yetkin yok.",
                ephemeral=True
            )
            return

    target = None

    for gid, giveaway in active_giveaways.items():
        if giveaway["guild_id"] == interaction.guild.id:
            target = gid
            break

    if not target:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Aktif çekiliş yok.",
            ephemeral=True
        )
        return

    giveaway = active_giveaways.pop(
        target
    )

    participants = list(
        giveaway["participants"]
    )

    if not participants:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Katılımcı yok."
        )
        return

    count = min(
        giveaway["winners"],
        len(participants)
    )

    winners = random.sample(
        participants,
        count
    )

    mentions = " ".join(
        f"<@{x}>"
        for x in winners
    )

    await interaction.response.send_message(
        f"🎉 **Çekiliş bitti!**\n\n"
        f"**Ödül:** {giveaway['prize']}\n"
        f"**Kazananlar:** {mentions}"
    )


# =========================================================
# /DUYURU
# =========================================================

class AnnouncementModal(
    discord.ui.Modal,
    title="Duyuru"
):

    title_text = discord.ui.TextInput(
        label="Başlık",
        max_length=100
    )

    description = discord.ui.TextInput(
        label="Açıklama",
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    async def on_submit(
        self,
        interaction
    ):
        embed = discord.Embed(
            title=str(self.title_text),
            description=str(self.description),
            color=discord.Color.blurple()
        )

        await interaction.channel.send(
            embed=embed
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Duyuru gönderildi.",
            ephemeral=True
        )


@bot.tree.command(
    name="duyuru",
    description="Embed duyuru gönderir."
)
async def announcement(
    interaction
):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Yetkin yok.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(
        AnnouncementModal()
    )


# =========================================================
# /KİLİTLE
# =========================================================

@bot.tree.command(
    name="kilitle",
    description="Bulunduğun kanalı kilitler."
)
async def lock(
    interaction
):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kanal yönetme yetkin yok.",
            ephemeral=True
        )
        return

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        f"{EMOJIS['locked']} Kanal kilitlendi."
    )


# =========================================================
# /KİLİT-AÇ
# =========================================================

@bot.tree.command(
    name="kilit-aç",
    description="Kanalın kilidini açar."
)
async def unlock(
    interaction
):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kanal yönetme yetkin yok.",
            ephemeral=True
        )
        return

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = None

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        f"{EMOJIS['unlock']} Kanalın kilidi açıldı."
    )


# =========================================================
# /YAVAŞ-MOD
# =========================================================

@bot.tree.command(
    name="yavaş-mod",
    description="Kanalın yavaş modunu ayarlar."
)
@app_commands.describe(
    saniye="0-21600 arası saniye."
)
async def slowmode(
    interaction,
    saniye: app_commands.Range[
        int,
        0,
        21600
    ]
):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kanal yönetme yetkin yok.",
            ephemeral=True
        )
        return

    await interaction.channel.edit(
        slowmode_delay=saniye
    )

    if saniye == 0:
        text = "Yavaş mod kapatıldı."
    else:
        text = (
            f"Yavaş mod `{saniye}` saniye olarak ayarlandı."
        )

    await interaction.response.send_message(
        f"{EMOJIS['yes']} {text}"
    )


# =========================================================
# ÜYE GİRİŞ
# =========================================================

@bot.event
async def on_member_join(
    member
):
    config = get_config(
        member.guild.id
    )

    # Oto rol
    role_id = config["autorole"]["role_id"]

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

    # Karşılama
    channel_id = config["welcome"]["channel_id"]

    if channel_id:
        channel = member.guild.get_channel(
            channel_id
        )

        if channel:
            description = (
                config["welcome"]["description"]
                .replace(
                    "{user}",
                    member.mention
                )
                .replace(
                    "{username}",
                    member.display_name
                )
            )

            embed = discord.Embed(
                title=config["welcome"]["title"],
                description=description,
                color=discord.Color.green()
            )

            if config["welcome"]["image"]:
                embed.set_image(
                    url=config["welcome"]["image"]
                )

            try:
                await channel.send(
                    embed=embed
                )
            except Exception:
                pass

    # DM
    if config["welcome"]["dm_enabled"]:
        try:
            message = (
                config["welcome"]["dm_message"]
                .replace(
                    "{user}",
                    member.mention
                )
                .replace(
                    "{username}",
                    member.display_name
                )
            )

            await member.send(
                message
            )
        except Exception:
            pass

    await send_log(
        member.guild,
        f"📥 {member.mention} sunucuya katıldı.",
        "member_join"
    )


# =========================================================
# ÜYE ÇIKIŞ
# =========================================================

@bot.event
async def on_member_remove(
    member
):
    await send_log(
        member.guild,
        f"📤 **{member}** sunucudan ayrıldı.",
        "member_leave"
    )


# =========================================================
# MESAJ
# =========================================================

spam_cache = {}


@bot.event
async def on_message(
    message
):
    if message.author.bot:
        return

    if not message.guild:
        return

    config = get_config(
        message.guild.id
    )

    content = message.content.lower()

    # Yasaklı kelimeler
    for word in config["moderation"]["bad_words"]:

        if word.lower() in content:

            try:
                await message.delete()
            except Exception:
                pass

            await message.channel.send(
                f"{EMOJIS['no']} {message.author.mention} "
                "yasaklı kelime kullanamazsın.",
                delete_after=5
            )

            break

    # Anti link
    if config["moderation"]["anti_link"]:

        links = [
            "http://",
            "https://",
            "discord.gg/",
            "www."
        ]

        if any(
            x in content
            for x in links
        ):
            if not message.author.guild_permissions.manage_messages:

                try:
                    await message.delete()
                except Exception:
                    pass

                await message.channel.send(
                    f"{EMOJIS['no']} {message.author.mention} "
                    "link göndermek yasak.",
                    delete_after=5
                )

    # Anti spam
    if config["moderation"]["anti_spam"]:

        now = datetime.now(
            timezone.utc
        ).timestamp()

        key = (
            message.guild.id,
            message.author.id
        )

        spam_cache.setdefault(
            key,
            []
        )

        spam_cache[key].append(
            now
        )

        spam_cache[key] = [
            x for x in spam_cache[key]
            if now - x <= 5
        ]

        if len(
            spam_cache[key]
        ) >= 6:

            try:
                await message.author.timeout(
                    timedelta(
                        minutes=1
                    ),
                    reason="Anti-spam"
                )
            except Exception:
                pass

            spam_cache[key] = []

    await bot.process_commands(
        message
    )


# =========================================================
# MESAJ SİLME
# =========================================================

@bot.event
async def on_message_delete(
    message
):
    if message.author.bot:
        return

    if message.guild:
        await send_log(
            message.guild,
            f"🗑️ **Mesaj silindi**\n"
            f"**Kullanıcı:** {message.author.mention}\n"
            f"**Kanal:** {message.channel.mention}\n"
            f"**Mesaj:** {message.content[:1000]}",
            "message_delete"
        )


# =========================================================
# MESAJ DÜZENLEME
# =========================================================

@bot.event
async def on_message_edit(
    before,
    after
):
    if before.author.bot:
        return

    if before.content == after.content:
        return

    if before.guild:
        await send_log(
            before.guild,
            f"✏️ **Mesaj düzenlendi**\n"
            f"**Kullanıcı:** {before.author.mention}\n"
            f"**Kanal:** {before.channel.mention}\n"
            f"**Eski:** {before.content[:500]}\n"
            f"**Yeni:** {after.content[:500]}",
            "message_edit"
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

    config = get_config(
        member.guild.id
    )

    channel_id = config["voice"]["channel_id"]

    if not channel_id:
        return

    channel = member.guild.get_channel(
        channel_id
    )

    if not channel:
        return

    if before.channel is None and after.channel:

        text = config["voice"]["join_message"]

        text = text.replace(
            "{user}",
            member.mention
        )

        await channel.send(
            text
        )

    elif before.channel and after.channel is None:

        text = config["voice"]["leave_message"]

        text = text.replace(
            "{user}",
            member.mention
        )

        await channel.send(
            text
        )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():
    print(
        f"Dynex aktif: {bot.user}"
    )

    print(
        f"Sunucu sayısı: {len(bot.guilds)}"
    )


# =========================================================
# HATA
# =========================================================

@bot.tree.error
async def command_error(
    interaction,
    error
):
    print(
        "Slash komut hatası:",
        repr(error)
    )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(
                f"{EMOJIS['no']} Komut çalıştırılırken hata oluştu.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Komut çalıştırılırken hata oluştu.",
                ephemeral=True
            )
    except Exception:
        pass


# =========================================================
# BAŞLAT
# =========================================================

@bot.tree.command(
    name="sil",
    description="Belirtilen miktarda mesajı siler."
)
@app_commands.describe(
    miktar="Silinecek mesaj sayısı (1-100)."
)
async def sil(
    interaction: discord.Interaction,
    miktar: app_commands.Range[int, 1, 100]
):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Mesajları silme yetkin yok.",
            ephemeral=True
        )
        return

    await interaction.response.defer(
        ephemeral=True
    )

    try:
        deleted = await interaction.channel.purge(
            limit=miktar
        )

        await interaction.followup.send(
            f"{EMOJIS['yes']} `{len(deleted)}` mesaj silindi.",
            ephemeral=True
        )

    except Exception as e:
        print("/sil hatası:", repr(e))

        await interaction.followup.send(
            f"{EMOJIS['no']} Mesajlar silinemedi.",
            ephemeral=True
        )


bot.run(TOKEN)
