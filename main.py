import os
import json
import random
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# DYNEX
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "D."

SUPPORT_SERVER_ID = 1551647711332139098
SUPPORT_INVITE = "https://discord.gg/2pFJwJNDR"

CONFIG_FILE = Path("config.json")

START_TIME = time.time()


# =========================================================
# CONFIG
# =========================================================

DEFAULT_SETTINGS = {
    "language": "tr",
    "giveaway_role": None,
    "dm_role": None,
    "ticket_role": None,
    "moderator_role": None,
    "log_channel": None,
    "welcome_channel": None,
    "welcome_enabled": False,
    "autorole": None,
    "game_channel": None,
}


def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps({}, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


config = load_config()


def save_config():
    CONFIG_FILE.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_settings(guild_id):
    gid = str(guild_id)

    if gid not in config:
        config[gid] = DEFAULT_SETTINGS.copy()
        save_config()

    changed = False

    for key, value in DEFAULT_SETTINGS.items():
        if key not in config[gid]:
            config[gid][key] = value
            changed = True

    if changed:
        save_config()

    return config[gid]


def set_setting(guild_id, key, value):
    settings = get_settings(guild_id)
    settings[key] = value
    save_config()


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# =========================================================
# LANGUAGE
# =========================================================

TEXTS = {
    "tr": {
        "no_permission": "Bu komutu kullanmak için yeterli yetkin yok.",
        "only_server": "Bu komut yalnızca sunucularda kullanılabilir.",
        "saved": "Ayar başarıyla kaydedildi.",
        "error": "Bir hata oluştu.",
        "language_saved": "Sunucu dili başarıyla değiştirildi.",
        "bot_info_error": "Bot bilgileri alınırken bir hata oluştu.",
        "not_set": "Ayarlanmadı",
    },

    "en": {
        "no_permission": "You don't have permission to use this command.",
        "only_server": "This command can only be used in servers.",
        "saved": "Setting saved successfully.",
        "error": "An error occurred.",
        "language_saved": "Server language has been changed.",
        "bot_info_error": "An error occurred while getting bot information.",
        "not_set": "Not set",
    },

    "az": {
        "no_permission": "Bu əmrdən istifadə etmək üçün icazən yoxdur.",
        "only_server": "Bu əmr yalnız serverlərdə istifadə edilə bilər.",
        "saved": "Parametr uğurla yadda saxlanıldı.",
        "error": "Xəta baş verdi.",
        "language_saved": "Server dili dəyişdirildi.",
        "bot_info_error": "Bot məlumatları alınarkən xəta baş verdi.",
        "not_set": "Təyin edilməyib",
    }
}


def t(guild, key):
    lang = "tr"

    if guild:
        lang = get_settings(guild.id).get("language", "tr")

    return TEXTS.get(lang, TEXTS["tr"]).get(key, key)


# =========================================================
# HELPERS
# =========================================================

def is_admin(interaction):
    return (
        interaction.user.guild_permissions.administrator
        or interaction.user.id == interaction.guild.owner_id
    )


def admin_only():
    async def predicate(interaction):
        return is_admin(interaction)

    return app_commands.check(predicate)


def format_uptime():
    seconds = int(time.time() - START_TIME)

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []

    if days:
        parts.append(f"{days} gün")
    if hours:
        parts.append(f"{hours} saat")
    if minutes:
        parts.append(f"{minutes} dakika")

    parts.append(f"{seconds} saniye")

    return ", ".join(parts)


def make_embed(title, description="", colour=discord.Colour.blurple()):
    return discord.Embed(
        title=title,
        description=description,
        colour=colour,
        timestamp=datetime.now(timezone.utc)
    )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash komutu senkronize edildi.")
    except Exception as e:
        print("Slash senkronizasyon hatası:", repr(e))

    print(f"Dynex giriş yaptı: {bot.user}")
    print(f"Sunucu sayısı: {len(bot.guilds)}")


# =========================================================
# HATA YAKALAMA
# =========================================================

@bot.tree.error
async def on_app_command_error(interaction, error):

    if isinstance(error, app_commands.errors.MissingPermissions):
        message = t(interaction.guild, "no_permission")

    elif isinstance(error, app_commands.errors.CheckFailure):
        message = t(interaction.guild, "no_permission")

    else:
        print("Slash komut hatası:", repr(error))
        message = t(interaction.guild, "error")

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except Exception:
        pass


# =========================================================
# /BOT
# =========================================================

@bot.tree.command(
    name="bot",
    description="Dynex botunun mevcut durumunu gösterir."
)
async def bot_info(interaction: discord.Interaction):

    try:
        await interaction.response.defer()

        guild_count = len(bot.guilds)

        support_guild = bot.get_guild(SUPPORT_SERVER_ID)

        if support_guild:
            support_members = support_guild.member_count
        else:
            support_members = 0

            try:
                support_guild = await bot.fetch_guild(SUPPORT_SERVER_ID)
                support_members = support_guild.member_count or 0
            except Exception:
                pass

        owner_text = "Bilinmiyor"

        try:
            application = await bot.application_info()

            if application.owner:
                owner = application.owner

                if isinstance(owner, discord.User):
                    owner_text = f"{owner.mention}"
                else:
                    owner_text = f"{owner.name}"
        except Exception as e:
            print("Owner alınamadı:", repr(e))

        embed = discord.Embed(
            title="Dynex Durum",
            colour=discord.Colour.blue()
        )

        embed.add_field(
            name="Sunucu sayısı",
            value=f"`{guild_count}`",
            inline=False
        )

        embed.add_field(
            name="Destek sunucusu üye sayısı",
            value=f"`{support_members}`",
            inline=False
        )

        embed.add_field(
            name="Prefix yani . Komut",
            value=f"`{PREFIX}`",
            inline=False
        )

        embed.add_field(
            name="Aktif kalma süresi",
            value=f"`{format_uptime()}`",
            inline=False
        )

        embed.add_field(
            name="Bot sahibi",
            value=owner_text,
            inline=False
        )

        embed.add_field(
            name="Destek sunucusu",
            value=f"[Destek sunucusuna katıl]({SUPPORT_INVITE})",
            inline=False
        )

        embed.set_thumbnail(url=bot.user.display_avatar.url)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print("/bot hatası:", repr(e))

        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    t(interaction.guild, "bot_info_error"),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    t(interaction.guild, "bot_info_error"),
                    ephemeral=True
                )
        except Exception:
            pass


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun gecikmesini gösterir."
)
async def ping(interaction):
    latency = round(bot.latency * 1000)

    if latency < 100:
        status = "🟢 Mükemmel"
    elif latency < 200:
        status = "🟢 İyi"
    elif latency < 300:
        status = "🟡 Orta"
    elif latency < 500:
        status = "🟠 Zayıf"
    else:
        status = "🔴 Berbat"

    embed = make_embed(
        "Dynex Ping",
        f"**Gecikme:** `{latency}ms`\n**Durum:** {status}",
        discord.Colour.blue()
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# /DIL
# =========================================================

@bot.tree.command(
    name="dil",
    description="Sunucunun dilini değiştirir."
)
@app_commands.describe(
    dil="Sunucu dili"
)
@app_commands.choices(
    dil=[
        app_commands.Choice(name="Türkçe", value="tr"),
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Azərbaycan", value="az"),
    ]
)
@admin_only()
async def language(interaction, dil: app_commands.Choice[str]):

    set_setting(
        interaction.guild.id,
        "language",
        dil.value
    )

    await interaction.response.send_message(
        f"🌐 Sunucu dili **{dil.name}** olarak ayarlandı."
    )


# =========================================================
# AYARLAR SELECT
# =========================================================

class SettingsSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Çekiliş Rolü",
                description="Çekiliş komutunu kullanabilecek rolü ayarla.",
                emoji="🎁",
                value="giveaway_role"
            ),

            discord.SelectOption(
                label="DM Duyuru Rolü",
                description="DM duyuru komutunu kullanabilecek rolü ayarla.",
                emoji="📨",
                value="dm_role"
            ),

            discord.SelectOption(
                label="Ticket Yetkili Rolü",
                description="Ticket sistemindeki yetkili rolünü ayarla.",
                emoji="🎫",
                value="ticket_role"
            ),

            discord.SelectOption(
                label="Moderatör Rolü",
                description="Moderasyon işlemlerinde kullanılacak rolü ayarla.",
                emoji="🛡️",
                value="moderator_role"
            ),

            discord.SelectOption(
                label="Log Kanalı",
                description="Bot loglarının gönderileceği kanalı ayarla.",
                emoji="📋",
                value="log_channel"
            ),

            discord.SelectOption(
                label="Karşılama Kanalı",
                description="Yeni üyelerin karşılanacağı kanalı ayarla.",
                emoji="👋",
                value="welcome_channel"
            ),

            discord.SelectOption(
                label="Otomatik Rol",
                description="Yeni üyelere verilecek rolü ayarla.",
                emoji="🎭",
                value="autorole"
            ),

            discord.SelectOption(
                label="Oyun Kanalı",
                description="Kelime ve sayı oyunlarının oynanacağı kanalı ayarla.",
                emoji="🎮",
                value="game_channel"
            ),

            discord.SelectOption(
                label="Sunucu Dili",
                description="Sunucunun dilini değiştir.",
                emoji="🌐",
                value="language"
            ),
        ]

        super().__init__(
            placeholder="Ayarlamak istediğin özelliği seç...",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction):

        if not is_admin(interaction):
            return await interaction.response.send_message(
                t(interaction.guild, "no_permission"),
                ephemeral=True
            )

        value = self.values[0]

        if value == "language":
            await interaction.response.send_message(
                "🌐 Dil seç:",
                view=LanguageView(),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"⚙️ **{self.options_by_value[value].label}** için aşağıdaki menüden seçim yap:",
            view=RoleChannelView(value),
            ephemeral=True
        )


class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SettingsSelect())


class LanguageSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Türkçe",
                emoji="🇹🇷",
                value="tr"
            ),
            discord.SelectOption(
                label="English",
                emoji="🇬🇧",
                value="en"
            ),
            discord.SelectOption(
                label="Azərbaycan",
                emoji="🇦🇿",
                value="az"
            ),
        ]

        super().__init__(
            placeholder="Bir dil seç...",
            options=options
        )

    async def callback(self, interaction):

        if not is_admin(interaction):
            return await interaction.response.send_message(
                "Yetkin yok.",
                ephemeral=True
            )

        set_setting(
            interaction.guild.id,
            "language",
            self.values[0]
        )

        await interaction.response.edit_message(
            content="✅ Sunucu dili başarıyla değiştirildi.",
            view=None
        )


class LanguageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(LanguageSelect())


class RoleChannelSelect(discord.ui.Select):

    def __init__(self, setting):

        self.setting = setting

        if setting in (
            "giveaway_role",
            "dm_role",
            "ticket_role",
            "moderator_role",
            "autorole"
        ):
            options = [
                discord.SelectOption(
                    label=role.name[:100],
                    value=str(role.id),
                    description=f"ID: {role.id}"[:100]
                )
                for role in setting_guild_roles
            ]
        else:
            options = [
                discord.SelectOption(
                    label=channel.name[:100],
                    value=str(channel.id),
                    description=f"ID: {channel.id}"[:100]
                )
                for channel in setting_guild_channels
            ]

        if not options:
            options = [
                discord.SelectOption(
                    label="Uygun seçenek bulunamadı",
                    value="none"
                )
            ]

        super().__init__(
            placeholder="Seçim yap...",
            options=options[:25]
        )

    async def callback(self, interaction):

        if not is_admin(interaction):
            return await interaction.response.send_message(
                "Yetkin yok.",
                ephemeral=True
            )

        value = self.values[0]

        if value == "none":
            return await interaction.response.send_message(
                "Uygun seçenek bulunamadı.",
                ephemeral=True
            )

        set_setting(
            interaction.guild.id,
            self.setting,
            int(value)
        )

        await interaction.response.edit_message(
            content="✅ Ayar başarıyla kaydedildi.",
            view=None
        )


setting_guild_roles = []
setting_guild_channels = []


class RoleChannelView(discord.ui.View):

    def __init__(self, setting):
        super().__init__(timeout=120)

        self.add_item(RoleChannelSelect(setting))


@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönet."
)
@admin_only()
async def settings(interaction):

    if not interaction.guild:
        return await interaction.response.send_message(
            "Bu komut sunucuda kullanılabilir.",
            ephemeral=True
        )

    global setting_guild_roles
    global setting_guild_channels

    setting_guild_roles = list(interaction.guild.roles)
    setting_guild_channels = list(interaction.guild.channels)

    settings_data = get_settings(interaction.guild.id)

    def role_name(role_id):
        if not role_id:
            return "Ayarlanmadı"

        role = interaction.guild.get_role(role_id)

        return role.mention if role else "Silinmiş rol"

    def channel_name(channel_id):
        if not channel_id:
            return "Ayarlanmadı"

        channel = interaction.guild.get_channel(channel_id)

        return channel.mention if channel else "Silinmiş kanal"

    embed = discord.Embed(
        title="Dynex Ayarları",
        description="Aşağıdaki menüden değiştirmek istediğin ayarı seç.",
        colour=discord.Colour.dark_blue()
    )

    embed.add_field(
        name="🎁 Çekiliş Rolü",
        value=role_name(settings_data["giveaway_role"]),
        inline=True
    )

    embed.add_field(
        name="📨 DM Duyuru Rolü",
        value=role_name(settings_data["dm_role"]),
        inline=True
    )

    embed.add_field(
        name="🎫 Ticket Rolü",
        value=role_name(settings_data["ticket_role"]),
        inline=True
    )

    embed.add_field(
        name="🛡️ Moderatör Rolü",
        value=role_name(settings_data["moderator_role"]),
        inline=True
    )

    embed.add_field(
        name="📋 Log Kanalı",
        value=channel_name(settings_data["log_channel"]),
        inline=True
    )

    embed.add_field(
        name="👋 Karşılama Kanalı",
        value=channel_name(settings_data["welcome_channel"]),
        inline=True
    )

    embed.add_field(
        name="🎭 Otomatik Rol",
        value=role_name(settings_data["autorole"]),
        inline=True
    )

    embed.add_field(
        name="🎮 Oyun Kanalı",
        value=channel_name(settings_data["game_channel"]),
        inline=True
    )

    embed.add_field(
        name="🌐 Dil",
        value=settings_data["language"],
        inline=True
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(),
        ephemeral=True
    )


# =========================================================
# /YARDIM
# =========================================================

@bot.tree.command(
    name="yardım",
    description="Dynex komutlarını gösterir."
)
async def help_command(interaction):

    embed = discord.Embed(
        title="Dynex Yardım",
        description="Dynex komut kategorileri",
        colour=discord.Colour.blue()
    )

    embed.add_field(
        name="⚙️ Yönetim",
        value="`/ayarlar`\n`/dil`\n`/bot`\n`/ping`",
        inline=True
    )

    embed.add_field(
        name="🎮 Eğlence",
        value="`/zar`\n`/yazıtura`\n`/rastgele`\n`/şans`\n`/8ball`",
        inline=True
    )

    embed.add_field(
        name="🎯 Oyunlar",
        value="`/sayıbaşlat`\n`/kelimebaşlat`",
        inline=True
    )

    embed.add_field(
        name="📨 Duyuru",
        value="`/dm`",
        inline=True
    )

    embed.add_field(
        name="🛡️ Moderasyon",
        value="`/temizle`\n`/timeout`\n`/kick`\n`/ban`",
        inline=True
    )

    embed.add_field(
        name="🎁 Çekiliş",
        value="`/çekiliş`",
        inline=True
    )

    embed.set_footer(
        text="Dynex • Destek sunucusu"
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# EĞLENCE
# =========================================================

@bot.tree.command(name="zar", description="Zar atar.")
async def dice(interaction):

    number = random.randint(1, 6)

    await interaction.response.send_message(
        f"🎲 Zar sonucu: **{number}**"
    )


@bot.tree.command(name="yazıtura", description="Yazı veya tura seçer.")
async def coin(interaction):

    result = random.choice(["Yazı", "Tura"])

    await interaction.response.send_message(
        f"🪙 Sonuç: **{result}**"
    )


@bot.tree.command(name="rastgele", description="1 ile 100 arasında sayı seçer.")
async def random_number(interaction):

    number = random.randint(1, 100)

    await interaction.response.send_message(
        f"🎯 Rastgele sayı: **{number}**"
    )


@bot.tree.command(name="şans", description="Şans yüzdesini gösterir.")
async def luck(interaction):

    number = random.randint(0, 100)

    await interaction.response.send_message(
        f"🍀 Şansın: **%{number}**"
    )


@bot.tree.command(name="8ball", description="Soruna cevap verir.")
@app_commands.describe(soru="8ball'a soracağın soru")
async def eightball(interaction, soru: str):

    answers = [
        "Kesinlikle.",
        "Büyük ihtimalle.",
        "Evet.",
        "Hayır.",
        "Sanmıyorum.",
        "Tekrar dene.",
        "Bunu zaman gösterecek.",
        "Hiç belli olmaz.",
    ]

    await interaction.response.send_message(
        f"🎱 **8 Ball**\n\n❓ {soru}\n\n💬 {random.choice(answers)}"
    )


# =========================================================
# SAYI SAYMA OYUNU
# =========================================================

counting_game = {}


@bot.tree.command(
    name="sayıbaşlat",
    description="Sayı sayma oyununu başlatır."
)
@admin_only()
async def start_counting(interaction):

    channel_id = interaction.channel.id

    counting_game[channel_id] = {
        "number": 1,
        "last_user": None
    }

    await interaction.response.send_message(
        "🔢 **Sayı sayma oyunu başladı!**\n"
        "İlk sayı: **1**\n"
        "Sayıları sırayla gönderin."
    )


# =========================================================
# KELİME OYUNU
# =========================================================

word_game = {}

WORDS = [
    "elma",
    "masa",
    "kalem",
    "kitap",
    "araba",
    "futbol",
    "discord",
    "bilgisayar",
    "telefon",
    "okul",
    "şehir",
    "oyun",
    "sunucu",
    "arkadaş",
    "başarı",
]


@bot.tree.command(
    name="kelimebaşlat",
    description="Kelime oyununu başlatır."
)
@admin_only()
async def start_word_game(interaction):

    channel_id = interaction.channel.id

    word = random.choice(WORDS)

    word_game[channel_id] = {
        "word": word,
        "used": False
    }

    await interaction.response.send_message(
        "🔤 **Kelime oyunu başladı!**\n"
        "Botun seçtiği kelimeyi tahmin etmeye çalışın.\n"
        f"💡 İpucu: Kelime **{len(word)} harfli**."
    )


# =========================================================
# MESAJ OYUN KONTROLLERİ
# =========================================================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    # Sayı sayma
    if message.channel.id in counting_game:

        game = counting_game[message.channel.id]

        try:
            number = int(message.content.strip())

            expected = game["number"]

            if number != expected:
                await message.channel.send(
                    f"❌ {message.author.mention} yanlış sayı!\n"
                    f"Beklenen sayı: **{expected}**"
                )

                game["number"] = 1

            else:
                game["number"] += 1

                if number % 10 == 0:
                    await message.channel.send(
                        f"✅ **{number}** doğru!"
                    )

        except ValueError:
            pass

    # Kelime oyunu
    if message.channel.id in word_game:

        game = word_game[message.channel.id]

        if message.content.lower().strip() == game["word"]:

            await message.channel.send(
                f"🎉 Tebrikler {message.author.mention}!\n"
                f"Kelimeyi doğru bildin: **{game['word']}**"
            )

            new_word = random.choice(WORDS)

            game["word"] = new_word

            await message.channel.send(
                f"🔤 Yeni kelime!\n"
                f"💡 **{len(new_word)} harfli**"
            )

    await bot.process_commands(message)


# =========================================================
# /DM
# =========================================================

class DMAnnouncementModal(discord.ui.Modal, title="DM Duyurusu"):

    baslik = discord.ui.TextInput(
        label="Başlık",
        placeholder="Duyuru başlığı",
        max_length=256
    )

    mesaj = discord.ui.TextInput(
        label="Mesaj",
        placeholder="Gönderilecek mesaj...",
        style=discord.TextStyle.paragraph,
        max_length=4000
    )

    def __init__(self, role):
        super().__init__()
        self.role = role

    async def on_submit(self, interaction):

        await interaction.response.defer(ephemeral=True)

        success = 0
        failed = 0

        embed = discord.Embed(
            title=str(self.baslik),
            description=str(self.mesaj),
            colour=discord.Colour.blue()
        )

        embed.set_footer(
            text="Dynex • Yönetim"
        )

        for member in self.role.members:

            if member.bot:
                continue

            try:
                await member.send(embed=embed)
                success += 1
            except Exception:
                failed += 1

            await asyncio.sleep(0.2)

        await interaction.followup.send(
            f"📨 DM duyurusu tamamlandı.\n\n"
            f"✅ Başarılı: **{success}**\n"
            f"❌ Başarısız: **{failed}**",
            ephemeral=True
        )


@bot.tree.command(
    name="dm",
    description="Belirli bir role sahip kişilere DM duyurusu gönderir."
)
@app_commands.describe(
    rol="DM gönderilecek kişilerde bulunması gereken rol."
)
async def dm_announcement(interaction, rol: discord.Role):

    settings_data = get_settings(interaction.guild.id)

    allowed_role_id = settings_data.get("dm_role")

    if not allowed_role_id:
        return await interaction.response.send_message(
            "❌ Önce `/ayarlar` üzerinden **DM Duyuru Rolü** ayarlanmalı.",
            ephemeral=True
        )

    if allowed_role_id not in [r.id for r in interaction.user.roles]:
        return await interaction.response.send_message(
            "❌ Bu komutu kullanma yetkin yok.",
            ephemeral=True
        )

    await interaction.response.send_modal(
        DMAnnouncementModal(rol)
    )


# =========================================================
# TEMİZLE
# =========================================================

@bot.tree.command(
    name="temizle",
    description="Mesajları siler."
)
@app_commands.describe(
    miktar="Silinecek mesaj sayısı."
)
@admin_only()
async def clear(interaction, miktar: app_commands.Range[int, 1, 100]):

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(
        limit=miktar
    )

    await interaction.followup.send(
        f"🧹 **{len(deleted)}** mesaj silindi.",
        ephemeral=True
    )


# =========================================================
# TIMEOUT
# =========================================================

@bot.tree.command(
    name="timeout",
    description="Bir kullanıcıya timeout verir."
)
@app_commands.describe(
    kullanıcı="Timeout verilecek kullanıcı.",
    dakika="Dakika."
)
@admin_only()
async def timeout(
    interaction,
    kullanıcı: discord.Member,
    dakika: app_commands.Range[int, 1, 40320]
):

    if kullanıcı.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ Bu kullanıcıya timeout veremezsin.",
            ephemeral=True
        )

    duration = discord.utils.utcnow() + __import__("datetime").timedelta(
        minutes=dakika
    )

    await kullanıcı.timeout(
        duration,
        reason=f"Dynex | {interaction.user}"
    )

    await interaction.response.send_message(
        f"🔇 {kullanıcı.mention} kullanıcısına **{dakika} dakika** timeout verildi."
    )


# =========================================================
# KICK
# =========================================================

@bot.tree.command(
    name="kick",
    description="Kullanıcıyı sunucudan atar."
)
@app_commands.describe(
    kullanıcı="Atılacak kullanıcı.",
    sebep="Atılma sebebi."
)
@admin_only()
async def kick(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):

    if kullanıcı.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ Bu kullanıcıyı atamazsın.",
            ephemeral=True
        )

    await kullanıcı.kick(
        reason=f"{sebep} | {interaction.user}"
    )

    await interaction.response.send_message(
        f"👢 {kullanıcı.mention} sunucudan atıldı.\n"
        f"**Sebep:** {sebep}"
    )


# =========================================================
# BAN
# =========================================================

@bot.tree.command(
    name="ban",
    description="Kullanıcıyı yasaklar."
)
@app_commands.describe(
    kullanıcı="Yasaklanacak kullanıcı.",
    sebep="Yasaklama sebebi."
)
@admin_only()
async def ban(
    interaction,
    kullanıcı: discord.Member,
    sebep: str = "Sebep belirtilmedi."
):

    if kullanıcı.top_role >= interaction.user.top_role:
        return await interaction.response.send_message(
            "❌ Bu kullanıcıyı yasaklayamazsın.",
            ephemeral=True
        )

    await kullanıcı.ban(
        reason=f"{sebep} | {interaction.user}"
    )

    await interaction.response.send_message(
        f"🔨 {kullanıcı.mention} yasaklandı.\n"
        f"**Sebep:** {sebep}"
    )


# =========================================================
# ÇEKİLİŞ
# =========================================================

@bot.tree.command(
    name="çekiliş",
    description="Basit çekiliş başlatır."
)
@app_commands.describe(
    ödül="Çekiliş ödülü.",
    süre="Süreyi saniye olarak yaz.",
    kazanan="Kazanan sayısı."
)
async def giveaway(
    interaction,
    ödül: str,
    süre: app_commands.Range[int, 10, 604800],
    kazanan: app_commands.Range[int, 1, 20]
):

    settings_data = get_settings(interaction.guild.id)

    role_id = settings_data.get("giveaway_role")

    if not role_id:
        return await interaction.response.send_message(
            "❌ Önce `/ayarlar` üzerinden **Çekiliş Rolü** ayarla.",
            ephemeral=True
        )

    if role_id not in [r.id for r in interaction.user.roles]:
        return await interaction.response.send_message(
            "❌ Çekiliş başlatma yetkin yok.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🎁 Çekiliş",
        description=(
            f"**Ödül:** {ödül}\n"
            f"**Kazanan:** {kazanan}\n\n"
            "Katılmak için 🎉 tepkisine bas!"
        ),
        colour=discord.Colour.blue()
    )

    embed.set_footer(
        text=f"{süre} saniye sonra sona erecek."
    )

    await interaction.response.send_message(
        embed=embed
    )

    message = await interaction.original_response()

    await message.add_reaction("🎉")

    await asyncio.sleep(süre)

    try:
        message = await interaction.channel.fetch_message(
            message.id
        )

        reaction = discord.utils.get(
            message.reactions,
            emoji="🎉"
        )

        if not reaction:
            return

        users = [
            user async for user in reaction.users()
            if not user.bot
        ]

        if not users:
            await interaction.channel.send(
                "❌ Çekilişe katılan olmadı."
            )
            return

        winners = random.sample(
            users,
            min(kazanan, len(users))
        )

        mentions = ", ".join(
            user.mention for user in winners
        )

        await interaction.channel.send(
            f"🎉 **Çekiliş sona erdi!**\n"
            f"🏆 Kazanan: {mentions}\n"
            f"🎁 Ödül: **{ödül}**"
        )

    except Exception as e:
        print("Çekiliş hatası:", repr(e))


# =========================================================
# OTOMATİK ROL + KARŞILAMA
# =========================================================

@bot.event
async def on_member_join(member):

    settings_data = get_settings(member.guild.id)

    autorole_id = settings_data.get("autorole")

    if autorole_id:

        role = member.guild.get_role(autorole_id)

        if role:
            try:
                await member.add_roles(
                    role,
                    reason="Dynex otomatik rol"
                )
            except Exception:
                pass

    if settings_data.get("welcome_enabled"):

        channel_id = settings_data.get("welcome_channel")

        if channel_id:

            channel = member.guild.get_channel(channel_id)

            if channel:

                embed = discord.Embed(
                    title="👋 Hoş geldin!",
                    description=(
                        f"{member.mention} aramıza katıldı!\n\n"
                        f"**Üye sayısı:** `{member.guild.member_count}`"
                    ),
                    colour=discord.Colour.blue()
                )

                try:
                    await channel.send(
                        embed=embed
                    )
                except Exception:
                    pass


# =========================================================
# /KARŞILAMA
# =========================================================

@bot.tree.command(
    name="karşılama",
    description="Karşılama sistemini açıp kapatır."
)
@admin_only()
async def welcome(interaction):

    settings_data = get_settings(interaction.guild.id)

    current = settings_data.get("welcome_enabled", False)

    set_setting(
        interaction.guild.id,
        "welcome_enabled",
        not current
    )

    durum = "açıldı" if not current else "kapatıldı"

    await interaction.response.send_message(
        f"👋 Karşılama sistemi **{durum}**."
    )


# =========================================================
# /SUNUCU
# =========================================================

@bot.tree.command(
    name="sunucu",
    description="Sunucu bilgilerini gösterir."
)
async def server_info(interaction):

    guild = interaction.guild

    embed = discord.Embed(
        title=guild.name,
        colour=discord.Colour.blue()
    )

    embed.add_field(
        name="👥 Üye",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="💬 Kanal",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="🎭 Rol",
        value=str(len(guild.roles)),
        inline=True
    )

    embed.add_field(
        name="🆔 Sunucu ID",
        value=str(guild.id),
        inline=False
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
async def user_info(
    interaction,
    kullanıcı: discord.Member = None
):

    kullanıcı = kullanıcı or interaction.user

    embed = discord.Embed(
        title=f"{kullanıcı.display_name}",
        colour=discord.Colour.blue()
    )

    embed.set_thumbnail(
        url=kullanıcı.display_avatar.url
    )

    embed.add_field(
        name="👤 Kullanıcı",
        value=kullanıcı.mention,
        inline=False
    )

    embed.add_field(
        name="🆔 ID",
        value=str(kullanıcı.id),
        inline=False
    )

    embed.add_field(
        name="📅 Hesap oluşturulma",
        value=discord.utils.format_dt(
            kullanıcı.created_at,
            style="F"
        ),
        inline=False
    )

    if interaction.guild:
        embed.add_field(
            name="📥 Sunucuya katılma",
            value=discord.utils.format_dt(
                kullanıcı.joined_at,
                style="F"
            ) if kullanıcı.joined_at else "Bilinmiyor",
            inline=False
        )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /DAVET
# =========================================================

@bot.tree.command(
    name="davet",
    description="Dynex davet bağlantısını gösterir."
)
async def invite(interaction):

    embed = discord.Embed(
        title="Dynex",
        description=(
            f"Botu sunucuna eklemek için:\n"
            f"[Dynex'i Davet Et]({SUPPORT_INVITE})"
        ),
        colour=discord.Colour.blue()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /SAY
# =========================================================

@bot.tree.command(
    name="say",
    description="Sunucudaki üyeleri sayar."
)
async def count_members(interaction):

    guild = interaction.guild

    humans = sum(
        1 for member in guild.members
        if not member.bot
    )

    bots = sum(
        1 for member in guild.members
        if member.bot
    )

    embed = discord.Embed(
        title="👥 Sunucu İstatistikleri",
        colour=discord.Colour.blue()
    )

    embed.add_field(
        name="Toplam",
        value=f"`{guild.member_count}`",
        inline=True
    )

    embed.add_field(
        name="İnsan",
        value=f"`{humans}`",
        inline=True
    )

    embed.add_field(
        name="Bot",
        value=f"`{bots}`",
        inline=True
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# /ROL
# =========================================================

@bot.tree.command(
    name="rolver",
    description="Bir kullanıcıya rol verir."
)
@app_commands.describe(
    kullanıcı="Rol verilecek kullanıcı.",
    rol="Verilecek rol."
)
@admin_only()
async def give_role(
    interaction,
    kullanıcı: discord.Member,
    rol: discord.Role
):

    if rol >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ Bu rol botun rolünden yukarıda.",
            ephemeral=True
        )

    await kullanıcı.add_roles(
        rol,
        reason=f"Dynex | {interaction.user}"
    )

    await interaction.response.send_message(
        f"✅ {kullanıcı.mention} kullanıcısına {rol.mention} verildi."
    )


@bot.tree.command(
    name="rolal",
    description="Bir kullanıcıdan rol alır."
)
@app_commands.describe(
    kullanıcı="Rolü alınacak kullanıcı.",
    rol="Alınacak rol."
)
@admin_only()
async def remove_role(
    interaction,
    kullanıcı: discord.Member,
    rol: discord.Role
):

    if rol >= interaction.guild.me.top_role:
        return await interaction.response.send_message(
            "❌ Bu rol botun rolünden yukarıda.",
            ephemeral=True
        )

    await kullanıcı.remove_roles(
        rol,
        reason=f"Dynex | {interaction.user}"
    )

    await interaction.response.send_message(
        f"✅ {kullanıcı.mention} kullanıcısından {rol.mention} alındı."
    )


# =========================================================
# BOT TOKEN KONTROLÜ
# =========================================================

if not TOKEN:
    print("HATA: DISCORD_TOKEN ortam değişkeni bulunamadı.")
else:
    bot.run(TOKEN)
