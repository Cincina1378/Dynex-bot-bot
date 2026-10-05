import os
import time
import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

# =========================================================
# AYARLAR
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

PREFIX = "D."
SUPPORT_SERVER_ID = 1551647711332139098
OWNER_ID = 1540359436244095137

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

start_time = time.time()

# Sunucu başına ayarlar
guild_settings = {}

# Kullanıcı başına dil
user_languages = {}

# =========================================================
# YARDIMCI FONKSİYONLAR
# =========================================================

def get_guild_settings(guild_id):
    if guild_id not in guild_settings:
        guild_settings[guild_id] = {
            "language": "tr",
            "giveaway_role": None,
            "dm_role": None,
            "welcome_channel": None,
            "log_channel": None,
            "ticket_category": None,
            "autorole": None,
            "mod_log": None,
            "game_channel": None
        }
    return guild_settings[guild_id]


def is_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator


def format_uptime():
    seconds = int(time.time() - start_time)

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
    if seconds or not parts:
        parts.append(f"{seconds} saniye")

    return ", ".join(parts)


async def get_support_member_count():
    guild = bot.get_guild(SUPPORT_SERVER_ID)

    if guild is not None:
        return guild.member_count

    try:
        guild = await bot.fetch_guild(SUPPORT_SERVER_ID)
        return guild.member_count or 0
    except Exception:
        return 0


def bot_color():
    return discord.Color.blue()


# =========================================================
# BOT READY
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

    try:
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=f"{PREFIX}yardım")
        )
    except Exception:
        pass


# =========================================================
# /BOT
# =========================================================

@bot.tree.command(
    name="bot",
    description="Dynex'in mevcut durumunu gösterir."
)
async def bot_info(interaction: discord.Interaction):

    await interaction.response.defer()

    try:
        guild_count = len(bot.guilds)

        support_count = await get_support_member_count()

        latency = round(bot.latency * 1000)

        if latency < 100:
            ping_text = "Mükemmel"
        elif latency < 200:
            ping_text = "İyi"
        elif latency < 350:
            ping_text = "Orta"
        elif latency < 500:
            ping_text = "Zayıf"
        else:
            ping_text = "Berbat"

        embed = discord.Embed(
            title="Dynex Durum",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Sunucu sayısı",
            value=f"`{guild_count}`",
            inline=False
        )

        embed.add_field(
            name="Destek sunucusu üye sayısı",
            value=f"`{support_count}`",
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
            name="Gecikme",
            value=f"`{latency}ms` • {ping_text}",
            inline=False
        )

        embed.add_field(
            name="Bot sahibi",
            value=f"<@{OWNER_ID}>",
            inline=False
        )

        embed.set_footer(text="Dynex")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print("/bot hatası:", repr(e))

        if interaction.response.is_done():
            await interaction.followup.send(
                "Bot bilgileri alınırken bir hata oluştu."
            )
        else:
            await interaction.response.send_message(
                "Bot bilgileri alınırken bir hata oluştu.",
                ephemeral=True
            )


# =========================================================
# /DİL
# SADECE KULLANAN KİŞİYİ DEĞİŞTİRİR
# =========================================================

@bot.tree.command(
    name="dil",
    description="Kendi Dynex dilini değiştir."
)
@app_commands.describe(
    dil="Türkçe, İngilizce veya Azerice"
)
@app_commands.choices(
    dil=[
        app_commands.Choice(name="Türkçe", value="tr"),
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Azərbaycan", value="az")
    ]
)
async def dil(
    interaction: discord.Interaction,
    dil: app_commands.Choice[str]
):

    user_languages[interaction.user.id] = dil.value

    names = {
        "tr": "Türkçe",
        "en": "English",
        "az": "Azərbaycan"
    }

    await interaction.response.send_message(
        f"Diliniz **{names[dil.value]}** olarak değiştirildi.",
        ephemeral=True
    )


# =========================================================
# AYARLAR VIEW
# =========================================================

class SettingsView(discord.ui.View):

    def __init__(self, owner_id):
        super().__init__(timeout=180)
        self.owner_id = owner_id

    async def interaction_check(self, interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "Bu ayarlar menüsü sana ait değil.",
                ephemeral=True
            )
            return False

        if not is_admin(interaction):
            await interaction.response.send_message(
                "Bu menüyü kullanmak için sunucuda Yönetici yetkisine sahip olmalısın.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.select(
        placeholder="Bir ayar seç...",
        options=[
            discord.SelectOption(
                label="Çekiliş Rolü",
                value="giveaway_role",
                emoji="🎉"
            ),
            discord.SelectOption(
                label="DM Duyuru Rolü",
                value="dm_role",
                emoji="📢"
            ),
            discord.SelectOption(
                label="Hoş Geldin Kanalı",
                value="welcome_channel",
                emoji="👋"
            ),
            discord.SelectOption(
                label="Log Kanalı",
                value="log_channel",
                emoji="📋"
            ),
            discord.SelectOption(
                label="Ticket Kategorisi",
                value="ticket_category",
                emoji="🎫"
            ),
            discord.SelectOption(
                label="Otorol",
                value="autorole",
                emoji="🪪"
            ),
            discord.SelectOption(
                label="Moderasyon Log",
                value="mod_log",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="Oyun Kanalı",
                value="game_channel",
                emoji="🎮"
            )
        ]
    )
    async def settings_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):

        setting = select.values[0]

        names = {
            "giveaway_role": "Çekiliş Rolü",
            "dm_role": "DM Duyuru Rolü",
            "welcome_channel": "Hoş Geldin Kanalı",
            "log_channel": "Log Kanalı",
            "ticket_category": "Ticket Kategorisi",
            "autorole": "Otorol",
            "mod_log": "Moderasyon Log",
            "game_channel": "Oyun Kanalı"
        }

        await interaction.response.send_message(
            f"**{names[setting]}** ayarını yapmak için aşağıdaki menüyü kullan.",
            view=SettingInputView(
                interaction.user.id,
                setting
            ),
            ephemeral=True
        )


class SettingInputView(discord.ui.View):

    def __init__(self, owner_id, setting):
        super().__init__(timeout=180)
        self.owner_id = owner_id
        self.setting = setting

    async def interaction_check(self, interaction):

        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "Bu menüyü sen açmadın.",
                ephemeral=True
            )
            return False

        if not is_admin(interaction):
            await interaction.response.send_message(
                "Bu ayarı değiştirmek için Yönetici yetkisi gerekiyor.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="ID Gir",
        style=discord.ButtonStyle.primary
    )
    async def id_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            SettingModal(
                self.owner_id,
                self.setting
            )
        )

    @discord.ui.button(
        label="Mevcut Ayarı Gör",
        style=discord.ButtonStyle.secondary
    )
    async def show_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        settings = get_guild_settings(interaction.guild.id)

        value = settings.get(self.setting)

        if value is None:
            text = "Ayarlanmadı."
        else:
            text = f"`{value}`"

        await interaction.response.send_message(
            f"Mevcut ayar: {text}",
            ephemeral=True
        )


class SettingModal(discord.ui.Modal):

    def __init__(self, owner_id, setting):
        super().__init__(title="Ayar Değiştir")
        self.owner_id = owner_id
        self.setting = setting

        self.value_input = discord.ui.TextInput(
            label="ID",
            placeholder="Rol / kanal / kategori ID'si",
            required=True,
            max_length=30
        )

        self.add_item(self.value_input)

    async def on_submit(self, interaction):

        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "Bu ayarı sen değiştiremezsin.",
                ephemeral=True
            )
            return

        if not is_admin(interaction):
            await interaction.response.send_message(
                "Bu ayarı değiştirmek için Yönetici yetkisi gerekiyor.",
                ephemeral=True
            )
            return

        value = self.value_input.value.strip()

        if not value.isdigit():
            await interaction.response.send_message(
                "Geçerli bir Discord ID gir.",
                ephemeral=True
            )
            return

        settings = get_guild_settings(interaction.guild.id)

        settings[self.setting] = int(value)

        await interaction.response.send_message(
            "Ayar başarıyla kaydedildi.",
            ephemeral=True
        )


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Sunucu ayarlarını yönet."
)
async def ayarlar(interaction: discord.Interaction):

    if interaction.guild is None:
        await interaction.response.send_message(
            "Bu komut sadece sunucularda kullanılabilir.",
            ephemeral=True
        )
        return

    if not is_admin(interaction):
        await interaction.response.send_message(
            "Bu komutu kullanmak için Yönetici yetkisine sahip olmalısın.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Dynex Ayarları",
        description=(
            "Aşağıdaki menüden ayarlamak istediğin sistemi seç.\n\n"
            "• Çekiliş rolü\n"
            "• DM duyuru rolü\n"
            "• Hoş geldin kanalı\n"
            "• Log kanalı\n"
            "• Ticket kategorisi\n"
            "• Otorol\n"
            "• Moderasyon log\n"
            "• Oyun kanalı"
        ),
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(interaction.user.id),
        ephemeral=True
    )


# =========================================================
# /YARDIM
# =========================================================

@bot.tree.command(
    name="yardım",
    description="Dynex komutlarını gösterir."
)
async def yardım(interaction):

    embed = discord.Embed(
        title="Dynex Yardım",
        description=(
            f"**Genel**\n"
            f"`/bot` • Bot bilgileri\n"
            f"`/dil` • Kendi dilini değiştir\n"
            f"`/ayarlar` • Sunucu ayarları\n\n"

            f"**Eğlence**\n"
            f"`/sayı-oyunu` • Sayı tahmin oyunu\n"
            f"`/kelime-oyunu` • Kelime oyunu\n"
            f"`/yazitura` • Yazı tura\n"
            f"`/zar` • Zar at\n"
            f"`/rastgele` • Rastgele sayı\n"
            f"`/8ball` • 8Ball\n\n"

            f"**Yönetim**\n"
            f"`/dm` • Role DM duyurusu\n"
            f"`/temizle` • Mesaj temizle"
        ),
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)


# =========================================================
# /ZAR
# =========================================================

@bot.tree.command(
    name="zar",
    description="1-6 arasında zar at."
)
async def zar(interaction):

    await interaction.response.send_message(
        f"🎲 Zar: **{random.randint(1, 6)}**"
    )


# =========================================================
# /YAZITURA
# =========================================================

@bot.tree.command(
    name="yazitura",
    description="Yazı veya tura at."
)
async def yazitura(interaction):

    await interaction.response.send_message(
        f"🪙 **{random.choice(['Yazı', 'Tura'])}**!"
    )


# =========================================================
# /RASTGELE
# =========================================================

@bot.tree.command(
    name="rastgele",
    description="Belirlediğin aralıkta rastgele sayı seç."
)
@app_commands.describe(
    minimum="Minimum sayı",
    maksimum="Maksimum sayı"
)
async def rastgele(
    interaction,
    minimum: int,
    maksimum: int
):

    if minimum > maksimum:
        await interaction.response.send_message(
            "Minimum sayı maksimumdan büyük olamaz.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🎯 Rastgele sayı: **{random.randint(minimum, maksimum)}**"
    )


# =========================================================
# /8BALL
# =========================================================

@bot.tree.command(
    name="8ball",
    description="Soruna rastgele cevap verir."
)
@app_commands.describe(
    soru="Sorun"
)
async def eightball(interaction, soru: str):

    answers = [
        "Evet.",
        "Hayır.",
        "Büyük ihtimalle.",
        "Sanmıyorum.",
        "Kesinlikle.",
        "Belki.",
        "Bunu zaman gösterecek.",
        "Şu an karar veremiyorum."
    ]

    await interaction.response.send_message(
        f"🎱 **{random.choice(answers)}**"
    )


# =========================================================
# SAYI OYUNU
# =========================================================

number_games = {}


@bot.tree.command(
    name="sayı-oyunu",
    description="Yönetici tarafından sayı tahmin oyunu başlatır."
)
@app_commands.describe(
    kanal="Oyunun oynanacağı kanal"
)
async def sayi_oyunu(
    interaction,
    kanal: discord.TextChannel
):

    if not is_admin(interaction):
        await interaction.response.send_message(
            "Bu oyunu sadece yöneticiler başlatabilir.",
            ephemeral=True
        )
        return

    number = random.randint(1, 100)

    number_games[kanal.id] = number

    await interaction.response.send_message(
        f"🎯 Sayı oyunu **{kanal.mention}** kanalında başladı!\n"
        f"1 ile 100 arasında bir sayı tuttum."
    )


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id in number_games:

        try:
            guess = int(message.content)
        except ValueError:
            guess = None

        if guess is not None:

            answer = number_games[message.channel.id]

            if guess == answer:

                await message.channel.send(
                    f"🎉 Tebrikler {message.author.mention}! "
                    f"Sayıyı doğru bildin: **{answer}**"
                )

                del number_games[message.channel.id]

            elif guess < answer:
                await message.channel.send(
                    "📈 Daha büyük bir sayı dene!"
                )

            else:
                await message.channel.send(
                    "📉 Daha küçük bir sayı dene!"
                )

    await bot.process_commands(message)


# =========================================================
# KELİME OYUNU
# =========================================================

word_games = {}

words = [
    "elma",
    "armut",
    "kalem",
    "kitap",
    "masa",
    "telefon",
    "bilgisayar",
    "futbol",
    "discord",
    "sunucu",
    "oyun",
    "araba",
    "ev",
    "okul",
    "deniz"
]


@bot.tree.command(
    name="kelime-oyunu",
    description="Yönetici tarafından kelime oyunu başlatır."
)
@app_commands.describe(
    kanal="Oyunun oynanacağı kanal"
)
async def kelime_oyunu(
    interaction,
    kanal: discord.TextChannel
):

    if not is_admin(interaction):
        await interaction.response.send_message(
            "Bu oyunu sadece yöneticiler başlatabilir.",
            ephemeral=True
        )
        return

    word = random.choice(words)

    word_games[kanal.id] = word

    await interaction.response.send_message(
        f"🔤 Kelime oyunu **{kanal.mention}** kanalında başladı!\n"
        f"Kelime: **{word[0]}{'_' * (len(word) - 1)}**"
    )


# =========================================================
# /TEMİZLE
# =========================================================

@bot.tree.command(
    name="temizle",
    description="Mesajları temizler."
)
@app_commands.describe(
    miktar="Silinecek mesaj sayısı"
)
async def temizle(
    interaction,
    miktar: int
):

    if not is_admin(interaction):
        await interaction.response.send_message(
            "Bu komutu kullanmak için Yönetici yetkisi gerekiyor.",
            ephemeral=True
        )
        return

    if miktar < 1 or miktar > 100:
        await interaction.response.send_message(
            "1 ile 100 arasında bir sayı gir.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=miktar)

    await interaction.followup.send(
        f"🧹 **{len(deleted)}** mesaj silindi.",
        ephemeral=True
    )


# =========================================================
# DM MODAL
# =========================================================

class DMModal(discord.ui.Modal):

    def __init__(self, role_id):
        super().__init__(title="DM Duyurusu")
        self.role_id = role_id

        self.baslik = discord.ui.TextInput(
            label="Başlık",
            placeholder="Duyuru başlığı",
            max_length=256
        )

        self.mesaj = discord.ui.TextInput(
            label="Mesaj",
            placeholder="Gönderilecek mesaj",
            style=discord.TextStyle.paragraph,
            max_length=4000
        )

        self.add_item(self.baslik)
        self.add_item(self.mesaj)

    async def on_submit(self, interaction):

        settings = get_guild_settings(interaction.guild.id)

        allowed_role = settings.get("dm_role")

        if allowed_role is None:
            await interaction.response.send_message(
                "DM gönderme yetkili rolü `/ayarlar` üzerinden ayarlanmamış.",
                ephemeral=True
            )
            return

        if allowed_role not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message(
                "DM duyurusu göndermek için ayarlanmış role sahip değilsin.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            await interaction.response.send_message(
                "Belirtilen rol bulunamadı.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        sent = 0
        failed = 0

        for member in role.members:

            if member.bot:
                continue

            try:

                embed = discord.Embed(
                    title=self.baslik.value,
                    description=self.mesaj.value,
                    color=discord.Color.blue()
                )

                embed.set_footer(text="Dynex")

                await member.send(embed=embed)

                sent += 1

            except Exception:
                failed += 1

            await asyncio.sleep(0.3)

        await interaction.followup.send(
            f"📨 DM duyurusu tamamlandı.\n\n"
            f"Başarılı: **{sent}**\n"
            f"Başarısız: **{failed}**",
            ephemeral=True
        )


# =========================================================
# /DM
# =========================================================

@bot.tree.command(
    name="dm",
    description="Bir role sahip kullanıcılara DM duyurusu gönder."
)
@app_commands.describe(
    rol="DM gönderilecek rol"
)
async def dm(
    interaction,
    rol: discord.Role
):

    settings = get_guild_settings(interaction.guild.id)

    allowed_role = settings.get("dm_role")

    if allowed_role is None:
        await interaction.response.send_message(
            "Önce `/ayarlar` üzerinden DM duyuru kullanma rolünü ayarla.",
            ephemeral=True
        )
        return

    if allowed_role not in [r.id for r in interaction.user.roles]:
        await interaction.response.send_message(
            "Bu komutu kullanma yetkin yok.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(
        DMModal(rol.id)
    )


# =========================================================
# HATA YAKALAMA
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    print(
        f"Slash komut hatası "
        f"({getattr(interaction.command, 'name', 'bilinmiyor')}):",
        repr(error)
    )

    try:

        message = "Komut çalıştırılırken bir hata oluştu."

        if isinstance(error, app_commands.MissingPermissions):
            message = "Bu komutu kullanmak için gerekli yetkiye sahip değilsin."

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

    except Exception as e:
        print("Hata mesajı gönderilemedi:", repr(e))


# =========================================================
# BAŞLAT
# =========================================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN bulunamadı. Hosting panelindeki Variables "
        "bölümüne DISCORD_TOKEN ekle."
    )

bot.run(TOKEN)
