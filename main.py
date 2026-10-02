# main.py
# Dynex Discord Bot
# Python 3.14 / discord.py

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
# AYARLAR
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
# VARSAYILAN CONFIG
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
    "warnings": {},
    "giveaways": {}
}


# =========================================================
# CONFIG YARDIMCILARI
# =========================================================

def deep_merge(default, current):
    if isinstance(default, dict) and isinstance(current, dict):
        result = {}

        for key, value in default.items():
            if key in current:
                result[key] = deep_merge(value, current[key])
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
                json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=4),
                encoding="utf-8"
            )
            return json.loads(json.dumps(DEFAULT_CONFIG))

        data = json.loads(
            CONFIG_FILE.read_text(encoding="utf-8")
        )

        merged = deep_merge(DEFAULT_CONFIG, data)

        # Eski hazır ticket seçeneklerini temizle
        options = merged.get("ticket", {}).get("options", [])

        if options == [
            {"name": "Destek", "emoji": "🎫"},
            {"name": "Şikayet", "emoji": "⚠️"}
        ]:
            merged["ticket"]["options"] = []

        return merged

    except Exception as e:
        print("Config yükleme hatası:", repr(e))
        return json.loads(json.dumps(DEFAULT_CONFIG))


CONFIG = load_config()


def save_config():
    try:
        CONFIG_FILE.write_text(
            json.dumps(CONFIG, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )
    except Exception as e:
        print("Config kayıt hatası:", repr(e))


# =========================================================
# EMOJİ YARDIMCILARI
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

        emoji = discord.utils.get(
            guild.emojis,
            name=name
        )

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

        return (
            discord.utils.get(
                guild.emojis,
                name=name
            )
            is not None
        )

    if value.startswith("<:") or value.startswith("<a:"):
        try:
            emoji = discord.PartialEmoji.from_str(value)
            return emoji.id is not None
        except Exception:
            return False

    return True


# =========================================================
# GENEL YARDIMCILAR
# =========================================================

def uptime_text():
    delta = datetime.now(timezone.utc) - START_TIME

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []

    if days:
        parts.append(f"{days}g")

    if hours:
        parts.append(f"{hours}s")

    if minutes:
        parts.append(f"{minutes}dk")

    parts.append(f"{seconds}sn")

    return " ".join(parts)


def get_language(guild_id):
    return CONFIG.get("language", {}).get(str(guild_id), "tr")


def get_text(guild_id, key, **kwargs):
    language = get_language(guild_id)

    texts = {
        "tr": {
            "language_saved": "Dil başarıyla değiştirildi.",
            "language_title": "Dil Ayarları",
            "language_description": "Botun bu sunucudaki dilini seçin.",
        },
        "en": {
            "language_saved": "Language successfully changed.",
            "language_title": "Language Settings",
            "language_description": "Choose the bot language for this server.",
        },
        "az": {
            "language_saved": "Dil uğurla dəyişdirildi.",
            "language_title": "Dil Ayarları",
            "language_description": "Botun bu serverdə dilini seçin.",
        }
    }

    text = texts.get(language, texts["tr"]).get(key, key)

    try:
        return text.format(**kwargs)
    except Exception:
        return text


async def send_log(guild, message):
    if guild is None:
        return

    channel_id = CONFIG.get("logs", {}).get("channel_id")

    if not channel_id:
        channel_id = CONFIG.get("moderation", {}).get("log_channel_id")

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if channel is None:
        return

    try:
        await channel.send(message)
    except Exception as e:
        print("Log gönderme hatası:", repr(e))


def is_admin(interaction):
    return interaction.user.guild_permissions.administrator


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.messages = True
intents.voice_states = True


class DynexBot(commands.Bot):

    async def setup_hook(self):
        try:
            self.add_view(TicketCloseView())
        except Exception as e:
            print("Ticket view yükleme hatası:", repr(e))

        try:
            synced = await self.tree.sync()
            print(f"{len(synced)} slash komutu senkronize edildi.")
        except Exception as e:
            print("Slash sync hatası:", repr(e))


bot = DynexBot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# =========================================================
# TICKET KAPATMA
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
        channel = interaction.channel

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                f"{EMOJIS['no']} Bu işlem sadece ticket kanalında kullanılabilir.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket kapatılıyor...",
            ephemeral=True
        )

        await asyncio.sleep(1)

        try:
            await channel.delete()
        except Exception as e:
            print("Ticket kapatma hatası:", repr(e))


# =========================================================
# TICKET PANEL
# =========================================================

class TicketOptionView(discord.ui.View):

    def __init__(self, options):
        super().__init__(timeout=None)

        for index, option in enumerate(options):
            name = option.get("name", f"Ticket {index + 1}")
            emoji_value = option.get("emoji", "")

            emoji = parse_emoji(
                emoji_value,
                None
            )

            button = discord.ui.Button(
                label=name[:80],
                style=discord.ButtonStyle.primary,
                custom_id=f"dynex_ticket_{index}"
            )

            if emoji is not None:
                try:
                    button.emoji = emoji
                except Exception:
                    pass

            async def callback(
                interaction: discord.Interaction,
                idx=index
            ):
                await create_ticket(
                    interaction,
                    idx
                )

            button.callback = callback
            self.add_item(button)


async def create_ticket(
    interaction: discord.Interaction,
    option_index: int
):
    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Bu komut sadece sunucularda kullanılabilir.",
            ephemeral=True
        )
        return

    options = CONFIG["ticket"]["options"]

    if option_index >= len(options):
        await interaction.response.send_message(
            f"{EMOJIS['no']} Ticket seçeneği bulunamadı.",
            ephemeral=True
        )
        return

    option = options[option_index]
    ticket_name = option.get("name", "ticket")

    existing = discord.utils.get(
        guild.text_channels,
        name=f"ticket-{interaction.user.id}"
    )

    if existing:
        await interaction.response.send_message(
            f"{EMOJIS['no']} Zaten açık bir ticketın var: {existing.mention}",
            ephemeral=True
        )
        return

    category_id = CONFIG["ticket"].get("category_id")
    staff_role_id = CONFIG["ticket"].get("staff_role_id")

    category = (
        guild.get_channel(category_id)
        if category_id
        else None
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

    if staff_role_id:
        staff_role = guild.get_role(staff_role_id)

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

    try:
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.id}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"{EMOJIS['dynex']} {ticket_name}",
            description=(
                f"{interaction.user.mention}, ticketın oluşturuldu.\n\n"
                "Yetkililer en kısa sürede ilgilenecektir."
            ),
            color=discord.Color.blurple()
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} Ticket oluşturuldu: {channel.mention}",
            ephemeral=True
        )

    except Exception as e:
        print("Ticket oluşturma hatası:", repr(e))

        await interaction.response.send_message(
            f"{EMOJIS['no']} Ticket oluşturulamadı.",
            ephemeral=True
        )


# =========================================================
# /DİL
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

    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if not interaction.guild:
            return

        CONFIG.setdefault("language", {})[
            str(interaction.guild.id)
        ] = self.values[0]

        save_config()

        await interaction.response.send_message(
            f"{EMOJIS['yes']} "
            f"{get_text(interaction.guild.id, 'language_saved')}",
            ephemeral=True
        )


class LanguageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(LanguageSelect())


@bot.tree.command(
    name="dil",
    description="Botun sunucu dilini değiştirir."
)
async def dil(interaction: discord.Interaction):
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
        title=get_text(
            interaction.guild.id,
            "language_title"
        ),
        description=get_text(
            interaction.guild.id,
            "language_description"
        ),
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=LanguageView(),
        ephemeral=True
    )


# =========================================================
# /BOT
# =========================================================

@bot.tree.command(
    name="bot",
    description="Dynex botunun mevcut durumunu gösterir."
)
async def bot_status(interaction: discord.Interaction):

    try:
        guild_count = len(bot.guilds)

        support_guild = bot.get_guild(
            SUPPORT_SERVER_ID
        )

        if support_guild is not None:
            support_member_count = support_guild.member_count

            if support_member_count is None:
                support_member_count = len(
                    support_guild.members
                )
        else:
            support_member_count = "Bilinmiyor"

        owner_text = "Bilinmiyor"

        try:
            application = await bot.application_info()

            if application.owner:
                owner_text = application.owner.mention

        except Exception as e:
            print("Owner alınamadı:", repr(e))

        embed = discord.Embed(
            title="Dynex Durum",
            color=discord.Color.black()
        )

        embed.description = (
            f"**Sunucu sayısı:** `{guild_count}`\n\n"
            f"**Destek sunucusu üye sayısı:** "
            f"`{support_member_count}`\n\n"
            f"**Prefix yani . Komut:** `D.`\n\n"
            f"**Aktif kalma süresi:** `{uptime_text()}`\n\n"
            f"**Bot sahibi:** {owner_text}"
        )

        await interaction.response.send_message(
            embed=embed
        )

    except Exception as e:
        print("/bot hatası:", repr(e))

        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    f"{EMOJIS['no']} Bot bilgileri alınırken hata oluştu.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"{EMOJIS['no']} Bot bilgileri alınırken hata oluştu.",
                    ephemeral=True
                )
        except Exception as follow_error:
            print("Hata mesajı gönderilemedi:", repr(follow_error))


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun gecikmesini gösterir."
)
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

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

    emoji_map = {
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
            f"{emoji_map.get(status, '')} `{status}`"
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
                "`/sil`"
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
                "`/kilitle`\n"
                "`/kilit-aç`\n"
                "`/yavaş-mod`"
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
        super().__init__(timeout=180)
        self.add_item(HelpSelect())


@bot.tree.command(
    name="yardım",
    description="Dynex komutlarını gösterir."
)
async def yardim(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Dynex Yardım",
        description="Bir kategori seçerek komutları görüntüleyebilirsin.",
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
async def sunucu(interaction: discord.Interaction):

    guild = interaction.guild

    if guild is None:
        return

    embed = discord.Embed(
        title=f"{guild.name} Sunucu Bilgileri",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Sunucu sahibi",
        value=guild.owner.mention if guild.owner else "Bilinmiyor",
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
        embed.set_thumbnail(url=guild.icon.url)

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

    member = kullanıcı or interaction.user

    embed = discord.Embed(
        title="Kullanıcı Bilgileri",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.description = (
        f"**Kullanıcı:** {member.mention}\n\n"
        f"**ID:** `{member.id}`\n\n"
        f"**Hesap oluşturma:** "
        f"<t:{int(member.created_at.timestamp())}:F>\n\n"
        f"**Sunucuya katılma:** "
        f"<t:{int(member.joined_at.timestamp())}:F>"
        if member.joined_at
        else
        f"**Kullanıcı:** {member.mention}\n\n"
        f"**ID:** `{member.id}`"
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
    kullanıcı="Avatarını görmek istediğin kullanıcı."
)
async def avatar(
    interaction: discord.Interaction,
    kullanıcı: discord.Member | None = None
):

    member = kullanıcı or interaction.user

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
async def roller(interaction: discord.Interaction):

    guild = interaction.guild

    if guild is None:
        return

    roles = [
        role.mention
        for role in reversed(guild.roles)
        if role != guild.default_role
    ]

    if not roles:
        description = "Sunucuda rol bulunmuyor."
    else:
        description = "\n".join(roles)

    if len(description) > 4000:
        description = description[:3990] + "\n..."

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
        print("/temizle hatası:", repr(e))

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
        print("/sil hatası:", repr(e))

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
        await kullanıcı.ban(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} yasaklandı."
        )

        await send_log(
            interaction.guild,
            f"🔨 {kullanıcı} banlandı.\nSebep: {sebep}"
        )

    except Exception as e:
        print("/ban hatası:", repr(e))

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
        await kullanıcı.kick(reason=sebep)

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} sunucudan atıldı."
        )

        await send_log(
            interaction.guild,
            f"👢 {kullanıcı} kicklendi.\nSebep: {sebep}"
        )

    except Exception as e:
        print("/kick hatası:", repr(e))

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
            timedelta(minutes=dakika),
            reason=sebep
        )

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {kullanıcı.mention} `{dakika}` dakika timeoutlandı."
        )

        await send_log(
            interaction.guild,
            f"⏱️ {kullanıcı} timeoutlandı.\nSüre: {dakika} dakika\nSebep: {sebep}"
        )

    except Exception as e:
        print("/timeout hatası:", repr(e))

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

    guild_id = str(interaction.guild.id)
    user_id = str(kullanıcı.id)

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
                    timedelta(minutes=minutes),
                    reason="Uyarı sınırına ulaşıldı."
                )

                await interaction.channel.send(
                    f"{EMOJIS['alarm']} "
                    f"{kullanıcı.mention} uyarı sınırına ulaştı ve "
                    f"`{minutes}` dakika timeoutlandı."
                )

            except Exception as e:
                print("Uyarı timeout hatası:", repr(e))


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

    guild_id = str(interaction.guild.id)
    user_id = str(kullanıcı.id)

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
        text=f"{interaction.guild.name}"
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
async def kilitle(interaction: discord.Interaction):

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
async def kilit_ac(interaction: discord.Interaction):

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
            text = f"Yavaş mod `{saniye}` saniye olarak ayarlandı."

        await interaction.response.send_message(
            f"{EMOJIS['yes']} {text}"
        )

    except Exception as e:
        print("/yavaş-mod hatası:", repr(e))

        await interaction.response.send_message(
            f"{EMOJIS['no']} Yavaş mod ayarlanamadı.",
            ephemeral=True
        )


# =========================================================
# /AYARLAR
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
                "Ticket kategorisi, yetkili rolü, panel kanalı ve "
                "ticket seçeneklerini ayarlamak için bu bölümü kullanabilirsin.\n\n"
                "Ticket seçenekleri başlangıçta boştur."
            )

        elif category == "welcome":
            description = (
                "**Welcome Ayarları**\n\n"
                "Karşılama kanalı, başlık, açıklama, görsel ve DM mesajını "
                "yapılandırabilirsin."
            )

        elif category == "autorole":
            description = (
                "**Otorol Ayarları**\n\n"
                "Sunucuya yeni katılan üyelere otomatik verilecek rolü ayarlayabilirsin."
            )

        elif category == "moderation":
            description = (
                "**Moderasyon Ayarları**\n\n"
                "Kötü kelimeler, uyarı sınırı, timeout, link engelleme, "
                "spam ve moderasyon log kanalını yapılandırabilirsin."
            )

        elif category == "logs":
            description = (
                "**Log Ayarları**\n\n"
                "Silinen mesaj, düzenlenen mesaj, giriş, çıkış, ban, kick ve "
                "timeout olaylarının log kanalını ayarlayabilirsin."
            )

        elif category == "voice":
            description = (
                "**Ses Bildirimleri**\n\n"
                "Ses kanalına giriş ve çıkış bildirimlerini ayarlayabilirsin."
            )

        else:
            description = (
                "**Çekiliş Ayarları**\n\n"
                "Yetkili rolünü, kanalını, log kanalını, varsayılan kazanan "
                "sayısını ve varsayılan süreyi ayarlayabilirsin."
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


class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SettingsSelect())


@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönetir."
)
async def ayarlar(interaction: discord.Interaction):

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
# EVENTLER
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


@bot.event
async def on_member_join(member):

    guild = member.guild

    # Otorol
    role_id = CONFIG.get(
        "autorole",
        {}
    ).get(
        "role_id"
    )

    if role_id:
        role = guild.get_role(role_id)

        if role:
            try:
                await member.add_roles(role)
            except Exception as e:
                print("Otorol hatası:", repr(e))

    # Welcome
    welcome_config = CONFIG.get(
        "welcome",
        {}
    )

    channel_id = welcome_config.get(
        "channel_id"
    )

    if channel_id:
        channel = guild.get_channel(
            channel_id
        )

        if channel:
            description = welcome_config.get(
                "description",
                "{member}, sunucumuza hoş geldin!"
            ).replace(
                "{member}",
                member.mention
            )

            embed = discord.Embed(
                title=welcome_config.get(
                    "title",
                    "Hoş Geldin!"
                ),
                description=description,
                color=discord.Color.blurple()
            )

            image = welcome_config.get(
                "image",
                ""
            )

            if image:
                embed.set_image(url=image)

            try:
                await channel.send(
                    embed=embed
                )
            except Exception as e:
                print("Welcome hatası:", repr(e))

    # Welcome DM
    dm_message = welcome_config.get(
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


@bot.event
async def on_member_remove(member):

    await send_log(
        member.guild,
        f"📤 {member} sunucudan ayrıldı."
    )


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not message.guild:
        return

    moderation = CONFIG.get(
        "moderation",
        {}
    )

    content_lower = message.content.lower()

    # Kötü kelime kontrolü
    bad_words = moderation.get(
        "bad_words",
        []
    )

    for word in bad_words:

        if word.lower() in content_lower:

            try:
                await message.delete()

                await message.channel.send(
                    f"{EMOJIS['no']} {message.author.mention}, "
                    "bu kelimeyi kullanamazsın.",
                    delete_after=5
                )

            except Exception as e:
                print("Kötü kelime hatası:", repr(e))

            break

    # Link kontrolü
    if moderation.get("anti_link", False):

        if (
            "http://" in content_lower
            or "https://" in content_lower
            or "discord.gg/" in content_lower
        ):

            if not message.author.guild_permissions.manage_messages:

                try:
                    await message.delete()

                    await message.channel.send(
                        f"{EMOJIS['no']} {message.author.mention}, "
                        "link paylaşamazsın.",
                        delete_after=5
                    )

                except Exception as e:
                    print("Link kontrol hatası:", repr(e))

    await bot.process_commands(message)


@bot.event
async def on_message_delete(message):

    if message.author.bot:
        return

    logs = CONFIG.get(
        "logs",
        {}
    )

    if not logs.get("delete", True):
        return

    await send_log(
        message.guild,
        f"🗑️ **Mesaj silindi**\n"
        f"**Kullanıcı:** {message.author.mention}\n"
        f"**Kanal:** {message.channel.mention}\n"
        f"**Mesaj:** {message.content[:1000]}"
    )


@bot.event
async def on_message_edit(before, after):

    if before.author.bot:
        return

    if before.content == after.content:
        return

    logs = CONFIG.get(
        "logs",
        {}
    )

    if not logs.get("edit", True):
        return

    await send_log(
        before.guild,
        f"✏️ **Mesaj düzenlendi**\n"
        f"**Kullanıcı:** {before.author.mention}\n"
        f"**Kanal:** {before.channel.mention}\n"
        f"**Eski:** {before.content[:500]}\n"
        f"**Yeni:** {after.content[:500]}"
    )


@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if before.channel == after.channel:
        return

    voice_config = CONFIG.get(
        "voice",
        {}
    )

    channel_id = voice_config.get(
        "channel_id"
    )

    if not channel_id:
        return

    notification_channel = member.guild.get_channel(
        channel_id
    )

    if notification_channel is None:
        return

    try:

        if after.channel and not before.channel:

            text = voice_config.get(
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

            text = voice_config.get(
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
        print("Ses bildirim hatası:", repr(e))


# =========================================================
# HATA YAKALAMA
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
