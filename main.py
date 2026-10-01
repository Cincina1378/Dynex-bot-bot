import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime, timezone


# =========================================================
# TOKEN
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

CONFIG_FILE = "config.json"


# =========================================================
# INTENTS
# =========================================================

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True
INTENTS.voice_states = True


# =========================================================
# DİLLER
# =========================================================

LANGUAGES = {
    "tr": "🇹🇷 Türkçe",
    "en": "🇬🇧 English",
    "az": "🇦🇿 Azərbaycan"
}


TEXTS = {

    "tr": {
        "language_name": "Türkçe",
        "language_title": "Dynex Dil Seçimi",
        "language_description": "Dynex'in kullanacağı dili seçin.",
        "language_changed": "Diliniz Türkçe olarak ayarlandı.",
        "already_language": "Zaten Türkçe kullanıyorsunuz.",

        "ping_title": "Dynex Ping Durumu",
        "ping_description": "Dynex'in internet bağlantı durumu",
        "ping": "Ping",
        "excellent": "Mükemmel",
        "good": "İyi",
        "medium": "Orta",
        "weak": "Zayıf",
        "bad": "Berbat",

        "settings_title": "Dynex Ayarları",
        "settings_description": "Sunucunuzun Dynex ayarlarını buradan yönetin.",

        "ticket": "🎫 Ticket",
        "logs": "📜 Loglar",
        "welcome": "👋 Hoş Geldin",
        "autorole": "👤 Otorol",
        "moderation": "🛡️ Moderasyon",

        "enabled": "Açık",
        "disabled": "Kapalı",

        "refresh": "🔄 Yenile",
        "reset": "♻️ Sıfırla",

        "ticket_open": "🎫 Ticket Aç",
        "ticket_close": "🔒 Ticket Kapat",
        "add_member": "👤 Üye Ekle",

        "ticket_created": "Ticket oluşturuldu.",
        "ticket_closed": "Ticket kapatılıyor.",
        "ticket_disabled": "Ticket sistemi şu anda kapalı.",

        "problem": "Sorun",
        "problem_placeholder": "Sorununuzu yazın.",

        "member_id": "Üye ID",
        "member_id_placeholder": "Eklenecek üyenin Discord ID'si",
        "member_added": "Üye ticket'a eklendi.",
        "invalid_member": "Geçerli bir üye bulunamadı.",

        "permission": "Bu işlem için yeterli yetkiniz yok.",
        "saved": "Ayar kaydedildi.",
        "reset_done": "Sunucu ayarları sıfırlandı.",

        "welcome_default": "Hoş geldin {member}!",

        "voice_title": "Ses Kanalı İstatistikleri",
        "voice_joined": "Katıldığı kanal",
        "voice_left": "Ayrıldığı kanal",
        "voice_duration": "Ses kanalında kalma süresi",
        "voice_members": "Çıkış anındaki üye sayısı",

        "voice_disable": "🔕 Ses Bildirimlerini Kapat",
        "voice_enable": "🔔 Ses Bildirimlerini Aç",

        "voice_disabled": "Ses bildirimleri kapatıldı.",
        "voice_enabled": "Ses bildirimleri açıldı.",

        "yes": "Evet",
        "no": "Hayır"
    },


    "en": {
        "language_name": "English",
        "language_title": "Dynex Language Selection",
        "language_description": "Select the language Dynex should use.",
        "language_changed": "Your language has been set to English.",
        "already_language": "You are already using English.",

        "ping_title": "Dynex Ping Status",
        "ping_description": "Dynex internet connection status",
        "ping": "Ping",
        "excellent": "Excellent",
        "good": "Good",
        "medium": "Medium",
        "weak": "Weak",
        "bad": "Very Bad",

        "settings_title": "Dynex Settings",
        "settings_description": "Manage your server's Dynex settings here.",

        "ticket": "🎫 Ticket",
        "logs": "📜 Logs",
        "welcome": "👋 Welcome",
        "autorole": "👤 Autorole",
        "moderation": "🛡️ Moderation",

        "enabled": "Enabled",
        "disabled": "Disabled",

        "refresh": "🔄 Refresh",
        "reset": "♻️ Reset",

        "ticket_open": "🎫 Open Ticket",
        "ticket_close": "🔒 Close Ticket",
        "add_member": "👤 Add Member",

        "ticket_created": "Ticket created.",
        "ticket_closed": "The ticket is being closed.",
        "ticket_disabled": "The ticket system is currently disabled.",

        "problem": "Problem",
        "problem_placeholder": "Describe your problem.",

        "member_id": "Member ID",
        "member_id_placeholder": "Discord ID of the member to add",
        "member_added": "The member was added to the ticket.",
        "invalid_member": "No valid member was found.",

        "permission": "You do not have permission to do this.",
        "saved": "Setting saved.",
        "reset_done": "Server settings have been reset.",

        "welcome_default": "Welcome {member}!",

        "voice_title": "Voice Channel Statistics",
        "voice_joined": "Joined channel",
        "voice_left": "Left channel",
        "voice_duration": "Time spent in voice",
        "voice_members": "Members when leaving",

        "voice_disable": "🔕 Disable Voice Notifications",
        "voice_enable": "🔔 Enable Voice Notifications",

        "voice_disabled": "Voice notifications have been disabled.",
        "voice_enabled": "Voice notifications have been enabled.",

        "yes": "Yes",
        "no": "No"
    },


    "az": {
        "language_name": "Azərbaycan",
        "language_title": "Dynex Dil Seçimi",
        "language_description": "Dynex üçün dili seçin.",
        "language_changed": "Diliniz Azərbaycan dili olaraq təyin edildi.",
        "already_language": "Artıq Azərbaycan dilindən istifadə edirsiniz.",

        "ping_title": "Dynex Ping Vəziyyəti",
        "ping_description": "Dynex internet bağlantı vəziyyəti",
        "ping": "Ping",
        "excellent": "Əla",
        "good": "Yaxşı",
        "medium": "Orta",
        "weak": "Zəif",
        "bad": "Çox Zəif",

        "settings_title": "Dynex Ayarları",
        "settings_description": "Dynex server ayarlarını buradan idarə edin.",

        "ticket": "🎫 Ticket",
        "logs": "📜 Loglar",
        "welcome": "👋 Qarşılama",
        "autorole": "👤 Avtorol",
        "moderation": "🛡️ Moderasiya",

        "enabled": "Aktiv",
        "disabled": "Deaktiv",

        "refresh": "🔄 Yenilə",
        "reset": "♻️ Sıfırla",

        "ticket_open": "🎫 Ticket Aç",
        "ticket_close": "🔒 Ticketi Bağla",
        "add_member": "👤 Üzv Əlavə Et",

        "ticket_created": "Ticket yaradıldı.",
        "ticket_closed": "Ticket bağlanır.",
        "ticket_disabled": "Ticket sistemi hazırda deaktivdir.",

        "problem": "Problem",
        "problem_placeholder": "Probleminizi yazın.",

        "member_id": "Üzv ID-si",
        "member_id_placeholder": "Əlavə ediləcək üzvün Discord ID-si",
        "member_added": "Üzv ticketə əlavə edildi.",
        "invalid_member": "Etibarlı üzv tapılmadı.",

        "permission": "Bunu etmək üçün icazəniz yoxdur.",
        "saved": "Ayar yadda saxlanıldı.",
        "reset_done": "Server ayarları sıfırlandı.",

        "welcome_default": "Xoş gəlmisən {member}!",

        "voice_title": "Səs Kanalı Statistikası",
        "voice_joined": "Qoşulduğu kanal",
        "voice_left": "Ayrıldığı kanal",
        "voice_duration": "Səs kanalında qalma müddəti",
        "voice_members": "Çıxış zamanı üzv sayı",

        "voice_disable": "🔕 Səs bildirişlərini söndür",
        "voice_enable": "🔔 Səs bildirişlərini aktiv et",

        "voice_disabled": "Səs bildirişləri söndürüldü.",
        "voice_enabled": "Səs bildirişləri aktiv edildi.",

        "yes": "Bəli",
        "no": "Xeyr"
    }
}


# =========================================================
# VARSAYILAN AYARLAR
# =========================================================

DEFAULT_CONFIG = {
    "language": "tr",
    "ticket": True,
    "ticket_category": None,
    "logs": False,
    "log_channel": None,
    "welcome": False,
    "welcome_channel": None,
    "welcome_message": "Hoş geldin {member}!",
    "autorole": False,
    "autorole_role": None,
    "moderation": True
}


configs = {}
user_settings = {}
voice_sessions = {}


# =========================================================
# VERİ SİSTEMİ
# =========================================================

def load_data():

    global configs
    global user_settings

    if not os.path.exists(CONFIG_FILE):
        configs = {}
        user_settings = {}
        return

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            configs = data.get(
                "configs",
                {}
            )

            user_settings = data.get(
                "user_settings",
                {}
            )

    except Exception:

        configs = {}
        user_settings = {}


def save_data():

    data = {
        "configs": configs,
        "user_settings": user_settings
    }

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


def get_config(guild_id):

    guild_id = str(guild_id)

    if guild_id not in configs:

        configs[guild_id] = DEFAULT_CONFIG.copy()

        save_data()

    return configs[guild_id]


def get_user_settings(user_id):

    user_id = str(user_id)

    if user_id not in user_settings:

        user_settings[user_id] = {
            "language": "tr",
            "voice_notifications": True
        }

        save_data()

    return user_settings[user_id]


def get_language(guild_id):

    config = get_config(guild_id)

    language = config.get(
        "language",
        "tr"
    )

    if language not in LANGUAGES:
        language = "tr"

    return language


def set_language(guild_id, language):

    if language not in LANGUAGES:
        language = "tr"

    config = get_config(guild_id)

    config["language"] = language

    save_data()


def get_voice_notifications(user_id):

    settings = get_user_settings(user_id)

    return settings.get(
        "voice_notifications",
        True
    )


def set_voice_notifications(
    user_id,
    value
):

    settings = get_user_settings(user_id)

    settings["voice_notifications"] = value

    save_data()


def t(language, key, **kwargs):

    language_texts = TEXTS.get(
        language,
        TEXTS["tr"]
    )

    text = language_texts.get(
        key,
        TEXTS["tr"].get(
            key,
            key
        )
    )

    if kwargs:

        try:
            text = text.format(**kwargs)

        except Exception:
            pass

    return text


# =========================================================
# BOT
# =========================================================

class DynexBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=INTENTS
        )

    async def setup_hook(self):

        await self.tree.sync()


bot = DynexBot()


# =========================================================
# DİL SEÇİMİ
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
            placeholder="Dil seçin / Select language",
            options=options,
            custom_id="dynex_language_select"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        language = self.values[0]

        set_language(
            interaction.guild.id,
            language
        )

        await interaction.response.send_message(
            t(
                language,
                "language_changed"
            ),
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
    description="Dynex dilini değiştir."
)
async def dil(
    interaction: discord.Interaction
):

    language = get_language(
        interaction.guild.id
    )

    embed = discord.Embed(
        title=t(
            language,
            "language_title"
        ),
        description=t(
            language,
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
# PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Botun ping durumunu gösterir."
)
async def ping(
    interaction: discord.Interaction
):

    language = get_language(
        interaction.guild.id
    )

    latency = round(
        bot.latency * 1000
    )

    if latency <= 80:

        status = t(
            language,
            "excellent"
        )

    elif latency <= 150:

        status = t(
            language,
            "good"
        )

    elif latency <= 250:

        status = t(
            language,
            "medium"
        )

    elif latency <= 400:

        status = t(
            language,
            "weak"
        )

    else:

        status = t(
            language,
            "bad"
        )

    embed = discord.Embed(
        title=t(
            language,
            "ping_title"
        ),
        description=t(
            language,
            "ping_description"
        ),
        color=discord.Color.from_rgb(
            0,
            0,
            0
        )
    )

    embed.add_field(
        name=t(
            language,
            "ping"
        ),
        value=(
            f"`{latency}ms`\n"
            f"**{status}**"
        ),
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# SES BİLDİRİMİ
# =========================================================

class VoiceNotificationView(
    discord.ui.View
):

    def __init__(self, user_id):

        super().__init__(
            timeout=None
        )

        self.user_id = user_id

        enabled = get_voice_notifications(
            user_id
        )

        button = discord.ui.Button(
            label=(
                "🔕 Ses Bildirimlerini Kapat"
                if enabled
                else
                "🔔 Ses Bildirimlerini Aç"
            ),
            style=(
                discord.ButtonStyle.danger
                if enabled
                else
                discord.ButtonStyle.success
            ),
            custom_id=f"dynex_voice_toggle:{user_id}"
        )

        button.callback = self.toggle

        self.add_item(button)


    async def toggle(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.user_id:

            await interaction.response.send_message(
                "Bu buton size ait değil.",
                ephemeral=True
            )

            return

        current = get_voice_notifications(
            self.user_id
        )

        new_value = not current

        set_voice_notifications(
            self.user_id,
            new_value
        )

        language = get_language(
            interaction.guild.id
        ) if interaction.guild else "tr"

        await interaction.response.send_message(
            t(
                language,
                "voice_enabled"
                if new_value
                else
                "voice_disabled"
            ),
            ephemeral=True
        )


async def send_voice_statistics(
    member,
    before,
    after
):

    if not get_voice_notifications(
        member.id
    ):

        return

    if before.channel is None:
        return

    start = voice_sessions.pop(
        member.id,
        None
    )

    if start is None:
        return

    end = datetime.now(
        timezone.utc
    )

    duration = end - start

    seconds = int(
        duration.total_seconds()
    )

    minutes = seconds // 60
    seconds = seconds % 60

    language = get_language(
        member.guild.id
    )

    embed = discord.Embed(
        title=t(
            language,
            "voice_title"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(
            language,
            "voice_joined"
        ),
        value=before.channel.name,
        inline=False
    )

    embed.add_field(
        name=t(
            language,
            "voice_left"
        ),
        value=(
            after.channel.name
            if after.channel
            else "—"
        ),
        inline=False
    )

    embed.add_field(
        name=t(
            language,
            "voice_duration"
        ),
        value=f"{minutes} dk {seconds} sn",
        inline=False
    )

    if after.channel:

        member_count = len(
            after.channel.members
        )

    else:

        member_count = len(
            before.channel.members
        )

    embed.add_field(
        name=t(
            language,
            "voice_members"
        ),
        value=str(
            member_count
        ),
        inline=False
    )

    try:

        await member.send(
            embed=embed,
            view=VoiceNotificationView(
                member.id
            )
        )

    except Exception:

        pass


@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    if before.channel is None and after.channel is not None:

        voice_sessions[
            member.id
        ] = datetime.now(
            timezone.utc
        )

    elif before.channel is not None and after.channel is None:

        await send_voice_statistics(
            member,
            before,
            after
        )

    elif (
        before.channel is not None
        and after.channel is not None
        and before.channel.id != after.channel.id
    ):

        await send_voice_statistics(
            member,
            before,
            after
        )

        voice_sessions[
            member.id
        ] = datetime.now(
            timezone.utc
        )


# =========================================================
# TICKET MODAL
# =========================================================

class TicketProblemModal(
    discord.ui.Modal,
    title="Ticket"
):

    problem = discord.ui.TextInput(
        label="Sorununuz",
        placeholder="Sorununuzu yazın.",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        language = get_language(
            guild.id
        )

        config = get_config(
            guild.id
        )

        if not config.get(
            "ticket",
            True
        ):

            await interaction.response.send_message(
                t(
                    language,
                    "ticket_disabled"
                ),
                ephemeral=True
            )

            return

        category = None

        category_id = config.get(
            "ticket_category"
        )

        if category_id:

            category = guild.get_channel(
                category_id
            )

        channel_name = (
            f"ticket-{interaction.user.name}"
        ).lower()

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True
                )
        }

        channel = await guild.create_text_channel(
            channel_name,
            overwrites=overwrites,
            category=category
        )

        embed = discord.Embed(
            title=t(
                language,
                "ticket_name"
            ),
            description=(
                f"**{t(language, 'problem')}:**\n"
                f"{self.problem.value}"
            ),
            color=discord.Color.blurple()
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"{t(language, 'ticket_created')} {channel.mention}",
            ephemeral=True
        )


# =========================================================
# ÜYE EKLEME MODAL
# =========================================================

class AddMemberModal(
    discord.ui.Modal,
    title="Üye Ekle"
):

    member_id = discord.ui.TextInput(
        label="Üye ID",
        placeholder="Eklenecek üyenin Discord ID'si",
        required=True
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:

            member_id = int(
                self.member_id.value
            )

        except ValueError:

            await interaction.response.send_message(
                "Geçerli bir ID girin.",
                ephemeral=True
            )

            return

        member = interaction.guild.get_member(
            member_id
        )

        if member is None:

            try:

                member = await interaction.guild.fetch_member(
                    member_id
                )

            except Exception:

                member = None

        if member is None:

            await interaction.response.send_message(
                "Geçerli bir üye bulunamadı.",
                ephemeral=True
            )

            return

        await interaction.channel.set_permissions(
            member,
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )

        await interaction.response.send_message(
            f"{member.mention} ticket'a eklendi."
        )


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )


    @discord.ui.button(
        label="🎫 Ticket Aç",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_ticket_open"
    )
    async def open_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        language = get_language(
            interaction.guild.id
        )

        await interaction.response.send_modal(
            TicketProblemModal()
        )


# =========================================================
# TICKET KAPATMA
# =========================================================

class TicketCloseView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )


    @discord.ui.button(
        label="🔒 Ticket Kapat",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_ticket_close"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        language = get_language(
            interaction.guild.id
        )

        await interaction.response.send_message(
            t(
                language,
                "ticket_closed"
            )
        )

        await interaction.channel.delete()


    @discord.ui.button(
        label="👤 Üye Ekle",
        style=discord.ButtonStyle.secondary,
        custom_id="dynex_ticket_add_member"
    )
    async def add_member(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            AddMemberModal()
        )


# =========================================================
# AYARLAR EMBED
# =========================================================

def settings_embed(
    guild_id
):

    language = get_language(
        guild_id
    )

    config = get_config(
        guild_id
    )

    embed = discord.Embed(
        title=t(
            language,
            "settings_title"
        ),
        description=t(
            language,
            "settings_description"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(
            language,
            "ticket"
        ),
        value=(
            t(language, "enabled")
            if config.get("ticket")
            else
            t(language, "disabled")
        ),
        inline=True
    )

    embed.add_field(
        name=t(
            language,
            "logs"
        ),
        value=(
            t(language, "enabled")
            if config.get("logs")
            else
            t(language, "disabled")
        ),
        inline=True
    )

    embed.add_field(
        name=t(
            language,
            "welcome"
        ),
        value=(
            t(language, "enabled")
            if config.get("welcome")
            else
            t(language, "disabled")
        ),
        inline=True
    )

    embed.add_field(
        name=t(
            language,
            "autorole"
        ),
        value=(
            t(language, "enabled")
            if config.get("autorole")
            else
            t(language, "disabled")
        ),
        inline=True
    )

    embed.add_field(
        name=t(
            language,
            "moderation"
        ),
        value=(
            t(language, "enabled")
            if config.get("moderation")
            else
            t(language, "disabled")
        ),
        inline=True
    )

    return embed


# =========================================================
# AYARLAR VIEW
# =========================================================

class SettingsView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )


    @discord.ui.button(
        label="🎫 Ticket",
        style=discord.ButtonStyle.primary
    )
    async def ticket_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["ticket"] = not config["ticket"]

        save_data()

        language = get_language(
            interaction.guild.id
        )

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


    @discord.ui.button(
        label="📜 Loglar",
        style=discord.ButtonStyle.secondary
    )
    async def logs_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["logs"] = not config["logs"]

        save_data()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


    @discord.ui.button(
        label="👋 Welcome",
        style=discord.ButtonStyle.secondary
    )
    async def welcome_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["welcome"] = not config["welcome"]

        save_data()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


    @discord.ui.button(
        label="👤 Autorole",
        style=discord.ButtonStyle.secondary
    )
    async def autorole_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["autorole"] = not config["autorole"]

        save_data()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


    @discord.ui.button(
        label="🛡️ Moderasyon",
        style=discord.ButtonStyle.secondary
    )
    async def moderation_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        config = get_config(
            interaction.guild.id
        )

        config["moderation"] = not config["moderation"]

        save_data()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


    @discord.ui.button(
        label="🔄 Yenile",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def refresh_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


    @discord.ui.button(
        label="♻️ Sıfırla",
        style=discord.ButtonStyle.danger,
        row=2
    )
    async def reset_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild_id = str(
            interaction.guild.id
        )

        configs[guild_id] = (
            DEFAULT_CONFIG.copy()
        )

        save_data()

        await interaction.response.edit_message(
            embed=settings_embed(
                interaction.guild.id
            ),
            view=self
        )


# =========================================================
# /AYARLAR
# =========================================================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönet."
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def ayarlar(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        embed=settings_embed(
            interaction.guild.id
        ),
        view=SettingsView(),
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

        await interaction.response.send_message(
            "Bu komutu kullanmak için yönetici olmalısınız.",
            ephemeral=True
        )


# =========================================================
# ÜYE GİRİŞİ
# =========================================================

@bot.event
async def on_member_join(
    member
):

    config = get_config(
        member.guild.id
    )

    if config.get(
        "autorole"
    ):

        role_id = config.get(
            "autorole_role"
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


    if config.get(
        "welcome"
    ):

        channel_id = config.get(
            "welcome_channel"
        )

        if channel_id:

            channel = member.guild.get_channel(
                channel_id
            )

            if channel:

                message = config.get(
                    "welcome_message",
                    "Hoş geldin {member}!"
                )

                message = message.replace(
                    "{member}",
                    member.mention
                )

                try:

                    await channel.send(
                        message
                    )

                except Exception:
                    pass


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(
        f"Dynex aktif: {bot.user}"
    )

    try:

        bot.add_view(
            TicketPanelView()
        )

        bot.add_view(
            TicketCloseView()
        )

    except Exception:

        pass


# =========================================================
# BAŞLAT
# =========================================================

load_data()


if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )


bot.run(TOKEN)
