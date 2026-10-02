import os
import json
import secrets
import asyncio
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
# CONFIG
# =========================================================

def deep_copy_default():
    return json.loads(json.dumps(DEFAULT_CONFIG))


def merge_config(default, current):
    if isinstance(default, dict) and isinstance(current, dict):
        result = {}

        for key, value in default.items():
            if key in current:
                result[key] = merge_config(value, current[key])
            else:
                result[key] = deep_copy(value)

        for key, value in current.items():
            if key not in result:
                result[key] = value

        return result

    return current


def deep_copy(value):
    return json.loads(json.dumps(value))


def load_all_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps({}, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    if not isinstance(data, dict):
        data = {}

    return data


ALL_CONFIG = load_all_config()


def get_config(guild_id: int):
    key = str(guild_id)

    if key not in ALL_CONFIG:
        ALL_CONFIG[key] = deep_copy_default()
        save_config()

    else:
        ALL_CONFIG[key] = merge_config(
            deep_copy_default(),
            ALL_CONFIG[key]
        )

    return ALL_CONFIG[key]


def save_config():
    CONFIG_FILE.write_text(
        json.dumps(ALL_CONFIG, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )


# =========================================================
# HELPERS
# =========================================================

def replace_variables(text, member):
    if not text:
        return ""

    guild = member.guild

    return str(text).replace(
        "{member}", member.mention
    ).replace(
        "{username}", member.name
    ).replace(
        "{displayname}", member.display_name
    ).replace(
        "{id}", str(member.id)
    ).replace(
        "{server}", guild.name
    ).replace(
        "{member_count}", str(guild.member_count or 0)
    )


def color_from_int(value):
    try:
        return discord.Color(int(value))
    except Exception:
        return discord.Color.blurple()


def parse_emoji(value, guild):
    if not value:
        return None

    value = str(value).strip()

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
        name = value[1:-1].strip()

        emoji = discord.utils.get(
            guild.emojis,
            name=name
        )

        if emoji:
            return emoji

        return None

    # Unicode emoji
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
            emoji = discord.PartialEmoji.from_str(value)
            return emoji.id is not None
        except Exception:
            return False

    return True


async def send_log(guild, embed):
    config = get_config(guild.id)

    if not config["logs"].get("channel"):
        return

    channel = guild.get_channel(
        int(config["logs"]["channel"])
    )

    if channel:
        try:
            await channel.send(embed=embed)
        except Exception:
            pass


def dynex_embed(title, description="", color=0x5865F2):
    return discord.Embed(
        title=title,
        description=description,
        color=color
    )


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


def language_name(code):
    return LANGUAGES.get(code, "Türkçe")


# =========================================================
# /dil
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

    async def callback(self, interaction: discord.Interaction):
        config = get_config(interaction.guild.id)

        config["language"] = self.values[0]
        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Dil **{language_name(self.values[0])}** "
                "olarak ayarlandı."
            ),
            embed=None,
            view=None
        )


class LanguageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(LanguageSelect())


@bot.tree.command(
    name="dil",
    description="Botun dilini değiştir."
)
@app_commands.guild_only()
async def language_command(interaction: discord.Interaction):

    embed = dynex_embed(
        f"{EMOJIS['settings']} Dynex Dil Ayarları",
        "Botun kullanacağı dili aşağıdaki menüden seç."
    )

    await interaction.response.send_message(
        embed=embed,
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# TICKET OPTION EMOJIS
# =========================================================

class TicketOptionEmojiModal(discord.ui.Modal, title="Ticket Seçeneği"):

    emoji = discord.ui.TextInput(
        label="Emoji",
        placeholder="🎫 veya :dikkat: veya <:Dynex:123456789>",
        required=False,
        max_length=100
    )

    name = discord.ui.TextInput(
        label="Seçenek adı",
        placeholder="Destek",
        required=True,
        max_length=50
    )

    button = discord.ui.TextInput(
        label="Buton yazısı",
        placeholder="Destek",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        config = get_config(guild.id)

        emoji_value = str(self.emoji.value).strip()

        if not emoji_exists(emoji_value, guild):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu özel emoji sunucuda bulunamadı.",
                ephemeral=True
            )
            return

        option_id = secrets.token_hex(4)

        config["ticket"]["options"].append({
            "id": option_id,
            "name": str(self.name.value),
            "button": str(self.button.value),
            "emoji": emoji_value
        })

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket seçeneği eklendi: **{self.name.value}**",
            ephemeral=True
        )


# =========================================================
# TICKET DELETE SELECT
# =========================================================

class TicketDeleteSelect(discord.ui.Select):

    def __init__(self, guild):

        config = get_config(guild.id)

        options = []

        for option in config["ticket"]["options"][:25]:

            emoji = parse_emoji(
                option.get("emoji"),
                guild
            )

            kwargs = {
                "label": option.get("name", "Seçenek"),
                "value": option["id"]
            }

            if emoji:
                kwargs["emoji"] = emoji

            options.append(
                discord.SelectOption(**kwargs)
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


    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "none":
            await interaction.response.send_message(
                f"{EMOJIS['no']} Silinecek seçenek yok.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        options = config["ticket"]["options"]

        target = next(
            (
                item
                for item in options
                if item["id"] == self.values[0]
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
            item
            for item in options
            if item["id"] != self.values[0]
        ]

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} **{target['name']}** ticket seçeneği silindi."
            ),
            view=None
        )


class TicketDeleteView(discord.ui.View):

    def __init__(self, guild):
        super().__init__(timeout=120)
        self.add_item(TicketDeleteSelect(guild))


# =========================================================
# TICKET EDIT MODAL
# =========================================================

class TicketEditSelect(discord.ui.Select):

    def __init__(self, guild):

        config = get_config(guild.id)

        options = []

        for option in config["ticket"]["options"][:25]:
            options.append(
                discord.SelectOption(
                    label=option.get("name", "Seçenek"),
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

        if self.values[0] == "none":
            await interaction.response.send_message(
                f"{EMOJIS['no']} Seçenek bulunamadı.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        option = next(
            (
                item
                for item in config["ticket"]["options"]
                if item["id"] == self.values[0]
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


class TicketEditView(discord.ui.View):

    def __init__(self, guild):
        super().__init__(timeout=120)
        self.add_item(TicketEditSelect(guild))


class TicketEditModal(discord.ui.Modal):

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

        self.add_item(self.name_input)
        self.add_item(self.button_input)
        self.add_item(self.emoji_input)

    async def on_submit(self, interaction):

        config = get_config(interaction.guild.id)

        emoji_value = str(
            self.emoji_input.value
        ).strip()

        if not emoji_exists(
            emoji_value,
            interaction.guild
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
# TICKET MAIN MODAL
# =========================================================

class TicketSettingsModal(discord.ui.Modal, title="Ticket Ayarları"):

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

        config = get_config(interaction.guild.id)

        config["ticket"]["title"] = str(
            self.title_input.value
        )

        config["ticket"]["description"] = str(
            self.description_input.value
        )

        config["ticket"]["image_url"] = (
            str(self.image_input.value).strip()
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

class TicketCategorySelect(discord.ui.ChannelSelect):

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

        config = get_config(interaction.guild.id)

        config["ticket"]["category"] = str(
            self.values[0].id
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Ticket kategorisi "
                f"{self.values[0].mention} olarak ayarlandı."
            ),
            view=None
        )


class TicketCategoryView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TicketCategorySelect())


# =========================================================
# TICKET ROLE SELECT
# =========================================================

class TicketRoleSelect(discord.ui.RoleSelect):

    def __init__(self):

        super().__init__(
            placeholder="Ticket yetkili rolünü seç",
            min_values=1,
            max_values=1,
            custom_id="dynex_ticket_role"
        )

    async def callback(self, interaction):

        config = get_config(interaction.guild.id)

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


class TicketRoleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TicketRoleSelect())


# =========================================================
# TICKET PANEL CHANNEL
# =========================================================

class TicketPanelChannelSelect(discord.ui.ChannelSelect):

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

        config = get_config(interaction.guild.id)

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


class TicketPanelChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(TicketPanelChannelSelect())


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(timeout=None)

        config = get_config(guild_id)

        for option in config["ticket"]["options"]:

            emoji = parse_emoji(
                option.get("emoji"),
                bot.get_guild(guild_id)
            )

            button = discord.ui.Button(
                label=option.get(
                    "button",
                    option.get("name", "Ticket")
                ),
                style=discord.ButtonStyle.primary,
                custom_id=f"dynex_ticket:{option['id']}",
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

            self.add_item(button)


async def create_ticket(
    interaction: discord.Interaction,
    option_id: str
):

    guild = interaction.guild
    member = interaction.user

    config = get_config(guild.id)

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

    category = None

    if config["ticket"].get("category"):
        category = guild.get_channel(
            int(config["ticket"]["category"])
        )

    # Aynı kişinin açık ticketı
    for channel in guild.text_channels:

        if channel.topic == f"DynexTicket:{member.id}":
            await interaction.response.send_message(
                f"{EMOJIS['wait']} Zaten açık bir ticketın var: {channel.mention}",
                ephemeral=True
            )
            return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    }

    role = None

    if config["ticket"].get("role"):
        role = guild.get_role(
            int(config["ticket"]["role"])
        )

        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

    channel_name = (
        f"ticket-{member.name.lower()}"
        .replace(" ", "-")[:90]
    )

    try:

        channel = await guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"DynexTicket:{member.id}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Ticket kanalı oluşturmak için yetkim yok.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=config["ticket"]["title"],
        description=(
            f"{config['ticket']['description']}\n\n"
            f"**Seçenek:** {option['name']}"
        ),
        color=discord.Color.blurple()
    )

    await channel.send(
        content=member.mention,
        embed=embed,
        view=TicketCloseView()
    )

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Ticket oluşturuldu: {channel.mention}",
        ephemeral=True
    )


# =========================================================
# CLOSE TICKET
# =========================================================

class TicketCloseView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.Button(
        label="Ticket Kapat",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_ticket_close"
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.channel.topic:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu kanal bir ticket değil.",
                ephemeral=True
            )
            return

        if not interaction.channel.topic.startswith(
            "DynexTicket:"
        ):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu kanal bir ticket değil.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{EMOJIS['wait']} Ticket kapatılıyor..."
        )

        await asyncio.sleep(2)

        try:
            await interaction.channel.delete()
        except Exception:
            pass


# =========================================================
# TICKET OPTIONS VIEW
# =========================================================

class TicketOptionsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.Button(
        label="Seçenek Ekle",
        style=discord.ButtonStyle.success
    )
    async def add_option(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            TicketOptionEmojiModal()
        )

    @discord.ui.Button(
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
            view=TicketDeleteView(interaction.guild)
        )

    @discord.ui.Button(
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
            view=TicketEditView(interaction.guild)
        )


# =========================================================
# SEND TICKET PANEL
# =========================================================

async def send_ticket_panel(interaction):

    config = get_config(interaction.guild.id)

    channel_id = config["ticket"].get("channel")

    if not channel_id:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Önce ticket panel kanalını seç.",
            ephemeral=True
        )
        return

    channel = interaction.guild.get_channel(
        int(channel_id)
    )

    if not channel:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Ticket panel kanalı bulunamadı.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=config["ticket"]["title"],
        description=config["ticket"]["description"],
        color=discord.Color.blurple()
    )

    image_url = config["ticket"].get("image_url")

    if image_url:
        embed.set_image(url=image_url)

    try:

        await channel.send(
            embed=embed,
            view=TicketPanelView(interaction.guild.id)
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} O kanala mesaj gönderemiyorum.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Ticket paneli {channel.mention} kanalına gönderildi.",
        ephemeral=True
    )


# =========================================================
# WELCOME MODAL
# =========================================================

class WelcomeSettingsModal(discord.ui.Modal, title="Hoş Geldin Ayarları"):

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

        config = get_config(interaction.guild.id)

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
            str(self.image_input.value).strip()
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


class WelcomeChannelSelect(discord.ui.ChannelSelect):

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

        config = get_config(interaction.guild.id)

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


class WelcomeChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(WelcomeChannelSelect())


# =========================================================
# AUTOROLE
# =========================================================

class AutoroleRoleSelect(discord.ui.RoleSelect):

    def __init__(self):

        super().__init__(
            placeholder="Otorol seç",
            min_values=1,
            max_values=1,
            custom_id="dynex_autorole"
        )

    async def callback(self, interaction):

        config = get_config(interaction.guild.id)

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


class AutoroleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(AutoroleRoleSelect())


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

        config = get_config(interaction.guild.id)

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
                int(self.max_warnings.value)
            )
        except Exception:
            max_warnings = 3

        try:
            timeout_minutes = max(
                1,
                int(self.timeout_minutes.value)
            )
        except Exception:
            timeout_minutes = 10

        action = str(
            self.warning_action.value
        ).lower().strip()

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


class ModerationLogChannelSelect(
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
            custom_id="dynex_moderation_log"
        )

    async def callback(self, interaction):

        config = get_config(interaction.guild.id)

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


class ModerationLogChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(
            ModerationLogChannelSelect()
        )


# =========================================================
# LOG SETTINGS
# =========================================================

class LogsSettingsModal(discord.ui.Modal, title="Log Ayarları"):

    delete_input = discord.ui.TextInput(
        label="Silinen mesajlar",
        placeholder="evet / hayır",
        default="evet",
        required=True
    )

    edit_input = discord.ui.TextInput(
        label="Düzenlenen mesajlar",
        placeholder="evet / hayır",
        default="evet",
        required=True
    )

    member_input = discord.ui.TextInput(
        label="Üye giriş/çıkış",
        placeholder="evet / hayır",
        default="evet",
        required=True
    )

    moderation_input = discord.ui.TextInput(
        label="Ban/Kick/Timeout",
        placeholder="evet / hayır",
        default="evet",
        required=True
    )

    async def on_submit(self, interaction):

        config = get_config(interaction.guild.id)

        def yes(value):
            return str(value).lower().strip() in (
                "evet",
                "yes",
                "e",
                "y",
                "true",
                "1"
            )

        config["logs"]["message_delete"] = yes(
            self.delete_input.value
        )

        config["logs"]["message_edit"] = yes(
            self.edit_input.value
        )

        config["logs"]["member_join"] = yes(
            self.member_input.value
        )

        moderation = yes(
            self.moderation_input.value
        )

        config["logs"]["ban"] = moderation
        config["logs"]["kick"] = moderation
        config["logs"]["timeout"] = moderation

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Log ayarları kaydedildi.",
            ephemeral=True
        )


class LogsChannelSelect(discord.ui.ChannelSelect):

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

        config = get_config(interaction.guild.id)

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


class LogsChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(LogsChannelSelect())


# =========================================================
# VOICE SETTINGS
# =========================================================

class VoiceSettingsModal(discord.ui.Modal, title="Ses Kanalı Ayarları"):

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

        config = get_config(interaction.guild.id)

        config["voice"]["join_message"] = str(
            self.join_input.value
        )

        config["voice"]["leave_message"] = str(
            self.leave_input.value
        )

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ses kanalı ayarları kaydedildi.",
            ephemeral=True
        )


class VoiceChannelSelect(discord.ui.ChannelSelect):

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

        config = get_config(interaction.guild.id)

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


class VoiceChannelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(VoiceChannelSelect())


# =========================================================
# SETTINGS MENU
# =========================================================

class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

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
            embed=dynex_embed(
                f"{EMOJIS['support']} Ticket Ayarları",
                "Ticket sisteminin ayarlarını buradan yönet."
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
            embed=dynex_embed(
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
            embed=dynex_embed(
                "👤 Otorol Ayarları",
                "Yeni üyelere verilecek rolü ayarla."
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
            embed=dynex_embed(
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
            embed=dynex_embed(
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
            embed=dynex_embed(
                "🔊 Ses Ayarları",
                "Ses kanalı bildirimlerini buradan yönet."
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
            embed=dynex_embed(
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

        ALL_CONFIG[str(interaction.guild.id)] = (
            deep_copy_default()
        )

        save_config()

        await interaction.response.edit_message(
            content=(
                f"{EMOJIS['yes']} Sunucunun Dynex ayarları "
                "varsayılan değerlere döndürüldü."
            ),
            embed=None,
            view=None
        )


# =========================================================
# TICKET SETTINGS VIEW
# =========================================================

class TicketSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Panel Ayarları",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def panel_settings(
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

        await send_ticket_panel(interaction)

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
            embed=dynex_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            content=None,
            view=SettingsView()
        )


# =========================================================
# WELCOME SETTINGS VIEW
# =========================================================

class WelcomeSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Mesaj Ayarları",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def modal(
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
            embed=dynex_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            content=None,
            view=SettingsView()
        )


# =========================================================
# AUTOROLE SETTINGS VIEW
# =========================================================

class AutoroleSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

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
            content="Yeni üyelere verilecek rolü seç:",
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
            embed=dynex_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            content=None,
            view=SettingsView()
        )


# =========================================================
# MODERATION SETTINGS VIEW
# =========================================================

class ModerationSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

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
    async def log_channel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="Moderasyon log kanalını seç:",
            embed=None,
            view=ModerationLogChannelView()
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
            embed=dynex_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            content=None,
            view=SettingsView()
        )


# =========================================================
# LOG SETTINGS VIEW
# =========================================================

class LogsSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

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
            embed=dynex_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            content=None,
            view=SettingsView()
        )


# =========================================================
# VOICE SETTINGS VIEW
# =========================================================

class VoiceSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

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
            embed=dynex_embed(
                f"{EMOJIS['settings']} Dynex Ayarları",
                "Ayarlarını yönetmek için bir bölüm seç."
            ),
            content=None,
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
@app_commands.default_permissions(administrator=True)
async def settings_command(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komutu kullanmak için yönetici olmalısın.",
            ephemeral=True
        )
        return

    embed = dynex_embed(
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
async def ping_command(interaction):

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

    embed = discord.Embed(
        title=f"{EMOJIS['dynex']} Dynex Bot Ping Durumu",
        description=(
            f"**Gecikme:** `{latency}ms`\n"
            f"**Durum:** {status}"
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# MODERATION COMMANDS
# =========================================================

@bot.tree.command(
    name="ban",
    description="Bir kullanıcıyı yasakla."
)
@app_commands.describe(
    member="Yasaklanacak kullanıcı",
    reason="Sebep"
)
@app_commands.default_permissions(ban_members=True)
async def ban_command(
    interaction,
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

        await member.ban(reason=reason)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {member.mention} yasaklandı."
        )

        config = get_config(interaction.guild.id)

        if config["logs"].get("ban"):
            embed = dynex_embed(
                "🔨 Ban",
                (
                    f"**Kullanıcı:** {member.mention}\n"
                    f"**Yetkili:** {interaction.user.mention}\n"
                    f"**Sebep:** {reason}"
                ),
                0xED4245
            )

            await send_log(
                interaction.guild,
                embed
            )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı yasaklayamıyorum.",
            ephemeral=True
        )


@bot.tree.command(
    name="kick",
    description="Bir kullanıcıyı sunucudan at."
)
@app_commands.describe(
    member="Atılacak kullanıcı",
    reason="Sebep"
)
@app_commands.default_permissions(kick_members=True)
async def kick_command(
    interaction,
    member: discord.Member,
    reason: str = "Belirtilmedi"
):

    try:

        await member.kick(reason=reason)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {member.mention} sunucudan atıldı."
        )

        config = get_config(interaction.guild.id)

        if config["logs"].get("kick"):
            embed = dynex_embed(
                "👢 Kick",
                (
                    f"**Kullanıcı:** {member.mention}\n"
                    f"**Yetkili:** {interaction.user.mention}\n"
                    f"**Sebep:** {reason}"
                ),
                0xFEE75C
            )

            await send_log(
                interaction.guild,
                embed
            )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı atamıyorum.",
            ephemeral=True
        )


@bot.tree.command(
    name="timeout",
    description="Bir kullanıcıyı sustur."
)
@app_commands.describe(
    member="Susturulacak kullanıcı",
    minutes="Dakika",
    reason="Sebep"
)
@app_commands.default_permissions(moderate_members=True)
async def timeout_command(
    interaction,
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

        until = discord.utils.utcnow() + discord.timedelta(
            minutes=minutes
        )

    except AttributeError:

        from datetime import timedelta

        until = discord.utils.utcnow() + timedelta(
            minutes=minutes
        )

    try:

        await member.timeout(
            until,
            reason=reason
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {member.mention} {minutes} dakika susturuldu."
        )

        config = get_config(interaction.guild.id)

        if config["logs"].get("timeout"):

            embed = dynex_embed(
                "🔇 Timeout",
                (
                    f"**Kullanıcı:** {member.mention}\n"
                    f"**Yetkili:** {interaction.user.mention}\n"
                    f"**Süre:** {minutes} dakika\n"
                    f"**Sebep:** {reason}"
                ),
                0x5865F2
            )

            await send_log(
                interaction.guild,
                embed
            )

    except discord.Forbidden:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı susturamıyorum.",
            ephemeral=True
        )


# =========================================================
# MESSAGE MODERATION
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not message.guild:
        await bot.process_commands(message)
        return

    config = get_config(message.guild.id)
    moderation = config["moderation"]

    # Link filtresi
    if moderation.get("anti_link"):

        lower = message.content.lower()

        blocked = (
            "http://",
            "https://",
            "discord.gg/",
            "www."
        )

        if any(item in lower for item in blocked):

            try:
                await message.delete()
            except Exception:
                pass

            if moderation.get("delete_after"):
                try:
                    await message.channel.send(
                        f"{EMOJIS['no']} {message.author.mention}, link paylaşamazsın.",
                        delete_after=5
                    )
                except Exception:
                    pass

            await bot.process_commands(message)
            return

    # Kelime filtresi
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
                f"{EMOJIS['no']} {message.author.mention}, bu kelimeyi kullanamazsın.",
                delete_after=5
            )
        except Exception:
            pass

    await bot.process_commands(message)


# =========================================================
# MESSAGE DELETE LOG
# =========================================================

@bot.event
async def on_message_delete(message):

    if not message.guild:
        return

    if message.author.bot:
        return

    config = get_config(message.guild.id)

    if not config["logs"].get(
        "message_delete",
        True
    ):
        return

    content = message.content or "Mesaj içeriği yok."

    embed = dynex_embed(
        "🗑️ Mesaj Silindi",
        (
            f"**Kullanıcı:** {message.author.mention}\n"
            f"**Kanal:** {message.channel.mention}\n"
            f"**İçerik:** {content[:1500]}"
        ),
        0xED4245
    )

    await send_log(
        message.guild,
        embed
    )


# =========================================================
# MESSAGE EDIT LOG
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

    embed = dynex_embed(
        "✏️ Mesaj Düzenlendi",
        (
            f"**Kullanıcı:** {before.author.mention}\n"
            f"**Kanal:** {before.channel.mention}\n\n"
            f"**Önce:** {before.content[:700]}\n"
            f"**Sonra:** {after.content[:700]}"
        ),
        0xFEE75C
    )

    await send_log(
        before.guild,
        embed
    )

    await bot.process_commands(after)


# =========================================================
# MEMBER JOIN
# =========================================================

@bot.event
async def on_member_join(member):

    config = get_config(
        member.guild.id
    )

    # Autorole
    role_id = config["autorole"].get(
        "role"
    )

    if role_id:

        role = member.guild.get_role(
            int(role_id)
        )

        if role:

            try:
                await member.add_roles(
                    role,
                    reason="Dynex Otorol"
                )
            except Exception:
                pass

    # Welcome
    welcome = config["welcome"]

    channel_id = welcome.get(
        "channel"
    )

    if channel_id:

        channel = member.guild.get_channel(
            int(channel_id)
        )

        if channel:

            embed = discord.Embed(
                title=welcome.get(
                    "title",
                    "Hoş Geldin!"
                ),
                description=replace_variables(
                    welcome.get(
                        "description",
                        ""
                    ),
                    member
                ),
                color=color_from_int(
                    welcome.get(
                        "color",
                        5793266
                    )
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
                    f"**Üye sayısı:** `{member.guild.member_count}`"
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

    # Join log
    if config["logs"].get(
        "member_join",
        True
    ):

        embed = dynex_embed(
            "📥 Üye Katıldı",
            (
                f"**Kullanıcı:** {member.mention}\n"
                f"**ID:** `{member.id}`"
            ),
            0x57F287
        )

        await send_log(
            member.guild,
            embed
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
# MEMBER LEAVE
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

    embed = dynex_embed(
        "📤 Üye Ayrıldı",
        (
            f"**Kullanıcı:** `{member}`\n"
            f"**ID:** `{member.id}`"
        ),
        0xED4245
    )

    await send_log(
        member.guild,
        embed
    )


# =========================================================
# VOICE LOG
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

    channel_id = config["voice"].get(
        "channel"
    )

    if not channel_id:
        return

    text_channel = member.guild.get_channel(
        int(channel_id)
    )

    if not text_channel:
        return

    # Katıldı
    if before.channel is None and after.channel is not None:

        message = replace_variables(
            config["voice"].get(
                "join_message",
                "{member} ses kanalına katıldı."
            ),
            member
        )

        try:
            await text_channel.send(
                f"🔊 {message}\n"
                f"**Kanal:** {after.channel.mention}"
            )
        except Exception:
            pass

    # Ayrıldı
    elif before.channel is not None and after.channel is None:

        message = replace_variables(
            config["voice"].get(
                "leave_message",
                "{member} ses kanalından ayrıldı."
            ),
            member
        )

        try:
            await text_channel.send(
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
        f"Dynex giriş yaptı: {bot.user} ({bot.user.id})"
    )

    try:

        synced = await bot.tree.sync()

        print(
            f"{len(synced)} slash komutu senkronize edildi."
        )

    except Exception as error:

        print(
            f"Slash komut senkronizasyon hatası: {error}"
        )


# =========================================================
# START
# =========================================================

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
