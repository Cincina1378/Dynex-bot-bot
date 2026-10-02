import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import copy
import random
import time
import re
import asyncio
from datetime import datetime, timedelta, timezone

# =========================================================
# DYNEX
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

SUPPORT_SERVER_ID = 1551647711332139098
SUPPORT_SERVER_INVITE = "https://discord.gg/2pFJwJNDR"

EMOJIS = {
    "dynex": "<:Dynex:1555263060350996510>",
    "dynexserver": "<:Dynexserver:1555263062112604270>",
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

CONFIG_FILE = "config.json"

DEFAULT_GUILD_CONFIG = {
    "ticket": {
        "category_id": None,
        "staff_role_id": None,
        "panel_channel_id": None,
        "panel_title": "Destek Talebi",
        "panel_description": "Destek talebi oluşturmak için aşağıdaki butona basın.",
        "panel_image": None,
        "button_label": "Destek Talebi",
        "button_emoji": "🎫",
        "options": []
    },
    "welcome": {
        "channel_id": None,
        "title": "Sunucumuza Hoş Geldin!",
        "description": "{member} sunucumuza katıldı.",
        "image": None,
        "dm_message": None
    },
    "moderation": {
        "bad_words": [],
        "warning_limit": 3,
        "warning_action": "timeout",
        "timeout_duration": 10,
        "anti_link": False,
        "anti_spam": False,
        "log_channel_id": None
    },
    "logs": {
        "channel_id": None,
        "delete": False,
        "edit": False,
        "join": False,
        "leave": False,
        "ban": False,
        "kick": False,
        "timeout": False
    },
    "autorole": {
        "role_id": None
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
    "dm": {
        "allowed_role_ids": []
    },
    "language": "tr",
    "warnings": {},
    "games": {
        "number_channel_id": None,
        "number_target": 50,
        "number_current": 0,
        "number_started": False,
        "word_channel_id": None,
        "words": [],
        "word_current": None,
        "word_started": False
    }
}

try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except Exception:
    CONFIG = {}


def merge_dict(default, current):
    if not isinstance(default, dict):
        return copy.deepcopy(current) if current is not None else copy.deepcopy(default)

    result = copy.deepcopy(default)

    if isinstance(current, dict):
        for key, value in current.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dict(result[key], value)
            else:
                result[key] = value

    return result


def get_guild_config(guild_id):
    gid = str(guild_id)

    if gid not in CONFIG:
        CONFIG[gid] = copy.deepcopy(DEFAULT_GUILD_CONFIG)
    else:
        CONFIG[gid] = merge_dict(DEFAULT_GUILD_CONFIG, CONFIG[gid])

    return CONFIG[gid]


def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Config kayıt hatası:", repr(e))


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


def channel_from_id(guild, channel_id):
    if not channel_id:
        return None
    return guild.get_channel(int(channel_id))


def role_from_id(guild, role_id):
    if not role_id:
        return None
    return guild.get_role(int(role_id))


def clean_channel_name(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9ğüşöçıİĞÜŞÖÇ\- ]", "", text)
    text = text.replace(" ", "-")
    text = text[:80].strip("-")
    return text or "ticket"


def format_duration(seconds):
    seconds = max(0, int(seconds))

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []

    if days:
        parts.append(f"{days}g")
    if hours:
        parts.append(f"{hours}s")
    if minutes:
        parts.append(f"{minutes}d")
    if seconds or not parts:
        parts.append(f"{seconds}sn")

    return " ".join(parts)


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="D.",
    intents=intents,
    help_command=None
)

tree = bot.tree

START_TIME = time.time()
APPLICATION_OWNER = None
SPAM_CACHE = {}
GIVEAWAYS = {}
TICKET_VIEW_REGISTERED = False


# =========================================================
# YARDIMCI
# =========================================================

async def send_log(guild, title, description, kind=None):
    cfg = get_guild_config(guild.id)
    logs = cfg["logs"]

    if not logs.get("channel_id"):
        return

    if kind and not logs.get(kind, False):
        return

    channel = guild.get_channel(int(logs["channel_id"]))

    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.from_rgb(0, 0, 0),
        timestamp=datetime.now(timezone.utc)
    )

    try:
        await channel.send(embed=embed)
    except Exception:
        pass


async def get_owner():
    global APPLICATION_OWNER

    if APPLICATION_OWNER:
        return APPLICATION_OWNER

    try:
        app = await bot.application_info()
        APPLICATION_OWNER = app.owner
    except Exception:
        APPLICATION_OWNER = None

    return APPLICATION_OWNER


def is_admin(member):
    return bool(member and member.guild_permissions.administrator)


def has_role(member, role_id):
    if not role_id:
        return False

    try:
        return any(role.id == int(role_id) for role in member.roles)
    except Exception:
        return False


def can_manage_giveaway(member, cfg):
    if is_admin(member):
        return True

    role_id = cfg["giveaway"].get("staff_role_id")

    return has_role(member, role_id)


def can_use_dm(member, cfg):
    if is_admin(member):
        return True

    allowed = cfg["dm"].get("allowed_role_ids", [])

    return any(role.id in allowed for role in member.roles)


async def safe_respond(interaction, content=None, embed=None, ephemeral=True, view=None):
    try:
        if interaction.response.is_done():
            return await interaction.followup.send(
                content=content,
                embed=embed,
                ephemeral=ephemeral,
                view=view
            )

        return await interaction.response.send_message(
            content=content,
            embed=embed,
            ephemeral=ephemeral,
            view=view
        )
    except Exception:
        return None


# =========================================================
# /BOT
# =========================================================

@tree.command(name="bot", description="Dynex botunun durumunu gösterir.")
async def bot_info(interaction: discord.Interaction):
    uptime = int(time.time() - START_TIME)

    support_guild = bot.get_guild(SUPPORT_SERVER_ID)
    support_members = support_guild.member_count if support_guild else 0

    owner = await get_owner()

    owner_text = owner.mention if owner else "Bilinmiyor"

    embed = discord.Embed(
        title="Dynex Durum",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    embed.add_field(
        name="Sunucu sayısı",
        value=str(len(bot.guilds)),
        inline=True
    )

    embed.add_field(
        name="Destek sunucusu üye sayısı",
        value=str(support_members),
        inline=True
    )

    embed.add_field(
        name="Prefix",
        value="`D.`",
        inline=True
    )

    embed.add_field(
        name="Aktiflik",
        value=format_duration(uptime),
        inline=True
    )

    embed.add_field(
        name="Bot sahibi",
        value=owner_text,
        inline=True
    )

    embed.add_field(
        name="Destek",
        value=f"[Destek sunucusuna katıl]({SUPPORT_SERVER_INVITE})",
        inline=True
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# /YARDIM
# =========================================================

@tree.command(name="yardım", description="Dynex komutlarını gösterir.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title=f"{EMOJIS['dynex']} Dynex Yardım",
        description="Aşağıdaki kategorilerde Dynex komutlarını kullanabilirsiniz.",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    embed.add_field(
        name="Genel",
        value=(
            "`/bot` `/yardım` `/ping` `/kullanıcı` "
            "`/avatar` `/sunucu` `/roller` `/dil`"
        ),
        inline=False
    )

    embed.add_field(
        name="Moderasyon",
        value=(
            "`/uyar` `/uyarılar` `/uyarı-sıfırla` `/timeout` "
            "`/kick` `/ban` `/temizle` `/sil` `/kilitle` "
            "`/kilit-aç` `/yavaş-mod`"
        ),
        inline=False
    )

    embed.add_field(
        name="Eğlence",
        value=(
            "`/sayı-oyunu-ayarla` `/sayı-oyunu-durdur` "
            "`/kelime-oyunu-ayarla` `/kelime-oyunu-durdur` "
            "`/kelime-ekle` `/kelime-çıkar` `/zar` "
            "`/yazı-tura` `/8ball` `/sayı-tahmin`"
        ),
        inline=False
    )

    embed.add_field(
        name="Ticket",
        value="`/ayarlar → Ticket` `/ticket-panel`",
        inline=False
    )

    embed.add_field(
        name="Çekiliş",
        value="`/çekiliş` `/çekiliş-bitir`",
        inline=False
    )

    embed.add_field(
        name="Sunucu",
        value="`/ayarlar` `/duyuru` `/dm`",
        inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


# =========================================================
# GENEL KOMUTLAR
# =========================================================

@tree.command(name="ping", description="Botun ping değerini gösterir.")
async def ping(interaction: discord.Interaction):
    ms = round(bot.latency * 1000)

    if ms <= 80:
        status = "Mükemmel"
    elif ms <= 150:
        status = "İyi"
    elif ms <= 250:
        status = "Orta"
    elif ms <= 400:
        status = "Zayıf"
    else:
        status = "Berbat"

    embed = discord.Embed(
        title="Dynex Ping",
        description=f"Bot gecikmesi: **{ms}ms**\nDurum: **{status}**",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    await interaction.response.send_message(embed=embed)


@tree.command(name="kullanıcı", description="Bir kullanıcının bilgilerini gösterir.")
@app_commands.describe(kullanıcı="Bilgilerini görmek istediğiniz kullanıcı.")
async def user_info(
    interaction: discord.Interaction,
    kullanıcı: discord.Member = None
):
    kullanıcı = kullanıcı or interaction.user

    embed = discord.Embed(
        title=f"{kullanıcı.display_name} Kullanıcı Bilgileri",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    embed.set_thumbnail(url=kullanıcı.display_avatar.url)

    embed.add_field(
        name="Kullanıcı",
        value=kullanıcı.mention,
        inline=False
    )

    embed.add_field(
        name="ID",
        value=str(kullanıcı.id),
        inline=True
    )

    embed.add_field(
        name="Hesap",
        value=discord.utils.format_dt(kullanıcı.created_at, "R"),
        inline=True
    )

    embed.add_field(
        name="Sunucuya katılım",
        value=discord.utils.format_dt(kullanıcı.joined_at, "R")
        if kullanıcı.joined_at else "Bilinmiyor",
        inline=True
    )

    await interaction.response.send_message(embed=embed)


@tree.command(name="avatar", description="Kullanıcının avatarını gösterir.")
@app_commands.describe(kullanıcı="Avatarını görmek istediğiniz kullanıcı.")
async def avatar(
    interaction: discord.Interaction,
    kullanıcı: discord.Member = None
):
    kullanıcı = kullanıcı or interaction.user

    embed = discord.Embed(
        title=f"{kullanıcı.display_name} Avatar",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    embed.set_image(url=kullanıcı.display_avatar.url)

    await interaction.response.send_message(embed=embed)


@tree.command(name="sunucu", description="Sunucu bilgilerini gösterir.")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=f"{guild.name} Sunucu Bilgileri",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="Sunucu ID", value=str(guild.id), inline=True)
    embed.add_field(name="Üye", value=str(guild.member_count), inline=True)
    embed.add_field(name="Kanal", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="Rol", value=str(len(guild.roles)), inline=True)
    embed.add_field(
        name="Oluşturulma",
        value=discord.utils.format_dt(guild.created_at, "R"),
        inline=True
    )

    await interaction.response.send_message(embed=embed)


@tree.command(name="roller", description="Sunucudaki rolleri listeler.")
async def roles(interaction: discord.Interaction):
    guild = interaction.guild

    role_list = [
        role.mention
        for role in reversed(guild.roles)
        if role != guild.default_role
    ]

    text = "\n".join(role_list)

    if not text:
        text = "Sunucuda özel rol bulunmuyor."

    if len(text) > 3900:
        text = text[:3900] + "\n..."

    embed = discord.Embed(
        title="Sunucu Rolleri",
        description=text,
        color=discord.Color.from_rgb(0, 0, 0)
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


# =========================================================
# MODERASYON
# =========================================================

@tree.command(name="temizle", description="Mesajları toplu olarak siler.")
@app_commands.describe(miktar="Silinecek mesaj sayısı.")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear_messages(
    interaction: discord.Interaction,
    miktar: app_commands.Range[int, 1, 100]
):
    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=miktar)

    await interaction.followup.send(
        f"{EMOJIS['yes']} **{len(deleted)}** mesaj silindi.",
        ephemeral=True
    )


@tree.command(name="sil", description="Belirli sayıda mesajı siler.")
@app_commands.describe(miktar="Silinecek mesaj sayısı.")
@app_commands.checks.has_permissions(manage_messages=True)
async def delete_messages(
    interaction: discord.Interaction,
    miktar: app_commands.Range[int, 1, 100]
):
    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=miktar)

    await interaction.followup.send(
        f"{EMOJIS['yes']} **{len(deleted)}** mesaj silindi.",
        ephemeral=True
    )


@tree.command(name="ban", description="Kullanıcıyı sunucudan yasaklar.")
@app_commands.describe(
    kullanıcı="Yasaklanacak kullanıcı.",
    sebep="Yasaklama sebebi."
)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(
    interaction: discord.Interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):
    if kullanıcı == interaction.user:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Kendinizi yasaklayamazsınız.",
            ephemeral=True
        )

    try:
        await kullanıcı.ban(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} yasaklandı."
        )

        await send_log(
            interaction.guild,
            "Üye Yasaklandı",
            f"{kullanıcı.mention} yasaklandı.\nSebep: {sebep}",
            "ban"
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı yasaklayamıyorum.",
            ephemeral=True
        )


@tree.command(name="kick", description="Kullanıcıyı sunucudan atar.")
@app_commands.describe(
    kullanıcı="Atılacak kullanıcı.",
    sebep="Atılma sebebi."
)
@app_commands.checks.has_permissions(kick_members=True)
async def kick(
    interaction: discord.Interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):
    if kullanıcı == interaction.user:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Kendinizi atamazsınız.",
            ephemeral=True
        )

    try:
        await kullanıcı.kick(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} sunucudan atıldı."
        )

        await send_log(
            interaction.guild,
            "Üye Atıldı",
            f"{kullanıcı.mention} atıldı.\nSebep: {sebep}",
            "kick"
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıyı atamıyorum.",
            ephemeral=True
        )


@tree.command(name="timeout", description="Kullanıcıya timeout uygular.")
@app_commands.describe(
    kullanıcı="Timeout uygulanacak kullanıcı.",
    dakika="Timeout süresi.",
    sebep="Timeout sebebi."
)
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    kullanıcı: discord.Member,
    dakika: app_commands.Range[int, 1, 40320],
    sebep: str = "Sebep belirtilmedi."
):
    if kullanıcı == interaction.user:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Kendinize timeout veremezsiniz.",
            ephemeral=True
        )

    try:
        until = discord.utils.utcnow() + timedelta(minutes=dakika)

        await kullanıcı.timeout(
            until,
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} **{dakika} dakika** timeout aldı."
        )

        await send_log(
            interaction.guild,
            "Timeout",
            f"{kullanıcı.mention} timeout aldı.\nSüre: {dakika} dakika\nSebep: {sebep}",
            "timeout"
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu kullanıcıya timeout veremiyorum.",
            ephemeral=True
        )


@tree.command(name="uyar", description="Kullanıcıya uyarı verir.")
@app_commands.describe(
    kullanıcı="Uyarılacak kullanıcı.",
    sebep="Uyarı sebebi."
)
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(
    interaction: discord.Interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):
    if kullanıcı == interaction.user:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Kendinizi uyaramazsınız.",
            ephemeral=True
        )

    cfg = get_guild_config(interaction.guild.id)
    warnings = cfg["warnings"]

    gid = str(interaction.guild.id)
    uid = str(kullanıcı.id)

    warnings.setdefault(gid, {})
    warnings[gid].setdefault(uid, [])

    warnings[gid][uid].append({
        "reason": sebep,
        "moderator": interaction.user.id,
        "time": datetime.now(timezone.utc).isoformat()
    })

    save_config()

    count = len(warnings[gid][uid])
    limit = max(1, int(cfg["moderation"].get("warning_limit", 3)))

    await interaction.response.send_message(
        f"{EMOJIS['yes']} {kullanıcı.mention} uyarıldı.\n"
        f"Uyarı sayısı: **{count}/{limit}**"
    )

    if count >= limit:
        action = cfg["moderation"].get("warning_action", "timeout")

        try:
            if action == "timeout":
                minutes = int(cfg["moderation"].get("timeout_duration", 10))
                await kullanıcı.timeout(
                    discord.utils.utcnow() + timedelta(minutes=minutes),
                    reason="Uyarı limiti aşıldı."
                )

            elif action == "kick":
                await kullanıcı.kick(reason="Uyarı limiti aşıldı.")

            elif action == "ban":
                await kullanıcı.ban(reason="Uyarı limiti aşıldı.")

        except Exception:
            pass


@tree.command(name="uyarılar", description="Kullanıcının uyarılarını gösterir.")
@app_commands.describe(kullanıcı="Uyarıları gösterilecek kullanıcı.")
@app_commands.checks.has_permissions(moderate_members=True)
async def warnings(
    interaction: discord.Interaction,
    kullanıcı: discord.Member
):
    cfg = get_guild_config(interaction.guild.id)

    gid = str(interaction.guild.id)
    uid = str(kullanıcı.id)

    data = cfg["warnings"].get(gid, {}).get(uid, [])

    if not data:
        return await interaction.response.send_message(
            f"{kullanıcı.mention} için kayıtlı uyarı yok.",
            ephemeral=True
        )

    lines = []

    for i, warning in enumerate(data[-10:], 1):
        lines.append(
            f"**{i}.** {warning.get('reason', 'Sebep yok')}"
        )

    embed = discord.Embed(
        title=f"{kullanıcı.display_name} Uyarıları",
        description="\n".join(lines),
        color=discord.Color.from_rgb(0, 0, 0)
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="uyarı-sıfırla", description="Kullanıcının uyarılarını sıfırlar.")
@app_commands.describe(kullanıcı="Uyarıları sıfırlanacak kullanıcı.")
@app_commands.checks.has_permissions(administrator=True)
async def reset_warnings(
    interaction: discord.Interaction,
    kullanıcı: discord.Member
):
    cfg = get_guild_config(interaction.guild.id)

    gid = str(interaction.guild.id)
    uid = str(kullanıcı.id)

    cfg["warnings"].setdefault(gid, {})
    cfg["warnings"][gid][uid] = []

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} {kullanıcı.mention} kullanıcısının uyarıları sıfırlandı.",
        ephemeral=True
    )


@tree.command(name="kilitle", description="Kanalı kilitler.")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock_channel(interaction: discord.Interaction):
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


@tree.command(name="kilit-aç", description="Kanal kilidini açar.")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock_channel(interaction: discord.Interaction):
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


@tree.command(name="yavaş-mod", description="Kanalın yavaş modunu ayarlar.")
@app_commands.describe(saniye="0 ile 21600 arasında saniye.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(
    interaction: discord.Interaction,
    saniye: app_commands.Range[int, 0, 21600]
):
    await interaction.channel.edit(slowmode_delay=saniye)

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Yavaş mod **{saniye} saniye** olarak ayarlandı."
    )


@tree.command(name="duyuru", description="Sunucuda duyuru gönderir.")
@app_commands.describe(
    başlık="Duyuru başlığı.",
    mesaj="Duyuru mesajı."
)
@app_commands.checks.has_permissions(manage_messages=True)
async def announcement(
    interaction: discord.Interaction,
    başlık: str,
    mesaj: str
):
    embed = discord.Embed(
        title=başlık,
        description=mesaj,
        color=discord.Color.from_rgb(0, 0, 0)
    )

    embed.set_footer(text=f"{interaction.guild.name} • Dynex")

    await interaction.response.send_message(embed=embed)


# =========================================================
# DİL
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

    async def callback(self, interaction: discord.Interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["language"] = self.values[0]

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Dil başarıyla değiştirildi.",
            ephemeral=True
        )


class LanguageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(LanguageSelect())


@tree.command(name="dil", description="Sunucunun dilini ayarlar.")
@app_commands.checks.has_permissions(administrator=True)
async def language(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Sunucunuz için bir dil seçin:",
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# DM
# =========================================================

class DmRoleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(
            placeholder="DM gönderilecek rolü seçin...",
            min_values=1,
            max_values=1,
            custom_id="dynex_dm_role_select"
        )

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]

        await interaction.response.send_modal(
            DmModal(role)
        )


class DmModal(discord.ui.Modal, title="Toplu DM"):
    def __init__(self, role):
        super().__init__(timeout=300)

        self.role = role

        self.title_input = discord.ui.TextInput(
            label="Başlık",
            placeholder="DM başlığı",
            max_length=256,
            required=True
        )

        self.message_input = discord.ui.TextInput(
            label="Mesaj",
            placeholder="Gönderilecek mesaj",
            style=discord.TextStyle.paragraph,
            max_length=1900,
            required=True
        )

        self.add_item(self.title_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = get_guild_config(interaction.guild.id)

        if not can_use_dm(interaction.user, cfg):
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Bu komutu kullanma yetkiniz yok.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        sent = 0
        failed = 0

        embed = discord.Embed(
            title=self.title_input.value,
            description=self.message_input.value,
            color=discord.Color.from_rgb(0, 0, 0)
        )

        for member in self.role.members:
            if member.bot:
                continue

            try:
                await member.send(embed=embed)
                sent += 1
            except Exception:
                failed += 1

        await interaction.followup.send(
            f"{EMOJIS['yes']} DM işlemi tamamlandı.\n"
            f"Gönderildi: **{sent}**\n"
            f"Gönderilemedi: **{failed}**",
            ephemeral=True
        )


class DmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(DmRoleSelect())


@tree.command(name="dm", description="Belirli bir role toplu DM gönderir.")
async def dm_command(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild.id)

    if not can_use_dm(interaction.user, cfg):
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komutu kullanma yetkiniz yok.",
            ephemeral=True
        )

    await interaction.response.send_message(
        "DM gönderilecek rolü seçin:",
        view=DmView(),
        ephemeral=True
    )


# =========================================================
# AYARLAR
# =========================================================

class SettingsMainSelect(discord.ui.Select):
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
                label="Moderation",
                value="moderation",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="Logs",
                value="logs",
                emoji="📋"
            ),
            discord.SelectOption(
                label="Autorole",
                value="autorole",
                emoji="🎭"
            ),
            discord.SelectOption(
                label="Voice",
                value="voice",
                emoji="🔊"
            ),
            discord.SelectOption(
                label="Giveaway",
                value="giveaway",
                emoji="🎉"
            ),
            discord.SelectOption(
                label="DM",
                value="dm",
                emoji="✉️"
            ),
            discord.SelectOption(
                label="Language",
                value="language",
                emoji="🌐"
            )
        ]

        super().__init__(
            placeholder="Bir ayar kategorisi seçin...",
            options=options,
            custom_id="dynex_settings_main"
        )

    async def callback(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Bu menüyü sadece yöneticiler kullanabilir.",
                ephemeral=True
            )

        value = self.values[0]

        if value == "ticket":
            view = TicketSettingsView()
            embed = ticket_settings_embed(interaction.guild)

        elif value == "welcome":
            view = WelcomeSettingsView()
            embed = welcome_settings_embed(interaction.guild)

        elif value == "moderation":
            view = ModerationSettingsView()
            embed = moderation_settings_embed(interaction.guild)

        elif value == "logs":
            view = LogsSettingsView()
            embed = logs_settings_embed(interaction.guild)

        elif value == "autorole":
            view = AutoroleSettingsView()
            embed = autorole_settings_embed(interaction.guild)

        elif value == "voice":
            view = VoiceSettingsView()
            embed = voice_settings_embed(interaction.guild)

        elif value == "giveaway":
            view = GiveawaySettingsView()
            embed = giveaway_settings_embed(interaction.guild)

        elif value == "dm":
            view = DmSettingsView()
            embed = dm_settings_embed(interaction.guild)

        else:
            view = LanguageView()
            embed = discord.Embed(
                title="Language",
                description="Sunucunun dilini seçin.",
                color=discord.Color.from_rgb(0, 0, 0)
            )

        await interaction.response.edit_message(
            embed=embed,
            view=view
        )


class SettingsMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.add_item(SettingsMainSelect())


def settings_main_embed(guild):
    return discord.Embed(
        title=f"{EMOJIS['settings']} Dynex Ayarları",
        description=(
            "Aşağıdaki menüden ayarlamak istediğiniz sistemi seçin.\n\n"
            "Ayarları değiştirdiğinizde config.json dosyasına kaydedilir."
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )


# =========================================================
# AYARLAR - TICKET
# =========================================================

def ticket_settings_embed(guild):
    cfg = get_guild_config(guild.id)["ticket"]

    category = guild.get_channel(cfg.get("category_id")) if cfg.get("category_id") else None
    role = guild.get_role(cfg.get("staff_role_id")) if cfg.get("staff_role_id") else None
    channel = guild.get_channel(cfg.get("panel_channel_id")) if cfg.get("panel_channel_id") else None

    options = cfg.get("options", [])

    text = (
        f"Kategori: {category.mention if category else 'Ayarlanmadı'}\n"
        f"Yetkili rolü: {role.mention if role else 'Ayarlanmadı'}\n"
        f"Panel kanalı: {channel.mention if channel else 'Ayarlanmadı'}\n"
        f"Panel başlığı: `{cfg.get('panel_title')}`\n"
        f"Panel açıklaması: `{cfg.get('panel_description')}`\n"
        f"Buton: `{cfg.get('button_label')}`\n"
        f"Buton emojisi: `{cfg.get('button_emoji') or 'Yok'}`\n"
        f"Seçenek sayısı: `{len(options)}`"
    )

    return discord.Embed(
        title="Ticket Ayarları",
        description=text,
        color=discord.Color.from_rgb(0, 0, 0)
    )


class BackToSettingsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Geri",
            style=discord.ButtonStyle.secondary,
            emoji="↩️"
        )

    async def callback(self, interaction):
        await interaction.response.edit_message(
            embed=settings_main_embed(interaction.guild),
            view=SettingsMainView()
        )


class TicketCategorySelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Ticket kategorisini seçin...",
            channel_types=[discord.ChannelType.category],
            min_values=1,
            max_values=1,
            custom_id="dynex_ticket_category"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["ticket"]["category_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(interaction.guild),
            view=TicketSettingsView()
        )


class TicketStaffRoleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(
            placeholder="Ticket yetkili rolünü seçin...",
            min_values=1,
            max_values=1,
            custom_id="dynex_ticket_staff"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["ticket"]["staff_role_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(interaction.guild),
            view=TicketSettingsView()
        )


class TicketPanelChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Panel kanalını seçin...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.news
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_ticket_panel_channel"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["ticket"]["panel_channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(interaction.guild),
            view=TicketSettingsView()
        )


class TicketTextModal(discord.ui.Modal, title="Ticket Panel Ayarları"):
    panel_title = discord.ui.TextInput(
        label="Panel başlığı",
        max_length=256,
        required=True
    )

    panel_description = discord.ui.TextInput(
        label="Panel açıklaması",
        style=discord.TextStyle.paragraph,
        max_length=1500,
        required=True
    )

    button_label = discord.ui.TextInput(
        label="Buton adı",
        max_length=80,
        required=True
    )

    button_emoji = discord.ui.TextInput(
        label="Buton emojisi",
        placeholder="🎫 / :dikkat: / <:isim:id> / boş",
        max_length=100,
        required=False
    )

    panel_image = discord.ui.TextInput(
        label="Panel görsel URL",
        placeholder="Boş bırakabilirsiniz",
        max_length=500,
        required=False
    )

    async def on_submit(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        emoji = self.button_emoji.value.strip()

        if emoji and not emoji_exists(emoji, interaction.guild):
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Bu emoji sunucuda bulunamadı.",
                ephemeral=True
            )

        cfg["ticket"]["panel_title"] = self.panel_title.value
        cfg["ticket"]["panel_description"] = self.panel_description.value
        cfg["ticket"]["button_label"] = self.button_label.value
        cfg["ticket"]["button_emoji"] = emoji
        cfg["ticket"]["panel_image"] = self.panel_image.value.strip() or None

        save_config()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(interaction.guild),
            view=TicketSettingsView()
        )


class TicketOptionModal(discord.ui.Modal, title="Ticket Seçeneği Ekle"):
    name_input = discord.ui.TextInput(
        label="Seçenek adı",
        placeholder="Örn: Genel Destek",
        max_length=80,
        required=True
    )

    emoji_input = discord.ui.TextInput(
        label="Emoji",
        placeholder="🎫 / :dikkat: / <:isim:id> / boş",
        max_length=100,
        required=False
    )

    description_input = discord.ui.TextInput(
        label="Açıklama",
        max_length=150,
        required=False
    )

    async def on_submit(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        emoji = self.emoji_input.value.strip()

        if emoji and not emoji_exists(emoji, interaction.guild):
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Emoji bulunamadı.",
                ephemeral=True
            )

        cfg["ticket"]["options"].append({
            "name": self.name_input.value,
            "emoji": emoji,
            "description": self.description_input.value
        })

        save_config()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(interaction.guild),
            view=TicketSettingsView()
        )


class TicketOptionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Seçenek Ekle",
            style=discord.ButtonStyle.primary,
            emoji="➕",
            row=3
        )

    async def callback(self, interaction):
        await interaction.response.send_modal(TicketOptionModal())


class TicketClearOptionsButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Seçenekleri Temizle",
            style=discord.ButtonStyle.danger,
            emoji="🗑️",
            row=3
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["ticket"]["options"] = []
        save_config()

        await interaction.response.edit_message(
            embed=ticket_settings_embed(interaction.guild),
            view=TicketSettingsView()
        )


class TicketSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(TicketCategorySelect())
        self.add_item(TicketStaffRoleSelect())
        self.add_item(TicketPanelChannelSelect())
        self.add_item(TicketOptionButton())
        self.add_item(TicketClearOptionsButton())
        self.add_item(BackToSettingsButton())


# =========================================================
# AYARLAR - WELCOME
# =========================================================

def welcome_settings_embed(guild):
    cfg = get_guild_config(guild.id)["welcome"]

    channel = (
        guild.get_channel(cfg["channel_id"])
        if cfg.get("channel_id")
        else None
    )

    embed = discord.Embed(
        title="Welcome Ayarları",
        description=(
            f"Kanal: {channel.mention if channel else 'Ayarlanmadı'}\n"
            f"Başlık: `{cfg.get('title')}`\n"
            f"Açıklama: `{cfg.get('description')}`\n"
            f"Görsel: `{cfg.get('image') or 'Yok'}`\n"
            f"DM: `{cfg.get('dm_message') or 'Kapalı'}`"
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )

    return embed


class WelcomeChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Hoş geldin kanalını seçin...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.news
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_welcome_channel"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["welcome"]["channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=welcome_settings_embed(interaction.guild),
            view=WelcomeSettingsView()
        )


class WelcomeModal(discord.ui.Modal, title="Welcome Ayarları"):
    title_input = discord.ui.TextInput(
        label="Başlık",
        max_length=256,
        required=True
    )

    description_input = discord.ui.TextInput(
        label="Açıklama",
        style=discord.TextStyle.paragraph,
        max_length=1500,
        required=True
    )

    image_input = discord.ui.TextInput(
        label="Görsel URL",
        required=False,
        max_length=500
    )

    dm_input = discord.ui.TextInput(
        label="DM mesajı",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1500
    )

    async def on_submit(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["welcome"]["title"] = self.title_input.value
        cfg["welcome"]["description"] = self.description_input.value
        cfg["welcome"]["image"] = self.image_input.value.strip() or None
        cfg["welcome"]["dm_message"] = self.dm_input.value.strip() or None

        save_config()

        await interaction.response.edit_message(
            embed=welcome_settings_embed(interaction.guild),
            view=WelcomeSettingsView()
        )


class WelcomeSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(WelcomeChannelSelect())

        button = discord.ui.Button(
            label="Mesaj Ayarları",
            style=discord.ButtonStyle.primary,
            emoji="✏️",
            row=1
        )

        async def callback(interaction):
            await interaction.response.send_modal(WelcomeModal())

        button.callback = callback

        self.add_item(button)
        self.add_item(BackToSettingsButton())


# =========================================================
# AYARLAR - MODERATION
# =========================================================

def moderation_settings_embed(guild):
    cfg = get_guild_config(guild.id)["moderation"]

    log_channel = (
        guild.get_channel(cfg["log_channel_id"])
        if cfg.get("log_channel_id")
        else None
    )

    return discord.Embed(
        title="Moderation Ayarları",
        description=(
            f"Kötü kelime sayısı: `{len(cfg.get('bad_words', []))}`\n"
            f"Uyarı limiti: `{cfg.get('warning_limit')}`\n"
            f"Limit eylemi: `{cfg.get('warning_action')}`\n"
            f"Timeout süresi: `{cfg.get('timeout_duration')} dakika`\n"
            f"Anti-link: `{'Açık' if cfg.get('anti_link') else 'Kapalı'}`\n"
            f"Anti-spam: `{'Açık' if cfg.get('anti_spam') else 'Kapalı'}`\n"
            f"Log kanalı: {log_channel.mention if log_channel else 'Ayarlanmadı'}"
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )


class ModerationLogChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Moderasyon log kanalını seçin...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.news
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_moderation_log"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["moderation"]["log_channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=moderation_settings_embed(interaction.guild),
            view=ModerationSettingsView()
        )


class ModerationModal(discord.ui.Modal, title="Moderation Ayarları"):
    bad_words = discord.ui.TextInput(
        label="Kötü kelimeler",
        placeholder="kelime1, kelime2, kelime3",
        required=False,
        max_length=1500
    )

    warning_limit = discord.ui.TextInput(
        label="Uyarı limiti",
        placeholder="3",
        required=True,
        max_length=3
    )

    warning_action = discord.ui.TextInput(
        label="Limit eylemi",
        placeholder="timeout / kick / ban",
        required=True,
        max_length=20
    )

    timeout_duration = discord.ui.TextInput(
        label="Timeout süresi",
        placeholder="10",
        required=True,
        max_length=5
    )

    async def on_submit(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        try:
            limit = max(1, int(self.warning_limit.value))
            timeout_duration = max(1, int(self.timeout_duration.value))
        except ValueError:
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Sayısal değerleri doğru girin.",
                ephemeral=True
            )

        action = self.warning_action.value.lower().strip()

        if action not in ("timeout", "kick", "ban"):
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Eylem `timeout`, `kick` veya `ban` olmalı.",
                ephemeral=True
            )

        words = [
            x.strip().lower()
            for x in self.bad_words.value.split(",")
            if x.strip()
        ]

        cfg["moderation"]["bad_words"] = words
        cfg["moderation"]["warning_limit"] = limit
        cfg["moderation"]["warning_action"] = action
        cfg["moderation"]["timeout_duration"] = timeout_duration

        save_config()

        await interaction.response.edit_message(
            embed=moderation_settings_embed(interaction.guild),
            view=ModerationSettingsView()
        )


class ModerationToggleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

        cfg = get_guild_config(0) if False else None

        self.link_button = discord.ui.Button(
            label="Anti-link",
            style=discord.ButtonStyle.secondary,
            row=0
        )

        self.spam_button = discord.ui.Button(
            label="Anti-spam",
            style=discord.ButtonStyle.secondary,
            row=0
        )

        async def link_callback(interaction):
            config = get_guild_config(interaction.guild.id)
            config["moderation"]["anti_link"] = not config["moderation"]["anti_link"]
            save_config()

            await interaction.response.edit_message(
                embed=moderation_settings_embed(interaction.guild),
                view=ModerationSettingsView()
            )

        async def spam_callback(interaction):
            config = get_guild_config(interaction.guild.id)
            config["moderation"]["anti_spam"] = not config["moderation"]["anti_spam"]
            save_config()

            await interaction.response.edit_message(
                embed=moderation_settings_embed(interaction.guild),
                view=ModerationSettingsView()
            )

        self.link_button.callback = link_callback
        self.spam_button.callback = spam_callback

        self.add_item(self.link_button)
        self.add_item(self.spam_button)


class ModerationSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(ModerationLogChannelSelect())

        settings_button = discord.ui.Button(
            label="Uyarı Ayarları",
            style=discord.ButtonStyle.primary,
            emoji="⚙️",
            row=1
        )

        async def settings_callback(interaction):
            await interaction.response.send_modal(ModerationModal())

        settings_button.callback = settings_callback

        self.add_item(settings_button)

        link_button = discord.ui.Button(
            label="Anti-link Aç/Kapat",
            style=discord.ButtonStyle.secondary,
            row=2
        )

        spam_button = discord.ui.Button(
            label="Anti-spam Aç/Kapat",
            style=discord.ButtonStyle.secondary,
            row=2
        )

        async def link_callback(interaction):
            cfg = get_guild_config(interaction.guild.id)
            cfg["moderation"]["anti_link"] = not cfg["moderation"]["anti_link"]
            save_config()

            await interaction.response.edit_message(
                embed=moderation_settings_embed(interaction.guild),
                view=ModerationSettingsView()
            )

        async def spam_callback(interaction):
            cfg = get_guild_config(interaction.guild.id)
            cfg["moderation"]["anti_spam"] = not cfg["moderation"]["anti_spam"]
            save_config()

            await interaction.response.edit_message(
                embed=moderation_settings_embed(interaction.guild),
                view=ModerationSettingsView()
            )

        link_button.callback = link_callback
        spam_button.callback = spam_callback

        self.add_item(link_button)
        self.add_item(spam_button)
        self.add_item(BackToSettingsButton())


# =========================================================
# AYARLAR - LOGS
# =========================================================

def logs_settings_embed(guild):
    cfg = get_guild_config(guild.id)["logs"]

    channel = (
        guild.get_channel(cfg["channel_id"])
        if cfg.get("channel_id")
        else None
    )

    enabled = []

    for key in (
        "delete",
        "edit",
        "join",
        "leave",
        "ban",
        "kick",
        "timeout"
    ):
        if cfg.get(key):
            enabled.append(key)

    return discord.Embed(
        title="Logs Ayarları",
        description=(
            f"Log kanalı: {channel.mention if channel else 'Ayarlanmadı'}\n"
            f"Aktif loglar: `{', '.join(enabled) if enabled else 'Yok'}`"
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )


class LogsChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Log kanalını seçin...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.news
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_logs_channel"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)
        cfg["logs"]["channel_id"] = self.values[0].id
        save_config()

        await interaction.response.edit_message(
            embed=logs_settings_embed(interaction.guild),
            view=LogsSettingsView()
        )


class LogsToggleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Mesaj silme", value="delete"),
            discord.SelectOption(label="Mesaj düzenleme", value="edit"),
            discord.SelectOption(label="Üye katılma", value="join"),
            discord.SelectOption(label="Üye ayrılma", value="leave"),
            discord.SelectOption(label="Ban", value="ban"),
            discord.SelectOption(label="Kick", value="kick"),
            discord.SelectOption(label="Timeout", value="timeout")
        ]

        super().__init__(
            placeholder="Açıp kapatmak istediğiniz logu seçin...",
            options=options,
            custom_id="dynex_logs_toggle"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)["logs"]

        key = self.values[0]
        cfg[key] = not cfg.get(key, False)

        save_config()

        await interaction.response.edit_message(
            embed=logs_settings_embed(interaction.guild),
            view=LogsSettingsView()
        )


class LogsSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(LogsChannelSelect())
        self.add_item(LogsToggleSelect())
        self.add_item(BackToSettingsButton())


# =========================================================
# AYARLAR - AUTOROLE
# =========================================================

def autorole_settings_embed(guild):
    cfg = get_guild_config(guild.id)["autorole"]

    role = (
        guild.get_role(cfg["role_id"])
        if cfg.get("role_id")
        else None
    )

    return discord.Embed(
        title="Autorole Ayarları",
        description=(
            f"Katılanlara verilecek rol: "
            f"{role.mention if role else 'Ayarlanmadı'}"
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )


class AutoroleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(
            placeholder="Autorole seçin...",
            min_values=1,
            max_values=1,
            custom_id="dynex_autorole"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["autorole"]["role_id"] = self.values[0].id

        save_config()

        await interaction.response.edit_message(
            embed=autorole_settings_embed(interaction.guild),
            view=AutoroleSettingsView()
        )


class AutoroleDisableButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Autorole Kapat",
            style=discord.ButtonStyle.danger,
            row=1
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["autorole"]["role_id"] = None

        save_config()

        await interaction.response.edit_message(
            embed=autorole_settings_embed(interaction.guild),
            view=AutoroleSettingsView()
        )


class AutoroleSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(AutoroleSelect())
        self.add_item(AutoroleDisableButton())
        self.add_item(BackToSettingsButton())


# =========================================================
# AYARLAR - VOICE
# =========================================================

def voice_settings_embed(guild):
    cfg = get_guild_config(guild.id)["voice"]

    channel = (
        guild.get_channel(cfg["channel_id"])
        if cfg.get("channel_id")
        else None
    )

    return discord.Embed(
        title="Voice Ayarları",
        description=(
            f"Bildirim kanalı: {channel.mention if channel else 'Ayarlanmadı'}\n"
            f"Katılma mesajı: `{cfg.get('join_message')}`\n"
            f"Ayrılma mesajı: `{cfg.get('leave_message')}`"
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )


class VoiceNotificationChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Ses bildirim kanalını seçin...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.news
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_voice_notification"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["voice"]["channel_id"] = self.values[0].id

        save_config()

        await interaction.response.edit_message(
            embed=voice_settings_embed(interaction.guild),
            view=VoiceSettingsView()
        )


class VoiceModal(discord.ui.Modal, title="Voice Ayarları"):
    join_message = discord.ui.TextInput(
        label="Katılma mesajı",
        max_length=500,
        required=True
    )

    leave_message = discord.ui.TextInput(
        label="Ayrılma mesajı",
        max_length=500,
        required=True
    )

    async def on_submit(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["voice"]["join_message"] = self.join_message.value
        cfg["voice"]["leave_message"] = self.leave_message.value

        save_config()

        await interaction.response.edit_message(
            embed=voice_settings_embed(interaction.guild),
            view=VoiceSettingsView()
        )


class VoiceSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(VoiceNotificationChannelSelect())

        button = discord.ui.Button(
            label="Mesajları Düzenle",
            style=discord.ButtonStyle.primary,
            row=1
        )

        async def callback(interaction):
            await interaction.response.send_modal(VoiceModal())

        button.callback = callback

        self.add_item(button)
        self.add_item(BackToSettingsButton())


# =========================================================
# AYARLAR - GIVEAWAY
# =========================================================

def giveaway_settings_embed(guild):
    cfg = get_guild_config(guild.id)["giveaway"]

    role = (
        guild.get_role(cfg["staff_role_id"])
        if cfg.get("staff_role_id")
        else None
    )

    channel = (
        guild.get_channel(cfg["channel_id"])
        if cfg.get("channel_id")
        else None
    )

    log_channel = (
        guild.get_channel(cfg["log_channel_id"])
        if cfg.get("log_channel_id")
        else None
    )

    return discord.Embed(
        title="Giveaway Ayarları",
        description=(
            f"Yetkili rolü: {role.mention if role else 'Ayarlanmadı'}\n"
            f"Kanal: {channel.mention if channel else 'Ayarlanmadı'}\n"
            f"Log kanalı: {log_channel.mention if log_channel else 'Ayarlanmadı'}\n"
            f"Varsayılan kazanan: `{cfg.get('default_winners')}`\n"
            f"Varsayılan süre: `{cfg.get('default_duration')} dakika`"
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )


class GiveawayStaffRoleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(
            placeholder="Çekiliş yetkili rolünü seçin...",
            min_values=1,
            max_values=1,
            custom_id="dynex_giveaway_staff"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["giveaway"]["staff_role_id"] = self.values[0].id

        save_config()

        await interaction.response.edit_message(
            embed=giveaway_settings_embed(interaction.guild),
            view=GiveawaySettingsView()
        )


class GiveawayChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Çekiliş kanalını seçin...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.news
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_giveaway_channel"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["giveaway"]["channel_id"] = self.values[0].id

        save_config()

        await interaction.response.edit_message(
            embed=giveaway_settings_embed(interaction.guild),
            view=GiveawaySettingsView()
        )


class GiveawayLogChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="Çekiliş log kanalını seçin...",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.news
            ],
            min_values=1,
            max_values=1,
            custom_id="dynex_giveaway_log"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["giveaway"]["log_channel_id"] = self.values[0].id

        save_config()

        await interaction.response.edit_message(
            embed=giveaway_settings_embed(interaction.guild),
            view=GiveawaySettingsView()
        )


class GiveawayDefaultsModal(discord.ui.Modal, title="Giveaway Varsayılanları"):
    winners = discord.ui.TextInput(
        label="Kazanan sayısı",
        placeholder="1",
        required=True,
        max_length=3
    )

    duration = discord.ui.TextInput(
        label="Süre dakika",
        placeholder="10",
        required=True,
        max_length=3
    )

    async def on_submit(self, interaction):
        try:
            winners = max(1, int(self.winners.value))
            duration = max(1, min(40, int(self.duration.value)))
        except ValueError:
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Sayısal değer girin.",
                ephemeral=True
            )

        cfg = get_guild_config(interaction.guild.id)

        cfg["giveaway"]["default_winners"] = winners
        cfg["giveaway"]["default_duration"] = duration

        save_config()

        await interaction.response.edit_message(
            embed=giveaway_settings_embed(interaction.guild),
            view=GiveawaySettingsView()
        )


class GiveawaySettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(GiveawayStaffRoleSelect())
        self.add_item(GiveawayChannelSelect())
        self.add_item(GiveawayLogChannelSelect())

        button = discord.ui.Button(
            label="Varsayılanlar",
            style=discord.ButtonStyle.primary,
            row=3
        )

        async def callback(interaction):
            await interaction.response.send_modal(GiveawayDefaultsModal())

        button.callback = callback

        self.add_item(button)
        self.add_item(BackToSettingsButton())


# =========================================================
# AYARLAR - DM
# =========================================================

def dm_settings_embed(guild):
    cfg = get_guild_config(guild.id)["dm"]

    roles = []

    for role_id in cfg.get("allowed_role_ids", []):
        role = guild.get_role(role_id)
        if role:
            roles.append(role.mention)

    return discord.Embed(
        title="DM Ayarları",
        description=(
            "Aşağıdaki roller `/dm` komutunu kullanabilir.\n\n"
            f"{', '.join(roles) if roles else 'Rol ayarlanmadı.'}\n\n"
            "Yöneticiler her zaman `/dm` kullanabilir."
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )


class DmSettingsRoleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(
            placeholder="DM kullanabilecek rolü seçin...",
            min_values=1,
            max_values=1,
            custom_id="dynex_dm_settings_role"
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        role_id = self.values[0].id

        if role_id not in cfg["dm"]["allowed_role_ids"]:
            cfg["dm"]["allowed_role_ids"].append(role_id)

        save_config()

        await interaction.response.edit_message(
            embed=dm_settings_embed(interaction.guild),
            view=DmSettingsView()
        )


class DmClearRolesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Rolleri Temizle",
            style=discord.ButtonStyle.danger,
            row=1
        )

    async def callback(self, interaction):
        cfg = get_guild_config(interaction.guild.id)

        cfg["dm"]["allowed_role_ids"] = []

        save_config()

        await interaction.response.edit_message(
            embed=dm_settings_embed(interaction.guild),
            view=DmSettingsView()
        )


class DmSettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

        self.add_item(DmSettingsRoleSelect())
        self.add_item(DmClearRolesButton())
        self.add_item(BackToSettingsButton())


# =========================================================
# /AYARLAR
# =========================================================

@tree.command(name="ayarlar", description="Dynex sunucu ayarlarını açar.")
@app_commands.checks.has_permissions(administrator=True)
async def settings(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=settings_main_embed(interaction.guild),
        view=SettingsMainView(),
        ephemeral=True
    )


# =========================================================
# TICKET
# =========================================================

class TicketCloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Ticket Kapat",
            style=discord.ButtonStyle.danger,
            emoji="🔒",
            custom_id="dynex_ticket_close"
        )

    async def callback(self, interaction):
        channel = interaction.channel

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket kapatılıyor...",
            ephemeral=True
        )

        await asyncio.sleep(2)

        try:
            await channel.delete(reason="Ticket kapatıldı.")
        except Exception:
            pass


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCloseButton())


class TicketOpenButton(discord.ui.Button):
    def __init__(self, guild):
        cfg = get_guild_config(guild.id)["ticket"]

        emoji_value = cfg.get("button_emoji")
        emoji = parse_emoji(emoji_value, guild)

        super().__init__(
            label=cfg.get("button_label") or "Destek Talebi",
            style=discord.ButtonStyle.primary,
            emoji=emoji,
            custom_id="dynex_ticket_open"
        )

    async def callback(self, interaction):
        guild = interaction.guild
        cfg = get_guild_config(guild.id)["ticket"]

        category = (
            guild.get_channel(cfg.get("category_id"))
            if cfg.get("category_id")
            else None
        )

        staff_role = (
            guild.get_role(cfg.get("staff_role_id"))
            if cfg.get("staff_role_id")
            else None
        )

        if not category:
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Ticket kategorisi ayarlanmamış.",
                ephemeral=True
            )

        existing = discord.utils.find(
            lambda c: (
                isinstance(c, discord.TextChannel)
                and c.topic
                and f"ticket-owner:{interaction.user.id}" in c.topic
            ),
            guild.text_channels
        )

        if existing:
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Zaten açık bir ticketınız var: {existing.mention}",
                ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                read_message_history=True
            )
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        channel = await guild.create_text_channel(
            name=f"ticket-{clean_channel_name(interaction.user.name)}",
            category=category,
            overwrites=overwrites,
            topic=f"ticket-owner:{interaction.user.id}"
        )

        embed = discord.Embed(
            title="Ticket",
            description=(
                f"{interaction.user.mention} ticketınız oluşturuldu.\n"
                "Yetkililer kısa süre içerisinde ilgilenecektir."
            ),
            color=discord.Color.from_rgb(0, 0, 0)
        )

        await channel.send(
            content=staff_role.mention if staff_role else None,
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket oluşturuldu: {channel.mention}",
            ephemeral=True
        )


class TicketOpenView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.add_item(TicketOpenButton(guild))


@tree.command(name="ticket-panel", description="Ayarlanmış ticket panelini gönderir.")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild.id)["ticket"]

    channel = (
        interaction.guild.get_channel(cfg.get("panel_channel_id"))
        if cfg.get("panel_channel_id")
        else None
    )

    if not channel:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Ticket panel kanalı ayarlanmamış.",
            ephemeral=True
        )

    embed = discord.Embed(
        title=cfg.get("panel_title") or "Destek Talebi",
        description=cfg.get("panel_description") or "",
        color=discord.Color.from_rgb(0, 0, 0)
    )

    if cfg.get("panel_image"):
        embed.set_image(url=cfg["panel_image"])

    await channel.send(
        embed=embed,
        view=TicketOpenView(interaction.guild)
    )

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Ticket paneli {channel.mention} kanalına gönderildi.",
        ephemeral=True
    )


# =========================================================
# GIVEAWAY
# =========================================================

class GiveawayJoinButton(discord.ui.Button):
    def __init__(self, message_id):
        super().__init__(
            label="Çekilişe Katıl",
            style=discord.ButtonStyle.primary,
            emoji="🎉",
            custom_id=f"cekilise_katil:{message_id}"
        )

    async def callback(self, interaction):
        data = GIVEAWAYS.get(self.view.message_id)

        if not data:
            return await interaction.response.send_message(
                f"{EMOJIS['no']} Bu çekiliş sona ermiş.",
                ephemeral=True
            )

        if interaction.user.id in data["participants"]:
            data["participants"].remove(interaction.user.id)
            joined = False
        else:
            data["participants"].add(interaction.user.id)
            joined = True

        await interaction.response.edit_message(
            embed=build_giveaway_embed(data),
            view=self.view
        )

        if joined:
            await interaction.followup.send(
                f"{EMOJIS['yes']} Çekilişe katıldınız.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "Çekilişten çıktınız.",
                ephemeral=True
            )


class GiveawayView(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.add_item(GiveawayJoinButton(message_id))


def build_giveaway_embed(data):
    remaining = max(
        0,
        int(data["end_time"] - time.time())
    )

    embed = discord.Embed(
        title="🎉 Çekiliş",
        description=(
            f"**Ödül:** {data['reward']}\n"
            f"**Kazanan:** {data['winners']}\n"
            f"**Katılımcı:** {len(data['participants'])}\n"
            f"**Bitiş:** {format_duration(remaining)}"
        ),
        color=discord.Color.from_rgb(0, 0, 0)
    )

    return embed


async def finish_giveaway(message_id):
    data = GIVEAWAYS.get(message_id)

    if not data:
        return

    channel = bot.get_channel(data["channel_id"])

    if not channel:
        GIVEAWAYS.pop(message_id, None)
        return

    try:
        message = await channel.fetch_message(message_id)
    except Exception:
        GIVEAWAYS.pop(message_id, None)
        return

    participants = list(data["participants"])

    if participants:
        winners_count = min(data["winners"], len(participants))
        winner_ids = random.sample(participants, winners_count)

        mentions = ", ".join(f"<@{uid}>" for uid in winner_ids)

        result = f"🎉 Kazananlar: {mentions}\nÖdül: **{data['reward']}**"
    else:
        result = "Çekilişe kimse katılmadığı için kazanan olmadı."

    embed = discord.Embed(
        title="🎉 Çekiliş Sona Erdi",
        description=result,
        color=discord.Color.from_rgb(0, 0, 0)
    )

    try:
        await message.edit(embed=embed, view=None)
    except Exception:
        pass

    cfg = get_guild_config(data["guild_id"])
    log_channel_id = cfg["giveaway"].get("log_channel_id")

    if log_channel_id:
        log_channel = channel.guild.get_channel(log_channel_id)

        if log_channel:
            try:
                await log_channel.send(
                    f"Çekiliş sona erdi. Ödül: **{data['reward']}**"
                )
            except Exception:
                pass

    GIVEAWAYS.pop(message_id, None)


@tree.command(name="çekiliş", description="Çekiliş başlatır.")
@app_commands.describe(
    ödül="Çekiliş ödülü.",
    kazanan_sayısı="Kazanan sayısı.",
    süre="Süre dakika olarak, en fazla 40."
)
async def giveaway(
    interaction: discord.Interaction,
    ödül: str,
    kazanan_sayısı: app_commands.Range[int, 1, 20],
    süre: app_commands.Range[int, 1, 40]
):
    cfg = get_guild_config(interaction.guild.id)

    if not can_manage_giveaway(interaction.user, cfg):
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Çekiliş başlatma yetkiniz yok.",
            ephemeral=True
        )

    target_channel = (
        interaction.guild.get_channel(cfg["giveaway"].get("channel_id"))
        if cfg["giveaway"].get("channel_id")
        else interaction.channel
    )

    await interaction.response.defer(ephemeral=True)

    data = {
        "guild_id": interaction.guild.id,
        "channel_id": target_channel.id,
        "reward": ödül,
        "winners": kazanan_sayısı,
        "participants": set(),
        "end_time": time.time() + süre * 60
    }

    embed = build_giveaway_embed(data)

    message = await target_channel.send(
        embed=embed,
        view=GiveawayView(0)
    )

    data["message_id"] = message.id
    GIVEAWAYS[message.id] = data

    await message.edit(
        embed=build_giveaway_embed(data),
        view=GiveawayView(message.id)
    )

    await interaction.followup.send(
        f"{EMOJIS['yes']} Çekiliş başlatıldı: {message.jump_url}",
        ephemeral=True
    )

    await asyncio.sleep(süre * 60)

    await finish_giveaway(message.id)


@tree.command(name="çekiliş-bitir", description="Bir çekilişi erken bitirir.")
@app_commands.describe(mesaj_id="Çekiliş mesaj ID'si.")
async def end_giveaway(
    interaction: discord.Interaction,
    mesaj_id: str
):
    cfg = get_guild_config(interaction.guild.id)

    if not can_manage_giveaway(interaction.user, cfg):
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Çekiliş bitirme yetkiniz yok.",
            ephemeral=True
        )

    try:
        message_id = int(mesaj_id)
    except ValueError:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Geçerli bir mesaj ID girin.",
            ephemeral=True
        )

    if message_id not in GIVEAWAYS:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Bu çekiliş bulunamadı.",
            ephemeral=True
        )

    await finish_giveaway(message_id)

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Çekiliş bitirildi.",
        ephemeral=True
    )


# =========================================================
# EĞLENCE
# =========================================================

@tree.command(name="zar", description="Zar atar.")
async def dice(interaction: discord.Interaction):
    number = random.randint(1, 6)

    await interaction.response.send_message(
        f"🎲 Zar sonucu: **{number}**"
    )


@tree.command(name="yazı-tura", description="Yazı veya tura atar.")
async def coin(interaction: discord.Interaction):
    result = random.choice(["Yazı", "Tura"])

    await interaction.response.send_message(
        f"🪙 Sonuç: **{result}**"
    )


@tree.command(name="8ball", description="8ball sorusunu cevaplar.")
@app_commands.describe(soru="Sorunuz.")
async def eight_ball(
    interaction: discord.Interaction,
    soru: str
):
    answers = [
        "Evet.",
        "Hayır.",
        "Büyük ihtimalle.",
        "Pek sanmıyorum.",
        "Kesinlikle.",
        "Bunu zaman gösterecek.",
        "Şimdilik belli değil."
    ]

    await interaction.response.send_message(
        f"🎱 **{random.choice(answers)}**"
    )


@tree.command(name="sayı-tahmin", description="1-100 arasında sayı tahmin eder.")
async def number_guess(interaction: discord.Interaction):
    number = random.randint(1, 100)

    await interaction.response.send_message(
        f"🎯 Aklımdan **1-100** arasında bir sayı tuttum.\n"
        f"Sayım: **{number}**",
        ephemeral=True
    )


# =========================================================
# SAYI OYUNU
# =========================================================

@tree.command(name="sayı-oyunu-ayarla", description="Sayı oyununu başlatır.")
@app_commands.describe(
    hedef="Ulaşılacak sayı.",
    kanal="Oyunun oynanacağı kanal."
)
@app_commands.checks.has_permissions(administrator=True)
async def number_game_setup(
    interaction: discord.Interaction,
    hedef: app_commands.Range[int, 1, 100000],
    kanal: discord.TextChannel = None
):
    cfg = get_guild_config(interaction.guild.id)

    kanal = kanal or interaction.channel

    cfg["games"]["number_channel_id"] = kanal.id
    cfg["games"]["number_target"] = hedef
    cfg["games"]["number_current"] = 0
    cfg["games"]["number_started"] = True

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Sayı oyunu {kanal.mention} kanalında başlatıldı.\n"
        f"Hedef: **{hedef}**"
    )


@tree.command(name="sayı-oyunu-durdur", description="Sayı oyununu durdurur.")
@app_commands.checks.has_permissions(administrator=True)
async def number_game_stop(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild.id)

    cfg["games"]["number_started"] = False

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Sayı oyunu durduruldu."
    )


# =========================================================
# KELİME OYUNU
# =========================================================

@tree.command(name="kelime-oyunu-ayarla", description="Kelime oyununu başlatır.")
@app_commands.describe(kanal="Oyunun oynanacağı kanal.")
@app_commands.checks.has_permissions(administrator=True)
async def word_game_setup(
    interaction: discord.Interaction,
    kanal: discord.TextChannel = None
):
    cfg = get_guild_config(interaction.guild.id)

    kanal = kanal or interaction.channel

    cfg["games"]["word_channel_id"] = kanal.id
    cfg["games"]["word_started"] = True
    cfg["games"]["word_current"] = None

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Kelime oyunu {kanal.mention} kanalında başlatıldı."
    )


@tree.command(name="kelime-oyunu-durdur", description="Kelime oyununu durdurur.")
@app_commands.checks.has_permissions(administrator=True)
async def word_game_stop(interaction: discord.Interaction):
    cfg = get_guild_config(interaction.guild.id)

    cfg["games"]["word_started"] = False

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} Kelime oyunu durduruldu."
    )


@tree.command(name="kelime-ekle", description="Kelime oyununa kelime ekler.")
@app_commands.describe(kelime="Eklenecek kelime.")
@app_commands.checks.has_permissions(administrator=True)
async def add_word(
    interaction: discord.Interaction,
    kelime: str
):
    cfg = get_guild_config(interaction.guild.id)

    kelime = kelime.strip().lower()

    if not kelime:
        return await interaction.response.send_message(
            f"{EMOJIS['no']} Kelime boş olamaz.",
            ephemeral=True
        )

    if kelime not in cfg["games"]["words"]:
        cfg["games"]["words"].append(kelime)

    save_config()

    await interaction.response.send_message(
        f"{EMOJIS['yes']} `{kelime}` kelimesi eklendi."
    )


@tree.command(name="kelime-çıkar", description="Kelime oyunundan kelime çıkarır.")
@app_commands.describe(kelime="Çıkarılacak kelime.")
@app_commands.checks.has_permissions(administrator=True)
async def remove_word(
    interaction: discord.Interaction,
    kelime: str
):
    cfg = get_guild_config(interaction.guild.id)

    kelime = kelime.strip().lower()

    if kelime in cfg["games"]["words"]:
        cfg["games"]["words"].remove(kelime)
        save_config()

        return await interaction.response.send_message(
            f"{EMOJIS['yes']} `{kelime}` kelimesi çıkarıldı."
        )

    await interaction.response.send_message(
        f"{EMOJIS['no']} Bu kelime kayıtlı değil.",
        ephemeral=True
    )


# =========================================================
# MESAJ SİSTEMLERİ
# =========================================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.guild:
        return

    cfg = get_guild_config(message.guild.id)

    # -------------------------
    # SAYI OYUNU
    # -------------------------

    games = cfg["games"]

    if (
        games.get("number_started")
        and games.get("number_channel_id") == message.channel.id
    ):
        try:
            number = int(message.content.strip())
        except ValueError:
            number = None

        if number is not None:
            current = int(games.get("number_current", 0))
            target = int(games.get("number_target", 50))

            if number == current + 1:
                games["number_current"] = number

                try:
                    await message.add_reaction("✅")
                except Exception:
                    pass

                if number >= target:
                    games["number_started"] = False

                    await message.channel.send(
                        f"🎉 Tebrikler! **{message.author.mention}** "
                        f"hedef olan **{target}** sayısına ulaştı."
                    )

                save_config()

            elif number != current:
                try:
                    await message.delete()
                except Exception:
                    pass

                await send_log(
                    message.guild,
                    "Sayı Oyunu Hatası",
                    f"{message.author.mention} yanlış sayı gönderdi.",
                    None
                )

    # -------------------------
    # KELİME OYUNU
    # -------------------------

    if (
        games.get("word_started")
        and games.get("word_channel_id") == message.channel.id
    ):
        word = message.content.strip().lower()

        if games.get("words"):
            if word in games["words"]:
                games["word_current"] = word

                try:
                    await message.add_reaction("✅")
                except Exception:
                    pass

                save_config()

        elif games.get("word_current"):
            previous = games["word_current"]

            if word.startswith(previous[-1:]):
                games["word_current"] = word
                save_config()

    # -------------------------
    # ANTI-LINK
    # -------------------------

    moderation = cfg["moderation"]

    if moderation.get("anti_link"):
        if re.search(r"(https?://|www\.)", message.content.lower()):
            if not message.author.guild_permissions.manage_messages:
                try:
                    await message.delete()
                except Exception:
                    pass

                try:
                    await message.channel.send(
                        f"{EMOJIS['no']} {message.author.mention} link göndermek yasak.",
                        delete_after=4
                    )
                except Exception:
                    pass

    # -------------------------
    # KÖTÜ KELİME
    # -------------------------

    bad_words = moderation.get("bad_words", [])

    if bad_words:
        lowered = message.content.lower()

        if any(word in lowered for word in bad_words):
            if not message.author.guild_permissions.manage_messages:
                try:
                    await message.delete()
                except Exception:
                    pass

    # -------------------------
    # ANTI-SPAM
    # -------------------------

    if moderation.get("anti_spam"):
        key = (message.guild.id, message.author.id)

        now = time.time()

        SPAM_CACHE.setdefault(key, [])

        SPAM_CACHE[key] = [
            timestamp
            for timestamp in SPAM_CACHE[key]
            if now - timestamp <= 6
        ]

        SPAM_CACHE[key].append(now)

        if len(SPAM_CACHE[key]) >= 5:
            SPAM_CACHE[key].clear()

            try:
                await message.author.timeout(
                    discord.utils.utcnow() + timedelta(seconds=30),
                    reason="Anti-spam"
                )

                await message.channel.send(
                    f"{EMOJIS['no']} {message.author.mention} spam nedeniyle "
                    f"30 saniye timeout aldı.",
                    delete_after=5
                )

            except Exception:
                pass

    await bot.process_commands(message)


# =========================================================
# WELCOME / AUTOROLE
# =========================================================

@bot.event
async def on_member_join(member):
    cfg = get_guild_config(member.guild.id)

    welcome = cfg["welcome"]

    channel = (
        member.guild.get_channel(welcome.get("channel_id"))
        if welcome.get("channel_id")
        else None
    )

    if channel:
        title = welcome.get("title", "Sunucumuza Hoş Geldin!")
        description = welcome.get(
            "description",
            "{member} sunucumuza katıldı."
        )

        description = description.replace(
            "{member}",
            member.mention
        ).replace(
            "{server}",
            member.guild.name
        )

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.from_rgb(0, 0, 0)
        )

        if welcome.get("image"):
            embed.set_image(url=welcome["image"])

        try:
            await channel.send(embed=embed)
        except Exception:
            pass

    role_id = cfg["autorole"].get("role_id")

    if role_id:
        role = member.guild.get_role(role_id)

        if role:
            try:
                await member.add_roles(
                    role,
                    reason="Dynex Autorole"
                )
            except Exception:
                pass

    dm_message = welcome.get("dm_message")

    if dm_message:
        try:
            await member.send(
                dm_message.replace(
                    "{member}",
                    member.mention
                ).replace(
                    "{server}",
                    member.guild.name
                )
            )
        except Exception:
            pass

    await send_log(
        member.guild,
        "Üye Katıldı",
        f"{member.mention} sunucuya katıldı.",
        "join"
    )


@bot.event
async def on_member_remove(member):
    await send_log(
        member.guild,
        "Üye Ayrıldı",
        f"{member.mention} sunucudan ayrıldı.",
        "leave"
    )


# =========================================================
# MESAJ LOGLARI
# =========================================================

@bot.event
async def on_message_delete(message):
    if not message.guild or message.author.bot:
        return

    cfg = get_guild_config(message.guild.id)

    if not cfg["logs"].get("delete"):
        return

    content = message.content or "Mesaj içeriği yok."

    if len(content) > 1500:
        content = content[:1500] + "..."

    await send_log(
        message.guild,
        "Mesaj Silindi",
        f"**Kullanıcı:** {message.author.mention}\n"
        f"**Kanal:** {message.channel.mention}\n"
        f"**Mesaj:** {content}",
        "delete"
    )


@bot.event
async def on_message_edit(before, after):
    if not before.guild or before.author.bot:
        return

    if before.content == after.content:
        return

    await send_log(
        before.guild,
        "Mesaj Düzenlendi",
        f"**Kullanıcı:** {before.author.mention}\n"
        f"**Kanal:** {before.channel.mention}\n"
        f"**Eski:** {before.content[:1000]}\n"
        f"**Yeni:** {after.content[:1000]}",
        "edit"
    )


@bot.event
async def on_member_ban(guild, user):
    await send_log(
        guild,
        "Üye Banlandı",
        f"{user.mention if hasattr(user, 'mention') else user} banlandı.",
        "ban"
    )


# =========================================================
# VOICE
# =========================================================

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    cfg = get_guild_config(member.guild.id)
    voice = cfg["voice"]

    channel_id = voice.get("channel_id")

    if not channel_id:
        return

    channel = member.guild.get_channel(channel_id)

    if not channel:
        return

    if before.channel is None and after.channel is not None:
        message = voice.get(
            "join_message",
            "{member} ses kanalına katıldı."
        )

        message = message.replace(
            "{member}",
            member.mention
        ).replace(
            "{channel}",
            after.channel.name
        )

        try:
            await channel.send(message)
        except Exception:
            pass

    elif before.channel is not None and after.channel is None:
        message = voice.get(
            "leave_message",
            "{member} ses kanalından ayrıldı."
        )

        message = message.replace(
            "{member}",
            member.mention
        ).replace(
            "{channel}",
            before.channel.name
        )

        try:
            await channel.send(message)
        except Exception:
            pass


# =========================================================
# HATA YÖNETİMİ
# =========================================================

@tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):
    original = error

    if isinstance(error, app_commands.CommandInvokeError):
        original = error.original

    if isinstance(original, app_commands.MissingPermissions):
        message = f"{EMOJIS['no']} Bu komut için gerekli yetkiye sahip değilsiniz."

    elif isinstance(original, discord.Forbidden):
        message = f"{EMOJIS['no']} Botun bu işlemi yapmaya yetkisi yok."

    elif isinstance(original, app_commands.TransformerError):
        message = f"{EMOJIS['no']} Girilen değer geçersiz."

    else:
        print("Slash komut hatası:", repr(original))
        message = f"{EMOJIS['no']} Komut çalıştırılırken bir hata oluştu."

    try:
        if interaction.response.is_done():
            await interaction.followup.send(
                message,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                message,
                ephemeral=True
            )
    except Exception:
        pass


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():
    global TICKET_VIEW_REGISTERED

    if not TICKET_VIEW_REGISTERED:
        bot.add_view(TicketCloseView())
        TICKET_VIEW_REGISTERED = True

    try:
        synced = await tree.sync()

        print(
            f"Dynex giriş yaptı: {bot.user} | "
            f"{len(bot.guilds)} sunucu | "
            f"{len(synced)} slash komut"
        )

    except Exception as e:
        print("Slash sync hatası:", repr(e))


# =========================================================
# BAŞLAT
# =========================================================

if not TOKEN:
    print("HATA: DISCORD_TOKEN environment variable bulunamadı.")
else:
    bot.run(TOKEN)
