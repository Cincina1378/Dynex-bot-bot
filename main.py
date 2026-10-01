import discord
from discord.ext import commands
from discord import app_commands
import os
import json

# =========================
# BOT
# =========================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "ticket_enabled": False,
    "ticket_category": None,
    "ticket_channel": None,
    "ticket_title": "Destek Talebi",
    "ticket_description": "Destek almak için aşağıdaki butona tıklayın.",
    "log_enabled": False,
    "log_channel": None,
    "welcome_enabled": False,
    "welcome_channel": None,
    "welcome_message": "Hoş geldin {user}!",
    "autorole_enabled": False,
    "autorole": None,
    "moderation_enabled": True
}


# =========================
# CONFIG
# =========================

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


configs = load_config()


def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4, ensure_ascii=False)


def get_config(guild_id):
    guild_id = str(guild_id)

    if guild_id not in configs:
        configs[guild_id] = DEFAULT_CONFIG.copy()
        save_config()

    for key, value in DEFAULT_CONFIG.items():
        if key not in configs[guild_id]:
            configs[guild_id][key] = value

    return configs[guild_id]


# =========================
# AYARLAR EMBED
# =========================

def settings_embed(guild):
    config = get_config(guild.id)

    embed = discord.Embed(
        title="<:Ayarlar:1555263064721334282> Dynex Ayarları",
        description=(
            "Aşağıdaki butonları kullanarak sunucunun "
            "Dynex sistemlerini yönetebilirsin."
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎫 Ticket",
        value=(
            f"Durum: **{'Açık' if config['ticket_enabled'] else 'Kapalı'}**\n"
            f"Kategori: "
            f"{f'<#{config['ticket_category']}>' if config['ticket_category'] else 'Ayarlanmadı'}"
        ),
        inline=True
    )

    embed.add_field(
        name="📋 Log",
        value=(
            f"Durum: **{'Açık' if config['log_enabled'] else 'Kapalı'}**\n"
            f"Kanal: "
            f"{f'<#{config['log_channel']}>' if config['log_channel'] else 'Ayarlanmadı'}"
        ),
        inline=True
    )

    embed.add_field(
        name="👋 Hoş Geldin",
        value=(
            f"Durum: **{'Açık' if config['welcome_enabled'] else 'Kapalı'}**\n"
            f"Kanal: "
            f"{f'<#{config['welcome_channel']}>' if config['welcome_channel'] else 'Ayarlanmadı'}"
        ),
        inline=True
    )

    embed.add_field(
        name="🎭 Otorol",
        value=(
            f"Durum: **{'Açık' if config['autorole_enabled'] else 'Kapalı'}**\n"
            f"Rol: "
            f"{f'<@&{config['autorole']}>' if config['autorole'] else 'Ayarlanmadı'}"
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

    embed.add_field(
        name="⚙️ Yönetim",
        value="Butonlardan istediğin sistemi doğrudan ayarlayabilirsin.",
        inline=True
    )

    return embed


# =========================
# TICKET MODAL
# =========================

class TicketModal(discord.ui.Modal, title="Ticket Paneli Oluştur"):

    panel_title = discord.ui.TextInput(
        label="Panel başlığı",
        placeholder="Destek Talebi",
        default="Destek Talebi",
        max_length=100
    )

    panel_description = discord.ui.TextInput(
        label="Panel açıklaması",
        placeholder="Destek almak için aşağıdaki butona tıklayın.",
        default="Destek almak için aşağıdaki butona tıklayın.",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    category_id = discord.ui.TextInput(
        label="Ticket kategori ID",
        placeholder="Kategori ID'sini gir",
        required=True,
        max_length=30
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            category_id = int(self.category_id.value)
        except:
            await interaction.response.send_message(
                "Geçerli bir kategori ID'si gir.",
                ephemeral=True
            )
            return

        category = interaction.guild.get_channel(category_id)

        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "Bu ID bir kategoriye ait değil.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        config["ticket_enabled"] = True
        config["ticket_category"] = category_id
        config["ticket_title"] = self.panel_title.value
        config["ticket_description"] = self.panel_description.value

        save_config()

        embed = discord.Embed(
            title=self.panel_title.value,
            description=self.panel_description.value,
            color=discord.Color.blue()
        )

        view = TicketPanelView()

        await interaction.channel.send(
            embed=embed,
            view=view
        )

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> Ticket paneli oluşturuldu.",
            ephemeral=True
        )


# =========================
# LOG MODAL
# =========================

class LogModal(discord.ui.Modal, title="Log Ayarları"):

    channel_id = discord.ui.TextInput(
        label="Log kanal ID",
        placeholder="Kanal ID'sini gir",
        required=True,
        max_length=30
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            channel_id = int(self.channel_id.value)
        except:
            await interaction.response.send_message(
                "Geçerli bir kanal ID'si gir.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(channel_id)

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "Bu ID bir yazı kanalına ait değil.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        config["log_enabled"] = True
        config["log_channel"] = channel_id

        save_config()

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> Log sistemi açıldı.",
            ephemeral=True
        )


# =========================
# WELCOME MODAL
# =========================

class WelcomeModal(discord.ui.Modal, title="Hoş Geldin Ayarları"):

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

    async def on_submit(self, interaction: discord.Interaction):

        try:
            channel_id = int(self.channel_id.value)
        except:
            await interaction.response.send_message(
                "Geçerli bir kanal ID'si gir.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(channel_id)

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
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
            "<:Dynexevet:1555263066235605023> Hoş geldin sistemi ayarlandı.",
            ephemeral=True
        )


# =========================
# OTOROL MODAL
# =========================

class AutoroleModal(discord.ui.Modal, title="Otorol Ayarları"):

    role_id = discord.ui.TextInput(
        label="Otorol rol ID",
        placeholder="Rol ID'sini gir",
        required=True,
        max_length=30
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            role_id = int(self.role_id.value)
        except:
            await interaction.response.send_message(
                "Geçerli bir rol ID'si gir.",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message(
                "Bu ID'ye ait rol bulunamadı.",
                ephemeral=True
            )
            return

        config = get_config(interaction.guild.id)

        config["autorole_enabled"] = True
        config["autorole"] = role_id

        save_config()

        await interaction.response.send_message(
            "<:Dynexevet:1555263066235605023> Otorol ayarlandı.",
            ephemeral=True
        )


# =========================
# TICKET PANELİ
# =========================

class TicketPanelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Destek Talebi Oluştur",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="dynex_ticket_create"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        config = get_config(interaction.guild.id)

        category_id = config.get("ticket_category")

        if not category_id:
            await interaction.response.send_message(
                "Ticket kategorisi ayarlanmamış.",
                ephemeral=True
            )
            return

        category = interaction.guild.get_channel(category_id)

        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "Ticket kategorisi bulunamadı.",
                ephemeral=True
            )
            return

        channel_name = f"ticket-{interaction.user.name}".lower()
        channel_name = channel_name.replace(" ", "-")

        existing = discord.utils.get(
            category.channels,
            name=channel_name
        )

        if existing:
            await interaction.response.send_message(
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
                    read_message_history=True
                ),
            interaction.guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True
                )
        }

        channel = await interaction.guild.create_text_channel(
            channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket",
            description=(
                f"{interaction.user.mention}, destek talebin oluşturuldu.\n\n"
                "Yetkililer kısa süre içinde ilgilenecektir."
            ),
            color=discord.Color.blue()
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"<:Dynexevet:1555263066235605023> Ticket oluşturuldu: {channel.mention}",
            ephemeral=True
        )


# =========================
# TICKET KAPAT
# =========================

class TicketCloseView(discord.ui.View):

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
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Ticket 5 saniye içinde kapatılıyor.",
            ephemeral=True
        )

        await discord.utils.sleep_until(
            discord.utils.utcnow()
        )

        await interaction.channel.delete(
            reason=f"Ticket kapatıldı: {interaction.user}"
        )


# =========================
# AYARLAR PANELİ
# =========================

class SettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary
    )
    async def ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            TicketModal()
        )


    @discord.ui.button(
        label="Log",
        emoji="📋",
        style=discord.ButtonStyle.secondary
    )
    async def log(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            LogModal()
        )


    @discord.ui.button(
        label="Hoş Geldin",
        emoji="👋",
        style=discord.ButtonStyle.secondary
    )
    async def welcome(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            WelcomeModal()
        )


    @discord.ui.button(
        label="Otorol",
        emoji="🎭",
        style=discord.ButtonStyle.secondary
    )
    async def autorole(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            AutoroleModal()
        )


    @discord.ui.button(
        label="Moderasyon",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary
    )
    async def moderation(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        config = get_config(interaction.guild.id)

        config["moderation_enabled"] = not config["moderation_enabled"]

        save_config()

        durum = (
            "açıldı"
            if config["moderation_enabled"]
            else "kapatıldı"
        )

        await interaction.response.edit_message(
            embed=settings_embed(interaction.guild),
            view=self
        )

        await interaction.followup.send(
            f"<:Dynexevet:1555263066235605023> Moderasyon sistemi {durum}.",
            ephemeral=True
        )


    @discord.ui.button(
        label="Ayarları Yenile",
        emoji="🔄",
        style=discord.ButtonStyle.success
    )
    async def refresh(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            embed=settings_embed(interaction.guild),
            view=self
        )


    @discord.ui.button(
        label="Sıfırla",
        emoji="🗑️",
        style=discord.ButtonStyle.danger
    )
    async def reset(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        configs[str(interaction.guild.id)] = DEFAULT_CONFIG.copy()
        save_config()

        await interaction.response.edit_message(
            embed=settings_embed(interaction.guild),
            view=self
        )

        await interaction.followup.send(
            "<:Dynexevet:1555263066235605023> Tüm ayarlar sıfırlandı.",
            ephemeral=True
        )


# =========================
# /AYARLAR
# =========================

@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını yönet."
)
@app_commands.checks.has_permissions(administrator=True)
async def ayarlar(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        embed=settings_embed(interaction.guild),
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

        embed = discord.Embed(
            title="<:Dynexhayir:1555265003727102134> Yetkin Yok",
            description=(
                "Bu paneli kullanmak için **Yönetici** "
                "yetkisine sahip olmalısın."
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


# =========================
# /PING
# =========================

@bot.tree.command(
    name="ping",
    description="Dynex gecikmesini gösterir."
)
async def ping(
    interaction: discord.Interaction
):

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
# ÜYE GİRİŞİ
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
        bot.add_view(TicketPanelView())
        bot.add_view(TicketCloseView())

        synced = await bot.tree.sync()

        print(f"Dynex aktif: {bot.user}")
        print(f"{len(synced)} slash komutu senkronize edildi.")

    except Exception as e:
        print("READY HATASI:", repr(e))


# =========================
# TOKEN
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
