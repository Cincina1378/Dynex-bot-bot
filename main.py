import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
import time
import random
import yt_dlp

# =========================
# AYARLAR
# =========================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
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

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    return data


def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


configs = load_config()


def get_config(guild_id):
    gid = str(guild_id)

    if gid not in configs:
        configs[gid] = DEFAULT_CONFIG.copy()
        save_config(configs)

    for key, value in DEFAULT_CONFIG.items():
        if key not in configs[gid]:
            configs[gid][key] = value

    return configs[gid]


# =========================
# MÜZİK
# =========================

music_states = {}


def get_music_state(guild_id):
    if guild_id not in music_states:
        music_states[guild_id] = {
            "queue": [],
            "current": None,
            "voice": None,
            "owner_id": None,
            "paused": False,
            "loop": False,
            "started_at": None,
            "paused_at": None,
            "paused_total": 0,
            "panel_message": None,
            "panel_view": None,
            "generation": 0
        }

    return music_states[guild_id]


YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": False,
    "extract_flat": False,
    "js_runtimes": {
        "node": {}
    },
    "remote_components": {
        "ejs": ["github"]
    }
}


async def extract_audio(url):
    loop = asyncio.get_running_loop()

    def extract():
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

            if not info:
                return None

            if "entries" in info:
                entries = info.get("entries")

                if not entries:
                    return None

                info = entries[0]

            return {
                "title": info.get("title", "Bilinmeyen Şarkı"),
                "url": info.get("url"),
                "webpage_url": info.get("webpage_url", url),
                "duration": info.get("duration") or 0,
                "thumbnail": info.get("thumbnail"),
                "original_url": url
            }

    try:
        return await loop.run_in_executor(None, extract)
    except Exception as e:
        print("YT-DLP HATASI:", repr(e))
        return None


def format_time(seconds):
    seconds = int(seconds or 0)

    minutes = seconds // 60
    seconds = seconds % 60

    return f"{minutes}:{seconds:02d}"


def get_elapsed(state):
    if not state["current"]:
        return 0

    if state["started_at"] is None:
        return 0

    if state["paused"]:
        if state["paused_at"] is None:
            return 0

        elapsed = state["paused_at"] - state["started_at"]
    else:
        elapsed = time.time() - state["started_at"]

    elapsed -= state["paused_total"]

    return max(0, elapsed)


def progress_bar(elapsed, duration):
    if not duration or duration <= 0:
        return "━━━━━━━━━━━━━━━━━━"

    total = 18

    position = int((elapsed / duration) * total)

    if position < 0:
        position = 0

    if position >= total:
        position = total - 1

    return (
        "━" * position
        + "🔵"
        + "━" * (total - position - 1)
    )


def music_embed(guild_id):
    state = get_music_state(guild_id)

    embed = discord.Embed(
        title="🎵 Dynex Müzik",
        color=discord.Color.blue()
    )

    current = state["current"]

    if not current:
        embed.description = "Şu anda müzik çalmıyor."
        return embed

    elapsed = get_elapsed(state)
    duration = current["duration"]

    if duration:
        if elapsed > duration:
            elapsed = duration

        bar = progress_bar(elapsed, duration)

        embed.description = (
            f"**{current['title']}**\n\n"
            f"`{format_time(elapsed)} {bar} {format_time(duration)}`"
        )
    else:
        embed.description = f"**{current['title']}**"

    if current.get("thumbnail"):
        embed.set_thumbnail(url=current["thumbnail"])

    if state["paused"]:
        status = "⏸️ Duraklatıldı"
    else:
        status = "▶️ Çalıyor"

    embed.add_field(
        name="Durum",
        value=status,
        inline=True
    )

    embed.add_field(
        name="Sıradaki",
        value=str(len(state["queue"])),
        inline=True
    )

    embed.add_field(
        name="Döngü",
        value="🔁 Açık" if state["loop"] else "Kapalı",
        inline=True
    )

    if state["owner_id"]:
        embed.set_footer(
            text=f"Panel sahibi: {guild_id}"
        )

    return embed


async def update_music_panel(guild_id):
    state = get_music_state(guild_id)

    message = state.get("panel_message")
    view = state.get("panel_view")

    if not message:
        return

    try:
        await message.edit(
            embed=music_embed(guild_id),
            view=view
        )
    except:
        pass


async def play_current(guild_id):
    state = get_music_state(guild_id)
    config = get_config(guild_id)

    voice = state["voice"]
    current = state["current"]

    if not voice or not current:
        return

    try:
        if voice.is_playing():
            voice.stop()
    except:
        pass

    ffmpeg_options = {
        "before_options": (
            "-reconnect 1 "
            "-reconnect_streamed 1 "
            "-reconnect_delay_max 5"
        ),
        "options": "-vn"
    }

    source = discord.FFmpegPCMAudio(
        current["url"],
        **ffmpeg_options
    )

    volume = config.get("music_default_volume", 50)
    volume = max(0, min(100, volume))

    source = discord.PCMVolumeTransformer(
        source,
        volume=volume / 100
    )

    state["paused"] = False
    state["paused_at"] = None
    state["paused_total"] = 0
    state["started_at"] = time.time()

    generation = state["generation"]

    def after(error):
        asyncio.run_coroutine_threadsafe(
            song_finished(guild_id, generation, error),
            bot.loop
        )

    try:
        voice.play(source, after=after)
    except Exception as e:
        print("PLAY HATASI:", repr(e))

    await update_music_panel(guild_id)


async def song_finished(guild_id, generation, error=None):
    state = get_music_state(guild_id)

    if generation != state["generation"]:
        return

    if error:
        print("MÜZİK HATASI:", repr(error))

    if state["loop"] and state["current"]:
        state["generation"] += 1
        await play_current(guild_id)
        return

    if state["queue"]:
        state["current"] = state["queue"].pop(0)
        state["generation"] += 1
        await play_current(guild_id)
        return

    state["current"] = None
    state["started_at"] = None
    state["paused"] = False

    await update_music_panel(guild_id)

    if state["voice"]:
        config = get_config(guild_id)

        if config.get("music_auto_leave", True):
            try:
                await state["voice"].disconnect()
            except:
                pass

            state["voice"] = None


# =========================
# MÜZİK PANELİ
# =========================

class MusicPanel(discord.ui.View):

    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    async def check_owner(self, interaction):
        state = get_music_state(self.guild_id)

        if state["owner_id"] != interaction.user.id:
            embed = discord.Embed(
                title="Erişim Reddedildi",
                description="Bu müzik panelini sadece paneli açan kişi kontrol edebilir.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="Önceki",
        emoji="⏮️",
        style=discord.ButtonStyle.secondary
    )
    async def previous(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        state = get_music_state(self.guild_id)

        if not state["queue"]:
            await interaction.response.send_message(
                "Sırada başka şarkı yok.",
                ephemeral=True
            )
            return

        if state["current"]:
            state["queue"].insert(0, state["current"])

        state["current"] = state["queue"].pop()

        state["generation"] += 1

        await interaction.response.defer()

        await play_current(self.guild_id)


    @discord.ui.button(
        label="Oynat / Duraklat",
        emoji="▶️",
        style=discord.ButtonStyle.primary
    )
    async def pause_play(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        state = get_music_state(self.guild_id)
        voice = state["voice"]

        if not voice:
            await interaction.response.send_message(
                "Ses kanalında değilim.",
                ephemeral=True
            )
            return

        if voice.is_playing():
            voice.pause()

            state["paused"] = True
            state["paused_at"] = time.time()

        elif voice.is_paused():
            voice.resume()

            if state["paused_at"]:
                state["paused_total"] += (
                    time.time() - state["paused_at"]
                )

            state["paused_at"] = None
            state["paused"] = False

        await interaction.response.defer()
        await update_music_panel(self.guild_id)


    @discord.ui.button(
        label="Sonraki",
        emoji="⏭️",
        style=discord.ButtonStyle.secondary
    )
    async def next_song(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        state = get_music_state(self.guild_id)

        if not state["queue"]:
            await interaction.response.send_message(
                "Sırada başka şarkı yok.",
                ephemeral=True
            )
            return

        state["current"] = state["queue"].pop(0)
        state["generation"] += 1

        await interaction.response.defer()

        await play_current(self.guild_id)


    @discord.ui.button(
        label="Karıştır",
        emoji="🔀",
        style=discord.ButtonStyle.secondary
    )
    async def shuffle(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        state = get_music_state(self.guild_id)

        if len(state["queue"]) < 2:
            await interaction.response.send_message(
                "Karıştırmak için en az 2 şarkı gerekli.",
                ephemeral=True
            )
            return

        random.shuffle(state["queue"])

        await interaction.response.send_message(
            "Müzik sırası karıştırıldı.",
            ephemeral=True
        )

        await update_music_panel(self.guild_id)


    @discord.ui.button(
        label="Döngü",
        emoji="🔁",
        style=discord.ButtonStyle.secondary
    )
    async def loop_song(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        state = get_music_state(self.guild_id)

        state["loop"] = not state["loop"]

        await interaction.response.defer()
        await update_music_panel(self.guild_id)


    @discord.ui.button(
        label="Sıra",
        emoji="📜",
        style=discord.ButtonStyle.secondary
    )
    async def queue_list(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        state = get_music_state(self.guild_id)

        if not state["queue"]:
            await interaction.response.send_message(
                "Müzik sırası boş.",
                ephemeral=True
            )
            return

        text = []

        for index, song in enumerate(state["queue"][:20], 1):
            text.append(
                f"`{index}.` {song['title']}"
            )

        embed = discord.Embed(
            title="📜 Müzik Sırası",
            description="\n".join(text),
            color=discord.Color.blue()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    @discord.ui.button(
        label="Durdur",
        emoji="⏹️",
        style=discord.ButtonStyle.danger
    )
    async def stop(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        state = get_music_state(self.guild_id)

        state["generation"] += 1
        state["queue"].clear()
        state["current"] = None
        state["started_at"] = None
        state["paused"] = False

        if state["voice"]:
            try:
                if state["voice"].is_playing():
                    state["voice"].stop()
            except:
                pass

            try:
                await state["voice"].disconnect()
            except:
                pass

        state["voice"] = None

        await interaction.response.defer()
        await update_music_panel(self.guild_id)


    @discord.ui.button(
        label="Yenile",
        emoji="🔄",
        style=discord.ButtonStyle.success
    )
    async def refresh(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not await self.check_owner(interaction):
            return

        await interaction.response.defer()
        await update_music_panel(self.guild_id)


# =========================
# /PLAY
# =========================

@bot.tree.command(
    name="play",
    description="Bir bağlantıdaki müziği oynatır."
)
@app_commands.describe(
    link="YouTube veya desteklenen müzik bağlantısı"
)
async def play(
    interaction: discord.Interaction,
    link: str
):
    config = get_config(interaction.guild.id)

    if not config.get("music_enabled", True):
        embed = discord.Embed(
            title="Müzik Kapalı",
            description="Bu sunucuda müzik sistemi kapalı.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        return

    if not interaction.user.voice:
        embed = discord.Embed(
            title="Ses Kanalı Gerekli",
            description="Önce bir ses kanalına gir.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        return

    if not link.startswith(("http://", "https://")):
        embed = discord.Embed(
            title="Geçersiz Bağlantı",
            description="Geçerli bir bağlantı gönder.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        return

    await interaction.response.defer()

    song = await extract_audio(link)

    if not song or not song.get("url"):
        embed = discord.Embed(
            title="Müzik Bulunamadı",
            description=(
                "Bağlantıdan müzik alınamadı.\n"
                "YouTube bağlantısının geçerli olduğundan emin ol."
            ),
            color=discord.Color.red()
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )
        return

    state = get_music_state(interaction.guild.id)

    channel = interaction.user.voice.channel

    try:
        if state["voice"] and state["voice"].is_connected():
            if state["voice"].channel != channel:
                await state["voice"].move_to(channel)
        else:
            state["voice"] = await channel.connect()
    except Exception as e:
        print("VOICE HATASI:", repr(e))

        embed = discord.Embed(
            title="Ses Kanalına Katılamadım",
            description="Bot ses kanalına bağlanamadı.",
            color=discord.Color.red()
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )
        return

    state["owner_id"] = interaction.user.id

    if state["current"]:
        state["queue"].append(song)

        embed = music_embed(interaction.guild.id)

        if state["panel_message"]:
            await state["panel_message"].edit(
                embed=embed,
                view=state["panel_view"]
            )

        await interaction.followup.send(
            f"**{song['title']}** sıraya eklendi.",
            ephemeral=True
        )

        return

    state["current"] = song
    state["generation"] += 1

    view = MusicPanel(interaction.guild.id)
    state["panel_view"] = view

    await play_current(interaction.guild.id)

    message = await interaction.followup.send(
        embed=music_embed(interaction.guild.id),
        view=view,
        wait=True
    )

    state["panel_message"] = message


# =========================
# /MÜZİK
# =========================

@bot.tree.command(
    name="müzik",
    description="Müzik panelini açar."
)
async def muzik(interaction: discord.Interaction):

    state = get_music_state(interaction.guild.id)

    if state["owner_id"] is None:
        state["owner_id"] = interaction.user.id

    view = MusicPanel(interaction.guild.id)

    state["panel_view"] = view

    message = await interaction.response.send_message(
        embed=music_embed(interaction.guild.id),
        view=view
    )

    try:
        state["panel_message"] = await interaction.original_response()
    except:
        pass


# =========================
# AYARLAR
# =========================

class SettingsView(discord.ui.View):

    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.guild_id = guild_id


    @discord.ui.button(
        label="Müzik",
        emoji="🎵",
        style=discord.ButtonStyle.primary
    )
    async def music_settings(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        config = get_config(self.guild_id)

        embed = discord.Embed(
            title="<:Ayarlar:1555263064721334282> Müzik Ayarları",
            description=(
                f"Müzik: {'Açık' if config['music_enabled'] else 'Kapalı'}\n"
                f"Varsayılan ses: %{config['music_default_volume']}\n"
                f"Maksimum ses: %{config['music_max_volume']}\n"
                f"Otomatik ayrılma: "
                f"{'Açık' if config['music_auto_leave'] else 'Kapalı'}"
            ),
            color=discord.Color.blue()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    @discord.ui.button(
        label="Genel",
        emoji="<:Dynexserver:1555263062112604270>",
        style=discord.ButtonStyle.secondary
    )
    async def general(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        config = get_config(self.guild_id)

        embed = discord.Embed(
            title="<:Ayarlar:1555263064721334282> Sunucu Ayarları",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Ticket",
            value="Açık" if config["ticket_enabled"] else "Kapalı",
            inline=True
        )

        embed.add_field(
            name="Log",
            value="Açık" if config["log_enabled"] else "Kapalı",
            inline=True
        )

        embed.add_field(
            name="Hoş Geldin",
            value="Açık" if config["welcome_enabled"] else "Kapalı",
            inline=True
        )

        embed.add_field(
            name="Otorol",
            value="Açık" if config["autorole_enabled"] else "Kapalı",
            inline=True
        )

        embed.add_field(
            name="Moderasyon",
            value="Açık" if config["moderation_enabled"] else "Kapalı",
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    @discord.ui.button(
        label="Sıfırla",
        emoji="🔄",
        style=discord.ButtonStyle.danger
    )
    async def reset(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        configs[str(self.guild_id)] = DEFAULT_CONFIG.copy()
        save_config(configs)

        embed = discord.Embed(
            title="<:Dynexevet:1555263066235605023> Ayarlar Sıfırlandı",
            description="Sunucu ayarları varsayılan değerlere döndürüldü.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını açar."
)
@app_commands.checks.has_permissions(manage_guild=True)
async def ayarlar(interaction: discord.Interaction):

    embed = discord.Embed(
        title="<:Ayarlar:1555263064721334282> Dynex Ayarları",
        description=(
            "Sunucunun Dynex ayarlarını bu panel üzerinden "
            "yönetebilirsin."
        ),
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed,
        view=SettingsView(interaction.guild.id),
        ephemeral=True
    )


@ayarlar.error
async def ayarlar_error(
    interaction: discord.Interaction,
    error
):
    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):
        embed = discord.Embed(
            title="<:Dynexhayir:1555265003727102134> Yetkin Yok",
            description="Bu komutu kullanmak için Sunucuyu Yönet yetkisi gerekiyor.",
            color=discord.Color.red()
        )

        if interaction.response.is_done():
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )


# =========================
# AYARLAR SIFIRLA
# =========================

@bot.tree.command(
    name="ayarlar-sifirla",
    description="Sunucu ayarlarını sıfırlar."
)
@app_commands.checks.has_permissions(administrator=True)
async def ayarlar_sifirla(
    interaction: discord.Interaction
):
    configs[str(interaction.guild.id)] = DEFAULT_CONFIG.copy()
    save_config(configs)

    embed = discord.Embed(
        title="<:Dynexevet:1555263066235605023> Sıfırlandı",
        description="Tüm Dynex ayarları sıfırlandı.",
        color=discord.Color.green()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# =========================
# PING
# =========================

@bot.tree.command(
    name="ping",
    description="Bot gecikmesini gösterir."
)
async def ping(interaction: discord.Interaction):

    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="<:Discord:1555263704646557816> Dynex Ping",
        description=f"**{latency}ms**",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================
# ÜYE GİRİŞ
# =========================

@bot.event
async def on_member_join(member):

    config = get_config(member.guild.id)

    if config.get("autorole_enabled"):
        role_id = config.get("autorole")

        if role_id:
            role = member.guild.get_role(role_id)

            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass

    if config.get("welcome_enabled"):
        channel_id = config.get("welcome_channel")

        if channel_id:
            channel = member.guild.get_channel(channel_id)

            if channel:
                message = config.get(
                    "welcome_message",
                    "Hoş geldin {user}!"
                )

                message = message.replace(
                    "{user}",
                    member.mention
                )

                try:
                    await channel.send(message)
                except:
                    pass


# =========================
# READY
# =========================

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
            "SLASH KOMUT HATASI:",
            repr(e)
        )


# =========================
# BAŞLAT
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
