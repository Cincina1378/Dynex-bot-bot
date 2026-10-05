import os
import json
import random
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# AYARLAR
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

PREFIX = "D."
SUPPORT_SERVER_ID = 1551647711332139098
SUPPORT_INVITE = "https://discord.gg/2pFJwJNDR"

CONFIG_FILE = Path("config.json")

START_TIME = time.time()

LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
    "az": "Azərbaycan dili"
}


# =========================================================
# CONFIG
# =========================================================

def load_config():
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


config = load_config()


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def guild_config(guild_id):
    gid = str(guild_id)

    if gid not in config:
        config[gid] = {
            "language": "tr",
            "giveaway_role": None,
            "dm_role": None,
            "log_channel": None,
            "counting_channel": None,
            "counting_number": 0,
            "word_channel": None,
            "word_last": None
        }
        save_config()

    return config[gid]


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.presences = True


class DynexBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None
        )
        self.synced = False

    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            print(f"{len(synced)} slash komutu senkronize edildi.")
        except Exception as e:
            print("Slash senkronizasyon hatası:", repr(e))

    async def on_ready(self):
        print(f"Dynex giriş yaptı: {self.user} ({self.user.id})")
        print(f"Sunucu sayısı: {len(self.guilds)}")


bot = DynexBot()


# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def is_admin(interaction: discord.Interaction):
    return (
        interaction.guild is not None
        and isinstance(interaction.user, discord.Member)
        and interaction.user.guild_permissions.administrator
    )


def admin_only():
    async def predicate(interaction: discord.Interaction):
        if not is_admin(interaction):
            raise app_commands.CheckFailure(
                "Bu komutu kullanmak için Yönetici yetkisine sahip olmalısın."
            )
        return True

    return app_commands.check(predicate)


def uptime_text():
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


def get_language(guild):
    if guild is None:
        return "tr"

    return guild_config(guild.id).get("language", "tr")


async def get_bot_owner():
    try:
        info = await bot.application_info()
        return info.owner
    except Exception:
        return None


async def send_log(guild, title, description):
    if guild is None:
        return

    data = guild_config(guild.id)
    channel_id = data.get("log_channel")

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if not channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.blurple(),
        timestamp=datetime.now(timezone.utc)
    )

    try:
        await channel.send(embed=embed)
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
        support = bot.get_guild(SUPPORT_SERVER_ID)

        if support:
            support_members = support.member_count or len(support.members)
        else:
            support_members = 0

        owner = await get_bot_owner()

        if owner:
            owner_text = owner.mention
        else:
            owner_text = "Bot sahibi alınamadı"

        embed = discord.Embed(
            title="Dynex Durum",
            color=discord.Color.black()
        )

        embed.add_field(
            name="Sunucu sayısı:",
            value=f"`{len(bot.guilds)}`",
            inline=False
        )

        embed.add_field(
            name="Destek sunucusu üye sayısı:",
            value=f"`{support_members}`",
            inline=False
        )

        embed.add_field(
            name="Prefix yani . Komut:",
            value=f"`{PREFIX}`",
            inline=False
        )

        embed.add_field(
            name="Aktif kalma süresi:",
            value=f"`{uptime_text()}`",
            inline=False
        )

        embed.add_field(
            name="Bot sahibi:",
            value=owner_text,
            inline=False
        )

        embed.add_field(
            name="Destek sunucusu:",
            value=f"[Destek sunucusuna katıl]({SUPPORT_INVITE})",
            inline=False
        )

        embed.set_footer(text="Dynex")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print("/bot hatası:", repr(e))

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Bot bilgileri alınırken bir hata oluştu.",
                ephemeral=True
            )


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun gecikmesini gösterir."
)
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

    if latency < 100:
        durum = "Mükemmel"
    elif latency < 180:
        durum = "İyi"
    elif latency < 300:
        durum = "Orta"
    elif latency < 500:
        durum = "Zayıf"
    else:
        durum = "Berbat"

    embed = discord.Embed(
        title="Dynex Ping",
        description=f"**Gecikme:** `{latency}ms`\n**Durum:** `{durum}`",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# /YARDIM
# =========================================================

@bot.tree.command(
    name="yardim",
    description="Dynex komutlarını gösterir."
)
async def help_command(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Dynex Yardım",
        description="Kullanabileceğin komutlardan bazıları:",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Genel",
        value=(
            "`/bot`\n"
            "`/ping`\n"
            "`/sunucu`\n"
            "`/kullanici`\n"
            "`/avatar`\n"
            "`/roller`"
        ),
        inline=True
    )

    embed.add_field(
        name="Eğlence",
        value=(
            "`/zar`\n"
            "`/yazitura`\n"
            "`/sans`\n"
            "`/sekiztop`\n"
            "`/sayi-tahmin`\n"
            "`/kelime`"
        ),
        inline=True
    )

    embed.add_field(
        name="Yönetim",
        value=(
            "`/ayarlar`\n"
            "`/dil`\n"
            "`/dm`\n"
            "`/temizle`\n"
            "`/timeout`\n"
            "`/kick`\n"
            "`/ban`"
        ),
        inline=True
    )

    embed.set_footer(text="Dynex")

    await interaction.response.send_message(embed=embed)


# =========================================================
# GENEL KOMUTLAR
# =========================================================

@bot.tree.command(
    name="sunucu",
    description="Sunucu bilgilerini gösterir."
)
async def server_info(interaction: discord.Interaction):

    guild = interaction.guild

    if guild is None:
        return await interaction.response.send_message(
            "Bu komut sunucuda kullanılabilir.",
            ephemeral=True
        )

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.blurple()
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

    embed.add_field(
        name="Sunucu sahibi",
        value=f"<@{guild.owner_id}>",
        inline=True
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="kullanici",
    description="Kullanıcı bilgilerini gösterir."
)
@app_commands.describe(kullanici="Bilgilerini görmek istediğin kullanıcı")
async def user_info(
    interaction: discord.Interaction,
    kullanici: discord.Member = None
):

    user = kullanici or interaction.user

    embed = discord.Embed(
        title="Kullanıcı Bilgileri",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(
        name="Kullanıcı",
        value=user.mention,
        inline=False
    )

    embed.add_field(
        name="ID",
        value=str(user.id),
        inline=True
    )

    embed.add_field(
        name="Hesap",
        value=f"<t:{int(user.created_at.timestamp())}:R>",
        inline=True
    )

    if isinstance(user, discord.Member):
        embed.add_field(
            name="Sunucuya katılma",
            value=f"<t:{int(user.joined_at.timestamp())}:R>"
            if user.joined_at else "Bilinmiyor",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="avatar",
    description="Kullanıcının avatarını gösterir."
)
@app_commands.describe(kullanici="Avatarını görmek istediğin kullanıcı")
async def avatar(
    interaction: discord.Interaction,
    kullanici: discord.User = None
):

    user = kullanici or interaction.user

    embed = discord.Embed(
        title=f"{user.display_name} Avatarı",
        color=discord.Color.blurple()
    )

    embed.set_image(url=user.display_avatar.url)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="roller",
    description="Sunucudaki rolleri gösterir."
)
async def roles(interaction: discord.Interaction):

    roles_list = [
        role.mention
        for role in reversed(interaction.guild.roles)
        if role.name != "@everyone"
    ]

    text = " ".join(roles_list)

    if len(text) > 4000:
        text = text[:3900] + "..."

    embed = discord.Embed(
        title="Sunucu Rolleri",
        description=text or "Rol bulunamadı.",
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# DİL
# =========================================================

@bot.tree.command(
    name="dil",
    description="Sunucunun Dynex dilini değiştirir."
)
@app_commands.describe(
    dil="Sunucuda kullanılacak dil"
)
@app_commands.choices(
    dil=[
        app_commands.Choice(name="Türkçe", value="tr"),
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Azərbaycan dili", value="az")
    ]
)
@admin_only()
async def language(
    interaction: discord.Interaction,
    dil: app_commands.Choice[str]
):

    data = guild_config(interaction.guild.id)

    data["language"] = dil.value

    save_config()

    await interaction.response.send_message(
        f"Sunucu dili **{dil.name}** olarak ayarlandı.",
        ephemeral=True
    )


# =========================================================
# AYARLAR
# =========================================================

class SettingsSelect(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Sunucu Dili",
                value="language",
                emoji="🌐"
            ),
            discord.SelectOption(
                label="Çekiliş Rolü",
                value="giveaway_role",
                emoji="🎁"
            ),
            discord.SelectOption(
                label="DM Gönderme Rolü",
                value="dm_role",
                emoji="📨"
            ),
            discord.SelectOption(
                label="Log Kanalı",
                value="log_channel",
                emoji="📋"
            ),
            discord.SelectOption(
                label="Sayı Sayma Kanalı",
                value="counting_channel",
                emoji="🔢"
            ),
            discord.SelectOption(
                label="Kelime Oyunu Kanalı",
                value="word_channel",
                emoji="🔤"
            )
        ]

        super().__init__(
            placeholder="Ayarlamak istediğin seçeneği seç...",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):

        if not is_admin(interaction):
            return await interaction.response.send_message(
                "Bu menüyü kullanmak için Yönetici yetkisine sahip olmalısın.",
                ephemeral=True
            )

        value = self.values[0]

        if value == "language":
            await interaction.response.send_message(
                "Dil seçimini aşağıdan yap:",
                view=LanguageView(),
                ephemeral=True
            )

        elif value == "giveaway_role":
            await interaction.response.send_modal(
                RoleIDModal(
                    "Çekiliş Rolü",
                    "giveaway_role"
                )
            )

        elif value == "dm_role":
            await interaction.response.send_modal(
                RoleIDModal(
                    "DM Gönderme Rolü",
                    "dm_role"
                )
            )

        elif value == "log_channel":
            await interaction.response.send_modal(
                ChannelIDModal(
                    "Log Kanalı",
                    "log_channel"
                )
            )

        elif value == "counting_channel":
            await interaction.response.send_modal(
                ChannelIDModal(
                    "Sayı Sayma Kanalı",
                    "counting_channel"
                )
            )

        elif value == "word_channel":
            await interaction.response.send_modal(
                ChannelIDModal(
                    "Kelime Oyunu Kanalı",
                    "word_channel"
                )
            )


class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(SettingsSelect())


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
                label="Azərbaycan dili",
                value="az",
                emoji="🇦🇿"
            )
        ]

        super().__init__(
            placeholder="Dil seç...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if not is_admin(interaction):
            return await interaction.response.send_message(
                "Yönetici yetkisi gerekiyor.",
                ephemeral=True
            )

        data = guild_config(interaction.guild.id)

        data["language"] = self.values[0]

        save_config()

        await interaction.response.edit_message(
            content=f"Dil **{LANGUAGES[self.values[0]]}** olarak değiştirildi.",
            view=None
        )


class LanguageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(LanguageSelect())


class RoleIDModal(discord.ui.Modal):

    def __init__(self, title, setting):
        super().__init__(title=title)

        self.setting = setting

        self.role_id = discord.ui.TextInput(
            label="Rol ID",
            placeholder="Örn: 123456789012345678",
            required=True,
            max_length=25
        )

        self.add_item(self.role_id)

    async def on_submit(self, interaction: discord.Interaction):

        try:
            role_id = int(self.role_id.value.strip())
        except ValueError:
            return await interaction.response.send_message(
                "Geçerli bir rol ID'si gir.",
                ephemeral=True
            )

        role = interaction.guild.get_role(role_id)

        if role is None:
            return await interaction.response.send_message(
                "Bu sunucuda böyle bir rol bulunamadı.",
                ephemeral=True
            )

        data = guild_config(interaction.guild.id)
        data[self.setting] = role.id

        save_config()

        await interaction.response.send_message(
            f"{role.mention} başarıyla ayarlandı.",
            ephemeral=True
        )


class ChannelIDModal(discord.ui.Modal):

    def __init__(self, title, setting):
        super().__init__(title=title)

        self.setting = setting

        self.channel_id = discord.ui.TextInput(
            label="Kanal ID",
            placeholder="Örn: 123456789012345678",
            required=True,
            max_length=25
        )

        self.add_item(self.channel_id)

    async def on_submit(self, interaction: discord.Interaction):

        try:
            channel_id = int(self.channel_id.value.strip())
        except ValueError:
            return await interaction.response.send_message(
                "Geçerli bir kanal ID'si gir.",
                ephemeral=True
            )

        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            return await interaction.response.send_message(
                "Bu sunucuda böyle bir kanal bulunamadı.",
                ephemeral=True
            )

        data = guild_config(interaction.guild.id)
        data[self.setting] = channel.id

        save_config()

        await interaction.response.send_message(
            f"{channel.mention} başarıyla ayarlandı.",
            ephemeral=True
        )


@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını açar."
)
@admin_only()
async def settings(interaction: discord.Interaction):

    data = guild_config(interaction.guild.id)

    language = LANGUAGES.get(
        data.get("language", "tr"),
        "Türkçe"
    )

    giveaway = (
        f"<@&{data['giveaway_role']}>"
        if data.get("giveaway_role")
        else "Ayarlanmadı"
    )

    dm_role = (
        f"<@&{data['dm_role']}>"
        if data.get("dm_role")
        else "Ayarlanmadı"
    )

    log_channel = (
        f"<#{data['log_channel']}>"
        if data.get("log_channel")
        else "Ayarlanmadı"
    )

    embed = discord.Embed(
        title="Dynex Ayarları",
        description="Aşağıdaki menüden değiştirmek istediğin ayarı seç.",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🌐 Dil",
        value=language,
        inline=False
    )

    embed.add_field(
        name="🎁 Çekiliş Rolü",
        value=giveaway,
        inline=True
    )

    embed.add_field(
        name="📨 DM Rolü",
        value=dm_role,
        inline=True
    )

    embed.add_field(
        name="📋 Log Kanalı",
        value=log_channel,
        inline=True
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(),
        ephemeral=True
    )


# =========================================================
# DM DUYURU
# =========================================================

class DmAnnouncementModal(discord.ui.Modal):

    def __init__(self, role: discord.Role):
        super().__init__(title="DM Duyurusu")

        self.role = role

        self.title_input = discord.ui.TextInput(
            label="Başlık",
            placeholder="Duyuru başlığı",
            required=True,
            max_length=256
        )

        self.message_input = discord.ui.TextInput(
            label="Mesaj",
            placeholder="Gönderilecek mesaj...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )

        self.add_item(self.title_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):

        data = guild_config(interaction.guild.id)
        allowed_role_id = data.get("dm_role")

        if not allowed_role_id:
            return await interaction.response.send_message(
                "Önce `/ayarlar` üzerinden DM Gönderme Rolünü ayarla.",
                ephemeral=True
            )

        if allowed_role_id not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message(
                "Bu komutu kullanma yetkin yok.",
                ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title=str(self.title_input.value),
            description=str(self.message_input.value),
            color=discord.Color.blue()
        )

        embed.set_footer(text="Dynex")

        sent = 0
        failed = 0

        for member in self.role.members:

            if member.bot:
                continue

            try:
                await member.send(embed=embed)
                sent += 1
            except Exception:
                failed += 1

            await asyncio.sleep(0.15)

        await interaction.followup.send(
            f"Duyuru gönderildi.\n\n"
            f"Başarılı: `{sent}`\n"
            f"Başarısız: `{failed}`",
            ephemeral=True
        )

        await send_log(
            interaction.guild,
            "DM Duyurusu",
            f"{interaction.user.mention} tarafından "
            f"{self.role.mention} rolüne DM gönderildi.\n"
            f"Başarılı: {sent}\n"
            f"Başarısız: {failed}"
        )


@bot.tree.command(
    name="dm",
    description="Belirlenen role DM duyurusu gönderir."
)
@app_commands.describe(rol="DM gönderilecek rol")
async def dm_announcement(
    interaction: discord.Interaction,
    rol: discord.Role
):

    data = guild_config(interaction.guild.id)
    allowed_role_id = data.get("dm_role")

    if not allowed_role_id:
        return await interaction.response.send_message(
            "DM gönderme rolü ayarlanmamış. `/ayarlar` komutundan ayarla.",
            ephemeral=True
        )

    if allowed_role_id not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message(
            "Bu komutu kullanma yetkin yok.",
            ephemeral=True
        )

    await interaction.response.send_modal(
        DmAnnouncementModal(rol)
    )


# =========================================================
# EĞLENCE
# =========================================================

@bot.tree.command(
    name="zar",
    description="Zar atar."
)
async def dice(interaction: discord.Interaction):

    number = random.randint(1, 6)

    await interaction.response.send_message(
        f"🎲 Zar sonucu: **{number}**"
    )


@bot.tree.command(
    name="yazitura",
    description="Yazı veya tura atar."
)
async def coin(interaction: discord.Interaction):

    result = random.choice(["Yazı", "Tura"])

    await interaction.response.send_message(
        f"🪙 Sonuç: **{result}**"
    )


@bot.tree.command(
    name="sans",
    description="Şansını dene."
)
async def luck(interaction: discord.Interaction):

    number = random.randint(1, 100)

    await interaction.response.send_message(
        f"🍀 Şansın: **%{number}**"
    )


@bot.tree.command(
    name="sekiztop",
    description="8 topa soru sor."
)
@app_commands.describe(soru="Sorun")
async def eight_ball(
    interaction: discord.Interaction,
    soru: str
):

    answers = [
        "Evet.",
        "Hayır.",
        "Kesinlikle.",
        "Bence evet.",
        "Bence hayır.",
        "Bunu zaman gösterecek.",
        "Şu an söylemek zor.",
        "Kesinlikle mümkün."
    ]

    await interaction.response.send_message(
        f"🎱 **Soru:** {soru}\n"
        f"**Cevap:** {random.choice(answers)}"
    )


@bot.tree.command(
    name="sayi-tahmin",
    description="1 ile 100 arasında sayı tahmin et."
)
@app_commands.describe(tahmin="Tahminin")
async def number_guess(
    interaction: discord.Interaction,
    tahmin: int
):

    if tahmin < 1 or tahmin > 100:
        return await interaction.response.send_message(
            "1 ile 100 arasında bir sayı yaz.",
            ephemeral=True
        )

    number = random.randint(1, 100)

    if tahmin == number:
        text = f"🎉 Bildin! Sayı **{number}** idi."
    elif tahmin < number:
        text = f"❌ Bilemedin. Sayı **{number}** idi. Tahminin daha küçüktü."
    else:
        text = f"❌ Bilemedin. Sayı **{number}** idi. Tahminin daha büyüktü."

    await interaction.response.send_message(text)


# =========================================================
# SAYI SAYMA
# =========================================================

@bot.tree.command(
    name="sayac-ayarla",
    description="Sayı sayma kanalını ayarlar."
)
@app_commands.describe(kanal="Sayı sayma kanalı")
@admin_only()
async def counting_setup(
    interaction: discord.Interaction,
    kanal: discord.TextChannel
):

    data = guild_config(interaction.guild.id)

    data["counting_channel"] = kanal.id
    data["counting_number"] = 0

    save_config()

    await interaction.response.send_message(
        f"🔢 Sayı sayma kanalı {kanal.mention} olarak ayarlandı.\n"
        f"Başlangıç sayısı: `1`"
    )


# =========================================================
# KELİME OYUNU
# =========================================================

@bot.tree.command(
    name="kelime-ayarla",
    description="Kelime oyunu kanalını ayarlar."
)
@app_commands.describe(kanal="Kelime oyunu kanalı")
@admin_only()
async def word_setup(
    interaction: discord.Interaction,
    kanal: discord.TextChannel
):

    data = guild_config(interaction.guild.id)

    data["word_channel"] = kanal.id
    data["word_last"] = None

    save_config()

    await interaction.response.send_message(
        f"🔤 Kelime oyunu {kanal.mention} kanalında başlatıldı."
    )


# =========================================================
# MODERASYON
# =========================================================

@bot.tree.command(
    name="temizle",
    description="Mesajları siler."
)
@app_commands.describe(miktar="Silinecek mesaj miktarı")
@admin_only()
async def clear(
    interaction: discord.Interaction,
    miktar: app_commands.Range[int, 1, 100]
):

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(
        limit=miktar
    )

    await interaction.followup.send(
        f"🧹 `{len(deleted)}` mesaj silindi.",
        ephemeral=True
    )


@bot.tree.command(
    name="timeout",
    description="Kullanıcıya timeout verir."
)
@app_commands.describe(
    kullanici="Timeout verilecek kullanıcı",
    dakika="Dakika"
)
@admin_only()
async def timeout(
    interaction: discord.Interaction,
    kullanici: discord.Member,
    dakika: app_commands.Range[int, 1, 10080]
):

    if kullanici == interaction.user:
        return await interaction.response.send_message(
            "Kendine timeout veremezsin.",
            ephemeral=True
        )

    until = discord.utils.utcnow() + timedelta(
        minutes=dakika
    )

    try:
        await kullanici.timeout(
            until,
            reason=f"{interaction.user} tarafından uygulandı."
        )

        await interaction.response.send_message(
            f"⏱️ {kullanici.mention} `{dakika}` dakika timeout aldı."
        )

        await send_log(
            interaction.guild,
            "Timeout",
            f"{kullanici.mention} → {dakika} dakika\n"
            f"Yetkili: {interaction.user.mention}"
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "Bu kullanıcıya timeout veremiyorum.",
            ephemeral=True
        )


@bot.tree.command(
    name="kick",
    description="Kullanıcıyı sunucudan atar."
)
@app_commands.describe(kullanici="Atılacak kullanıcı")
@admin_only()
async def kick(
    interaction: discord.Interaction,
    kullanici: discord.Member
):

    try:
        await kullanici.kick(
            reason=f"{interaction.user} tarafından atıldı."
        )

        await interaction.response.send_message(
            f"👢 {kullanici.mention} sunucudan atıldı."
        )

        await send_log(
            interaction.guild,
            "Kick",
            f"Kullanıcı: {kullanici.mention}\n"
            f"Yetkili: {interaction.user.mention}"
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "Bu kullanıcıyı atamıyorum.",
            ephemeral=True
        )


@bot.tree.command(
    name="ban",
    description="Kullanıcıyı yasaklar."
)
@app_commands.describe(kullanici="Yasaklanacak kullanıcı")
@admin_only()
async def ban(
    interaction: discord.Interaction,
    kullanici: discord.Member
):

    try:
        await kullanici.ban(
            reason=f"{interaction.user} tarafından yasaklandı."
        )

        await interaction.response.send_message(
            f"🔨 {kullanici.mention} yasaklandı."
        )

        await send_log(
            interaction.guild,
            "Ban",
            f"Kullanıcı: {kullanici.mention}\n"
            f"Yetkili: {interaction.user.mention}"
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "Bu kullanıcıyı yasaklayamıyorum.",
            ephemeral=True
        )


@bot.tree.command(
    name="kilitle",
    description="Bulunduğun kanalı kilitler."
)
@admin_only()
async def lock(interaction: discord.Interaction):

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔒 Kanal kilitlendi."
    )


@bot.tree.command(
    name="kilit-ac",
    description="Kanal kilidini açar."
)
@admin_only()
async def unlock(interaction: discord.Interaction):

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = None

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔓 Kanalın kilidi açıldı."
    )


@bot.tree.command(
    name="yavas-mod",
    description="Kanala yavaş mod verir."
)
@app_commands.describe(
    saniye="Yavaş mod süresi"
)
@admin_only()
async def slowmode(
    interaction: discord.Interaction,
    saniye: app_commands.Range[int, 0, 21600]
):

    await interaction.channel.edit(
        slowmode_delay=saniye
    )

    await interaction.response.send_message(
        f"🐌 Yavaş mod `{saniye}` saniye olarak ayarlandı."
    )


# =========================================================
# MESAJ OLAYLARI
# =========================================================

@bot.event
async def on_message(message: discord.Message):

    if message.author.bot:
        return

    if message.guild:

        data = guild_config(message.guild.id)

        # -------------------------
        # SAYI SAYMA
        # -------------------------

        counting_channel = data.get("counting_channel")

        if counting_channel == message.channel.id:

            expected = data.get("counting_number", 0) + 1

            try:
                number = int(message.content.strip())
            except ValueError:
                await message.delete()
                return

            if number != expected:

                await message.delete()

                data["counting_number"] = 0

                save_config()

                await message.channel.send(
                    f"❌ Yanlış sayı! Oyun sıfırlandı.\n"
                    f"Yeni başlangıç: **1**",
                    delete_after=4
                )

                return

            data["counting_number"] = number

            save_config()

            await message.add_reaction("✅")

        # -------------------------
        # KELİME OYUNU
        # -------------------------

        word_channel = data.get("word_channel")

        if word_channel == message.channel.id:

            word = message.content.strip().lower()

            if (
                word
                and word.isalpha()
                and len(word) >= 2
            ):

                last_word = data.get("word_last")

                if last_word:

                    last_letter = last_word[-1]

                    if not word.startswith(last_letter):
                        await message.delete()

                        await message.channel.send(
                            f"❌ Bu kelime **{last_letter}** harfiyle başlamalı.",
                            delete_after=3
                        )

                        return

                data["word_last"] = word

                save_config()

                await message.add_reaction("🔤")

    await bot.process_commands(message)


# =========================================================
# HATA YÖNETİMİ
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(error, app_commands.CheckFailure):

        text = str(error)

        if not text:
            text = "Bu komutu kullanmak için gerekli yetkiye sahip değilsin."

        if interaction.response.is_done():
            await interaction.followup.send(
                text,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                text,
                ephemeral=True
            )

        return

    if isinstance(error, app_commands.CommandOnCooldown):

        text = (
            f"Bu komutu tekrar kullanmak için "
            f"`{error.retry_after:.1f}` saniye beklemelisin."
        )

        if interaction.response.is_done():
            await interaction.followup.send(
                text,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                text,
                ephemeral=True
            )

        return

    print(
        f"Komut hatası "
        f"({interaction.command.name if interaction.command else 'bilinmeyen'}):",
        repr(error)
    )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(
                "Komut çalıştırılırken bir hata oluştu.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Komut çalıştırılırken bir hata oluştu.",
                ephemeral=True
            )
    except Exception:
        pass


# =========================================================
# ÇALIŞTIR
# =========================================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN değişkeni bulunamadı."
    )

bot.run(TOKEN)
