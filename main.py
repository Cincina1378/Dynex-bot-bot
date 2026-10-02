import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# TEMEL AYARLAR
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = Path("config.json")

PREFIX = "D."
SUPPORT_SERVER_ID = 1551647711332139098

START_TIME = datetime.now(timezone.utc)


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
# VARSAYILAN AYARLAR
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
# CONFIG SİSTEMİ
# =========================================================

def load_configs():
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


configs = load_configs()


def deep_copy_default():
    return json.loads(json.dumps(DEFAULT_CONFIG))


def merge_config(old, default):
    if isinstance(default, dict):
        result = {}

        for key, value in default.items():
            if key in old:
                result[key] = merge_config(old[key], value)
            else:
                result[key] = deep_copy_value(value)

        for key, value in old.items():
            if key not in result:
                result[key] = value

        return result

    return old if old is not None else deep_copy_value(default)


def deep_copy_value(value):
    return json.loads(json.dumps(value))


def save_configs():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(configs, f, ensure_ascii=False, indent=4)


def get_config(guild_id):
    gid = str(guild_id)

    if gid not in configs:
        configs[gid] = deep_copy_default()
        save_configs()
    else:
        configs[gid] = merge_config(configs[gid], DEFAULT_CONFIG)

    # Eski sürümdeki hazır ticket seçeneklerini temizle.
    old_options = configs[gid]["ticket"].get("options", [])

    if len(old_options) == 2:
        names = {
            str(x.get("name", "")).lower()
            for x in old_options
            if isinstance(x, dict)
        }

        if names == {"destek", "şikayet"}:
            configs[gid]["ticket"]["options"] = []
            save_configs()

    return configs[gid]


# =========================================================
# EMOJİ
# =========================================================

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


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def is_admin(interaction):
    return interaction.user.guild_permissions.administrator


async def admin_only(interaction):
    if not is_admin(interaction):
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu işlem için yönetici yetkisine sahip olmalısın.",
            ephemeral=True
        )
        return False

    return True


def uptime_text():
    elapsed = datetime.now(timezone.utc) - START_TIME

    total = int(elapsed.total_seconds())

    days = total // 86400
    total %= 86400

    hours = total // 3600
    total %= 3600

    minutes = total // 60
    seconds = total % 60

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


def get_user_warning_count(guild_id, user_id):
    config = get_config(guild_id)
    warnings = config["warnings"].get(str(user_id), [])
    return len(warnings)


def add_warning(guild_id, user_id, reason, moderator_id):
    config = get_config(guild_id)

    uid = str(user_id)

    if uid not in config["warnings"]:
        config["warnings"][uid] = []

    config["warnings"][uid].append({
        "reason": reason,
        "moderator": moderator_id,
        "time": datetime.now(timezone.utc).isoformat()
    })

    save_configs()

    return len(config["warnings"][uid])


async def send_log(guild, message, log_type="message"):
    config = get_config(guild.id)

    if not config["logs"].get(log_type, False):
        return

    channel_id = config["logs"].get("channel_id")

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if not channel:
        return

    try:
        await channel.send(message)
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
        self.add_view(TicketCloseView())

        try:
            await self.tree.sync()
            print("Slash komutları senkronize edildi.")
        except Exception as e:
            print("Slash sync hatası:", e)


bot = DynexBot(
    command_prefix=PREFIX,
    intents=intents
)


# =========================================================
# TICKET KAPAT
# =========================================================

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

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
        if not interaction.channel:
            return

        await interaction.response.send_message(
            f"{EMOJIS['locked']} Ticket 5 saniye içinde kapatılıyor."
        )

        await asyncio.sleep(5)

        try:
            await interaction.channel.delete()
        except Exception:
            pass


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=None)

        config = get_config(guild.id)

        for option in config["ticket"]["options"]:
            option_id = option.get("id")
            name = option.get("button") or option.get("name") or "Ticket"
            emoji = parse_emoji(option.get("emoji"), guild)

            button = discord.ui.Button(
                label=name[:80],
                style=discord.ButtonStyle.primary,
                custom_id=f"dynex_ticket_{option_id}",
                emoji=emoji
            )

            async def callback(
                interaction: discord.Interaction,
                option_id=option_id
            ):
                await self.create_ticket(interaction, option_id)

            button.callback = callback
            self.add_item(button)

    async def create_ticket(self, interaction, option_id):
        guild = interaction.guild

        if not guild:
            return

        config = get_config(guild.id)

        option = None

        for item in config["ticket"]["options"]:
            if item.get("id") == option_id:
                option = item
                break

        if not option:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu ticket seçeneği artık mevcut değil.",
                ephemeral=True
            )
            return

        existing = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{interaction.user.id}"
        )

        if existing:
            await interaction.response.send_message(
                f"{EMOJIS['wait']} Zaten açık bir ticketın var: {existing.mention}",
                ephemeral=True
            )
            return

        category = None

        if config["ticket"]["category_id"]:
            category = guild.get_channel(
                config["ticket"]["category_id"]
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        role = None

        if config["ticket"]["role_id"]:
            role = guild.get_role(config["ticket"]["role_id"])

            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

        try:
            channel = await guild.create_text_channel(
                f"ticket-{interaction.user.id}",
                category=category,
                overwrites=overwrites
            )
        except Exception:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Ticket oluşturulamadı. Botun kanal oluşturma yetkisini kontrol et.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=option.get("name", "Ticket"),
            description=(
                f"{interaction.user.mention}, ticketın oluşturuldu.\n\n"
                "Yetkililer en kısa sürede ilgilenecektir."
            ),
            color=discord.Color.blurple()
        )

        await channel.send(
            content=role.mention if role else None,
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket oluşturuldu: {channel.mention}",
            ephemeral=True
        )


# =========================================================
# AYAR MENÜSÜ
# =========================================================

class SettingsSelect(discord.ui.Select):
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
            ),
        ]

        super().__init__(
            placeholder="Bir ayar kategorisi seç...",
            options=options
        )

    async def callback(self, interaction):
        value = self.values[0]

        if value == "ticket":
            await interaction.response.edit_message(
                content=f"{EMOJIS['settings']} **Ticket Ayarları**",
                view=TicketSettingsView()
            )

        elif value == "welcome":
            await interaction.response.edit_message(
                content=f"{EMOJIS['settings']} **Karşılama Ayarları**",
                view=WelcomeSettingsView()
            )

        elif value == "moderation":
            await interaction.response.edit_message(
                content=f"{EMOJIS['settings']} **Moderasyon Ayarları**",
                view=ModerationSettingsView()
            )

        elif value == "logs":
            await interaction.response.edit_message(
                content=f"{EMOJIS['settings']} **Log Ayarları**",
                view=LogsSettingsView()
            )

        elif value == "autorole":
            await interaction.response.edit_message(
                content=f"{EMOJIS['settings']} **Oto Rol Ayarları**",
                view=AutoroleSettingsView()
            )

        elif value == "voice":
            await interaction.response.edit_message(
                content=f"{EMOJIS['settings']} **Ses Ayarları**",
                view=VoiceSettingsView()
            )

        elif value == "giveaway":
            await interaction.response.edit_message(
                content=f"{EMOJIS['settings']} **Çekiliş Ayarları**",
                view=GiveawaySettingsView()
            )


class SettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(SettingsSelect())


# =========================================================
# TICKET AYARLARI
# =========================================================

class TicketSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Kategori", style=discord.ButtonStyle.secondary)
    async def category(self, interaction, button):
        await interaction.response.send_message(
            "Ticket kategorisini seç:",
            view=TicketCategoryView(),
            ephemeral=True
        )

    @discord.ui.button(label="Yetkili Rolü", style=discord.ButtonStyle.secondary)
    async def role(self, interaction, button):
        await interaction.response.send_message(
            "Ticket yetkili rolünü seç:",
            view=TicketRoleView(),
            ephemeral=True
        )

    @discord.ui.button(label="Panel Kanalı", style=discord.ButtonStyle.secondary)
    async def channel(self, interaction, button):
        await interaction.response.send_message(
            "Ticket panel kanalını seç:",
            view=TicketChannelView(),
            ephemeral=True
        )

    @discord.ui.button(label="Panel Bilgileri", style=discord.ButtonStyle.primary)
    async def info(self, interaction, button):
        await interaction.response.send_modal(TicketPanelModal())

    @discord.ui.button(label="Seçenekler", style=discord.ButtonStyle.success)
    async def options(self, interaction, button):
        await interaction.response.edit_message(
            content="**Ticket Seçenekleri**",
            view=TicketOptionsView()
        )

    @discord.ui.button(label="Paneli Gönder", style=discord.ButtonStyle.success)
    async def send_panel(self, interaction, button):
        config = get_config(interaction.guild.id)

        if not config["ticket"]["panel_channel_id"]:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Önce panel kanalını ayarla.",
                ephemeral=True
            )
            return

        if not config["ticket"]["options"]:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Önce en az bir ticket seçeneği eklemelisin.",
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
            embed.set_image(url=config["ticket"]["panel_image"])

        await channel.send(
            embed=embed,
            view=TicketPanelView(interaction.guild)
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket paneli gönderildi.",
            ephemeral=True
        )

    @discord.ui.button(label="Geri", style=discord.ButtonStyle.secondary)
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content=f"{EMOJIS['settings']} **Dynex Ayarları**",
            view=SettingsView()
        )


class TicketCategoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.category],
                placeholder="Ticket kategorisini seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        selected = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["ticket"]["category_id"] = selected.id
        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket kategorisi ayarlandı.",
            ephemeral=True
        )


class TicketRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.RoleSelect(
                placeholder="Ticket yetkili rolünü seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        selected = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["ticket"]["role_id"] = selected.id
        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket yetkili rolü ayarlandı.",
            ephemeral=True
        )


class TicketChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Panel kanalını seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        selected = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["ticket"]["panel_channel_id"] = selected.id
        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket panel kanalı ayarlandı.",
            ephemeral=True
        )


class TicketPanelModal(discord.ui.Modal, title="Ticket Paneli"):
    title_input = discord.ui.TextInput(
        label="Panel başlığı",
        default="Destek Talebi",
        max_length=100
    )

    description_input = discord.ui.TextInput(
        label="Panel açıklaması",
        style=discord.TextStyle.paragraph,
        default="Destek almak için aşağıdaki seçeneklerden birini seç.",
        max_length=1000
    )

    image_input = discord.ui.TextInput(
        label="Görsel URL",
        required=False
    )

    async def on_submit(self, interaction):
        config = get_config(interaction.guild.id)

        config["ticket"]["panel_title"] = str(self.title_input)
        config["ticket"]["panel_description"] = str(self.description_input)
        config["ticket"]["panel_image"] = str(self.image_input)

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket panel bilgileri kaydedildi.",
            ephemeral=True
        )


# =========================================================
# TICKET SEÇENEKLERİ
# =========================================================

class TicketOptionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Seçenek Ekle",
        style=discord.ButtonStyle.success
    )
    async def add_option(self, interaction, button):
        await interaction.response.send_modal(AddTicketOptionModal())

    @discord.ui.button(
        label="Seçenekleri Gör",
        style=discord.ButtonStyle.secondary
    )
    async def show_options(self, interaction, button):
        config = get_config(interaction.guild.id)
        options = config["ticket"]["options"]

        if not options:
            await interaction.response.send_message(
                "Henüz ticket seçeneği eklenmemiş.",
                ephemeral=True
            )
            return

        text = []

        for i, option in enumerate(options, 1):
            emoji = option.get("emoji") or "Yok"

            text.append(
                f"**{i}. {option.get('name', 'İsimsiz')}** "
                f"— Buton: `{option.get('button', '')}` "
                f"— Emoji: `{emoji}`"
            )

        await interaction.response.send_message(
            "\n".join(text),
            ephemeral=True
        )

    @discord.ui.button(
        label="Seçenek Sil",
        style=discord.ButtonStyle.danger
    )
    async def delete_option(self, interaction, button):
        config = get_config(interaction.guild.id)

        if not config["ticket"]["options"]:
            await interaction.response.send_message(
                "Silinecek seçenek yok.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            DeleteTicketOptionModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="**Ticket Ayarları**",
            view=TicketSettingsView()
        )


class AddTicketOptionModal(discord.ui.Modal, title="Ticket Seçeneği Ekle"):
    name_input = discord.ui.TextInput(
        label="Seçenek adı",
        placeholder="Örneğin: Destek",
        max_length=50
    )

    button_input = discord.ui.TextInput(
        label="Buton yazısı",
        placeholder="Örneğin: Destek",
        max_length=50
    )

    emoji_input = discord.ui.TextInput(
        label="Emoji",
        placeholder="🎫 veya :emoji: veya <:isim:id>",
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction):
        if not emoji_exists(
            str(self.emoji_input),
            interaction.guild
        ):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu emoji sunucuda bulunamadı.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        option_id = (
            str(self.name_input)
            .lower()
            .replace(" ", "_")
        )

        option_id = "".join(
            c for c in option_id
            if c.isalnum() or c == "_"
        )

        if not option_id:
            option_id = f"ticket_{len(config['ticket']['options']) + 1}"

        existing_ids = {
            x.get("id")
            for x in config["ticket"]["options"]
        }

        base_id = option_id
        counter = 2

        while option_id in existing_ids:
            option_id = f"{base_id}_{counter}"
            counter += 1

        config["ticket"]["options"].append({
            "id": option_id,
            "name": str(self.name_input),
            "button": str(self.button_input),
            "emoji": str(self.emoji_input)
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
    option_input = discord.ui.TextInput(
        label="Silinecek seçenek",
        placeholder="Seçenek adını yaz"
    )

    async def on_submit(self, interaction):
        config = get_config(interaction.guild.id)

        target = str(self.option_input).lower()

        old = config["ticket"]["options"]

        new = [
            x for x in old
            if str(x.get("name", "")).lower() != target
            and str(x.get("id", "")).lower() != target
        ]

        if len(old) == len(new):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu ticket seçeneği bulunamadı.",
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
# KARŞILAMA AYARLARI
# =========================================================

class WelcomeSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Kanal",
        style=discord.ButtonStyle.secondary
    )
    async def channel(self, interaction, button):
        await interaction.response.send_message(
            "Karşılama kanalını seç:",
            view=WelcomeChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Mesaj",
        style=discord.ButtonStyle.primary
    )
    async def message(self, interaction, button):
        await interaction.response.send_modal(
            WelcomeModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class WelcomeChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Karşılama kanalını seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        channel = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["welcome"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Karşılama kanalı ayarlandı.",
            ephemeral=True
        )


class WelcomeModal(discord.ui.Modal, title="Karşılama Ayarları"):
    title_input = discord.ui.TextInput(
        label="Başlık",
        default="Hoş Geldin!",
        max_length=100
    )

    description_input = discord.ui.TextInput(
        label="Açıklama",
        default="{user}, sunucumuza hoş geldin!",
        max_length=1000
    )

    image_input = discord.ui.TextInput(
        label="Görsel URL",
        required=False
    )

    dm_input = discord.ui.TextInput(
        label="DM mesajı",
        required=False,
        max_length=1000
    )

    async def on_submit(self, interaction):
        config = get_config(interaction.guild.id)

        config["welcome"]["title"] = str(self.title_input)
        config["welcome"]["description"] = str(
            self.description_input
        )
        config["welcome"]["image"] = str(self.image_input)

        dm = str(self.dm_input)

        if dm:
            config["welcome"]["dm_enabled"] = True
            config["welcome"]["dm_message"] = dm
        else:
            config["welcome"]["dm_enabled"] = False
            config["welcome"]["dm_message"] = ""

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Karşılama ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# OTO ROL
# =========================================================

class AutoroleSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Rol Seç",
        style=discord.ButtonStyle.success
    )
    async def role(self, interaction, button):
        await interaction.response.send_message(
            "Oto rolü seç:",
            view=AutoroleRoleView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class AutoroleRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.RoleSelect(
                placeholder="Oto rolü seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        role = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["autorole"]["role_id"] = role.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Oto rol ayarlandı.",
            ephemeral=True
        )


# =========================================================
# MODERASYON
# =========================================================

class ModerationSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Ayarlar",
        style=discord.ButtonStyle.primary
    )
    async def settings(self, interaction, button):
        await interaction.response.send_modal(
            ModerationModal()
        )

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def channel(self, interaction, button):
        await interaction.response.send_message(
            "Moderasyon log kanalını seç:",
            view=ModerationChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class ModerationChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Log kanalını seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        channel = self.children[0].values[0]

        config = get_config(interaction.guild.id)
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
        placeholder="kelime1, kelime2, kelime3",
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
        placeholder="açık / kapalı",
        default="kapalı"
    )

    anti_spam = discord.ui.TextInput(
        label="Anti-spam",
        placeholder="açık / kapalı",
        default="kapalı"
    )

    async def on_submit(self, interaction):
        config = get_config(interaction.guild.id)

        words = [
            x.strip()
            for x in str(self.bad_words).split(",")
            if x.strip()
        ]

        try:
            max_warnings = max(
                1,
                int(str(self.max_warnings))
            )
        except Exception:
            max_warnings = 3

        try:
            timeout = max(
                1,
                int(str(self.timeout_minutes))
            )
        except Exception:
            timeout = 10

        config["moderation"]["bad_words"] = words
        config["moderation"]["max_warnings"] = max_warnings
        config["moderation"]["timeout_minutes"] = timeout

        config["moderation"]["anti_link"] = (
            str(self.anti_link).lower() in
            ["açık", "acik", "evet", "on", "true"]
        )

        config["moderation"]["anti_spam"] = (
            str(self.anti_spam).lower() in
            ["açık", "acik", "evet", "on", "true"]
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Moderasyon ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# LOG AYARLARI
# =========================================================

class LogsSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def channel(self, interaction, button):
        await interaction.response.send_message(
            "Log kanalını seç:",
            view=LogsChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Log Türleri",
        style=discord.ButtonStyle.primary
    )
    async def types(self, interaction, button):
        await interaction.response.send_modal(
            LogsModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class LogsChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Log kanalını seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        channel = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["logs"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Log kanalı ayarlandı.",
            ephemeral=True
        )


class LogsModal(discord.ui.Modal, title="Log Ayarları"):
    message_delete = discord.ui.TextInput(
        label="Mesaj silme",
        default="açık"
    )

    message_edit = discord.ui.TextInput(
        label="Mesaj düzenleme",
        default="açık"
    )

    member_logs = discord.ui.TextInput(
        label="Üye giriş/çıkış",
        default="açık"
    )

    moderation_logs = discord.ui.TextInput(
        label="Ban/Kick/Timeout",
        default="açık"
    )

    async def on_submit(self, interaction):
        config = get_config(interaction.guild.id)

        def enabled(value):
            return str(value).lower() in [
                "açık",
                "acik",
                "evet",
                "on",
                "true"
            ]

        config["logs"]["message_delete"] = enabled(
            self.message_delete
        )

        config["logs"]["message_edit"] = enabled(
            self.message_edit
        )

        config["logs"]["member_join"] = enabled(
            self.member_logs
        )

        config["logs"]["member_leave"] = enabled(
            self.member_logs
        )

        config["logs"]["ban"] = enabled(
            self.moderation_logs
        )

        config["logs"]["kick"] = enabled(
            self.moderation_logs
        )

        config["logs"]["timeout"] = enabled(
            self.moderation_logs
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Log ayarları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# SES AYARLARI
# =========================================================

class VoiceSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Kanal",
        style=discord.ButtonStyle.secondary
    )
    async def channel(self, interaction, button):
        await interaction.response.send_message(
            "Ses bildirim kanalını seç:",
            view=VoiceChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Mesajlar",
        style=discord.ButtonStyle.primary
    )
    async def messages(self, interaction, button):
        await interaction.response.send_modal(
            VoiceModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class VoiceChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Bildirim kanalını seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        channel = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["voice"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ses bildirim kanalı ayarlandı.",
            ephemeral=True
        )


class VoiceModal(discord.ui.Modal, title="Ses Mesajları"):
    join_message = discord.ui.TextInput(
        label="Giriş mesajı",
        default="{user} ses kanalına katıldı."
    )

    leave_message = discord.ui.TextInput(
        label="Çıkış mesajı",
        default="{user} ses kanalından ayrıldı."
    )

    async def on_submit(self, interaction):
        config = get_config(interaction.guild.id)

        config["voice"]["join_message"] = str(
            self.join_message
        )

        config["voice"]["leave_message"] = str(
            self.leave_message
        )

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ses mesajları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# ÇEKİLİŞ AYARLARI
# =========================================================

class GiveawaySettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Yetkili Rolü",
        style=discord.ButtonStyle.secondary
    )
    async def role(self, interaction, button):
        await interaction.response.send_message(
            "Çekiliş yetkili rolünü seç:",
            view=GiveawayRoleView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Çekiliş Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def channel(self, interaction, button):
        await interaction.response.send_message(
            "Çekiliş kanalını seç:",
            view=GiveawayChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Log Kanalı",
        style=discord.ButtonStyle.secondary
    )
    async def log_channel(self, interaction, button):
        await interaction.response.send_message(
            "Çekiliş log kanalını seç:",
            view=GiveawayLogChannelView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Varsayılanlar",
        style=discord.ButtonStyle.primary
    )
    async def defaults(self, interaction, button):
        await interaction.response.send_modal(
            GiveawayDefaultsModal()
        )

    @discord.ui.button(
        label="Geri",
        style=discord.ButtonStyle.secondary
    )
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="**Dynex Ayarları**",
            view=SettingsView()
        )


class GiveawayRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.RoleSelect(
                placeholder="Çekiliş yetkili rolünü seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        role = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["giveaway"]["staff_role_id"] = role.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş yetkili rolü ayarlandı.",
            ephemeral=True
        )


class GiveawayChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Çekiliş kanalını seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        channel = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["giveaway"]["channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş kanalı ayarlandı.",
            ephemeral=True
        )


class GiveawayLogChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.add_item(
            discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Çekiliş log kanalını seç..."
            )
        )

        self.children[0].callback = self.callback

    async def callback(self, interaction):
        channel = self.children[0].values[0]

        config = get_config(interaction.guild.id)
        config["giveaway"]["log_channel_id"] = channel.id

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş log kanalı ayarlandı.",
            ephemeral=True
        )


class GiveawayDefaultsModal(
    discord.ui.Modal,
    title="Çekiliş Varsayılanları"
):
    winners = discord.ui.TextInput(
        label="Varsayılan kazanan sayısı",
        default="1",
        max_length=2
    )

    duration = discord.ui.TextInput(
        label="Varsayılan süre (dakika)",
        default="10",
        max_length=2
    )

    async def on_submit(self, interaction):
        config = get_config(interaction.guild.id)

        try:
            winners = max(1, int(str(self.winners)))
        except Exception:
            winners = 1

        try:
            duration = max(
                1,
                min(40, int(str(self.duration)))
            )
        except Exception:
            duration = 10

        config["giveaway"]["default_winners"] = winners
        config["giveaway"]["default_duration"] = duration

        save_configs()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Çekiliş varsayılanları kaydedildi.",
            ephemeral=True
        )


# =========================================================
# ÇEKİLİŞ SİSTEMİ
# =========================================================

active_giveaways = {}


class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(
        label="Çekilişe Katıl",
        style=discord.ButtonStyle.success,
        custom_id="dynex_giveaway_join"
    )
    async def join(self, interaction, button):
        giveaway = active_giveaways.get(self.giveaway_id)

        if not giveaway:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu çekiliş artık aktif değil.",
                ephemeral=True
            )
            return

        if interaction.user.id in giveaway["participants"]:
            giveaway["participants"].remove(
                interaction.user.id
            )

            await interaction.response.send_message(
                "Çekilişten ayrıldın.",
                ephemeral=True
            )
        else:
            giveaway["participants"].add(
                interaction.user.id
            )

            await interaction.response.send_message(
                f"{EMOJIS['yes']} Çekilişe katıldın!",
                ephemeral=True
            )


async def finish_giveaway(giveaway_id):
    giveaway = active_giveaways.get(giveaway_id)

    if not giveaway:
        return

    await asyncio.sleep(giveaway["duration"])

    giveaway = active_giveaways.get(giveaway_id)

    if not giveaway:
        return

    guild = bot.get_guild(giveaway["guild_id"])

    if not guild:
        active_giveaways.pop(giveaway_id, None)
        return

    channel = guild.get_channel(
        giveaway["channel_id"]
    )

    if not channel:
        active_giveaways.pop(giveaway_id, None)
        return

    participants = list(
        giveaway["participants"]
    )

    if not participants:
        await channel.send(
            f"{EMOJIS['no']} Çekiliş bitti fakat katılımcı yoktu."
        )

        active_giveaways.pop(giveaway_id, None)
        return

    import random

    count = min(
        giveaway["winners"],
        len(participants)
    )

    winners = random.sample(
        participants,
        count
    )

    mentions = " ".join(
        f"<@{user_id}>"
        for user_id in winners
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

    log_channel_id = get_config(
        guild.id
    )["giveaway"]["log_channel_id"]

    if log_channel_id:
        log_channel = guild.get_channel(
            log_channel_id
        )

        if log_channel:
            await log_channel.send(
                f"🎉 Çekiliş bitti.\n"
                f"Ödül: **{giveaway['prize']}**\n"
                f"Kazananlar: {mentions}"
            )

    active_giveaways.pop(
        giveaway_id,
        None
    )


# =========================================================
# SLASH: AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönet."
)
@app_commands.default_permissions(administrator=True)
async def ayarlar(interaction):
    if not await admin_only(interaction):
        return

    await interaction.response.send_message(
        f"{EMOJIS['settings']} **Dynex Ayarları**\n"
        "Aşağıdan ayarlamak istediğin sistemi seç.",
        view=SettingsView(),
        ephemeral=True
    )


# =========================================================
# SLASH: DİL
# =========================================================

class LanguageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

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

        async def callback(interaction):
            config = get_config(interaction.guild.id)
            config["language"] = select.values[0]

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
async def dil(interaction):
    if not await admin_only(interaction):
        return

    await interaction.response.send_message(
        "Dil seç:",
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# SLASH: BOT
# =========================================================

@bot.tree.command(
    name="bot",
    description="Dynex botunun mevcut durumunu gösterir."
)
async def bot_status(interaction):
    support_guild = bot.get_guild(
        SUPPORT_SERVER_ID
    )

    if support_guild:
        support_members = support_guild.member_count
    else:
        support_members = "Bilinmiyor"

    embed = discord.Embed(
        title="Dynex Durum",
        color=discord.Color.black()
    )

    embed.description = (
        f"**Sunucu sayısı:** {len(bot.guilds)}\n\n"
        f"**Destek sunucusu üye sayısı:** {support_members}\n\n"
        f"**Prefix yani . Komut:** `{PREFIX}`\n\n"
        f"**Aktif kalma süresi:** {uptime_text()}"
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# SLASH: PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Dynex bağlantı durumunu gösterir."
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
        title="İttifak Ordusu Botunun Ping(internet) Durumu",
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
# SLASH: SUNUCU
# =========================================================

@bot.tree.command(
    name="sunucu",
    description="Sunucu bilgilerini gösterir."
)
async def server_info(interaction):
    guild = interaction.guild

    if not guild:
        return

    embed = discord.Embed(
        title=f"{guild.name}",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Sunucu ID",
        value=str(guild.id),
        inline=False
    )

    embed.add_field(
        name="Üye sayısı",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="Kanal sayısı",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="Rol sayısı",
        value=str(len(guild.roles)),
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
# SLASH: KULLANICI
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
        value=str(user.id),
        inline=False
    )

    embed.add_field(
        name="Hesap",
        value=discord.utils.format_dt(
            user.created_at,
            "F"
        ),
        inline=False
    )

    if isinstance(user, discord.Member):
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
# SLASH: AVATAR
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
# SLASH: TEMİZLE
# =========================================================

@bot.tree.command(
    name="temizle",
    description="Belirtilen miktarda mesaj siler."
)
@app_commands.describe(
    miktar="Silinecek mesaj miktarı."
)
@app_commands.default_permissions(manage_messages=True)
async def temizle(
    interaction,
    miktar: app_commands.Range[int, 1, 100]
):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Mesajları yönet yetkin yok.",
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
        f"{EMOJIS['yes']} **{len(deleted)}** mesaj silindi.",
        ephemeral=True
    )


# =========================================================
# SLASH: BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Kullanıcıyı sunucudan yasaklar."
)
@app_commands.describe(
    kullanıcı="Yasaklanacak kullanıcı.",
    sebep="Yasaklama sebebi."
)
@app_commands.default_permissions(ban_members=True)
async def ban(
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

    if kullanıcı == interaction.user:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kendini banlayamazsın.",
            ephemeral=True
        )
        return

    try:
        await kullanıcı.ban(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} yasaklandı.\n"
            f"**Sebep:** {sebep}"
        )

        await send_log(
            interaction.guild,
            f"🔨 {kullanıcı} banlandı.\nSebep: {sebep}",
            "ban"
        )

    except Exception:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kullanıcı banlanamadı.",
            ephemeral=True
        )


# =========================================================
# SLASH: KICK
# =========================================================

@bot.tree.command(
    name="kick",
    description="Kullanıcıyı sunucudan atar."
)
@app_commands.describe(
    kullanıcı="Atılacak kullanıcı.",
    sebep="Atılma sebebi."
)
@app_commands.default_permissions(kick_members=True)
async def kick(
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
        await kullanıcı.kick(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} sunucudan atıldı.\n"
            f"**Sebep:** {sebep}"
        )

        await send_log(
            interaction.guild,
            f"👢 {kullanıcı} kicklendi.\nSebep: {sebep}",
            "kick"
        )

    except Exception:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Kullanıcı kicklenemedi.",
            ephemeral=True
        )


# =========================================================
# SLASH: TIMEOUT
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
@app_commands.default_permissions(moderate_members=True)
async def timeout(
    interaction,
    kullanıcı: discord.Member,
    dakika: app_commands.Range[int, 1, 40320],
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
            timedelta(minutes=dakika),
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} "
            f"**{dakika} dakika** timeout aldı.\n"
            f"**Sebep:** {sebep}"
        )

        await send_log(
            interaction.guild,
            f"⏱️ {kullanıcı} timeout aldı.\n"
            f"Süre: {dakika} dakika\n"
            f"Sebep: {sebep}",
            "timeout"
        )

    except Exception:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Timeout verilemedi.",
            ephemeral=True
        )


# =========================================================
# SLASH: UYAR
# =========================================================

@bot.tree.command(
    name="uyar",
    description="Kullanıcıya uyarı verir."
)
@app_commands.describe(
    kullanıcı="Uyarılacak kullanıcı.",
    sebep="Uyarı sebebi."
)
@app_commands.default_permissions(moderate_members=True)
async def warn(
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

    count = add_warning(
        interaction.guild.id,
        kullanıcı.id,
        sebep,
        interaction.user.id
    )

    config = get_config(
        interaction.guild.id
    )

    limit = config["moderation"]["max_warnings"]

    await interaction.response.send_message(
        f"{EMOJIS['yes']} {kullanıcı.mention} uyarıldı.\n"
        f"**Sebep:** {sebep}\n"
        f"**Uyarı:** `{count}/{limit}`"
    )

    if count >= limit:
        action = config["moderation"]["warning_action"]

        if action == "timeout":
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
# SLASH: UYARILAR
# =========================================================

@bot.tree.command(
    name="uyarılar",
    description="Kullanıcının uyarılarını gösterir."
)
@app_commands.describe(
    kullanıcı="Uyarıları gösterilecek kullanıcı."
)
async def warnings(
    interaction,
    kullanıcı: discord.Member = None
):
    user = kullanıcı or interaction.user

    config = get_config(
        interaction.guild.id
    )

    data = config["warnings"].get(
        str(user.id),
        []
    )

    if not data:
        await interaction.response.send_message(
            f"{EMOJIS['correct']} {user.mention} için kayıtlı uyarı yok.",
            ephemeral=True
        )
        return

    lines = []

    for i, warning in enumerate(data[-10:], 1):
        lines.append(
            f"**{i}.** {warning['reason']}"
        )

    embed = discord.Embed(
        title=f"{user.display_name} Uyarıları",
        description="\n".join(lines),
        color=discord.Color.orange()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# SLASH: ÇEKİLİŞ
# =========================================================

@bot.tree.command(
    name="çekiliş",
    description="Yeni bir çekiliş başlatır."
)
@app_commands.describe(
    ödül="Çekiliş ödülü.",
    kazanan="Kazanan sayısı.",
    süre="Süre, dakika cinsinden. En fazla 40."
)
async def giveaway(
    interaction,
    ödül: str,
    kazanan: app_commands.Range[int, 1, 20],
    süre: app_commands.Range[int, 1, 40]
):
    config = get_config(
        interaction.guild.id
    )

    staff_role_id = config["giveaway"]["staff_role_id"]

    if staff_role_id:
        role = interaction.guild.get_role(
            staff_role_id
        )

        if role and role not in interaction.user.roles:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu komutu kullanmak için "
                f"{role.mention} rolüne sahip olmalısın.",
                ephemeral=True
            )
            return

    if not staff_role_id:
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Çekiliş yetkili rolü ayarlanmamış.",
                ephemeral=True
            )
            return

    channel = interaction.channel

    if config["giveaway"]["channel_id"]:
        configured_channel = interaction.guild.get_channel(
            config["giveaway"]["channel_id"]
        )

        if configured_channel:
            channel = configured_channel

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
            f"**Kazanan:** {kazanan} kişi\n"
            f"**Süre:** {süre} dakika\n\n"
            "Katılmak için aşağıdaki butona bas!"
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Çekiliş oluşturuldu.",
        ephemeral=True
    )

    await channel.send(
        embed=embed,
        view=GiveawayView(giveaway_id)
    )

    asyncio.create_task(
        finish_giveaway(giveaway_id)
    )


# =========================================================
# SLASH: ÇEKİLİŞ BİTİR
# =========================================================

@bot.tree.command(
    name="çekiliş-bitir",
    description="Aktif çekilişi bitirir."
)
async def giveaway_end(interaction):
    config = get_config(
        interaction.guild.id
    )

    staff_role_id = config["giveaway"]["staff_role_id"]

    if staff_role_id:
        role = interaction.guild.get_role(
            staff_role_id
        )

        if role and role not in interaction.user.roles:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Çekiliş yetkin yok.",
                ephemeral=True
            )
            return

    found = None

    for gid, data in active_giveaways.items():
        if data["guild_id"] == interaction.guild.id:
            found = gid
            break

    if not found:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Aktif çekiliş bulunamadı.",
            ephemeral=True
        )
        return

    data = active_giveaways[found]

    import random

    participants = list(
        data["participants"]
    )

    if not participants:
        active_giveaways.pop(found, None)

        await interaction.response.send_message(
            f"{EMOJIS['no']} Çekilişte katılımcı yoktu."
        )
        return

    winners_count = min(
        data["winners"],
        len(participants)
    )

    winners = random.sample(
        participants,
        winners_count
    )

    mentions = " ".join(
        f"<@{x}>"
        for x in winners
    )

    active_giveaways.pop(
        found,
        None
    )

    await interaction.response.send_message(
        f"🎉 Çekiliş bitti!\n\n"
        f"**Ödül:** {data['prize']}\n"
        f"**Kazananlar:** {mentions}"
    )


# =========================================================
# SLASH: DUYURU
# =========================================================

class AnnouncementModal(
    discord.ui.Modal,
    title="Duyuru"
):
    title_input = discord.ui.TextInput(
        label="Başlık",
        max_length=100
    )

    description_input = discord.ui.TextInput(
        label="Açıklama",
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    async def on_submit(self, interaction):
        embed = discord.Embed(
            title=str(self.title_input),
            description=str(self.description_input),
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
@app_commands.default_permissions(manage_messages=True)
async def duyuru(interaction):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu işlem için yetkin yok.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(
        AnnouncementModal()
    )


# =========================================================
# SLASH: ROLLER
# =========================================================

@bot.tree.command(
    name="roller",
    description="Sunucudaki rolleri listeler."
)
async def roller(interaction):
    roles = [
        role for role in interaction.guild.roles
        if role != interaction.guild.default_role
    ]

    roles.reverse()

    if not roles:
        await interaction.response.send_message(
            "Sunucuda rol bulunmuyor."
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
# EVENT: READY
# =========================================================

@bot.event
async def on_ready():
    print(
        f"Dynex aktif: {bot.user} "
        f"| {len(bot.guilds)} sunucu"
    )


# =========================================================
# EVENT: ÜYE GİRİŞ
# =========================================================

@bot.event
async def on_member_join(member):
    config = get_config(
        member.guild.id
    )

    # Oto rol
    role_id = config["autorole"]["role_id"]

    if role_id:
        role = member.guild.get_role(role_id)

        if role:
            try:
                await member.add_roles(role)
            except Exception:
                pass

    # Karşılama
    welcome = config["welcome"]

    channel_id = welcome["channel_id"]

    if channel_id:
        channel = member.guild.get_channel(
            channel_id
        )

        if channel:
            description = welcome["description"]

            description = description.replace(
                "{user}",
                member.mention
            )

            description = description.replace(
                "{username}",
                member.display_name
            )

            embed = discord.Embed(
                title=welcome["title"],
                description=description,
                color=discord.Color.green()
            )

            if welcome["image"]:
                embed.set_image(
                    url=welcome["image"]
                )

            try:
                await channel.send(
                    embed=embed
                )
            except Exception:
                pass

    # DM
    if welcome["dm_enabled"] and welcome["dm_message"]:
        try:
            message = welcome["dm_message"].replace(
                "{user}",
                member.mention
            )

            await member.send(message)
        except Exception:
            pass

    await send_log(
        member.guild,
        f"📥 {member.mention} sunucuya katıldı.",
        "member_join"
    )


# =========================================================
# EVENT: ÜYE ÇIKIŞ
# =========================================================

@bot.event
async def on_member_remove(member):
    await send_log(
        member.guild,
        f"📤 **{member}** sunucudan ayrıldı.",
        "member_leave"
    )


# =========================================================
# EVENT: MESAJ
# =========================================================

spam_cache = {}


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.guild:
        return

    config = get_config(
        message.guild.id
    )

    content = message.content.lower()

    # Yasaklı kelime
    for word in config["moderation"]["bad_words"]:
        if word.lower() in content:
            try:
                await message.delete()
            except Exception:
                pass

            count = add_warning(
                message.guild.id,
                message.author.id,
                "Yasaklı kelime kullanımı.",
                bot.user.id
            )

            try:
                await message.channel.send(
                    f"{EMOJIS['no']} {message.author.mention} "
                    "yasaklı kelime kullanamazsın.",
                    delete_after=5
                )
            except Exception:
                pass

            if count >= config["moderation"]["max_warnings"]:
                try:
                    await message.author.timeout(
                        timedelta(
                            minutes=config["moderation"]["timeout_minutes"]
                        ),
                        reason="Uyarı limiti doldu."
                    )
                except Exception:
                    pass

            break

    # Anti-link
    if config["moderation"]["anti_link"]:
        links = [
            "http://",
            "https://",
            "discord.gg/",
            "www."
        ]

        if any(x in content for x in links):
            if not message.author.guild_permissions.manage_messages:
                try:
                    await message.delete()
                except Exception:
                    pass

                try:
                    await message.channel.send(
                        f"{EMOJIS['no']} {message.author.mention} "
                        "link göndermek yasak.",
                        delete_after=5
                    )
                except Exception:
                    pass

    # Basit anti-spam
    if config["moderation"]["anti_spam"]:
        now = datetime.now(
            timezone.utc
        ).timestamp()

        key = (
            message.guild.id,
            message.author.id
        )

        if key not in spam_cache:
            spam_cache[key] = []

        spam_cache[key].append(now)

        spam_cache[key] = [
            x for x in spam_cache[key]
            if now - x <= 5
        ]

        if len(spam_cache[key]) >= 6:
            try:
                await message.author.timeout(
                    timedelta(minutes=1),
                    reason="Anti-spam"
                )
            except Exception:
                pass

            spam_cache[key] = []

    await bot.process_commands(message)


# =========================================================
# EVENT: MESAJ SİLME
# =========================================================

@bot.event
async def on_message_delete(message):
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
# EVENT: MESAJ DÜZENLEME
# =========================================================

@bot.event
async def on_message_edit(before, after):
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
# EVENT: SES
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

    text_channel = member.guild.get_channel(
        channel_id
    )

    if not text_channel:
        return

    if before.channel is None and after.channel:
        message = config["voice"]["join_message"]
        message = message.replace(
            "{user}",
            member.mention
        )

        try:
            await text_channel.send(message)
        except Exception:
            pass

    elif before.channel and after.channel is None:
        message = config["voice"]["leave_message"]
        message = message.replace(
            "{user}",
            member.mention
        )

        try:
            await text_channel.send(message)
        except Exception:
            pass


# =========================================================
# HATA YAKALAMA
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction,
    error
):
    print("Slash komut hatası:", repr(error))

    try:
        if interaction.response.is_done():
            await interaction.followup.send(
                f"{EMOJIS['no']} Komut çalıştırılırken bir hata oluştu.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"{EMOJIS['no']} Komut çalıştırılırken bir hata oluştu.",
                ephemeral=True
            )
    except Exception:
        pass


# =========================================================
# BAŞLAT
# =========================================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
