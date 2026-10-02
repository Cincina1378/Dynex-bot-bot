# =========================================================
# DYNEX DISCORD BOT - main.py
# Python 3.14
# discord.py
# =========================================================

import os
import json
import random
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
    "lock": "<:Dynexkilitli:1555263063366565918>",
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
    "language": {},

    "ticket": {
        "category_id": None,
        "staff_role_id": None,
        "panel_channel_id": None,
        "panel_title": "Destek Sistemi",
        "panel_description": "Destek talebi oluşturmak için aşağıdaki butonlardan birine basın.",
        "panel_image": "",
        "options": []
    },

    "welcome": {
        "channel_id": None,
        "title": "Hoş Geldin!",
        "description": "{member}, sunucumuza hoş geldin!",
        "image": "",
        "dm": ""
    },

    "autorole": {
        "role_id": None
    },

    "moderation": {
        "bad_words": [],
        "warning_limit": 3,
        "warning_action": "timeout",
        "timeout_minutes": 10,
        "anti_link": False,
        "anti_spam": False,
        "log_channel_id": None
    },

    "logs": {
        "channel_id": None,
        "delete": True,
        "edit": True,
        "join": True,
        "leave": True,
        "ban": True,
        "kick": True,
        "timeout": True
    },

    "voice": {
        "channel_id": None,
        "join_message": "{member} ses kanalına katıldı.",
        "leave_message": "{member} ses kanalından ayrıldı."
    },

    "giveaway": {
        "staff_role_id": None,
        "channel_id": None,
        "log_channel_id": None,
        "default_winners": 1,
        "default_duration": 10
    },

    "fun": {
        "number_channel_id": None,
        "number_min": 1,
        "number_max": 100,

        "word_channel_id": None,
        "word_words": [
            "elma",
            "kitap",
            "kalem",
            "okul",
            "bilgisayar",
            "discord",
            "sunucu",
            "oyun",
            "telefon",
            "araba"
        ]
    },

    "dm": {
        "allowed_role_ids": []
    },

    "warnings": {},
    "giveaways": {}
}


# =========================================================
# CONFIG
# =========================================================

def deep_merge(default, current):
    if isinstance(default, dict) and isinstance(current, dict):
        result = {}

        for key, value in default.items():
            if key in current:
                result[key] = deep_merge(
                    value,
                    current[key]
                )
            else:
                result[key] = value

        for key, value in current.items():
            if key not in result:
                result[key] = value

        return result

    return current


def load_config():
    try:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(
                json.dumps(
                    DEFAULT_CONFIG,
                    ensure_ascii=False,
                    indent=4
                ),
                encoding="utf-8"
            )

            return json.loads(
                json.dumps(DEFAULT_CONFIG)
            )

        data = json.loads(
            CONFIG_FILE.read_text(
                encoding="utf-8"
            )
        )

        config = deep_merge(
            DEFAULT_CONFIG,
            data
        )

        old_options = [
            {
                "name": "Destek",
                "emoji": "🎫"
            },
            {
                "name": "Şikayet",
                "emoji": "⚠️"
            }
        ]

        if config.get("ticket", {}).get("options") == old_options:
            config["ticket"]["options"] = []

        return config

    except Exception as e:
        print("Config yükleme hatası:", repr(e))

        return json.loads(
            json.dumps(DEFAULT_CONFIG)
        )


CONFIG = load_config()


def save_config():
    try:
        CONFIG_FILE.write_text(
            json.dumps(
                CONFIG,
                ensure_ascii=False,
                indent=4
            ),
            encoding="utf-8"
        )
    except Exception as e:
        print("Config kayıt hatası:", repr(e))


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def uptime_text():
    delta = datetime.now(timezone.utc) - START_TIME

    days = delta.days
    hours, remainder = divmod(
        delta.seconds,
        3600
    )
    minutes, seconds = divmod(
        remainder,
        60
    )

    parts = []

    if days:
        parts.append(f"{days}g")

    if hours:
        parts.append(f"{hours}s")

    if minutes:
        parts.append(f"{minutes}dk")

    parts.append(f"{seconds}sn")

    return " ".join(parts)


def parse_emoji(value, guild):
    if not value:
        return None

    value = str(value).strip()

    if value.startswith("<:") or value.startswith("<a:"):
        try:
            emoji = discord.PartialEmoji.from_str(
                value
            )

            if emoji.id:
                return emoji

        except Exception:
            return None

    if value.startswith(":") and value.endswith(":"):
        if guild is None:
            return None

        name = value[1:-1].strip()

        return discord.utils.get(
            guild.emojis,
            name=name
        )

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


async def send_log(guild, message):
    if guild is None:
        return

    channel_id = CONFIG.get(
        "logs",
        {}
    ).get(
        "channel_id"
    )

    if not channel_id:
        channel_id = CONFIG.get(
            "moderation",
            {}
        ).get(
            "log_channel_id"
        )

    if not channel_id:
        return

    channel = guild.get_channel(
        channel_id
    )

    if channel is None:
        return

    try:
        await channel.send(
            message
        )
    except Exception as e:
        print(
            "Log gönderme hatası:",
            repr(e)
        )


def has_dm_permission(interaction):
    if interaction.user.guild_permissions.administrator:
        return True

    allowed_roles = CONFIG.get(
        "dm",
        {}
    ).get(
        "allowed_role_ids",
        []
    )

    user_role_ids = {
        role.id
        for role in interaction.user.roles
    }

    return any(
        role_id in user_role_ids
        for role_id in allowed_roles
    )


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True
intents.messages = True
intents.voice_states = True


# =========================================================
# BOT
# =========================================================

class DynexBot(commands.Bot):

    async def setup_hook(self):

        try:
            self.add_view(
                TicketCloseView()
            )
        except Exception as e:
            print(
                "Ticket view hatası:",
                repr(e)
            )

        try:
            synced = await self.tree.sync()

            print(
                f"{len(synced)} slash komutu senkronize edildi."
            )

        except Exception as e:
            print(
                "Slash sync hatası:",
                repr(e)
            )


bot = DynexBot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# =========================================================
# TICKET
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
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not isinstance(
            interaction.channel,
            discord.TextChannel
        ):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu işlem ticket kanalında kullanılabilir.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket kapatılıyor...",
            ephemeral=True
        )

        await asyncio.sleep(1)

        try:
            await interaction.channel.delete()
        except Exception as e:
            print(
                "Ticket kapatma hatası:",
                repr(e)
            )


# =========================================================
# /BOT
# =========================================================

@bot.tree.command(
    name="bot",
    description="Dynex botunun mevcut durumunu gösterir."
)
async def bot_status(
    interaction: discord.Interaction
):

    try:

        guild_count = len(
            bot.guilds
        )

        support_guild = bot.get_guild(
            SUPPORT_SERVER_ID
        )

        if support_guild:

            support_members = (
                support_guild.member_count
            )

            if support_members is None:
                support_members = len(
                    support_guild.members
                )

        else:
            support_members = "Bilinmiyor"

        owner_text = "Bilinmiyor"

        try:
            app_info = await bot.application_info()

            if app_info.owner:
                owner_text = (
                    app_info.owner.mention
                )

        except Exception as e:
            print(
                "Bot sahibi alınamadı:",
                repr(e)
            )

        embed = discord.Embed(
            title="Dynex Durum",
            color=discord.Color.from_rgb(
                0,
                0,
                0
            )
        )

        embed.description = (
            f"**Sunucu sayısı:** `{guild_count}`\n\n"
            f"**Destek sunucusu üye sayısı:** "
            f"`{support_members}`\n\n"
            f"**Prefix yani . Komut:** `{PREFIX}`\n\n"
            f"**Aktif kalma süresi:** "
            f"`{uptime_text()}`\n\n"
            f"**Bot sahibi:** {owner_text}"
        )

        await interaction.response.send_message(
            embed=embed
        )

    except Exception as e:

        print(
            "/bot hatası:",
            repr(e)
        )

        if not interaction.response.is_done():

            await interaction.response.send_message(
                f"{EMOJIS['no']} Bot bilgileri alınırken hata oluştu.",
                ephemeral=True
            )

        else:

            await interaction.followup.send(
                f"{EMOJIS['no']} Bot bilgileri alınırken hata oluştu.",
                ephemeral=True
            )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun gecikmesini gösterir."
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

    status_emojis = {
        "Mükemmel": "<:Dynexevet:1555263066235605023>",
        "İyi": "<:Dynexevet:1555263066235605023>",
        "Orta": "<:Bekle:1555263067716198701>",
        "Zayıf": "<:Dynexhayir:1555265003727102134>",
        "Berbat": "<:Dynexhayir:1555265003727102134>"
    }

    embed = discord.Embed(
        title="Dynex Ping Durumu",
        description=(
            f"**Gecikme:** `{latency} ms`\n\n"
            f"**Durum:** "
            f"{status_emojis[status]} `{status}`"
        ),
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /YARDIM
# =========================================================

class HelpSelect(discord.ui.Select):

    def __init__(self):

        options = [
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
                label="Eğlence",
                value="fun",
                emoji="🎮"
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
                emoji="⚙️"
            )
        ]

        super().__init__(
            placeholder="Bir kategori seçin...",
            options=options,
            custom_id="dynex_help_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        category = self.values[0]

        texts = {

            "general": (
                "**Genel Komutlar**\n\n"
                "`/bot`\n"
                "`/yardım`\n"
                "`/ping`\n"
                "`/kullanıcı`\n"
                "`/avatar`\n"
                "`/sunucu`\n"
                "`/roller`"
            ),

            "moderation": (
                "**Moderasyon Komutları**\n\n"
                "`/uyar`\n"
                "`/uyarılar`\n"
                "`/timeout`\n"
                "`/kick`\n"
                "`/ban`\n"
                "`/temizle`\n"
                "`/sil`\n"
                "`/kilitle`\n"
                "`/kilit-aç`\n"
                "`/yavaş-mod`"
            ),

            "fun": (
                "**Eğlence Komutları**\n\n"
                "`/sayı-oyunu-ayarla`\n"
                "`/sayı-oyunu-durdur`\n"
                "`/kelime-oyunu-ayarla`\n"
                "`/kelime-oyunu-durdur`\n"
                "`/kelime-ekle`\n"
                "`/kelime-çıkar`\n"
                "`/zar`\n"
                "`/yazı-tura`\n"
                "`/8ball`\n"
                "`/sayı-tahmin`"
            ),

            "ticket": (
                "**Ticket**\n\n"
                "`/ayarlar` → Ticket"
            ),

            "giveaway": (
                "**Çekiliş**\n\n"
                "`/çekiliş`\n"
                "`/çekiliş-bitir`"
            ),

            "server": (
                "**Sunucu**\n\n"
                "`/sunucu`\n"
                "`/roller`\n"
                "`/ayarlar`\n"
                "`/dil`\n"
                "`/dm`"
            )
        }

        embed = discord.Embed(
            title="Dynex Yardım",
            description=texts.get(
                category,
                "Kategori bulunamadı."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self.view
        )


class HelpView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=180
        )

        self.add_item(
            HelpSelect()
        )


@bot.tree.command(
    name="yardım",
    description="Dynex komutlarını gösterir."
)
async def yardim(
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="Dynex Yardım",
        description=(
            "Bir kategori seçerek komutları görüntüleyebilirsin."
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=HelpView()
    )


# =========================================================
# /SUNUCU
# =========================================================

@bot.tree.command(
    name="sunucu",
    description="Sunucu bilgilerini gösterir."
)
async def sunucu(
    interaction: discord.Interaction
):

    guild = interaction.guild

    if guild is None:
        return

    embed = discord.Embed(
        title=f"{guild.name} Sunucu Bilgileri",
        color=discord.Color.blurple()
    )

    owner = guild.owner

    embed.add_field(
        name="Sunucu sahibi",
        value=(
            owner.mention
            if owner
            else "Bilinmiyor"
        ),
        inline=False
    )

    embed.add_field(
        name="Üye sayısı",
        value=str(
            guild.member_count
        ),
        inline=True
    )

    embed.add_field(
        name="Kanal sayısı",
        value=str(
            len(guild.channels)
        ),
        inline=True
    )

    embed.add_field(
        name="Rol sayısı",
        value=str(
            len(guild.roles)
        ),
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
    kullanıcı="Bilgilerini görmek istediğin kullanıcı."
)
async def kullanici(
    interaction: discord.Interaction,
    kullanıcı: discord.Member | None = None
):

    member = (
        kullanıcı
        or interaction.user
    )

    embed = discord.Embed(
        title="Kullanıcı Bilgileri",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    description = (
        f"**Kullanıcı:** {member.mention}\n\n"
        f"**ID:** `{member.id}`\n\n"
        f"**Hesap oluşturma:** "
        f"<t:{int(member.created_at.timestamp())}:F>"
    )

    if member.joined_at:
        description += (
            f"\n\n**Sunucuya katılma:** "
            f"<t:{int(member.joined_at.timestamp())}:F>"
        )

    embed.description = description

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
    kullanıcı="Avatarını görmek istediğin kullanıcı."
)
async def avatar(
    interaction: discord.Interaction,
    kullanıcı: discord.Member | None = None
):

    member = (
        kullanıcı
        or interaction.user
    )

    embed = discord.Embed(
        title=f"{member.display_name} Avatar",
        color=discord.Color.blurple()
    )

    embed.set_image(
        url=member.display_avatar.url
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
async def roller(
    interaction: discord.Interaction
):

    guild = interaction.guild

    if guild is None:
        return

    roles = [
        role.mention
        for role in reversed(
            guild.roles
        )
        if role != guild.default_role
    ]

    description = (
        "\n".join(roles)
        if roles
        else "Sunucuda rol bulunmuyor."
    )

    if len(description) > 4000:
        description = (
            description[:3990]
            + "\n..."
        )

    embed = discord.Embed(
        title="Sunucu Rolleri",
        description=description,
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
    description="Belirtilen miktarda mesajı temizler."
)
@app_commands.describe(
    miktar="1 ile 100 arasında mesaj sayısı."
)
async def temizle(
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
            f"{EMOJIS['yes']} `{len(deleted)}` mesaj temizlendi.",
            ephemeral=True
        )

    except Exception as e:

        print(
            "/temizle hatası:",
            repr(e)
        )

        await interaction.followup.send(
            f"{EMOJIS['no']} Mesajlar temizlenemedi.",
            ephemeral=True
        )


# =========================================================
# /SİL
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

        print(
            "/sil hatası:",
            repr(e)
        )

        await interaction.followup.send(
            f"{EMOJIS['no']} Mesajlar silinemedi.",
            ephemeral=True
        )


# =========================================================
# /BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Kullanıcıyı sunucudan yasaklar."
)
@app_commands.describe(
    kullanıcı="Yasaklanacak kullanıcı.",
    sebep="Yasaklama sebebi."
)
async def ban(
    interaction: discord.Interaction,
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

        await kullanıcı.ban(
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} yasaklandı."
        )

        await send_log(
            interaction.guild,
            f"🔨 {kullanıcı} banlandı.\nSebep: {sebep}"
        )

    except Exception as e:

        print(
            "/ban hatası:",
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
    sebep="Atılma sebebi."
)
async def kick(
    interaction: discord.Interaction,
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
            f"{EMOJIS['yes']} {kullanıcı.mention} sunucudan atıldı."
        )

        await send_log(
            interaction.guild,
            f"👢 {kullanıcı} kicklendi.\nSebep: {sebep}"
        )

    except Exception as e:

        print(
            "/kick hatası:",
            repr(e)
        )

        await interaction.response.send_message(
            f"{EMOJIS['no']} Kullanıcı atılamadı.",
            ephemeral=True
        )


# =========================================================
# /TIMEOUT
# =========================================================

@bot.tree.command(
    name="timeout",
    description="Kullanıcıya timeout uygular."
)
@app_commands.describe(
    kullanıcı="Timeout uygulanacak kullanıcı.",
    dakika="Timeout süresi.",
    sebep="Sebep."
)
async def timeout(
    interaction: discord.Interaction,
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
            timedelta(
                minutes=dakika
            ),
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} "
            f"`{dakika}` dakika timeoutlandı."
        )

        await send_log(
            interaction.guild,
            f"⏱️ {kullanıcı} timeoutlandı.\n"
            f"Süre: {dakika} dakika\n"
            f"Sebep: {sebep}"
        )

    except Exception as e:

        print(
            "/timeout hatası:",
            repr(e)
        )

        await interaction.response.send_message(
            f"{EMOJIS['no']} Timeout uygulanamadı.",
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
async def uyar(
    interaction: discord.Interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):

    if not interaction.user.guild_permissions.moderate_members:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komutu kullanmak için yetkin yok.",
            ephemeral=True
        )
        return

    guild_id = str(
        interaction.guild.id
    )

    user_id = str(
        kullanıcı.id
    )

    warnings = CONFIG.setdefault(
        "warnings",
        {}
    )

    guild_warnings = warnings.setdefault(
        guild_id,
        {}
    )

    current = guild_warnings.get(
        user_id,
        0
    )

    current += 1

    guild_warnings[user_id] = current

    save_config()

    limit = CONFIG["moderation"].get(
        "warning_limit",
        3
    )

    await interaction.response.send_message(
        f"{EMOJIS['yes']} {kullanıcı.mention} uyarıldı.\n"
        f"**Uyarı:** `{current}/{limit}`\n"
        f"**Sebep:** {sebep}"
    )

    if current >= limit:

        action = CONFIG["moderation"].get(
            "warning_action",
            "timeout"
        )

        if action == "timeout":

            minutes = CONFIG["moderation"].get(
                "timeout_minutes",
                10
            )

            try:

                await kullanıcı.timeout(
                    timedelta(
                        minutes=minutes
                    ),
                    reason="Uyarı sınırına ulaşıldı."
                )

                await interaction.channel.send(
                    f"{EMOJIS['alarm']} "
                    f"{kullanıcı.mention} uyarı sınırına ulaştı "
                    f"ve `{minutes}` dakika timeoutlandı."
                )

            except Exception as e:

                print(
                    "Uyarı timeout hatası:",
                    repr(e)
                )


# =========================================================
# /UYARILAR
# =========================================================

@bot.tree.command(
    name="uyarılar",
    description="Kullanıcının uyarı sayısını gösterir."
)
@app_commands.describe(
    kullanıcı="Uyarıları görüntülenecek kullanıcı."
)
async def uyarilar(
    interaction: discord.Interaction,
    kullanıcı: discord.Member
):

    guild_id = str(
        interaction.guild.id
    )

    user_id = str(
        kullanıcı.id
    )

    count = CONFIG.get(
        "warnings",
        {}
    ).get(
        guild_id,
        {}
    ).get(
        user_id,
        0
    )

    await interaction.response.send_message(
        f"{kullanıcı.mention} toplam `{count}` uyarıya sahip.",
        ephemeral=True
    )


# =========================================================
# /DUYURU
# =========================================================

@bot.tree.command(
    name="duyuru",
    description="Duyuru gönderir."
)
@app_commands.describe(
    başlık="Duyuru başlığı.",
    mesaj="Duyuru mesajı."
)
async def duyuru(
    interaction: discord.Interaction,
    başlık: str,
    mesaj: str
):

    if not interaction.user.guild_permissions.manage_guild:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Sunucuyu yönet yetkin yok.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=başlık,
        description=mesaj,
        color=discord.Color.blurple()
    )

    embed.set_footer(
        text=interaction.guild.name
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /KİLİTLE
# =========================================================

@bot.tree.command(
    name="kilitle",
    description="Mevcut kanalı kilitler."
)
async def kilitle(
    interaction: discord.Interaction
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
        f"{EMOJIS['lock']} Kanal kilitlendi."
    )


# =========================================================
# /KİLİT-AÇ
# =========================================================

@bot.tree.command(
    name="kilit-aç",
    description="Mevcut kanalın kilidini açar."
)
async def kilit_ac(
    interaction: discord.Interaction
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
    saniye="0 ile 21600 arasında saniye."
)
async def yavas_mod(
    interaction: discord.Interaction,
    saniye: app_commands.Range[int, 0, 21600]
):

    if not interaction.user.guild_permissions.manage_channels:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Kanal yönetme yetkin yok.",
            ephemeral=True
        )
        return

    try:

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

    except Exception as e:

        print(
            "/yavaş-mod hatası:",
            repr(e)
        )

        await interaction.response.send_message(
            f"{EMOJIS['no']} Yavaş mod ayarlanamadı.",
            ephemeral=True
        )


# =========================================================
# EĞLENCE - ZAR
# =========================================================

@bot.tree.command(
    name="zar",
    description="Zar atar."
)
@app_commands.describe(
    taraf="Kaç yüzlü zar atılacağı."
)
async def zar(
    interaction: discord.Interaction,
    taraf: app_commands.Range[int, 2, 100]
):

    result = random.randint(
        1,
        taraf
    )

    await interaction.response.send_message(
        f"🎲 {interaction.user.mention} **{taraf} yüzlü zar** attı: "
        f"`{result}`"
    )


# =========================================================
# EĞLENCE - YAZI TURA
# =========================================================

@bot.tree.command(
    name="yazı-tura",
    description="Yazı veya tura seçer."
)
async def yazi_tura(
    interaction: discord.Interaction
):

    result = random.choice(
        ["Yazı", "Tura"]
    )

    await interaction.response.send_message(
        f"🪙 {interaction.user.mention} için sonuç: **{result}**"
    )


# =========================================================
# EĞLENCE - 8BALL
# =========================================================

@bot.tree.command(
    name="8ball",
    description="Soruna rastgele cevap verir."
)
@app_commands.describe(
    soru="8ball'a soracağın soru."
)
async def eight_ball(
    interaction: discord.Interaction,
    soru: str
):

    answers = [
        "Evet.",
        "Hayır.",
        "Kesinlikle.",
        "Sanırım evet.",
        "Sanırım hayır.",
        "Bunu zaman gösterecek.",
        "Şimdilik belli değil.",
        "Bence olabilir.",
        "Pek mümkün görünmüyor.",
        "Kesin bir şey söyleyemem."
    ]

    answer = random.choice(
        answers
    )

    embed = discord.Embed(
        title="🎱 8Ball",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Soru",
        value=soru,
        inline=False
    )

    embed.add_field(
        name="Cevap",
        value=answer,
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# EĞLENCE - SAYI TAHMİN
# =========================================================

@bot.tree.command(
    name="sayı-tahmin",
    description="1 ile 100 arasında sayı tahmin et."
)
@app_commands.describe(
    sayı="1 ile 100 arasında tahmin."
)
async def sayi_tahmin(
    interaction: discord.Interaction,
    sayı: app_commands.Range[int, 1, 100]
):

    target = random.randint(
        1,
        100
    )

    if sayı == target:
        result = (
            f"🎉 Doğru bildin! Sayı `{target}` idi."
        )

    elif sayı < target:
        result = (
            f"❌ Daha büyük bir sayı! "
            f"Doğru sayı `{target}` idi."
        )

    else:
        result = (
            f"❌ Daha küçük bir sayı! "
            f"Doğru sayı `{target}` idi."
        )

    await interaction.response.send_message(
        f"{interaction.user.mention} {result}"
    )


# =========================================================
# SAYI SAYMA OYUNU
# =========================================================

NUMBER_GAMES = {}


@bot.tree.command(
    name="sayı-oyunu-ayarla",
    description="Sayı sayma oyununu ayarlar."
)
@app_commands.describe(
    kanal="Oyunun oynanacağı kanal.",
    minimum="Başlangıç sayısı.",
    maksimum="Bitiş sayısı."
)
async def sayi_oyunu_ayarla(
    interaction: discord.Interaction,
    kanal: discord.TextChannel,
    minimum: app_commands.Range[int, 1, 1000000],
    maksimum: app_commands.Range[int, 2, 1000000]
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı sadece yöneticiler kullanabilir.",
            ephemeral=True
        )
        return

    if minimum >= maksimum:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Minimum sayı maksimum sayıdan küçük olmalı.",
            ephemeral=True
        )
        return

    CONFIG["fun"]["number_channel_id"] = kanal.id
    CONFIG["fun"]["number_min"] = minimum
    CONFIG["fun"]["number_max"] = maksimum

    NUMBER_GAMES[
        interaction.guild.id
    ] = {
        "channel_id": kanal.id,
        "current": minimum
    }

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Sayı sayma oyunu ayarlandı.\n\n"
        f"**Kanal:** {kanal.mention}\n"
        f"**Başlangıç:** `{minimum}`\n"
        f"**Bitiş:** `{maksimum}`"
    )

    await kanal.send(
        f"🔢 **Sayı Sayma Oyunu Başladı!**\n\n"
        f"Sıradaki sayı: **{minimum}**"
    )


@bot.tree.command(
    name="sayı-oyunu-durdur",
    description="Sayı sayma oyununu durdurur."
)
async def sayi_oyunu_durdur(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı sadece yöneticiler kullanabilir.",
            ephemeral=True
        )
        return

    NUMBER_GAMES.pop(
        interaction.guild.id,
        None
    )

    CONFIG["fun"]["number_channel_id"] = None

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Sayı sayma oyunu durduruldu."
    )


# =========================================================
# KELİME OYUNU
# =========================================================

WORD_GAMES = {}


@bot.tree.command(
    name="kelime-oyunu-ayarla",
    description="Kelime oyununu ayarlar."
)
@app_commands.describe(
    kanal="Kelime oyununun oynanacağı kanal."
)
async def kelime_oyunu_ayarla(
    interaction: discord.Interaction,
    kanal: discord.TextChannel
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı sadece yöneticiler kullanabilir.",
            ephemeral=True
        )
        return

    words = CONFIG["fun"].get(
        "word_words",
        []
    )

    if not words:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Kelime listesi boş.",
            ephemeral=True
        )
        return

    first_word = random.choice(
        words
    )

    CONFIG["fun"]["word_channel_id"] = kanal.id

    WORD_GAMES[
        interaction.guild.id
    ] = {
        "channel_id": kanal.id,
        "last_word": first_word,
        "used_words": [
            first_word
        ]
    }

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Kelime oyunu ayarlandı.\n"
        f"**Kanal:** {kanal.mention}"
    )

    await kanal.send(
        f"🔤 **Kelime Oyunu Başladı!**\n\n"
        f"İlk kelime: **{first_word}**\n\n"
        f"Son harfi **{first_word[-1].upper()}** "
        f"olan yeni bir kelime yaz!"
    )


@bot.tree.command(
    name="kelime-oyunu-durdur",
    description="Kelime oyununu durdurur."
)
async def kelime_oyunu_durdur(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı sadece yöneticiler kullanabilir.",
            ephemeral=True
        )
        return

    WORD_GAMES.pop(
        interaction.guild.id,
        None
    )

    CONFIG["fun"]["word_channel_id"] = None

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Kelime oyunu durduruldu."
    )


@bot.tree.command(
    name="kelime-ekle",
    description="Kelime oyununa kelime ekler."
)
@app_commands.describe(
    kelime="Eklenecek kelime."
)
async def kelime_ekle(
    interaction: discord.Interaction,
    kelime: str
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı sadece yöneticiler kullanabilir.",
            ephemeral=True
        )
        return

    kelime = kelime.strip().lower()

    if not kelime.isalpha():

        await interaction.response.send_message(
            f"{EMOJIS['no']} Sadece harflerden oluşan bir kelime yaz.",
            ephemeral=True
        )
        return

    words = CONFIG["fun"].setdefault(
        "word_words",
        []
    )

    if kelime in words:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kelime zaten listede.",
            ephemeral=True
        )
        return

    words.append(
        kelime
    )

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} `{kelime}` kelime listesine eklendi."
    )


@bot.tree.command(
    name="kelime-çıkar",
    description="Kelime oyunundan kelime çıkarır."
)
@app_commands.describe(
    kelime="Çıkarılacak kelime."
)
async def kelime_cikar(
    interaction: discord.Interaction,
    kelime: str
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı sadece yöneticiler kullanabilir.",
            ephemeral=True
        )
        return

    kelime = kelime.strip().lower()

    words = CONFIG["fun"].setdefault(
        "word_words",
        []
    )

    if kelime not in words:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kelime listede bulunmuyor.",
            ephemeral=True
        )
        return

    words.remove(
        kelime
    )

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} `{kelime}` kelime listesinden çıkarıldı."
    )


# =========================================================
# DM SİSTEMİ
# =========================================================

class DMModal(discord.ui.Modal):

    def __init__(
        self,
        target_role: discord.Role
    ):
        super().__init__(
            title="Rol Üyelerine DM Gönder"
        )

        self.target_role = target_role

        self.baslik = discord.ui.TextInput(
            label="Başlık",
            placeholder="DM başlığı",
            required=True,
            max_length=256
        )

        self.mesaj = discord.ui.TextInput(
            label="Mesaj",
            placeholder="Göndermek istediğin mesaj...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )

        self.add_item(
            self.baslik
        )

        self.add_item(
            self.mesaj
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if not has_dm_permission(
            interaction
        ):

            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu komutu kullanma yetkin artık yok.",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        guild = interaction.guild

        if guild is None:
            return

        members = [
            member
            for member in guild.members
            if self.target_role in member.roles
            and not member.bot
        ]

        embed = discord.Embed(
            title=str(
                self.baslik.value
            ),
            description=str(
                self.mesaj.value
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text=guild.name
        )

        sent = 0
        failed = 0

        for member in members:

            try:

                await member.send(
                    embed=embed
                )

                sent += 1

            except Exception:

                failed += 1

            await asyncio.sleep(
                0.15
            )

        await interaction.followup.send(
            f"{EMOJIS['yes']} DM gönderme tamamlandı.\n\n"
            f"**Rol:** {self.target_role.mention}\n"
            f"**Başarılı:** `{sent}`\n"
            f"**Gönderilemedi:** `{failed}`",
            ephemeral=True
        )

        await send_log(
            guild,
            f"📨 **Rol DM gönderimi**\n"
            f"**Gönderen:** {interaction.user.mention}\n"
            f"**Rol:** {self.target_role.mention}\n"
            f"**Başarılı:** `{sent}`\n"
            f"**Başarısız:** `{failed}`"
        )


@bot.tree.command(
    name="dm",
    description="Bir role sahip kullanıcılara DM gönderir."
)
@app_commands.describe(
    rol="DM gönderilecek rol."
)
async def dm(
    interaction: discord.Interaction,
    rol: discord.Role
):

    if not has_dm_permission(
        interaction
    ):

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komutu kullanma yetkin yok.",
            ephemeral=True
        )
        return

    allowed_roles = CONFIG["dm"].get(
        "allowed_role_ids",
        []
    )

    if (
        not interaction.user.guild_permissions.administrator
        and rol.id not in allowed_roles
    ):
        # Hedef rolün seçilmesiyle kullanıcının yetkisini karıştırmamak için
        # sadece izin verilen personel rollerini kontrol ediyoruz.
        pass

    await interaction.response.send_modal(
        DMModal(
            rol
        )
    )


# =========================================================
# DM ROL AYARLARI
# =========================================================

class DMRoleSelect(
    discord.ui.RoleSelect
):

    def __init__(self):
        super().__init__(
            placeholder="DM komutunu kullanabilecek rolleri seç...",
            min_values=0,
            max_values=10,
            custom_id="dynex_dm_role_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                f"{EMOJIS['no']} Sadece yöneticiler DM rollerini değiştirebilir.",
                ephemeral=True
            )
            return

        selected_ids = [
            role.id
            for role in self.values
        ]

        CONFIG["dm"]["allowed_role_ids"] = selected_ids

        save_config()

        if selected_ids:

            roles_text = " ".join(
                f"<@&{role_id}>"
                for role_id in selected_ids
            )

        else:

            roles_text = "Hiçbir rol seçilmedi."

        await interaction.response.send_message(
            f"{EMOJIS['yes']} DM komutunu kullanabilecek roller güncellendi.\n\n"
            f"{roles_text}",
            ephemeral=True
        )


class DMSettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=180
        )

        self.add_item(
            DMRoleSelect()
        )


@bot.tree.command(
    name="dm-ayarları",
    description="DM komutunu kullanabilecek rolleri ayarlar."
)
async def dm_ayarlari(
    interaction: discord.Interaction
):

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı sadece yöneticiler kullanabilir.",
            ephemeral=True
        )
        return

    allowed_ids = CONFIG["dm"].get(
        "allowed_role_ids",
        []
    )

    if allowed_ids:

        roles_text = "\n".join(
            f"<@&{role_id}>"
            for role_id in allowed_ids
        )

    else:

        roles_text = "Henüz rol ayarlanmadı."

    embed = discord.Embed(
        title="📨 DM Ayarları",
        description=(
            "Aşağıdaki menüden `/dm` komutunu "
            "kullanabilecek rolleri seç.\n\n"
            f"**Mevcut roller:**\n{roles_text}"
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=DMSettingsView(),
        ephemeral=True
    )


# =========================================================
# /AYARLAR
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
                label="Otorol",
                value="autorole",
                emoji="🎭"
            ),
            discord.SelectOption(
                label="Moderasyon",
                value="moderation",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="Loglar",
                value="logs",
                emoji="📋"
            ),
            discord.SelectOption(
                label="Ses Bildirimleri",
                value="voice",
                emoji="🔊"
            ),
            discord.SelectOption(
                label="Çekiliş",
                value="giveaway",
                emoji="🎉"
            ),
            discord.SelectOption(
                label="DM",
                value="dm",
                emoji="📨"
            )
        ]

        super().__init__(
            placeholder="Bir ayar kategorisi seçin...",
            options=options,
            custom_id="dynex_settings_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu ayarlara erişmek için Yönetici yetkisine sahip olmalısın.",
                ephemeral=True
            )
            return

        category = self.values[0]

        if category == "ticket":

            description = (
                "**Ticket Ayarları**\n\n"
                "Ticket kategorisi, yetkili rolü, panel kanalı "
                "ve ticket seçeneklerini yönetebilirsin.\n\n"
                "Ticket seçenekleri başlangıçta boştur."
            )

        elif category == "welcome":

            description = (
                "**Welcome Ayarları**\n\n"
                "Karşılama kanalı, başlık, açıklama, görsel "
                "ve DM mesajını yapılandırabilirsin."
            )

        elif category == "autorole":

            description = (
                "**Otorol Ayarları**\n\n"
                "Yeni üyelerin otomatik alacağı rolü ayarlayabilirsin."
            )

        elif category == "moderation":

            description = (
                "**Moderasyon Ayarları**\n\n"
                "Kötü kelimeler, uyarı sınırı, timeout, "
                "link engelleme ve spam ayarları."
            )

        elif category == "logs":

            description = (
                "**Log Ayarları**\n\n"
                "Sunucudaki olayların gönderileceği log kanalını ayarlayabilirsin."
            )

        elif category == "voice":

            description = (
                "**Ses Bildirimleri**\n\n"
                "Ses kanalına giriş ve çıkış bildirimlerini ayarlayabilirsin."
            )

        elif category == "giveaway":

            description = (
                "**Çekiliş Ayarları**\n\n"
                "Çekiliş yetkili rolünü, kanalını ve varsayılan ayarları yönetebilirsin."
            )

        else:

            description = (
                "**DM Ayarları**\n\n"
                "`/dm` komutunu kullanabilecek rolleri ayarlamak için:\n"
                "`/dm-ayarları`\n\n"
                "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
            )

        embed = discord.Embed(
            title=f"{EMOJIS['settings']} {category.title()} Ayarları",
            description=description,
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self.view
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


@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönetir."
)
async def ayarlar(
    interaction: discord.Interaction
):

    if not interaction.guild:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komut sadece sunucularda kullanılabilir.",
            ephemeral=True
        )
        return

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarlara erişmek için Yönetici yetkisine sahip olmalısın.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"{EMOJIS['settings']} Dynex Ayarları",
        description=(
            "Aşağıdaki menüden değiştirmek istediğin ayar kategorisini seç."
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(),
        ephemeral=True
    )


# =========================================================
# DİL
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
                label="Azərbaycan",
                value="az",
                emoji="🇦🇿"
            )
        ]

        super().__init__(
            placeholder="Bir dil seçin...",
            options=options,
            custom_id="dynex_language_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.guild:
            return

        CONFIG.setdefault(
            "language",
            {}
        )[
            str(interaction.guild.id)
        ] = self.values[0]

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Dil başarıyla değiştirildi.",
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
    description="Botun sunucu dilini değiştirir."
)
async def dil(
    interaction: discord.Interaction
):

    if not interaction.guild:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komut sadece sunucularda kullanılabilir.",
            ephemeral=True
        )
        return

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu ayarı değiştirmek için Yönetici yetkisine sahip olmalısın.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Dil Ayarları",
        description="Botun sunucudaki dilini seç.",
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# MESAJ EVENTİ
# =========================================================

@bot.event
async def on_message(
    message: discord.Message
):

    if message.author.bot:
        return

    if not message.guild:
        await bot.process_commands(
            message
        )
        return

    guild_id = message.guild.id

    # -----------------------------------------------------
    # SAYI OYUNU
    # -----------------------------------------------------

    number_game = NUMBER_GAMES.get(
        guild_id
    )

    if number_game:

        if message.channel.id == number_game["channel_id"]:

            try:
                number = int(
                    message.content.strip()
                )
            except ValueError:
                number = None

            if number is not None:

                expected = number_game["current"]

                if number == expected:

                    maximum = CONFIG["fun"].get(
                        "number_max",
                        100
                    )

                    if number >= maximum:

                        await message.add_reaction(
                            "🎉"
                        )

                        await message.channel.send(
                            f"🎉 **Oyun tamamlandı!**\n"
                            f"{message.author.mention} "
                            f"son sayıyı söyledi: `{number}`"
                        )

                        number_game["current"] = CONFIG["fun"].get(
                            "number_min",
                            1
                        )

                    else:

                        number_game["current"] = (
                            number + 1
                        )

                        try:
                            await message.add_reaction(
                                "✅"
                            )
                        except Exception:
                            pass

                else:

                    try:
                        await message.delete()
                    except Exception:
                        pass

                    await message.channel.send(
                        f"{EMOJIS['no']} "
                        f"{message.author.mention}, "
                        f"sıradaki sayı **{expected}**!",
                        delete_after=3
                    )

    # -----------------------------------------------------
    # KELİME OYUNU
    # -----------------------------------------------------

    word_game = WORD_GAMES.get(
        guild_id
    )

    if word_game:

        if message.channel.id == word_game["channel_id"]:

            word = (
                message.content
                .strip()
                .lower()
            )

            if (
                word
                and word.isalpha()
                and len(word) >= 2
            ):

                last_word = word_game[
                    "last_word"
                ]

                required_letter = (
                    last_word[-1].lower()
                )

                if not word.startswith(
                    required_letter
                ):

                    try:
                        await message.delete()
                    except Exception:
                        pass

                    await message.channel.send(
                        f"{EMOJIS['no']} "
                        f"{message.author.mention}, "
                        f"kelime **{required_letter.upper()}** "
                        f"harfiyle başlamalı!",
                        delete_after=3
                    )

                elif word in word_game[
                    "used_words"
                ]:

                    try:
                        await message.delete()
                    except Exception:
                        pass

                    await message.channel.send(
                        f"{EMOJIS['no']} "
                        "Bu kelime daha önce kullanıldı!",
                        delete_after=3
                    )

                else:

                    word_game[
                        "last_word"
                    ] = word

                    word_game[
                        "used_words"
                    ].append(
                        word
                    )

                    try:
                        await message.add_reaction(
                            "✅"
                        )
                    except Exception:
                        pass

    # -----------------------------------------------------
    # MODERASYON
    # -----------------------------------------------------

    moderation = CONFIG.get(
        "moderation",
        {}
    )

    content_lower = message.content.lower()

    bad_words = moderation.get(
        "bad_words",
        []
    )

    for bad_word in bad_words:

        if bad_word.lower() in content_lower:

            try:

                await message.delete()

                await message.channel.send(
                    f"{EMOJIS['no']} "
                    f"{message.author.mention}, "
                    "bu kelimeyi kullanamazsın.",
                    delete_after=5
                )

            except Exception as e:

                print(
                    "Kötü kelime hatası:",
                    repr(e)
                )

            break

    # Link koruması
    if moderation.get(
        "anti_link",
        False
    ):

        if (
            "http://" in content_lower
            or "https://" in content_lower
            or "discord.gg/" in content_lower
        ):

            if not message.author.guild_permissions.manage_messages:

                try:

                    await message.delete()

                    await message.channel.send(
                        f"{EMOJIS['no']} "
                        f"{message.author.mention}, "
                        "link paylaşamazsın.",
                        delete_after=5
                    )

                except Exception as e:

                    print(
                        "Link kontrol hatası:",
                        repr(e)
                    )

    await bot.process_commands(
        message
    )


# =========================================================
# ÜYE GİRİŞ
# =========================================================

@bot.event
async def on_member_join(
    member: discord.Member
):

    guild = member.guild

    # Otorol
    role_id = CONFIG.get(
        "autorole",
        {}
    ).get(
        "role_id"
    )

    if role_id:

        role = guild.get_role(
            role_id
        )

        if role:

            try:
                await member.add_roles(
                    role
                )
            except Exception as e:
                print(
                    "Otorol hatası:",
                    repr(e)
                )

    # Welcome
    welcome = CONFIG.get(
        "welcome",
        {}
    )

    channel_id = welcome.get(
        "channel_id"
    )

    if channel_id:

        channel = guild.get_channel(
            channel_id
        )

        if channel:

            description = welcome.get(
                "description",
                "{member}, sunucumuza hoş geldin!"
            ).replace(
                "{member}",
                member.mention
            )

            embed = discord.Embed(
                title=welcome.get(
                    "title",
                    "Hoş Geldin!"
                ),
                description=description,
                color=discord.Color.blurple()
            )

            image = welcome.get(
                "image",
                ""
            )

            if image:
                embed.set_image(
                    url=image
                )

            try:
                await channel.send(
                    embed=embed
                )
            except Exception as e:
                print(
                    "Welcome hatası:",
                    repr(e)
                )

    # DM
    dm_message = welcome.get(
        "dm",
        ""
    )

    if dm_message:

        try:

            await member.send(
                dm_message.replace(
                    "{member}",
                    member.mention
                )
            )

        except Exception:
            pass

    await send_log(
        guild,
        f"📥 {member.mention} sunucuya katıldı."
    )


# =========================================================
# ÜYE ÇIKIŞ
# =========================================================

@bot.event
async def on_member_remove(
    member: discord.Member
):

    await send_log(
        member.guild,
        f"📤 {member} sunucudan ayrıldı."
    )


# =========================================================
# MESAJ SİLİNDİ
# =========================================================

@bot.event
async def on_message_delete(
    message: discord.Message
):

    if message.author.bot:
        return

    if not message.guild:
        return

    if not CONFIG["logs"].get(
        "delete",
        True
    ):
        return

    await send_log(
        message.guild,
        f"🗑️ **Mesaj silindi**\n"
        f"**Kullanıcı:** {message.author.mention}\n"
        f"**Kanal:** {message.channel.mention}\n"
        f"**Mesaj:** {message.content[:1000]}"
    )


# =========================================================
# MESAJ DÜZENLENDİ
# =========================================================

@bot.event
async def on_message_edit(
    before,
    after
):

    if before.author.bot:
        return

    if not before.guild:
        return

    if before.content == after.content:
        return

    if not CONFIG["logs"].get(
        "edit",
        True
    ):
        return

    await send_log(
        before.guild,
        f"✏️ **Mesaj düzenlendi**\n"
        f"**Kullanıcı:** {before.author.mention}\n"
        f"**Kanal:** {before.channel.mention}\n"
        f"**Eski:** {before.content[:500]}\n"
        f"**Yeni:** {after.content[:500]}"
    )


# =========================================================
# SES EVENTİ
# =========================================================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if before.channel == after.channel:
        return

    voice = CONFIG.get(
        "voice",
        {}
    )

    channel_id = voice.get(
        "channel_id"
    )

    if not channel_id:
        return

    notification_channel = (
        member.guild.get_channel(
            channel_id
        )
    )

    if not notification_channel:
        return

    try:

        if after.channel and not before.channel:

            text = voice.get(
                "join_message",
                "{member} ses kanalına katıldı."
            ).replace(
                "{member}",
                member.mention
            )

            await notification_channel.send(
                text
            )

        elif before.channel and not after.channel:

            text = voice.get(
                "leave_message",
                "{member} ses kanalından ayrıldı."
            ).replace(
                "{member}",
                member.mention
            )

            await notification_channel.send(
                text
            )

    except Exception as e:

        print(
            "Ses bildirim hatası:",
            repr(e)
        )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(
        f"Dynex giriş yaptı: "
        f"{bot.user} ({bot.user.id})"
    )

    print(
        f"Sunucu sayısı: {len(bot.guilds)}"
    )


# =========================================================
# SLASH KOMUT HATALARI
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    print(
        "Slash komut hatası:",
        repr(error)
    )

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

    except Exception as e:

        print(
            "Hata mesajı gönderilemedi:",
            repr(e)
        )


# =========================================================
# BAŞLAT
# =========================================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN ortam değişkeni bulunamadı."
    )

bot.run(TOKEN)
