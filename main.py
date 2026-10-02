import os
import json
import secrets
import asyncio
from datetime import timedelta
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# DYNEX
# =========================================================

CONFIG_FILE = Path("config.json")

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
# DEFAULT CONFIG
# =========================================================

DEFAULT_CONFIG = {
    "language": "tr",

    "ticket": {
        "category": None,
        "role": None,
        "channel": None,
        "title": "Destek Talebi",
        "description": "Aşağıdaki seçeneklerden uygun olanı seçerek ticket oluşturabilirsin.",
        "image_url": None,
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
        "channel": None,
        "message": "Sunucumuza hoş geldin {member}!",
        "title": "Hoş Geldin!",
        "description": "{member} sunucumuza katıldı.",
        "color": 5793266,
        "image_url": None,
        "thumbnail_url": None,
        "show_member": True,
        "show_username": True,
        "show_id": False,
        "show_server": True,
        "show_member_count": True,
        "show_join_number": False,
        "dm_enabled": False,
        "dm_message": "Sunucumuza hoş geldin!"
    },

    "autorole": {
        "role": None
    },

    "logs": {
        "channel": None,
        "message_delete": True,
        "message_edit": True,
        "member_join": True,
        "member_leave": True,
        "ban": True,
        "kick": True,
        "timeout": True
    },

    "moderation": {
        "channel": None,
        "bad_words": [],
        "max_warnings": 3,
        "warning_action": "timeout",
        "timeout_minutes": 10,
        "delete_after": True,
        "anti_link": False,
        "anti_spam": False
    },

    "voice": {
        "channel": None,
        "join_message": "{member} ses kanalına katıldı.",
        "leave_message": "{member} ses kanalından ayrıldı."
    }
}


# =========================================================
# CONFIG FUNCTIONS
# =========================================================

def copy_data(data):
    return json.loads(json.dumps(data))


def load_configs():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            "{}",
            encoding="utf-8"
        )
        return {}

    try:
        data = json.loads(
            CONFIG_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, dict):
            return data

    except Exception:
        pass

    return {}


ALL_CONFIG = load_configs()


def merge_dict(default, current):
    if not isinstance(default, dict):
        return current

    if not isinstance(current, dict):
        return copy_data(default)

    result = {}

    for key, value in default.items():

        if key in current:

            if isinstance(value, dict):
                result[key] = merge_dict(
                    value,
                    current[key]
                )
            else:
                result[key] = current[key]

        else:
            result[key] = copy_data(value)

    for key, value in current.items():

        if key not in result:
            result[key] = value

    return result


def save_config():
    CONFIG_FILE.write_text(
        json.dumps(
            ALL_CONFIG,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )


def get_config(guild_id):
    key = str(guild_id)

    if key not in ALL_CONFIG:
        ALL_CONFIG[key] = copy_data(
            DEFAULT_CONFIG
        )
    else:
        ALL_CONFIG[key] = merge_dict(
            DEFAULT_CONFIG,
            ALL_CONFIG[key]
        )

    save_config()

    return ALL_CONFIG[key]


# =========================================================
# HELPERS
# =========================================================

def replace_variables(text, member):

    if not text:
        return ""

    guild = member.guild

    return (
        str(text)
        .replace("{member}", member.mention)
        .replace("{username}", member.name)
        .replace("{displayname}", member.display_name)
        .replace("{id}", str(member.id))
        .replace("{server}", guild.name)
        .replace(
            "{member_count}",
            str(guild.member_count or 0)
        )
    )


def parse_emoji(value, guild):

    if not value:
        return None

    value = str(value).strip()

    # <:isim:id>
    if value.startswith("<:") or value.startswith("<a:"):

        try:
            emoji = discord.PartialEmoji.from_str(
                value
            )

            if emoji.id:
                return emoji

        except Exception:
            return None

    # :isim:
    if value.startswith(":") and value.endswith(":"):

        name = value[1:-1].strip()

        emoji = discord.utils.get(
            guild.emojis,
            name=name
        )

        return emoji

    # Unicode
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
            emoji = discord.PartialEmoji.from_str(
                value
            )

            return emoji.id is not None

        except Exception:
            return False

    return True


def make_embed(
    title,
    description="",
    color=0x5865F2
):

    return discord.Embed(
        title=title,
        description=description,
        color=color
    )


def get_text_channel(
    guild,
    channel_id
):

    if not channel_id:
        return None

    try:
        return guild.get_channel(
            int(channel_id)
        )
    except Exception:
        return None


async def send_log(guild, embed):

    config = get_config(guild.id)

    channel = get_text_channel(
        guild,
        config["logs"].get("channel")
    )

    if channel:

        try:
            await channel.send(
                embed=embed
            )
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

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# LANGUAGE
# =========================================================

LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
    "az": "Azərbaycan dili"
}


# =========================================================
# LANGUAGE SELECT
# =========================================================

class LanguageSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Türkçe",
                value="tr"
            ),
            discord.SelectOption(
                label="English",
                value="en"
            ),
            discord.SelectOption(
                label="Azərbaycan dili",
                value="az"
            )
        ]

        super().__init__(
            placeholder="Dil seç",
            options=options,
            custom_id="dynex_language_select"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["language"] = self.values[0]

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Dil "
                f"**{LANGUAGES[self.values[0]]}** "
                "olarak ayarlandı."
            ),
            embed=None,
            view=None
        )


class LanguageView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            LanguageSelect()
        )


# =========================================================
# /DIL
# =========================================================

@bot.tree.command(
    name="dil",
    description="Botun dilini değiştir."
)
@app_commands.guild_only()
async def dil(
    interaction: discord.Interaction
):

    embed = make_embed(
        f"{EMOJIS['settings']} Dynex Dil Ayarları",
        "Botun kullanacağı dili seç."
    )

    await interaction.response.send_message(
        embed=embed,
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# TICKET ADD MODAL
# =========================================================

class TicketAddModal(
    discord.ui.Modal,
    title="Ticket Seçeneği Ekle"
):

    name_input = discord.ui.TextInput(
        label="Seçenek adı",
        placeholder="Destek",
        required=True,
        max_length=50
    )

    button_input = discord.ui.TextInput(
        label="Buton yazısı",
        placeholder="Destek",
        required=True,
        max_length=50
    )

    emoji_input = discord.ui.TextInput(
        label="Emoji",
        placeholder="🎫 veya :dikkat: veya <:Dynex:123>",
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction):

        guild = interaction.guild

        emoji_value = str(
            self.emoji_input.value
        ).strip()

        if not emoji_exists(
            emoji_value,
            guild
        ):

            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu özel emoji sunucuda bulunamadı.",
                ephemeral=True
            )

            return

        config = get_config(
            guild.id
        )

        option_id = secrets.token_hex(4)

        config["ticket"]["options"].append(
            {
                "id": option_id,
                "name": str(
                    self.name_input.value
                ),
                "button": str(
                    self.button_input.value
                ),
                "emoji": emoji_value
            }
        )

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket seçeneği eklendi.",
            ephemeral=True
        )


# =========================================================
# TICKET EDIT MODAL
# =========================================================

class TicketEditModal(
    discord.ui.Modal
):

    def __init__(
        self,
        option_id,
        name,
        button,
        emoji
    ):

        super().__init__(
            title="Ticket Seçeneğini Düzenle"
        )

        self.option_id = option_id

        self.name_input = discord.ui.TextInput(
            label="Seçenek adı",
            default=name,
            required=True,
            max_length=50
        )

        self.button_input = discord.ui.TextInput(
            label="Buton yazısı",
            default=button,
            required=True,
            max_length=50
        )

        self.emoji_input = discord.ui.TextInput(
            label="Emoji",
            default=emoji,
            required=False,
            max_length=100
        )

        self.add_item(
            self.name_input
        )

        self.add_item(
            self.button_input
        )

        self.add_item(
            self.emoji_input
        )

    async def on_submit(self, interaction):

        guild = interaction.guild
        config = get_config(guild.id)

        emoji_value = str(
            self.emoji_input.value
        ).strip()

        if not emoji_exists(
            emoji_value,
            guild
        ):

            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu özel emoji sunucuda bulunamadı.",
                ephemeral=True
            )

            return

        for option in config["ticket"]["options"]:

            if option["id"] == self.option_id:

                option["name"] = str(
                    self.name_input.value
                )

                option["button"] = str(
                    self.button_input.value
                )

                option["emoji"] = emoji_value

                break

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket seçeneği güncellendi.",
            ephemeral=True
        )


# =========================================================
# TICKET DELETE SELECT
# =========================================================

class TicketDeleteSelect(
    discord.ui.Select
):

    def __init__(self, guild):

        config = get_config(
            guild.id
        )

        options = []

        for option in config["ticket"]["options"][:25]:

            emoji = parse_emoji(
                option.get("emoji"),
                guild
            )

            kwargs = {
                "label": option["name"],
                "value": option["id"]
            }

            if emoji:
                kwargs["emoji"] = emoji

            options.append(
                discord.SelectOption(
                    **kwargs
                )
            )

        if not options:

            options.append(
                discord.SelectOption(
                    label="Seçenek bulunamadı",
                    value="none"
                )
            )

        super().__init__(
            placeholder="Silinecek seçeneği seç",
            options=options,
            custom_id="dynex_ticket_delete_select"
        )

    async def callback(self, interaction):

        selected = self.values[0]

        if selected == "none":

            await interaction.response.send_message(
                f"{EMOJIS['no']} Silinecek seçenek yok.",
                ephemeral=True
            )

            return

        config = get_config(
            interaction.guild.id
        )

        target = next(
            (
                option
                for option in config["ticket"]["options"]
                if option["id"] == selected
            ),
            None
        )

        if not target:

            await interaction.response.send_message(
                f"{EMOJIS['no']} Seçenek bulunamadı.",
                ephemeral=True
            )

            return

        config["ticket"]["options"] = [
            option
            for option in config["ticket"]["options"]
            if option["id"] != selected
        ]

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} **{target['name']}** "
                "seçeneği silindi."
            ),
            view=None
        )


class TicketDeleteView(
    discord.ui.View
):

    def __init__(self, guild):

        super().__init__(
            timeout=120
        )

        self.add_item(
            TicketDeleteSelect(guild)
        )


# =========================================================
# TICKET EDIT SELECT
# =========================================================

class TicketEditSelect(
    discord.ui.Select
):

    def __init__(self, guild):

        config = get_config(
            guild.id
        )

        options = []

        for option in config["ticket"]["options"][:25]:

            options.append(
                discord.SelectOption(
                    label=option["name"],
                    value=option["id"]
                )
            )

        if not options:

            options.append(
                discord.SelectOption(
                    label="Seçenek bulunamadı",
                    value="none"
                )
            )

        super().__init__(
            placeholder="Düzenlenecek seçeneği seç",
            options=options,
            custom_id="dynex_ticket_edit_select"
        )

    async def callback(self, interaction):

        selected = self.values[0]

        if selected == "none":

            await interaction.response.send_message(
                f"{EMOJIS['no']} Seçenek bulunamadı.",
                ephemeral=True
            )

            return

        config = get_config(
            interaction.guild.id
        )

        option = next(
            (
                item
                for item in config["ticket"]["options"]
                if item["id"] == selected
            ),
            None
        )

        if not option:

            await interaction.response.send_message(
                f"{EMOJIS['no']} Seçenek bulunamadı.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            TicketEditModal(
                option["id"],
                option["name"],
                option["button"],
                option.get("emoji", "")
            )
        )


class TicketEditView(
    discord.ui.View
):

    def __init__(self, guild):

        super().__init__(
            timeout=120
        )

        self.add_item(
            TicketEditSelect(guild)
        )


# =========================================================
# TICKET PANEL SETTINGS MODAL
# =========================================================

class TicketSettingsModal(
    discord.ui.Modal,
    title="Ticket Panel Ayarları"
):

    title_input = discord.ui.TextInput(
        label="Ticket başlığı",
        default="Destek Talebi",
        required=True,
        max_length=256
    )

    description_input = discord.ui.TextInput(
        label="Ticket açıklaması",
        style=discord.TextStyle.paragraph,
        default="Aşağıdaki seçeneklerden uygun olanı seçerek ticket oluşturabilirsin.",
        required=True,
        max_length=4000
    )

    image_input = discord.ui.TextInput(
        label="Panel resmi",
        placeholder="https://...",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["title"] = str(
            self.title_input.value
        )

        config["ticket"]["description"] = str(
            self.description_input.value
        )

        config["ticket"]["image_url"] = (
            str(
                self.image_input.value
            ).strip()
            or None
        )

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket panel ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# TICKET CATEGORY SELECT
# =========================================================

class TicketCategorySelect(
    discord.ui.ChannelSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Ticket kategorisini seç",
            channel_types=[
                discord.ChannelType.category
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_ticket_category"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["category"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Ticket kategorisi "
                f"{self.values[0].name} olarak ayarlandı."
            ),
            view=None
        )


class TicketCategoryView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            TicketCategorySelect()
        )


# =========================================================
# TICKET ROLE SELECT
# =========================================================

class TicketRoleSelect(
    discord.ui.RoleSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Ticket yetkili rolünü seç",
            min_values=1,
            max_values=1,
            custom_id="dynex_ticket_role"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["role"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Ticket yetkili rolü "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class TicketRoleView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            TicketRoleSelect()
        )


# =========================================================
# TICKET PANEL CHANNEL
# =========================================================

class TicketPanelChannelSelect(
    discord.ui.ChannelSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Ticket panel kanalını seç",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_ticket_panel_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"]["channel"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Ticket panel kanalı "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class TicketPanelChannelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            TicketPanelChannelSelect()
        )


# =========================================================
# TICKET CLOSE
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

        channel = interaction.channel

        if not channel:

            await interaction.response.send_message(
                f"{EMOJIS['no']} Kanal bulunamadı.",
                ephemeral=True
            )

            return

        topic = channel.topic or ""

        if not topic.startswith(
            "DynexTicket:"
        ):

            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu kanal bir Dynex ticketı değil.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            f"{EMOJIS['wait']} Ticket kapatılıyor..."
        )

        await asyncio.sleep(2)

        try:
            await channel.delete(
                reason="Dynex ticket kapatıldı"
            )
        except Exception:
            pass


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(
    discord.ui.View
):

    def __init__(self, guild_id):

        super().__init__(
            timeout=None
        )

        guild = bot.get_guild(
            guild_id
        )

        if not guild:
            return

        config = get_config(
            guild_id
        )

        for option in config["ticket"]["options"]:

            emoji = parse_emoji(
                option.get("emoji"),
                guild
            )

            button = discord.ui.Button(
                label=option.get(
                    "button",
                    option["name"]
                ),
                style=discord.ButtonStyle.primary,
                custom_id=(
                    f"dynex_ticket:"
                    f"{option['id']}"
                ),
                emoji=emoji
            )

            async def callback(
                interaction,
                option_id=option["id"]
            ):

                await create_ticket(
                    interaction,
                    option_id
                )

            button.callback = callback

            self.add_item(
                button
            )


# =========================================================
# CREATE TICKET
# =========================================================

async def create_ticket(
    interaction,
    option_id
):

    guild = interaction.guild
    member = interaction.user

    config = get_config(
        guild.id
    )

    option = next(
        (
            item
            for item in config["ticket"]["options"]
            if item["id"] == option_id
        ),
        None
    )

    if not option:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Ticket seçeneği bulunamadı.",
            ephemeral=True
        )

        return

    # Aynı kullanıcının ticketı
    for channel in guild.text_channels:

        if channel.topic == (
            f"DynexTicket:{member.id}"
        ):

            await interaction.response.send_message(
                (
                    f"{EMOJIS['wait']} Zaten açık bir ticketın var: "
                    f"{channel.mention}"
                ),
                ephemeral=True
            )

            return

    category = None

    if config["ticket"].get("category"):

        try:

            category = guild.get_channel(
                int(
                    config["ticket"]["category"]
                )
            )

        except Exception:
            category = None

    overwrites = {

        guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

        member:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
    }

    role = None

    if config["ticket"].get("role"):

        try:

            role = guild.get_role(
                int(
                    config["ticket"]["role"]
                )
            )

        except Exception:
            role = None

    if role:

        overwrites[role] = (
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        )

    safe_name = "".join(
        char
        for char in member.name.lower()
        if char.isalnum() or char in "-_"
    )

    if not safe_name:
        safe_name = "kullanici"

    channel_name = (
        f"ticket-{safe_name}"
    )[:100]

    try:

        channel = await guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"DynexTicket:{member.id}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Ticket kanalı oluşturma yetkim yok.",
            ephemeral=True
        )

        return

    embed = make_embed(
        config["ticket"]["title"],
        (
            f"{config['ticket']['description']}\n\n"
            f"**Seçenek:** {option['name']}"
        )
    )

    if config["ticket"].get(
        "image_url"
    ):

        embed.set_image(
            url=config["ticket"]["image_url"]
        )

    await channel.send(
        content=member.mention,
        embed=embed,
        view=TicketCloseView()
    )

    await interaction.response.send_message(
        (
            f"{EMOJIS['yes']} Ticket oluşturuldu: "
            f"{channel.mention}"
        ),
        ephemeral=True
    )


# =========================================================
# TICKET OPTIONS VIEW
# =========================================================

class TicketOptionsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

    @discord.ui.button(
        label="Seçenek Ekle",
        style=discord.ButtonStyle.success
    )
    async def add_option(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            TicketAddModal()
        )

    @discord.ui.button(
        label="Seçenek Sil",
        style=discord.ButtonStyle.danger
    )
    async def delete_option(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Silinecek ticket seçeneğini seç:",
            embed=None,
            view=TicketDeleteView(
                interaction.guild
            )
        )

    @discord.ui.button(
        label="Seçenek Düzenle",
        style=discord.ButtonStyle.primary
    )
    async def edit_option(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Düzenlenecek ticket seçeneğini seç:",
            embed=None,
            view=TicketEditView(
                interaction.guild
            )
        )


# =========================================================
# SEND TICKET PANEL
# =========================================================

async def send_ticket_panel(
    interaction
):

    config = get_config(
        interaction.guild.id
    )

    channel = get_text_channel(
        interaction.guild,
        config["ticket"].get("channel")
    )

    if not channel:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Önce ticket panel kanalını seç.",
            ephemeral=True
        )

        return

    embed = make_embed(
        config["ticket"]["title"],
        config["ticket"]["description"]
    )

    if config["ticket"].get(
        "image_url"
    ):

        embed.set_image(
            url=config["ticket"]["image_url"]
        )

    try:

        await channel.send(
            embed=embed,
            view=TicketPanelView(
                interaction.guild.id
            )
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} O kanala mesaj gönderemiyorum.",
            ephemeral=True
        )

        return

    await interaction.response.send_message(
        (
            f"{EMOJIS['yes']} Ticket paneli "
            f"{channel.mention} kanalına gönderildi."
        ),
        ephemeral=True
    )


# =========================================================
# WELCOME MODAL
# =========================================================

class WelcomeSettingsModal(
    discord.ui.Modal,
    title="Hoş Geldin Ayarları"
):

    title_input = discord.ui.TextInput(
        label="Başlık",
        default="Hoş Geldin!",
        required=True,
        max_length=256
    )

    description_input = discord.ui.TextInput(
        label="Açıklama",
        default="{member} sunucumuza katıldı.",
        required=True,
        max_length=4000
    )

    message_input = discord.ui.TextInput(
        label="Mesaj",
        default="Sunucumuza hoş geldin {member}!",
        required=True,
        max_length=2000
    )

    image_input = discord.ui.TextInput(
        label="Resim URL",
        required=False,
        max_length=500
    )

    dm_input = discord.ui.TextInput(
        label="DM mesajı",
        default="Sunucumuza hoş geldin!",
        required=False,
        max_length=2000
    )

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["welcome"]["title"] = str(
            self.title_input.value
        )

        config["welcome"]["description"] = str(
            self.description_input.value
        )

        config["welcome"]["message"] = str(
            self.message_input.value
        )

        config["welcome"]["image_url"] = (
            str(
                self.image_input.value
            ).strip()
            or None
        )

        config["welcome"]["dm_message"] = str(
            self.dm_input.value
        )

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Hoş geldin ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# WELCOME CHANNEL
# =========================================================

class WelcomeChannelSelect(
    discord.ui.ChannelSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Hoş geldin kanalını seç",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_welcome_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["welcome"]["channel"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Hoş geldin kanalı "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class WelcomeChannelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            WelcomeChannelSelect()
        )


# =========================================================
# AUTOROLE
# =========================================================

class AutoroleSelect(
    discord.ui.RoleSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Otorol seç",
            min_values=1,
            max_values=1,
            custom_id="dynex_autorole"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["autorole"]["role"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Otorol "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class AutoroleView(
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
# MODERATION MODAL
# =========================================================

class ModerationSettingsModal(
    discord.ui.Modal,
    title="Moderasyon Ayarları"
):

    bad_words = discord.ui.TextInput(
        label="Yasaklı kelimeler",
        placeholder="kelime1, kelime2, kelime3",
        required=False,
        max_length=2000
    )

    max_warnings = discord.ui.TextInput(
        label="Maksimum uyarı",
        default="3",
        required=True,
        max_length=3
    )

    warning_action = discord.ui.TextInput(
        label="Uyarı sonrası işlem",
        placeholder="timeout / kick / ban",
        default="timeout",
        required=True,
        max_length=20
    )

    timeout_minutes = discord.ui.TextInput(
        label="Timeout süresi",
        default="10",
        required=True,
        max_length=5
    )

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        words = [
            word.strip().lower()
            for word in str(
                self.bad_words.value
            ).split(",")
            if word.strip()
        ]

        try:

            max_warnings = max(
                1,
                int(
                    self.max_warnings.value
                )
            )

        except Exception:

            max_warnings = 3

        try:

            timeout_minutes = max(
                1,
                int(
                    self.timeout_minutes.value
                )
            )

        except Exception:

            timeout_minutes = 10

        action = str(
            self.warning_action.value
        ).strip().lower()

        if action not in (
            "timeout",
            "kick",
            "ban"
        ):

            action = "timeout"

        config["moderation"]["bad_words"] = words
        config["moderation"]["max_warnings"] = max_warnings
        config["moderation"]["warning_action"] = action
        config["moderation"]["timeout_minutes"] = timeout_minutes

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Moderasyon ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# MODERATION CHANNEL
# =========================================================

class ModerationChannelSelect(
    discord.ui.ChannelSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Moderasyon log kanalını seç",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_moderation_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["moderation"]["channel"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Moderasyon log kanalı "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class ModerationChannelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            ModerationChannelSelect()
        )


# =========================================================
# LOG MODAL
# =========================================================

class LogsSettingsModal(
    discord.ui.Modal,
    title="Log Ayarları"
):

    delete_input = discord.ui.TextInput(
        label="Silinen mesajlar",
        default="evet",
        required=True
    )

    edit_input = discord.ui.TextInput(
        label="Düzenlenen mesajlar",
        default="evet",
        required=True
    )

    member_input = discord.ui.TextInput(
        label="Üye giriş ve çıkış",
        default="evet",
        required=True
    )

    moderation_input = discord.ui.TextInput(
        label="Ban, kick ve timeout",
        default="evet",
        required=True
    )

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        def is_yes(value):

            return str(value).strip().lower() in (
                "evet",
                "yes",
                "e",
                "y",
                "true",
                "1"
            )

        config["logs"]["message_delete"] = is_yes(
            self.delete_input.value
        )

        config["logs"]["message_edit"] = is_yes(
            self.edit_input.value
        )

        member_logs = is_yes(
            self.member_input.value
        )

        config["logs"]["member_join"] = member_logs
        config["logs"]["member_leave"] = member_logs

        moderation_logs = is_yes(
            self.moderation_input.value
        )

        config["logs"]["ban"] = moderation_logs
        config["logs"]["kick"] = moderation_logs
        config["logs"]["timeout"] = moderation_logs

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Log ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# LOG CHANNEL
# =========================================================

class LogsChannelSelect(
    discord.ui.ChannelSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Log kanalını seç",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_logs_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["logs"]["channel"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Log kanalı "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class LogsChannelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            LogsChannelSelect()
        )


# =========================================================
# VOICE MODAL
# =========================================================

class VoiceSettingsModal(
    discord.ui.Modal,
    title="Ses Bildirim Ayarları"
):

    join_input = discord.ui.TextInput(
        label="Katılma mesajı",
        default="{member} ses kanalına katıldı.",
        required=True,
        max_length=1000
    )

    leave_input = discord.ui.TextInput(
        label="Ayrılma mesajı",
        default="{member} ses kanalından ayrıldı.",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["voice"]["join_message"] = str(
            self.join_input.value
        )

        config["voice"]["leave_message"] = str(
            self.leave_input.value
        )

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ses bildirim ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# VOICE CHANNEL
# =========================================================

class VoiceChannelSelect(
    discord.ui.ChannelSelect
):

    def __init__(self):

        super().__init__(
            placeholder="Bildirim kanalını seç",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_voice_channel"
        )

    async def callback(self, interaction):

        config = get_config(
            interaction.guild.id
        )

        config["voice"]["channel"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Ses bildirim kanalı "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class VoiceChannelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=120
        )

        self.add_item(
            VoiceChannelSelect()
        )


# =========================================================
# SETTINGS MAIN VIEW
# =========================================================

class SettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
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
            content=None,
            embed=make_embed(
                f"{EMOJIS['support']} Ticket Ayarları",
                "Ticket sistemini buradan yönet."
            ),
            view=TicketSettingsView()
        )

    @discord.ui.button(
        label="Hoş Geldin",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def welcome(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                "👋 Hoş Geldin Ayarları",
                "Hoş geldin sistemini buradan yönet."
            ),
            view=WelcomeSettingsView()
        )

    @discord.ui.button(
        label="Otorol",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def autorole(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                "👤 Otorol Ayarları",
                "Yeni üyelerin alacağı rolü seç."
            ),
            view=AutoroleSettingsView()
        )

    @discord.ui.button(
        label="Moderasyon",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def moderation(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                "🛡️ Moderasyon Ayarları",
                "Moderasyon sistemini buradan yönet."
            ),
            view=ModerationSettingsView()
        )

    @discord.ui.button(
        label="Log",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def logs(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                "📜 Log Ayarları",
                "Log sistemini buradan yönet."
            ),
            view=LogsSettingsView()
        )

    @discord.ui.button(
        label="Ses",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def voice(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                "🔊 Ses Ayarları",
                "Ses bildirimlerini buradan yönet."
            ),
            view=VoiceSettingsView()
        )

    @discord.ui.button(
        label="Dil",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def language(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                f"{EMOJIS['settings']} Dil Ayarları",
                "Botun dilini seç."
            ),
            view=LanguageView()
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

        ALL_CONFIG[
            str(interaction.guild.id)
        ] = copy_data(
            DEFAULT_CONFIG
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Sunucu ayarları "
                "varsayılan değerlere döndürüldü."
            ),
            embed=None,
            view=None
        )


# =========================================================
# TICKET SETTINGS VIEW
# =========================================================

class TicketSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Panel Ayarları",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def panel(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            TicketSettingsModal()
        )

    @discord.ui.button(
        label="Kategori Seç",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def category(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Ticket kanallarının oluşturulacağı kategoriyi seç:",
            embed=None,
            view=TicketCategoryView()
        )

    @discord.ui.button(
        label="Yetkili Rolü",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def role(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Ticket yetkilisi olacak rolü seç:",
            embed=None,
            view=TicketRoleView()
        )

    @discord.ui.button(
        label="Panel Kanalı",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def panel_channel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Ticket panelinin gönderileceği kanalı seç:",
            embed=None,
            view=TicketPanelChannelView()
        )

    @discord.ui.button(
        label="Seçenekler",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def options(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Ticket seçeneklerini yönet:",
            embed=None,
            view=TicketOptionsView()
        )

    @discord.ui.button(
        label="Paneli Gönder",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def send_panel(
        self,
        interaction,
        button
    ):

        await send_ticket_panel(
            interaction
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            view=SettingsView()
        )


# =========================================================
# WELCOME SETTINGS VIEW
# =========================================================

class WelcomeSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Mesaj Ayarları",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def settings(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            WelcomeSettingsModal()
        )

    @discord.ui.button(
        label="Kanal Seç",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def channel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Hoş geldin mesajlarının gönderileceği kanalı seç:",
            embed=None,
            view=WelcomeChannelView()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            view=SettingsView()
        )


# =========================================================
# AUTOROLE SETTINGS VIEW
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
        style=discord.ButtonStyle.primary
    )
    async def role(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Yeni üyeye verilecek rolü seç:",
            embed=None,
            view=AutoroleView()
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
            content=None,
            embed=make_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            view=SettingsView()
        )


# =========================================================
# MODERATION SETTINGS VIEW
# =========================================================

class ModerationSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Ceza Ayarları",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def settings(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            ModerationSettingsModal()
        )

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def channel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Moderasyon log kanalını seç:",
            embed=None,
            view=ModerationChannelView()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            view=SettingsView()
        )


# =========================================================
# LOG SETTINGS VIEW
# =========================================================

class LogsSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Log Ayarları",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def settings(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            LogsSettingsModal()
        )

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def channel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Logların gönderileceği kanalı seç:",
            embed=None,
            view=LogsChannelView()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            view=SettingsView()
        )


# =========================================================
# VOICE SETTINGS VIEW
# =========================================================

class VoiceSettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

    @discord.ui.button(
        label="Mesaj Ayarları",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def settings(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            VoiceSettingsModal()
        )

    @discord.ui.button(
        label="Bildirim Kanalı",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def channel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Ses bildirimlerinin gönderileceği kanalı seç:",
            embed=None,
            view=VoiceChannelView()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def back(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content=None,
            embed=make_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
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
@app_commands.guild_only()
@app_commands.default_permissions(
    administrator=True
)
async def ayarlar(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komutu kullanmak için yönetici olmalısın.",
            ephemeral=True
        )

        return

    embed = make_embed(
        f"{EMOJIS['settings']} Dynex Ayarları",
        "Ayarlarını yönetmek için bir bölüm seç."
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(),
        ephemeral=True
    )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun gecikmesini göster."
)
async def ping(
    interaction: discord.Interaction
):

    latency = round(
        bot.latency * 1000
    )

    if latency < 80:
        status = "Mükemmel"
    elif latency < 150:
        status = "İyi"
    elif latency < 250:
        status = "Orta"
    elif latency < 400:
        status = "Zayıf"
    else:
        status = "Berbat"

    embed = make_embed(
        f"{EMOJIS['dynex']} Dynex Bot Ping Durumu",
        (
            f"**Gecikme:** `{latency}ms`\n"
            f"**Durum:** {status}"
        )
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Bir kullanıcıyı yasakla."
)
@app_commands.describe(
    member="Yasaklanacak kullanıcı",
    reason="Sebep"
)
@app_commands.default_permissions(
    ban_members=True
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "Belirtilmedi"
):

    if member == interaction.user:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Kendini yasaklayamazsın.",
            ephemeral=True
        )

        return

    try:

        await member.ban(
            reason=reason
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {member.mention} yasaklandı."
        )

        config = get_config(
            interaction.guild.id
        )

        if config["logs"].get("ban"):

            await send_log(
                interaction.guild,
                make_embed(
                    "🔨 Ban",
                    (
                        f"**Kullanıcı:** {member.mention}\n"
                        f"**Yetkili:** {interaction.user.mention}\n"
                        f"**Sebep:** {reason}"
                    ),
                    0xED4245
                )
            )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı yasaklayamıyorum.",
            ephemeral=True
        )


# =========================================================
# /KICK
# =========================================================

@bot.tree.command(
    name="kick",
    description="Bir kullanıcıyı sunucudan at."
)
@app_commands.describe(
    member="Atılacak kullanıcı",
    reason="Sebep"
)
@app_commands.default_permissions(
    kick_members=True
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "Belirtilmedi"
):

    try:

        await member.kick(
            reason=reason
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {member.mention} sunucudan atıldı."
        )

        config = get_config(
            interaction.guild.id
        )

        if config["logs"].get("kick"):

            await send_log(
                interaction.guild,
                make_embed(
                    "👢 Kick",
                    (
                        f"**Kullanıcı:** {member.mention}\n"
                        f"**Yetkili:** {interaction.user.mention}\n"
                        f"**Sebep:** {reason}"
                    ),
                    0xFEE75C
                )
            )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı atamıyorum.",
            ephemeral=True
        )


# =========================================================
# /TIMEOUT
# =========================================================

@bot.tree.command(
    name="timeout",
    description="Bir kullanıcıyı sustur."
)
@app_commands.describe(
    member="Susturulacak kullanıcı",
    minutes="Dakika",
    reason="Sebep"
)
@app_commands.default_permissions(
    moderate_members=True
)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int,
    reason: str = "Belirtilmedi"
):

    if minutes < 1:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Süre en az 1 dakika olmalı.",
            ephemeral=True
        )

        return

    if minutes > 40320:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Süre en fazla 28 gün olabilir.",
            ephemeral=True
        )

        return

    try:

        until = (
            discord.utils.utcnow()
            + timedelta(minutes=minutes)
        )

        await member.timeout(
            until,
            reason=reason
        )

        await interaction.response.send_message(
            (
                f"{EMOJIS['yes']} {member.mention} "
                f"{minutes} dakika susturuldu."
            )
        )

        config = get_config(
            interaction.guild.id
        )

        if config["logs"].get("timeout"):

            await send_log(
                interaction.guild,
                make_embed(
                    "🔇 Timeout",
                    (
                        f"**Kullanıcı:** {member.mention}\n"
                        f"**Yetkili:** {interaction.user.mention}\n"
                        f"**Süre:** {minutes} dakika\n"
                        f"**Sebep:** {reason}"
                    )
                )
            )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı susturamıyorum.",
            ephemeral=True
        )


# =========================================================
# MESSAGE EVENT
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not message.guild:

        await bot.process_commands(
            message
        )

        return

    config = get_config(
        message.guild.id
    )

    moderation = config["moderation"]

    # LINK FILTER
    if moderation.get(
        "anti_link"
    ):

        content = message.content.lower()

        blocked = (
            "http://",
            "https://",
            "discord.gg/",
            "www."
        )

        if any(
            item in content
            for item in blocked
        ):

            try:
                await message.delete()
            except Exception:
                pass

            try:

                await message.channel.send(
                    (
                        f"{EMOJIS['no']} "
                        f"{message.author.mention}, "
                        "link paylaşamazsın."
                    ),
                    delete_after=5
                )

            except Exception:
                pass

            return

    # BAD WORDS
    words = moderation.get(
        "bad_words",
        []
    )

    content_lower = message.content.lower()

    if words and any(
        word in content_lower
        for word in words
    ):

        try:
            await message.delete()
        except Exception:
            pass

        try:

            await message.channel.send(
                (
                    f"{EMOJIS['no']} "
                    f"{message.author.mention}, "
                    "bu kelimeyi kullanamazsın."
                ),
                delete_after=5
            )

        except Exception:
            pass

        return

    await bot.process_commands(
        message
    )


# =========================================================
# MESSAGE DELETE
# =========================================================

@bot.event
async def on_message_delete(message):

    if not message.guild:
        return

    if message.author.bot:
        return

    config = get_config(
        message.guild.id
    )

    if not config["logs"].get(
        "message_delete",
        True
    ):
        return

    content = (
        message.content
        or "Mesaj içeriği yok."
    )

    await send_log(
        message.guild,
        make_embed(
            "🗑️ Mesaj Silindi",
            (
                f"**Kullanıcı:** {message.author.mention}\n"
                f"**Kanal:** {message.channel.mention}\n"
                f"**İçerik:** {content[:1500]}"
            ),
            0xED4245
        )
    )


# =========================================================
# MESSAGE EDIT
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

    config = get_config(
        before.guild.id
    )

    if not config["logs"].get(
        "message_edit",
        True
    ):
        return

    await send_log(
        before.guild,
        make_embed(
            "✏️ Mesaj Düzenlendi",
            (
                f"**Kullanıcı:** {before.author.mention}\n"
                f"**Kanal:** {before.channel.mention}\n\n"
                f"**Önce:** {before.content[:700]}\n"
                f"**Sonra:** {after.content[:700]}"
            ),
            0xFEE75C
        )
    )


# =========================================================
# MEMBER JOIN
# =========================================================

@bot.event
async def on_member_join(member):

    config = get_config(
        member.guild.id
    )

    # AUTOROLE
    role_id = config["autorole"].get(
        "role"
    )

    if role_id:

        try:

            role = member.guild.get_role(
                int(role_id)
            )

            if role:
                await member.add_roles(
                    role,
                    reason="Dynex Otorol"
                )

        except Exception:
            pass

    # WELCOME
    welcome = config["welcome"]

    channel = get_text_channel(
        member.guild,
        welcome.get("channel")
    )

    if channel:

        embed = make_embed(
            welcome.get(
                "title",
                "Hoş Geldin!"
            ),
            replace_variables(
                welcome.get(
                    "description",
                    ""
                ),
                member
            ),
            welcome.get(
                "color",
                5793266
            )
        )

        if welcome.get(
            "image_url"
        ):

            embed.set_image(
                url=welcome["image_url"]
            )

        if welcome.get(
            "thumbnail_url"
        ):

            embed.set_thumbnail(
                url=welcome["thumbnail_url"]
            )

        extra = []

        if welcome.get(
            "show_member"
        ):
            extra.append(
                f"**Üye:** {member.mention}"
            )

        if welcome.get(
            "show_username"
        ):
            extra.append(
                f"**Kullanıcı:** `{member.name}`"
            )

        if welcome.get(
            "show_id"
        ):
            extra.append(
                f"**ID:** `{member.id}`"
            )

        if welcome.get(
            "show_server"
        ):
            extra.append(
                f"**Sunucu:** `{member.guild.name}`"
            )

        if welcome.get(
            "show_member_count"
        ):
            extra.append(
                (
                    f"**Üye sayısı:** "
                    f"`{member.guild.member_count}`"
                )
            )

        if extra:

            embed.add_field(
                name="Bilgiler",
                value="\n".join(extra),
                inline=False
            )

        try:

            await channel.send(
                content=replace_variables(
                    welcome.get(
                        "message",
                        ""
                    ),
                    member
                ),
                embed=embed
            )

        except Exception:
            pass

    # JOIN LOG
    if config["logs"].get(
        "member_join",
        True
    ):

        await send_log(
            member.guild,
            make_embed(
                "📥 Üye Katıldı",
                (
                    f"**Kullanıcı:** {member.mention}\n"
                    f"**ID:** `{member.id}`"
                ),
                0x57F287
            )
        )

    # DM
    if welcome.get(
        "dm_enabled"
    ):

        try:

            await member.send(
                replace_variables(
                    welcome.get(
                        "dm_message",
                        ""
                    ),
                    member
                )
            )

        except Exception:
            pass


# =========================================================
# MEMBER REMOVE
# =========================================================

@bot.event
async def on_member_remove(member):

    config = get_config(
        member.guild.id
    )

    if not config["logs"].get(
        "member_leave",
        True
    ):
        return

    await send_log(
        member.guild,
        make_embed(
            "📤 Üye Ayrıldı",
            (
                f"**Kullanıcı:** `{member}`\n"
                f"**ID:** `{member.id}`"
            ),
            0xED4245
        )
    )


# =========================================================
# VOICE
# =========================================================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    config = get_config(
        member.guild.id
    )

    channel = get_text_channel(
        member.guild,
        config["voice"].get("channel")
    )

    if not channel:
        return

    if (
        before.channel is None
        and after.channel is not None
    ):

        message = replace_variables(
            config["voice"].get(
                "join_message",
                "{member} ses kanalına katıldı."
            ),
            member
        )

        try:

            await channel.send(
                f"🔊 {message}\n"
                f"**Kanal:** {after.channel.mention}"
            )

        except Exception:
            pass

    elif (
        before.channel is not None
        and after.channel is None
    ):

        message = replace_variables(
            config["voice"].get(
                "leave_message",
                "{member} ses kanalından ayrıldı."
            ),
            member
        )

        try:

            await channel.send(
                f"🔊 {message}\n"
                f"**Kanal:** {before.channel.mention}"
            )

        except Exception:
            pass


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(
        f"Dynex giriş yaptı: "
        f"{bot.user} ({bot.user.id})"
    )

    try:

        synced = await bot.tree.sync()

        print(
            f"{len(synced)} slash komutu senkronize edildi."
        )

    except Exception as error:

        print(
            f"Slash komut hatası: {error}"
        )


# =========================================================
# START
# =========================================================

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN bulunamadı."
    )

bot.run(TOKEN)
