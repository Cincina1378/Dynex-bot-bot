import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "ticket_enabled": False,
    "ticket_category": None,
    "ticket_role": None,
    "ticket_title": "Destek Talebi",
    "ticket_description": "Destek almak için aşağıdaki butona tıklayın.",
    "ticket_message": "Ticketiniz başarıyla oluşturuldu.",
    "log_enabled": False,
    "log_channel": None,
    "welcome_enabled": False,
    "welcome_channel": None,
    "welcome_message": "Hoş geldin {user}!",
    "autorole_enabled": False,
    "autorole": None,
    "moderation_enabled": True
}

configs = {}
voice_sessions = {}


def load_config():
    global configs

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            configs = json.load(f)
    except:
        configs = {}


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            configs,
            f,
            indent=4,
            ensure_ascii=False
        )


def get_config(guild_id):
    guild_id = str(guild_id)

    if guild_id not in configs:
        configs[guild_id] = DEFAULT_CONFIG.copy()
        save_config()

    for key, value in DEFAULT_CONFIG.items():
        if key not in configs[guild_id]:
            configs[guild_id][key] = value

    return configs[guild_id]


load_config()


# =========================================================
# AYARLAR EMBED
# =========================================================

def settings_embed(guild):
    config = get_config(guild.id)

    ticket_category = (
        f"<#{config['ticket_category']}>"
        if config["ticket_category"]
        else "Ayarlanmadı"
    )

    ticket_role = (
        f"<@&{config['ticket_role']}>"
        if config["ticket_role"]
        else "Ayarlanmadı"
    )

    log_channel = (
        f"<#{config['log_channel']}>"
        if config["log_channel"]
        else "Ayarlanmadı"
    )

    welcome_channel = (
        f"<#{config['welcome_channel']}>"
        if config["welcome_channel"]
        else "Ayarlanmadı"
    )

    autorole = (
        f"<@&{config['autorole']}>"
        if config["autorole"]
        else "Ayarlanmadı"
    )

    embed = discord.Embed(
        title="<:Ayarlar:1555263064721334282> Dynex Ayarları",
        description=(
            "Aşağıdaki butonlardan sunucunun sistemlerini "
            "yönetebilirsin."
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎫 Ticket",
        value=(
            f"Durum: **{'Açık' if config['ticket_enabled'] else 'Kapalı'}**\n"
            f"Kategori: {ticket_category}\n"
            f"Yetkili: {ticket_role}"
        ),
        inline=False
    )

    embed.add_field(
        name="📋 Log",
        value=(
            f"Durum: **{'Açık' if config['log_enabled'] else 'Kapalı'}**\n"
            f"Kanal: {log_channel}"
        ),
        inline=True
    )

    embed.add_field(
        name="👋 Hoş Geldin",
        value=(
            f"Durum: **{'Açık' if config['welcome_enabled'] else 'Kapalı'}**\n"
            f"Kanal: {welcome_channel}"
        ),
        inline=True
    )

    embed.add_field(
        name="🎭 Otorol",
        value=(
            f"Durum: **{'Açık' if config['autorole_enabled'] else 'Kapalı'}\n"
            f"Rol: {autorole}"
        ),
        inline=True
    )

    embed.add_field(
        name="🛡️ Moderasyon",
        value=(
            f"Durum: **"
            f"{'Açık' if config['moderation_enabled'] else 'Kapalı'}**"
        ),
        inline=True
    )

    return embed


# =========================================================
# TICKET AYARLARI
# =========================================================

class TicketSettingsModal(
    discord.ui.Modal,
    title="Ticket Sistemi Ayarları"
):

    title_input = discord.ui.TextInput(
        label="Panel başlığı",
        placeholder="Destek Talebi",
        default="Destek Talebi",
        max_length=100
    )

    description_input = discord.ui.TextInput(
        label="Panel açıklaması",
        placeholder="Destek almak için butona tıklayın.",
        default="Destek almak için aşağıdaki butona tıklayın.",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    category_input = discord.ui.TextInput(
        label="Ticket kategori ID",
        placeholder="Kategori ID'sini gir",
        required=True,
        max_length=30
    )

    role_input = discord.ui.TextInput(
        label="Ticket yetkili rol ID",
        placeholder="Yetkili rolünün ID'sini gir",
        required=True,
        max_length=30
    )

    message_input = discord.ui.TextInput(
        label="Ticket iç mesajı",
        placeholder="Ticketiniz başarıyla oluşturuldu.",
        default="Ticketiniz başarıyla oluşturuldu.",
        style=discord.TextStyle.paragraph,
        max_length=1500
    )

    async def on_submit(self, interaction):

        try:
            category_id = int(self.category_input.value)
            role_id = int(self.role_input.value)
        except:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Kategori ve rol ID'si sayı olmalıdır.",
                ephemeral=True
            )
            return

        category = interaction.guild.get_channel(category_id)
        role = interaction.guild.get_role(role_id)

        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Girilen kategori bulunamadı.",
                ephemeral=True
            )
            return

        if not role:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Girilen yetkili rolü bulunamadı.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        config["ticket_enabled"] = True
        config["ticket_category"] = category_id
        config["ticket_role"] = role_id
        config["ticket_title"] = self.title_input.value
        config["ticket_description"] = self.description_input.value
        config["ticket_message"] = self.message_input.value

        save_config()

        embed = discord.Embed(
            title=self.title_input.value,
            description=self.description_input.value,
            color=discord.Color.blue()
        )

        await interaction.channel.send(
            embed=embed,
            view=TicketPanelView()
        )

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> "
            "Ticket paneli oluşturuldu.",
            ephemeral=True
        )


class TicketProblemModal(
    discord.ui.Modal,
    title="Ticket Oluştur"
):

    problem = discord.ui.TextInput(
        label="Sorun",
        placeholder="Sorununuzu buraya yazın...",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=2,
        max_length=2000
    )

    async def on_submit(self, interaction):

        config = get_config(interaction.guild.id)

        category = interaction.guild.get_channel(
            config.get("ticket_category")
        )

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Ticket kategorisi bulunamadı.",
                ephemeral=True
            )
            return

        if not role:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Ticket yetkili rolü bulunamadı.",
                ephemeral=True
            )
            return

        channel_name = (
            f"ticket-{interaction.user.name}"
            .lower()
            .replace(" ", "-")
        )

        existing = discord.utils.get(
            category.channels,
            name=channel_name
        )

        if existing:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                f"Zaten açık bir ticketın var: {existing.mention}",
                ephemeral=True
            )
            return

        overwrites = {
            interaction.guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                ),

            role:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_messages=True
                ),

            interaction.guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True,
                    manage_messages=True
                )
        }

        channel = await interaction.guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"dynex_ticket_owner:{interaction.user.id}"
        )

        embed = discord.Embed(
            title="🎫 Ticket",
            description=(
                f"{config.get('ticket_message')}\n\n"
                f"**Ticketiniz sorun:**\n"
                f"{self.problem.value}"
            ),
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"Ticket sahibi: {interaction.user}"
        )

        await channel.send(
            content=(
                f"{role.mention} | "
                f"{interaction.user.mention}"
            ),
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> "
            f"Ticket oluşturuldu: {channel.mention}",
            ephemeral=True
        )


# =========================================================
# ÜYE EKLE
# =========================================================

class AddMemberModal(
    discord.ui.Modal,
    title="Ticket'a Üye Ekle"
):

    member_id = discord.ui.TextInput(
        label="Üye ID",
        placeholder="Eklemek istediğin kullanıcının ID'si",
        required=True,
        max_length=30
    )

    async def on_submit(self, interaction):

        config = get_config(interaction.guild.id)

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not interaction.channel.topic:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu kanal bir ticket değil.",
                ephemeral=True
            )
            return

        try:
            owner_id = int(
                interaction.channel.topic.split(":")[1]
            )
        except:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Ticket sahibi bulunamadı.",
                ephemeral=True
            )
            return

        is_owner = interaction.user.id == owner_id
        is_authorized = role and role in interaction.user.roles

        if not is_owner and not is_authorized:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu butonu sadece ticket sahibi veya "
                "ticket yetkilisi kullanabilir.",
                ephemeral=True
            )
            return

        try:
            member_id = int(self.member_id.value)
        except:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Geçerli bir kullanıcı ID'si gir.",
                ephemeral=True
            )
            return

        member = interaction.guild.get_member(member_id)

        if not member:
            try:
                member = await interaction.guild.fetch_member(
                    member_id
                )
            except:
                member = None

        if not member:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu kullanıcı sunucuda bulunamadı.",
                ephemeral=True
            )
            return

        try:
            await interaction.channel.set_permissions(
                member,
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )
        except:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Kullanıcı ticket'a eklenemedi.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> "
            f"{member.mention} ticket'a eklendi."
        )


# =========================================================
# TICKET PANEL
# =========================================================

class TicketPanelView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ticket Aç",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_ticket_create"
    )
    async def create_ticket(
        self,
        interaction,
        button
    ):
        await interaction.response.send_modal(
            TicketProblemModal()
        )


class TicketCloseView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ticket Kapat",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="dynex_ticket_close"
    )
    async def close_ticket(
        self,
        interaction,
        button
    ):

        config = get_config(interaction.guild.id)

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not interaction.channel.topic:
            await interaction.response.send_message(
                "Bu kanal bir ticket değil.",
                ephemeral=True
            )
            return

        try:
            owner_id = int(
                interaction.channel.topic.split(":")[1]
            )
        except:
            await interaction.response.send_message(
                "Ticket sahibi bulunamadı.",
                ephemeral=True
            )
            return

        is_owner = interaction.user.id == owner_id
        is_authorized = role and role in interaction.user.roles

        if not is_owner and not is_authorized:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu ticketı sadece ticket sahibi veya "
                "ticket yetkilisi kapatabilir.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔒 Ticket 5 saniye içinde kapatılıyor."
        )

        await asyncio.sleep(5)

        try:
            await interaction.channel.delete(
                reason=f"Ticket kapatıldı: {interaction.user}"
            )
        except:
            pass

    @discord.ui.button(
        label="Üye Ekle",
        emoji="👤",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_ticket_add_member"
    )
    async def add_member(
        self,
        interaction,
        button
    ):

        config = get_config(interaction.guild.id)

        role = interaction.guild.get_role(
            config.get("ticket_role")
        )

        if not interaction.channel.topic:
            await interaction.response.send_message(
                "Bu kanal bir ticket değil.",
                ephemeral=True
            )
            return

        try:
            owner_id = int(
                interaction.channel.topic.split(":")[1]
            )
        except:
            await interaction.response.send_message(
                "Ticket sahibi bulunamadı.",
                ephemeral=True
            )
            return

        is_owner = interaction.user.id == owner_id
        is_authorized = role and role in interaction.user.roles

        if not is_owner and not is_authorized:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu butonu sadece ticket sahibi veya "
                "ticket yetkilisi kullanabilir.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            AddMemberModal()
        )


# =========================================================
# LOG
# =========================================================

class LogModal(
    discord.ui.Modal,
    title="Log Ayarları"
):

    channel_id = discord.ui.TextInput(
        label="Log kanal ID",
        placeholder="Kanal ID'sini gir",
        required=True,
        max_length=30
    )

    async def on_submit(self, interaction):

        try:
            channel_id = int(self.channel_id.value)
        except:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Geçerli bir kanal ID'si gir.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(channel_id)

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu ID bir yazı kanalına ait değil.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        config["log_enabled"] = True
        config["log_channel"] = channel_id

        save_config()

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> "
            "Log sistemi ayarlandı.",
            ephemeral=True
        )


# =========================================================
# HOŞ GELDİN
# =========================================================

class WelcomeModal(
    discord.ui.Modal,
    title="Hoş Geldin Ayarları"
):

    channel_id = discord.ui.TextInput(
        label="Hoş geldin kanal ID",
        placeholder="Kanal ID'sini gir",
        required=True,
        max_length=30
    )

    message = discord.ui.TextInput(
        label="Hoş geldin mesajı",
        placeholder="Hoş geldin {user}!",
        default="Hoş geldin {user}!",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    async def on_submit(self, interaction):

        try:
            channel_id = int(self.channel_id.value)
        except:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Geçerli bir kanal ID'si gir.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(channel_id)

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu ID bir yazı kanalına ait değil.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        config["welcome_enabled"] = True
        config["welcome_channel"] = channel_id
        config["welcome_message"] = self.message.value

        save_config()

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> "
            "Hoş geldin sistemi ayarlandı.",
            ephemeral=True
        )


# =========================================================
# OTOROL
# =========================================================

class AutoroleModal(
    discord.ui.Modal,
    title="Otorol Ayarları"
):

    role_id = discord.ui.TextInput(
        label="Otorol rol ID",
        placeholder="Rol ID'sini gir",
        required=True,
        max_length=30
    )

    async def on_submit(self, interaction):

        try:
            role_id = int(self.role_id.value)
        except:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Geçerli bir rol ID'si gir.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message(
                "<:Dynexhayir:1555265003727102134> "
                "Bu ID'ye ait rol bulunamadı.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        config["autorole_enabled"] = True
        config["autorole"] = role_id

        save_config()

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> "
            "Otorol ayarlandı.",
            ephemeral=True
        )


# =========================================================
# AYARLAR
# =========================================================

class SettingsView(
    discord.ui.View
):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary
    )
    async def ticket(self, interaction, button):
        await interaction.response.send_modal(
            TicketSettingsModal()
        )

    @discord.ui.button(
        label="Log",
        emoji="📋",
        style=discord.ButtonStyle.secondary
    )
    async def log(self, interaction, button):
        await interaction.response.send_modal(
            LogModal()
        )

    @discord.ui.button(
        label="Hoş Geldin",
        emoji="👋",
        style=discord.ButtonStyle.secondary
    )
    async def welcome(self, interaction, button):
        await interaction.response.send_modal(
            WelcomeModal()
        )

    @discord.ui.button(
        label="Otorol",
        emoji="🎭",
        style=discord.ButtonStyle.secondary
    )
    async def autorole(self, interaction, button):
        await interaction.response.send_modal(
            AutoroleModal()
        )

    @discord.ui.button(
        label="Moderasyon",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary
    )
    async def moderation(self, interaction, button):

        config = get_config(interaction.guild.id)

        config["moderation_enabled"] = not config[
            "moderation_enabled"
        ]

        save_config()

        await interaction.response.edit_message(
            embed=settings_embed(interaction.guild),
            view=self
        )

    @discord.ui.button(
        label="Yenile",
        emoji="🔄",
        style=discord.ButtonStyle.success
    )
    async def refresh(self, interaction, button):

        await interaction.response.edit_message(
            embed=settings_embed(interaction.guild),
            view=self
        )

    @discord.ui.button(
        label="Sıfırla",
        emoji="🗑️",
        style=discord.ButtonStyle.danger
    )
    async def reset(self, interaction, button):

        configs[str(interaction.guild.id)] = (
            DEFAULT_CONFIG.copy()
        )

        save_config()

        await interaction.response.edit_message(
            embed=settings_embed(interaction.guild),
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
async def ayarlar(interaction):

    await interaction.response.send_message(
        embed=settings_embed(interaction.guild),
        view=SettingsView(),
        ephemeral=True
    )


@ayarlar.error
async def ayarlar_error(interaction, error):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        embed = discord.Embed(
            title="<:Dynexhayir:1555265003727102134> Yetkin Yok",
            description=(
                "Bu paneli kullanmak için "
                "**Yönetici** yetkisine sahip olmalısın."
            ),
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


# =========================================================
# /PING
# =========================================================

@bot.tree.command(
    name="ping",
    description="Dynex gecikmesini gösterir."
)
async def ping(interaction):

    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="<:Discord:1555263704646557816> Dynex Ping",
        description=f"**{latency}ms**",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# SES İSTATİSTİKLERİ
# =========================================================

@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    # Kullanıcı bir ses kanalına yeni girdiyse
    if before.channel is None and after.channel is not None:

        voice_sessions[
            (member.guild.id, member.id)
        ] = {
            "channel_id": after.channel.id,
            "started_at": datetime.now(timezone.utc)
        }

        return

    # Kullanıcı başka bir ses kanalına geçtiyse
    if (
        before.channel is not None
        and after.channel is not None
        and before.channel.id != after.channel.id
    ):

        key = (member.guild.id, member.id)

        voice_sessions[key] = {
            "channel_id": after.channel.id,
            "started_at": datetime.now(timezone.utc)
        }

        return

    # Kullanıcı sesten tamamen çıktıysa
    if before.channel is not None and after.channel is None:

        key = (member.guild.id, member.id)

        session = voice_sessions.pop(key, None)

        if not session:
            return

        started_at = session["started_at"]
        ended_at = datetime.now(timezone.utc)

        duration_seconds = int(
            (ended_at - started_at).total_seconds()
        )

        if duration_seconds < 0:
            duration_seconds = 0

        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60

        if hours > 0:
            duration_text = (
                f"{hours} saat "
                f"{minutes} dakika "
                f"{seconds} saniye"
            )
        elif minutes > 0:
            duration_text = (
                f"{minutes} dakika "
                f"{seconds} saniye"
            )
        else:
            duration_text = (
                f"{seconds} saniye"
            )

        # Kullanıcı çıktıktan SONRA kanalda kalan kişi sayısı
        remaining_members = len(
            [
                m for m in before.channel.members
                if not m.bot
            ]
        )

        guild_name = member.guild.name

        message = (
            f"🔊 **{guild_name} adlı sunucunun ses istatikleri**\n\n"
            f"**Bugün {guild_name} adlı sunucuda sesli sohbete "
            f"katıldın. İşte istatiklerin:**\n\n"
            f"Sunucu adı: **{guild_name}**\n"
            f"Kaldığın süre: **{duration_text}**\n"
            f"Sen çıkınca sesli sohbete kalan üye sayısı: "
            f"**{remaining_members}**\n\n"
            f"**Dynex sizin sunucu dostunuz…**"
        )

        try:
            await member.send(message)
        except discord.Forbidden:
            print(
                f"{member} DM'lerini kapattığı için "
                f"ses istatistiği gönderilemedi."
            )
        except Exception as e:
            print(
                "SES İSTATİSTİĞİ DM HATASI:",
                repr(e)
            )


# =========================================================
# ÜYE GİRİŞ
# =========================================================

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

            channel = member.guild.get_channel(
                channel_id
            )

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


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    try:
        bot.add_view(TicketPanelView())
        bot.add_view(TicketCloseView())

        synced = await bot.tree.sync()

        print(f"Dynex aktif: {bot.user}")
        print(
            f"{len(synced)} slash komutu senkronize edildi."
        )

    except Exception as e:
        print(
            "READY HATASI:",
            repr(e)
        )


# =========================================================
# TOKEN
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
