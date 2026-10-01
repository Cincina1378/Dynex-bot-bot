# main.py

import discord
from discord.ext import commands
from discord import app_commands
import os
import json


# =========================================================
# DYNEX EMOJİLERİ
# =========================================================

EVET = "<:Dynexevet:1555263066235605023>"
HAYIR = "<:Dynexhayir:1555265003727102134>"
DYNEX = "<:Dynex:1555263060350996510>"
SERVER = "<:Dynexserver:1555263062112604270>"
KILITLI = "<:Dynexkilitli:1555263063366565918>"
AYARLAR = "<:Ayarlar:1555263064721334282>"
BEKLE = "<:Bekle:1555263067716198701>"
HAKKINDA = "<:Hakknda:1555263069318287464>"
LOADING = "<:Loading:1555263071151325184>"
AKKILITLI = "<:Dynexakkilit:1555263072988434493>"
ALARM = "<:Alarm:1555263612426395739>"
GELISTIRICI = "<:Gelitirici:1555263614783463525>"
TAKVIYE = "<:Takviye:1555263624787005470>"
DORU = "<:Doru:1555263630440923187>"
DISCORD = "<:Discord:1555263704646557816>"
IMG = "<:IMG_4870:1555265003727102134>"


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


# =========================================================
# CONFIG
# =========================================================

def default_config():
    return {
        "ticket_enabled": False,
        "ticket_category": None,

        "music_enabled": True,
        "music_max_volume": 100,
        "music_default_volume": 50,
        "music_auto_leave": True,

        "log_enabled": False,
        "log_channel": None,

        "welcome_enabled": False,
        "welcome_channel": None,
        "welcome_message": "Hoş geldin {user}!",

        "autorole_enabled": False,
        "autorole": None,

        "moderation_enabled": True
    }


def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {}

        return data

    except Exception:
        return {}


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            indent=4,
            ensure_ascii=False
        )


config = load_config()


def get_guild_config(guild_id):
    gid = str(guild_id)

    if gid not in config:
        config[gid] = default_config()
        save_config()

    current = config[gid]
    changed = False

    for key, value in default_config().items():
        if key not in current:
            current[key] = value
            changed = True

    if changed:
        save_config()

    return current


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def is_admin(interaction):
    return (
        interaction.guild is not None
        and interaction.user.guild_permissions.manage_guild
    )


def error_embed(text):
    return discord.Embed(
        description=f"{HAYIR} {text}",
        color=discord.Color.red()
    )


def success_embed(text):
    return discord.Embed(
        description=f"{EVET} {text}",
        color=discord.Color.green()
    )


def info_embed(text):
    return discord.Embed(
        description=f"{DYNEX} {text}",
        color=discord.Color.blurple()
    )


# =========================================================
# MÜZİK PANELİ
# =========================================================

class MusicPanel(discord.ui.View):

    def __init__(self, owner_id):
        super().__init__(timeout=None)

        self.owner_id = owner_id
        self.paused = False
        self.loop_enabled = False

    async def check_owner(self, interaction):

        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu müzik panelini yalnızca paneli açan kişi kullanabilir."
                ),
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="Önceki",
        emoji="⏮️",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_previous"
    )
    async def previous(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        await interaction.response.send_message(
            embed=success_embed(
                "Önceki şarkıya geçildi."
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Oynat / Duraklat",
        emoji="▶️",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_music_pause"
    )
    async def pause(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        self.paused = not self.paused

        if self.paused:
            button.emoji = "▶️"
            text = "Müzik duraklatıldı."
        else:
            button.emoji = "⏸️"
            text = "Müzik devam ettirildi."

        await interaction.response.edit_message(
            view=self
        )

        await interaction.followup.send(
            embed=success_embed(text),
            ephemeral=True
        )

    @discord.ui.button(
        label="Sonraki",
        emoji="⏭️",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_next"
    )
    async def next(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        await interaction.response.send_message(
            embed=success_embed(
                "Sonraki şarkıya geçildi."
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Karıştır",
        emoji="🔀",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_shuffle"
    )
    async def shuffle(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        await interaction.response.send_message(
            embed=success_embed(
                "Müzik kuyruğu karıştırıldı."
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Döngü",
        emoji="🔁",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_loop"
    )
    async def loop_button(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        self.loop_enabled = not self.loop_enabled

        durum = "açıldı" if self.loop_enabled else "kapatıldı"

        await interaction.response.send_message(
            embed=success_embed(
                f"Döngü {durum}."
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Kuyruk",
        emoji="📜",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_queue"
    )
    async def queue(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        await interaction.response.send_message(
            embed=info_embed(
                "Müzik kuyruğu şu anda boş."
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Durdur",
        emoji="⏹️",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_music_stop"
    )
    async def stop(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        await interaction.response.send_message(
            embed=success_embed(
                "Müzik durduruldu."
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Yenile",
        emoji="🔄",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_refresh"
    )
    async def refresh(self, interaction, button):

        if not await self.check_owner(interaction):
            return

        await interaction.response.send_message(
            embed=info_embed(
                "Müzik bilgileri yenilendi."
            ),
            ephemeral=True
        )


# =========================================================
# MÜZİK AYARLARI MODAL
# =========================================================

class MusicSettingsModal(
    discord.ui.Modal,
    title="Müzik Ayarları"
):

    max_volume = discord.ui.TextInput(
        label="Maksimum Ses",
        placeholder="Örnek: 100",
        required=True,
        min_length=1,
        max_length=3
    )

    default_volume = discord.ui.TextInput(
        label="Varsayılan Ses",
        placeholder="Örnek: 50",
        required=True,
        min_length=1,
        max_length=3
    )

    async def on_submit(self, interaction):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        try:
            max_volume = int(self.max_volume.value)
            default_volume = int(self.default_volume.value)

        except ValueError:
            await interaction.response.send_message(
                embed=error_embed(
                    "Ses değerleri yalnızca sayı olabilir."
                ),
                ephemeral=True
            )
            return

        if max_volume < 1 or max_volume > 200:
            await interaction.response.send_message(
                embed=error_embed(
                    "Maksimum ses 1 ile 200 arasında olmalıdır."
                ),
                ephemeral=True
            )
            return

        if default_volume < 0 or default_volume > max_volume:
            await interaction.response.send_message(
                embed=error_embed(
                    f"Varsayılan ses 0 ile {max_volume} arasında olmalıdır."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["music_max_volume"] = max_volume
        guild_config["music_default_volume"] = default_volume

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                f"Müzik ayarları güncellendi.\n\n"
                f"**Maksimum ses:** %{max_volume}\n"
                f"**Varsayılan ses:** %{default_volume}"
            ),
            ephemeral=True
        )


# =========================================================
# KANAL AYARI
# =========================================================

class ChannelModal(
    discord.ui.Modal,
    title="Kanal Ayarı"
):

    channel_id = discord.ui.TextInput(
        label="Kanal ID",
        placeholder="Discord kanal ID'sini yazın",
        required=True,
        min_length=1
    )

    def __init__(self, setting):
        super().__init__()
        self.setting = setting

    async def on_submit(self, interaction):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        try:
            channel_id = int(self.channel_id.value)

        except ValueError:
            await interaction.response.send_message(
                embed=error_embed(
                    "Geçerli bir kanal ID'si girin."
                ),
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ID ile bir kanal bulunamadı."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config[self.setting] = channel.id

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                f"Kanal ayarlandı: {channel.mention}"
            ),
            ephemeral=True
        )


# =========================================================
# ROL AYARI
# =========================================================

class RoleModal(
    discord.ui.Modal,
    title="Oto Rol Ayarı"
):

    role_id = discord.ui.TextInput(
        label="Rol ID",
        placeholder="Discord rol ID'sini yazın",
        required=True,
        min_length=1
    )

    async def on_submit(self, interaction):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        try:
            role_id = int(self.role_id.value)

        except ValueError:
            await interaction.response.send_message(
                embed=error_embed(
                    "Geçerli bir rol ID'si girin."
                ),
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(role_id)

        if role is None:
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ID ile bir rol bulunamadı."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["autorole"] = role.id
        guild_config["autorole_enabled"] = True

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                f"Oto rol ayarlandı: {role.mention}"
            ),
            ephemeral=True
        )


# =========================================================
# KARŞILAMA MESAJI
# =========================================================

class WelcomeModal(
    discord.ui.Modal,
    title="Karşılama Mesajı"
):

    message = discord.ui.TextInput(
        label="Karşılama Mesajı",
        placeholder="Hoş geldin {user}!",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["welcome_message"] = self.message.value
        guild_config["welcome_enabled"] = True

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                "Karşılama mesajı kaydedildi."
            ),
            ephemeral=True
        )


# =========================================================
# AYARLAR PANELİ
# =========================================================

class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    def create_embed(self, guild_config):

        ticket = (
            "Açık"
            if guild_config["ticket_enabled"]
            else "Kapalı"
        )

        music = (
            "Açık"
            if guild_config["music_enabled"]
            else "Kapalı"
        )

        logs = (
            "Açık"
            if guild_config["log_enabled"]
            else "Kapalı"
        )

        welcome = (
            "Açık"
            if guild_config["welcome_enabled"]
            else "Kapalı"
        )

        autorole = (
            "Açık"
            if guild_config["autorole_enabled"]
            else "Kapalı"
        )

        moderation = (
            "Açık"
            if guild_config["moderation_enabled"]
            else "Kapalı"
        )

        embed = discord.Embed(
            title=f"{AYARLAR} Dynex • Sunucu Ayarları",
            description=(
                f"{SERVER} **Sunucu Sistemleri**\n\n"
                f"🎫 **Ticket:** {ticket}\n"
                f"🎵 **Müzik:** {music}\n"
                f"📋 **Log:** {logs}\n"
                f"👋 **Karşılama:** {welcome}\n"
                f"🤖 **Oto Rol:** {autorole}\n"
                f"🛡️ **Moderasyon:** {moderation}\n\n"
                f"🔊 **Maksimum Müzik Sesi:** "
                f"%{guild_config['music_max_volume']}\n"
                f"🔉 **Varsayılan Müzik Sesi:** "
                f"%{guild_config['music_default_volume']}\n\n"
                f"{DYNEX} Ayarları aşağıdaki butonlardan yönetin."
            ),
            color=discord.Color.blurple()
        )

        return embed

    async def update_panel(self, interaction):

        guild_config = get_guild_config(
            interaction.guild.id
        )

        await interaction.response.edit_message(
            embed=self.create_embed(guild_config),
            view=self
        )

    @discord.ui.button(
        label="Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def ticket(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["ticket_enabled"] = not guild_config[
            "ticket_enabled"
        ]

        save_config()

        await self.update_panel(interaction)

    @discord.ui.button(
        label="Müzik",
        emoji="🎵",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def music(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            MusicSettingsModal()
        )

    @discord.ui.button(
        label="Müzik Aç/Kapat",
        emoji="🔊",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def music_toggle(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["music_enabled"] = not guild_config[
            "music_enabled"
        ]

        save_config()

        await self.update_panel(interaction)

    @discord.ui.button(
        label="Log",
        emoji="📋",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def logs(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["log_enabled"] = not guild_config[
            "log_enabled"
        ]

        save_config()

        await self.update_panel(interaction)

    @discord.ui.button(
        label="Log Kanalı",
        emoji="📢",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def log_channel(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            ChannelModal("log_channel")
        )

    @discord.ui.button(
        label="Karşılama",
        emoji="👋",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def welcome(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["welcome_enabled"] = not guild_config[
            "welcome_enabled"
        ]

        save_config()

        await self.update_panel(interaction)

    @discord.ui.button(
        label="Karşılama Kanalı",
        emoji="💬",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def welcome_channel(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            ChannelModal("welcome_channel")
        )

    @discord.ui.button(
        label="Karşılama Mesajı",
        emoji="✏️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def welcome_message(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            WelcomeModal()
        )

    @discord.ui.button(
        label="Oto Rol",
        emoji="🤖",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def autorole(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["autorole_enabled"] = not guild_config[
            "autorole_enabled"
        ]

        save_config()

        await self.update_panel(interaction)

    @discord.ui.button(
        label="Oto Rol Seç",
        emoji="🎭",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def autorole_select(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            RoleModal()
        )

    @discord.ui.button(
        label="Moderasyon",
        emoji="🛡️",
        style=discord.ButtonStyle.primary,
        row=3
    )
    async def moderation(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        guild_config = get_guild_config(
            interaction.guild.id
        )

        guild_config["moderation_enabled"] = not guild_config[
            "moderation_enabled"
        ]

        save_config()

        await self.update_panel(interaction)

    @discord.ui.button(
        label="Ayarları Sıfırla",
        emoji="♻️",
        style=discord.ButtonStyle.danger,
        row=3
    )
    async def reset(self, interaction, button):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        guild_id = str(interaction.guild.id)

        config[guild_id] = default_config()

        save_config()

        await self.update_panel(interaction)


# =========================================================
# ON READY
# =========================================================

@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()

        print(
            f"Dynex aktif: {bot.user}"
        )

        print(
            f"{len(synced)} slash komutu senkronize edildi."
        )

    except Exception as e:
        print(
            f"Slash komut senkronizasyon hatası: {e}"
        )


# =========================================================
# ÜYE KATILDI
# =========================================================

@bot.event
async def on_member_join(member):

    guild_config = get_guild_config(
        member.guild.id
    )

    # OTO ROL

    if guild_config["autorole_enabled"]:

        role_id = guild_config.get("autorole")

        if role_id:

            role = member.guild.get_role(
                role_id
            )

            if role:

                try:
                    await member.add_roles(role)

                except Exception:
                    pass

    # KARŞILAMA

    if guild_config["welcome_enabled"]:

        channel_id = guild_config.get(
            "welcome_channel"
        )

        if channel_id:

            channel = member.guild.get_channel(
                channel_id
            )

            if channel:

                message = guild_config.get(
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
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Sunucunun Dynex ayarlarını yönetir."
)
@app_commands.checks.has_permissions(
    manage_guild=True
)
async def ayarlar(
    interaction: discord.Interaction
):

    guild_config = get_guild_config(
        interaction.guild.id
    )

    view = SettingsView()

    await interaction.response.send_message(
        embed=view.create_embed(guild_config),
        view=view,
        ephemeral=True
    )


# =========================================================
# /MUZIK
# =========================================================

@bot.tree.command(
    name="muzik",
    description="Dynex müzik yönetim panelini açar."
)
async def muzik(
    interaction: discord.Interaction
):

    guild_config = get_guild_config(
        interaction.guild.id
    )

    if not guild_config["music_enabled"]:

        await interaction.response.send_message(
            embed=error_embed(
                "Bu sunucuda müzik sistemi kapalı."
            ),
            ephemeral=True
        )
        return

    if not interaction.user.voice:

        await interaction.response.send_message(
            embed=error_embed(
                "Önce bir ses kanalına girmen gerekiyor."
            ),
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🎵 Dynex • Müzik",
        description=(
            "Müzik yönetim paneli hazır.\n\n"

            "⏮️ **Önceki**\n"
            "▶️ **Oynat / Duraklat**\n"
            "⏭️ **Sonraki**\n"
            "🔀 **Karıştır**\n"
            "🔁 **Döngü**\n"
            "📜 **Kuyruk**\n"
            "⏹️ **Durdur**\n"
            "🔄 **Yenile**\n\n"

            "🔵 **İlerleme:**\n"
            "`0:00 ━━━━━━━━━🔵━━━━━━━━ 0:00`\n\n"

            f"🔊 **Maksimum ses:** "
            f"%{guild_config['music_max_volume']}\n"

            f"🔉 **Varsayılan ses:** "
            f"%{guild_config['music_default_volume']}\n\n"

            f"{KILITLI} Paneli yalnızca açan kişi kontrol edebilir."
        ),
        color=discord.Color.blurple()
    )

    embed.set_footer(
        text=f"Panel sahibi: {interaction.user}"
    )

    await interaction.response.send_message(
        embed=embed,
        view=MusicPanel(
            interaction.user.id
        )
    )


# =========================================================
# /AYARLAR-SIFIRLA
# =========================================================

@bot.tree.command(
    name="ayarlar-sifirla",
    description="Sunucunun Dynex ayarlarını sıfırlar."
)
@app_commands.checks.has_permissions(
    manage_guild=True
)
async def ayarlar_sifirla(
    interaction: discord.Interaction
):

    guild_id = str(
        interaction.guild.id
    )

    config[guild_id] = default_config()

    save_config()

    await interaction.response.send_message(
        embed=success_embed(
            "Dynex sunucu ayarları sıfırlandı."
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
async def ping(
    interaction: discord.Interaction
):

    latency = round(
        bot.latency * 1000
    )

    await interaction.response.send_message(
        embed=info_embed(
            f"**Pong!** `{latency}ms`"
        )
    )


# =========================================================
# HATA YAKALAMA
# =========================================================

@ayarlar.error
async def ayarlar_error(
    interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        if not interaction.response.is_done():

            await interaction.response.send_message(
                embed=error_embed(
                    f"{KILITLI} Bu komutu kullanmak için "
                    "sunucuyu yönetme yetkisine sahip olmalısın."
                ),
                ephemeral=True
            )


@ayarlar_sifirla.error
async def ayarlar_sifirla_error(
    interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        if not interaction.response.is_done():

            await interaction.response.send_message(
                embed=error_embed(
                    f"{KILITLI} Bu komutu kullanmak için "
                    "sunucuyu yönetme yetkisine sahip olmalısın."
                ),
                ephemeral=True
            )


# =========================================================
# TOKEN
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN bulunamadı. "
        "Bot-Hosting ortam değişkenlerine "
        "DISCORD_TOKEN ekleyin."
    )


bot.run(TOKEN)
