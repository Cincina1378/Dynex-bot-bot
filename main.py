import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
import time
import random
import yt_dlp


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


# =========================================================
# DOSYA
# =========================================================

CONFIG_FILE = "config.json"


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
        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                {},
                f,
                indent=4,
                ensure_ascii=False
            )

        return {}

    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return {}


def save_config():
    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:
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

    changed = False

    for key, value in default_config().items():
        if key not in config[gid]:
            config[gid][key] = value
            changed = True

    if changed:
        save_config()

    return config[gid]


# =========================================================
# GENEL YARDIMCILAR
# =========================================================

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


def is_admin(interaction):
    return (
        interaction.guild is not None
        and interaction.user.guild_permissions.manage_guild
    )


# =========================================================
# MÜZİK SİSTEMİ
# =========================================================

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


# =========================================================
# YOUTUBE / YT-DLP
# =========================================================

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "extract_flat": False
}


def extract_audio(url):
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
        info = ydl.extract_info(
            url,
            download=False
        )

        if not info:
            raise RuntimeError(
                "Müzik bilgisi alınamadı."
            )

        if "entries" in info:
            entries = info.get("entries")

            if not entries:
                raise RuntimeError(
                    "Müzik bulunamadı."
                )

            info = entries[0]

        stream_url = info.get("url")

        if not stream_url:
            raise RuntimeError(
                "Ses akışı bulunamadı."
            )

        return {
            "title": info.get(
                "title",
                "Bilinmeyen şarkı"
            ),
            "url": stream_url,
            "webpage_url": info.get(
                "webpage_url",
                url
            ),
            "duration": int(
                info.get("duration") or 0
            ),
            "thumbnail": info.get(
                "thumbnail"
            ),
            "original_url": url
        }


async def get_audio(url):
    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        None,
        lambda: extract_audio(url)
    )


# =========================================================
# SÜRE
# =========================================================

def format_time(seconds):
    seconds = max(
        0,
        int(seconds)
    )

    hours = seconds // 3600
    minutes = (
        seconds % 3600
    ) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"

    return f"{minutes}:{secs:02d}"


def get_elapsed(state):
    current = state["current"]

    if not current:
        return 0

    if state["started_at"] is None:
        return 0

    if state["paused"]:
        end = state["paused_at"] or time.time()

        elapsed = (
            end
            - state["started_at"]
            - state["paused_total"]
        )

    else:
        elapsed = (
            time.time()
            - state["started_at"]
            - state["paused_total"]
        )

    return max(
        0,
        min(
            elapsed,
            current["duration"]
        )
    )


def progress_bar(elapsed, duration):
    if duration <= 0:
        return "`0:00 ━━━━━━━━━🔵━━━━━━━━ 0:00`"

    total_blocks = 18

    position = int(
        (elapsed / duration)
        * total_blocks
    )

    position = max(
        0,
        min(
            position,
            total_blocks
        )
    )

    left = "━" * position
    right = "━" * (
        total_blocks - position
    )

    return (
        f"`{format_time(elapsed)} "
        f"{left}🔵{right} "
        f"{format_time(duration)}`"
    )


# =========================================================
# MÜZİK EMBED
# =========================================================

def music_embed(guild_id):
    state = get_music_state(guild_id)

    current = state["current"]

    if not current:
        embed = discord.Embed(
            title="🎵 Dynex • Müzik",
            description=(
                "Şu anda müzik çalmıyor.\n\n"
                "Şarkı eklemek için `/play` kullan."
            ),
            color=discord.Color.blurple()
        )

        return embed

    elapsed = get_elapsed(state)
    duration = current["duration"]

    if state["paused"]:
        status = "⏸️ Duraklatıldı"
    else:
        status = "▶️ Çalıyor"

    queue = state["queue"]

    description = (
        f"**{current['title']}**\n\n"
        f"{status}\n\n"
        f"{progress_bar(elapsed, duration)}\n\n"
        f"📜 **Kuyruk:** `{len(queue)}` şarkı\n"
        f"🔁 **Döngü:** "
        f"{'Açık' if state['loop'] else 'Kapalı'}"
    )

    embed = discord.Embed(
        title="🎵 Dynex • Müzik",
        description=description,
        color=discord.Color.blurple()
    )

    if current.get("thumbnail"):
        embed.set_thumbnail(
            url=current["thumbnail"]
        )

    if state["owner_id"]:
        guild = bot.get_guild(guild_id)

        if guild:
            member = guild.get_member(
                state["owner_id"]
            )

            if member:
                embed.set_footer(
                    text=f"Panel sahibi: {member}"
                )

    return embed


# =========================================================
# MÜZİĞİ ÇAL
# =========================================================

async def play_current(guild_id):
    state = get_music_state(guild_id)

    voice = state["voice"]
    current = state["current"]

    if not voice or not current:
        return

    state["generation"] += 1
    generation = state["generation"]

    try:
        if voice.is_playing():
            voice.stop()

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

        guild_config = get_guild_config(
            guild_id
        )

        volume = (
            guild_config[
                "music_default_volume"
            ] / 100
        )

        source = discord.PCMVolumeTransformer(
            source,
            volume=volume
        )

        state["paused"] = False
        state["started_at"] = time.time()
        state["paused_at"] = None
        state["paused_total"] = 0

        def after_play(error):

            if error:
                print(
                    f"Müzik oynatma hatası: {error}"
                )

            asyncio.run_coroutine_threadsafe(
                song_finished(
                    guild_id,
                    generation
                ),
                bot.loop
            )

        voice.play(
            source,
            after=after_play
        )

    except Exception as e:
        print(
            f"FFmpeg oynatma hatası: {e}"
        )


async def song_finished(
    guild_id,
    generation
):
    state = get_music_state(guild_id)

    if generation != state["generation"]:
        return

    if state["loop"] and state["current"]:

        await play_current(
            guild_id
        )

        return

    if state["queue"]:

        state["current"] = state[
            "queue"
        ].pop(0)

        await play_current(
            guild_id
        )

    else:

        state["current"] = None
        state["started_at"] = None
        state["paused_at"] = None

        voice = state["voice"]

        if voice and voice.is_connected():

            try:
                await voice.disconnect()
            except Exception:
                pass

        state["voice"] = None

    await update_music_panel(
        guild_id
    )


# =========================================================
# PANEL GÜNCELLE
# =========================================================

async def update_music_panel(guild_id):
    state = get_music_state(guild_id)

    message = state.get(
        "panel_message"
    )

    view = state.get(
        "panel_view"
    )

    if not message:
        return

    try:
        await message.edit(
            embed=music_embed(guild_id),
            view=view
        )

    except Exception:
        pass


# =========================================================
# MÜZİK PANELİ
# =========================================================

class MusicPanel(discord.ui.View):

    def __init__(self, owner_id):
        super().__init__(
            timeout=None
        )

        self.owner_id = owner_id

    async def check_owner(
        self,
        interaction
    ):

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
    async def previous(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        state = get_music_state(
            interaction.guild.id
        )

        if not state["current"]:
            await interaction.response.send_message(
                embed=error_embed(
                    "Şu anda çalan bir şarkı yok."
                ),
                ephemeral=True
            )
            return

        if state["queue"]:

            previous = state["queue"].pop()

            state["queue"].insert(
                0,
                state["current"]
            )

            state["current"] = previous

            await play_current(
                interaction.guild.id
            )

            await interaction.response.edit_message(
                embed=music_embed(
                    interaction.guild.id
                ),
                view=self
            )

        else:

            await interaction.response.send_message(
                embed=info_embed(
                    "Önceki şarkı bulunmuyor."
                ),
                ephemeral=True
            )

    @discord.ui.button(
        label="Oynat / Duraklat",
        emoji="⏸️",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_music_pause"
    )
    async def pause(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        state = get_music_state(
            interaction.guild.id
        )

        voice = state["voice"]

        if not voice or not voice.is_connected():
            await interaction.response.send_message(
                embed=error_embed(
                    "Bot bir ses kanalında değil."
                ),
                ephemeral=True
            )
            return

        if state["paused"]:

            if voice.is_paused():
                voice.resume()

            if state["paused_at"]:
                state["paused_total"] += (
                    time.time()
                    - state["paused_at"]
                )

            state["paused"] = False
            state["paused_at"] = None

        else:

            if voice.is_playing():
                voice.pause()

            state["paused"] = True
            state["paused_at"] = time.time()

        await interaction.response.edit_message(
            embed=music_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="Sonraki",
        emoji="⏭️",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_next"
    )
    async def next(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        state = get_music_state(
            interaction.guild.id
        )

        if not state["queue"]:

            await interaction.response.send_message(
                embed=info_embed(
                    "Kuyrukta başka şarkı yok."
                ),
                ephemeral=True
            )
            return

        state["generation"] += 1

        state["current"] = state[
            "queue"
        ].pop(0)

        await play_current(
            interaction.guild.id
        )

        await interaction.response.edit_message(
            embed=music_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="Karıştır",
        emoji="🔀",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_shuffle"
    )
    async def shuffle(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        state = get_music_state(
            interaction.guild.id
        )

        if len(state["queue"]) < 2:

            await interaction.response.send_message(
                embed=info_embed(
                    "Karıştırmak için kuyrukta en az 2 şarkı olmalı."
                ),
                ephemeral=True
            )
            return

        random.shuffle(
            state["queue"]
        )

        await interaction.response.edit_message(
            embed=music_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="Döngü",
        emoji="🔁",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_loop"
    )
    async def loop_button(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        state = get_music_state(
            interaction.guild.id
        )

        state["loop"] = not state[
            "loop"
        ]

        await interaction.response.edit_message(
            embed=music_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="Kuyruk",
        emoji="📜",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_queue"
    )
    async def queue(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        state = get_music_state(
            interaction.guild.id
        )

        if not state["queue"]:

            text = "Kuyruk boş."

        else:

            lines = []

            for index, song in enumerate(
                state["queue"][:15],
                start=1
            ):
                lines.append(
                    f"`{index}.` {song['title']}"
                )

            text = "\n".join(
                lines
            )

        await interaction.response.send_message(
            embed=discord.Embed(
                title="📜 Müzik Kuyruğu",
                description=text,
                color=discord.Color.blurple()
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="Durdur",
        emoji="⏹️",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_music_stop"
    )
    async def stop(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        state = get_music_state(
            interaction.guild.id
        )

        state["generation"] += 1
        state["queue"].clear()
        state["current"] = None
        state["started_at"] = None
        state["paused_at"] = None
        state["paused_total"] = 0

        voice = state["voice"]

        if voice:

            try:

                if voice.is_playing():
                    voice.stop()

                if voice.is_connected():
                    await voice.disconnect()

            except Exception:
                pass

        state["voice"] = None

        await interaction.response.edit_message(
            embed=music_embed(
                interaction.guild.id
            ),
            view=self
        )

    @discord.ui.button(
        label="Yenile",
        emoji="🔄",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_music_refresh"
    )
    async def refresh(
        self,
        interaction,
        button
    ):

        if not await self.check_owner(
            interaction
        ):
            return

        await interaction.response.edit_message(
            embed=music_embed(
                interaction.guild.id
            ),
            view=self
        )


# =========================================================
# /PLAY
# =========================================================

@bot.tree.command(
    name="play",
    description="Bir müzik bağlantısını oynatır."
)
@app_commands.describe(
    link="Müzik bağlantısı"
)
async def play(
    interaction: discord.Interaction,
    link: str
):

    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            embed=error_embed(
                "Bu komut yalnızca sunucularda kullanılabilir."
            ),
            ephemeral=True
        )
        return

    guild_config = get_guild_config(
        guild.id
    )

    if not guild_config[
        "music_enabled"
    ]:

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

    if not link.startswith(
        (
            "http://",
            "https://"
        )
    ):

        await interaction.response.send_message(
            embed=error_embed(
                "Geçerli bir bağlantı gir."
            ),
            ephemeral=True
        )
        return

    await interaction.response.defer()

    try:

        song = await get_audio(
            link
        )

    except Exception as e:

        print(
            f"yt-dlp hatası: {e}"
        )

        await interaction.followup.send(
            embed=error_embed(
                "Bu bağlantıdan müzik bilgisi alınamadı."
            ),
            ephemeral=True
        )
        return

    state = get_music_state(
        guild.id
    )

    voice_channel = (
        interaction.user.voice.channel
    )

    voice = state["voice"]

    try:

        if voice and voice.is_connected():

            if voice.channel.id != voice_channel.id:

                await voice.move_to(
                    voice_channel
                )

        else:

            voice = await voice_channel.connect()

            state["voice"] = voice

    except Exception as e:

        print(
            f"Ses kanalına bağlanma hatası: {e}"
        )

        await interaction.followup.send(
            embed=error_embed(
                "Ses kanalına bağlanamadım. "
                "Botun ses kanalına bağlanma ve konuşma izinlerini kontrol et."
            ),
            ephemeral=True
        )
        return

    state["owner_id"] = (
        interaction.user.id
    )

    if state["current"]:

        state["queue"].append(
            song
        )

        await interaction.followup.send(
            embed=success_embed(
                f"**{song['title']}** kuyruğa eklendi."
            )
        )

    else:

        state["current"] = song

        await play_current(
            guild.id
        )

        await interaction.followup.send(
            embed=music_embed(
                guild.id
            ),
            view=MusicPanel(
                interaction.user.id
            )
        )

        message = (
            await interaction.original_response()
        )

        state["panel_message"] = message

        view = state.get(
            "panel_view"
        )

        if view is None:
            view = MusicPanel(
                interaction.user.id
            )

            state["panel_view"] = view

            await message.edit(
                embed=music_embed(
                    guild.id
                ),
                view=view
            )


# =========================================================
# /MÜZİK
# =========================================================

@bot.tree.command(
    name="müzik",
    description="Dynex müzik panelini açar."
)
async def muzik(
    interaction: discord.Interaction
):

    guild = interaction.guild

    if guild is None:
        return

    state = get_music_state(
        guild.id
    )

    if state["owner_id"] is None:

        state["owner_id"] = (
            interaction.user.id
        )

    view = MusicPanel(
        state["owner_id"]
    )

    state["panel_view"] = view

    await interaction.response.send_message(
        embed=music_embed(
            guild.id
        ),
        view=view
    )

    state["panel_message"] = (
        await interaction.original_response()
    )


# =========================================================
# AYARLAR PANELİ
# =========================================================

class MusicSettingsModal(
    discord.ui.Modal,
    title="Müzik Ayarları"
):

    max_volume = discord.ui.TextInput(
        label="Maksimum Ses",
        placeholder="100",
        required=True,
        max_length=3
    )

    default_volume = discord.ui.TextInput(
        label="Varsayılan Ses",
        placeholder="50",
        required=True,
        max_length=3
    )

    async def on_submit(
        self,
        interaction
    ):

        if not is_admin(interaction):

            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        try:

            maximum = int(
                self.max_volume.value
            )

            default = int(
                self.default_volume.value
            )

        except ValueError:

            await interaction.response.send_message(
                embed=error_embed(
                    "Ses değerleri sayı olmalıdır."
                ),
                ephemeral=True
            )
            return

        if maximum < 1 or maximum > 200:

            await interaction.response.send_message(
                embed=error_embed(
                    "Maksimum ses 1-200 arasında olmalıdır."
                ),
                ephemeral=True
            )
            return

        if default < 0 or default > maximum:

            await interaction.response.send_message(
                embed=error_embed(
                    "Varsayılan ses maksimum sesten büyük olamaz."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "music_max_volume"
        ] = maximum

        settings[
            "music_default_volume"
        ] = default

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                "Müzik ayarları güncellendi."
            ),
            ephemeral=True
        )


class ChannelModal(
    discord.ui.Modal,
    title="Kanal Ayarı"
):

    channel_id = discord.ui.TextInput(
        label="Kanal ID",
        placeholder="Kanal ID",
        required=True
    )

    def __init__(self, setting):
        super().__init__()
        self.setting = setting

    async def on_submit(
        self,
        interaction
    ):

        if not is_admin(interaction):

            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        try:

            channel_id = int(
                self.channel_id.value
            )

        except ValueError:

            await interaction.response.send_message(
                embed=error_embed(
                    "Geçerli bir kanal ID'si gir."
                ),
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(
            channel_id
        )

        if channel is None:

            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ID ile kanal bulunamadı."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            self.setting
        ] = channel.id

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                f"Kanal ayarlandı: {channel.mention}"
            ),
            ephemeral=True
        )


class RoleModal(
    discord.ui.Modal,
    title="Oto Rol"
):

    role_id = discord.ui.TextInput(
        label="Rol ID",
        placeholder="Rol ID",
        required=True
    )

    async def on_submit(
        self,
        interaction
    ):

        if not is_admin(interaction):

            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        try:

            role_id = int(
                self.role_id.value
            )

        except ValueError:

            await interaction.response.send_message(
                embed=error_embed(
                    "Geçerli bir rol ID'si gir."
                ),
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(
            role_id
        )

        if role is None:

            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ID ile rol bulunamadı."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings["autorole"] = role.id
        settings["autorole_enabled"] = True

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                f"Oto rol ayarlandı: {role.mention}"
            ),
            ephemeral=True
        )


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

    async def on_submit(
        self,
        interaction
    ):

        if not is_admin(interaction):

            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri değiştirebilir."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "welcome_message"
        ] = self.message.value

        settings[
            "welcome_enabled"
        ] = True

        save_config()

        await interaction.response.send_message(
            embed=success_embed(
                "Karşılama mesajı kaydedildi."
            ),
            ephemeral=True
        )


class SettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(
            timeout=300
        )

    def panel_embed(
        self,
        guild_config
    ):

        return discord.Embed(
            title=f"{AYARLAR} Dynex • Sunucu Ayarları",
            description=(
                f"{SERVER} **Sistemler**\n\n"

                f"🎫 Ticket: "
                f"{'Açık' if guild_config['ticket_enabled'] else 'Kapalı'}\n"

                f"🎵 Müzik: "
                f"{'Açık' if guild_config['music_enabled'] else 'Kapalı'}\n"

                f"📋 Log: "
                f"{'Açık' if guild_config['log_enabled'] else 'Kapalı'}\n"

                f"👋 Karşılama: "
                f"{'Açık' if guild_config['welcome_enabled'] else 'Kapalı'}\n"

                f"🤖 Oto Rol: "
                f"{'Açık' if guild_config['autorole_enabled'] else 'Kapalı'}\n"

                f"🛡️ Moderasyon: "
                f"{'Açık' if guild_config['moderation_enabled'] else 'Kapalı'}\n\n"

                f"🔊 Maksimum ses: "
                f"%{guild_config['music_max_volume']}\n"

                f"🔉 Varsayılan ses: "
                f"%{guild_config['music_default_volume']}"
            ),
            color=discord.Color.blurple()
        )

    async def update(
        self,
        interaction
    ):

        settings = get_guild_config(
            interaction.guild.id
        )

        await interaction.response.edit_message(
            embed=self.panel_embed(settings),
            view=self
        )

    @discord.ui.button(
        label="Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def ticket(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "ticket_enabled"
        ] = not settings[
            "ticket_enabled"
        ]

        save_config()

        await self.update(
            interaction
        )

    @discord.ui.button(
        label="Müzik Ayarları",
        emoji="🎵",
        style=discord.ButtonStyle.primary,
        row=0
    )
    async def music(
        self,
        interaction,
        button
    ):

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
    async def music_toggle(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "music_enabled"
        ] = not settings[
            "music_enabled"
        ]

        save_config()

        await self.update(
            interaction
        )

    @discord.ui.button(
        label="Log",
        emoji="📋",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def logs(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "log_enabled"
        ] = not settings[
            "log_enabled"
        ]

        save_config()

        await self.update(
            interaction
        )

    @discord.ui.button(
        label="Log Kanalı",
        emoji="📢",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def log_channel(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            ChannelModal(
                "log_channel"
            )
        )

    @discord.ui.button(
        label="Karşılama",
        emoji="👋",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def welcome(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "welcome_enabled"
        ] = not settings[
            "welcome_enabled"
        ]

        save_config()

        await self.update(
            interaction
        )

    @discord.ui.button(
        label="Karşılama Kanalı",
        emoji="💬",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def welcome_channel(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            ChannelModal(
                "welcome_channel"
            )
        )

    @discord.ui.button(
        label="Karşılama Mesajı",
        emoji="✏️",
        style=discord.ButtonStyle.secondary,
        row=2
    )
    async def welcome_message(
        self,
        interaction,
        button
    ):

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
    async def autorole(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "autorole_enabled"
        ] = not settings[
            "autorole_enabled"
        ]

        save_config()

        await self.update(
            interaction
        )

    @discord.ui.button(
        label="Oto Rol Seç",
        emoji="🎭",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def autorole_select(
        self,
        interaction,
        button
    ):

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
    async def moderation(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        settings = get_guild_config(
            interaction.guild.id
        )

        settings[
            "moderation_enabled"
        ] = not settings[
            "moderation_enabled"
        ]

        save_config()

        await self.update(
            interaction
        )

    @discord.ui.button(
        label="Sıfırla",
        emoji="♻️",
        style=discord.ButtonStyle.danger,
        row=3
    )
    async def reset(
        self,
        interaction,
        button
    ):

        if not is_admin(interaction):
            await interaction.response.send_message(
                embed=error_embed(
                    "Bu ayarı yalnızca sunucu yöneticileri kullanabilir."
                ),
                ephemeral=True
            )
            return

        config[
            str(interaction.guild.id)
        ] = default_config()

        save_config()

        await self.update(
            interaction
        )


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönetir."
)
@app_commands.checks.has_permissions(
    manage_guild=True
)
async def ayarlar(
    interaction: discord.Interaction
):

    settings = get_guild_config(
        interaction.guild.id
    )

    view = SettingsView()

    await interaction.response.send_message(
        embed=view.panel_embed(
            settings
        ),
        view=view,
        ephemeral=True
    )


# =========================================================
# /AYARLAR-SIFIRLA
# =========================================================

@bot.tree.command(
    name="ayarlar-sifirla",
    description="Dynex ayarlarını sıfırlar."
)
@app_commands.checks.has_permissions(
    manage_guild=True
)
async def ayarlar_sifirla(
    interaction: discord.Interaction
):

    config[
        str(interaction.guild.id)
    ] = default_config()

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
# ÜYE GİRİŞ
# =========================================================

@bot.event
async def on_member_join(
    member
):

    settings = get_guild_config(
        member.guild.id
    )

    if settings[
        "autorole_enabled"
    ]:

        role_id = settings.get(
            "autorole"
        )

        if role_id:

            role = member.guild.get_role(
                role_id
            )

            if role:

                try:
                    await member.add_roles(
                        role
                    )
                except Exception:
                    pass

    if settings[
        "welcome_enabled"
    ]:

        channel_id = settings.get(
            "welcome_channel"
        )

        if channel_id:

            channel = member.guild.get_channel(
                channel_id
            )

            if channel:

                message = settings.get(
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
# HAZIR
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
            f"Slash komut hatası: {e}"
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
                    f"{KILITLI} Bu komut için sunucuyu yönetme yetkisi gerekiyor."
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
                    f"{KILITLI} Bu komut için sunucuyu yönetme yetkisi gerekiyor."
                ),
                ephemeral=True
            )


# =========================================================
# TOKEN
# =========================================================

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN bulunamadı."
    )


bot.run(TOKEN)
