import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from datetime import datetime, timezone


TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = "config.json"

INTENTS = discord.Intents.default()
INTENTS.guilds = True
INTENTS.members = True
INTENTS.voice_states = True


DEFAULT_CONFIG = {
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


LANGUAGES = {
    "tr": "🇹🇷 Türkçe",
    "en": "🇬🇧 English",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "it": "🇮🇹 Italiano",
    "pt": "🇵🇹 Português",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "ko": "🇰🇷 한국어",
    "nl": "🇳🇱 Nederlands",
    "pl": "🇵🇱 Polski",
    "uk": "🇺🇦 Українська",
    "az": "🇦🇿 Azərbaycan"
}


TEXTS = {
    "tr": {
        "language_name": "Türkçe",
        "language_changed": "Diliniz Türkçe olarak ayarlandı.",
        "already_language": "Zaten Türkçe kullanıyorsunuz.",
        "language_title": "Dynex Dil Seçimi",
        "language_description": "Dynex'in kullanacağı dili seçin.",
        "settings_title": "Dynex Ayarları",
        "ticket": "🎫 Ticket",
        "logs": "📜 Loglar",
        "welcome": "👋 Hoş Geldin",
        "autorole": "👤 Otorol",
        "moderation": "🛡️ Moderasyon",
        "refresh": "🔄 Yenile",
        "reset": "♻️ Sıfırla",
        "enabled": "Açık",
        "disabled": "Kapalı",
        "ticket_open": "Ticket Aç",
        "ticket_close": "Ticket Kapat",
        "add_member": "Üye Ekle",
        "ticket_created": "Ticket oluşturuldu.",
        "ticket_closed": "Ticket kapatılıyor.",
        "ticket_disabled": "Ticket sistemi şu anda kapalı.",
        "ticket_name": "Ticket",
        "problem": "Sorun",
        "problem_placeholder": "Sorununuzu yazın",
        "member_id": "Üye ID",
        "member_id_placeholder": "Eklenecek üyenin Discord ID'si",
        "member_added": "Üye ticket'a eklendi.",
        "invalid_member": "Geçerli bir üye bulunamadı.",
        "permission": "Bu işlem için yeterli yetkiniz yok.",
        "saved": "Ayar kaydedildi.",
        "reset_done": "Sunucu ayarları sıfırlandı.",
        "ping_title": "Dynex Ping durumu",
        "ping_description": "**Dynex**'in ping durumu",
        "voice_title": "Ses Kanalı İstatistikleri",
        "voice_joined": "Katıldığı kanal",
        "voice_left": "Ayrıldığı kanal",
        "voice_duration": "Ses kanalında kalma süresi",
        "voice_members": "Çıkış anındaki üye sayısı",
        "voice_disable": "🔕 Ses Bildirimlerini Kapat",
        "voice_enable": "🔔 Ses Bildirimlerini Aç",
        "voice_disabled": "Ses bildirimleri kapatıldı.",
        "voice_enabled": "Ses bildirimleri açıldı.",
        "welcome_default": "Hoş geldin {member}!",
        "yes": "Evet",
        "no": "Hayır"
    },

    "en": {
        "language_name": "English",
        "language_changed": "Your language has been set to English.",
        "already_language": "You are already using English.",
        "language_title": "Dynex Language Selection",
        "language_description": "Select the language Dynex should use.",
        "settings_title": "Dynex Settings",
        "ticket": "🎫 Ticket",
        "logs": "📜 Logs",
        "welcome": "👋 Welcome",
        "autorole": "👤 Autorole",
        "moderation": "🛡️ Moderation",
        "refresh": "🔄 Refresh",
        "reset": "♻️ Reset",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "ticket_open": "Open Ticket",
        "ticket_close": "Close Ticket",
        "add_member": "Add Member",
        "ticket_created": "Ticket created.",
        "ticket_closed": "The ticket is being closed.",
        "ticket_disabled": "The ticket system is currently disabled.",
        "ticket_name": "Ticket",
        "problem": "Problem",
        "problem_placeholder": "Describe your problem",
        "member_id": "Member ID",
        "member_id_placeholder": "Discord ID of the member to add",
        "member_added": "The member was added to the ticket.",
        "invalid_member": "No valid member was found.",
        "permission": "You do not have permission to do this.",
        "saved": "Setting saved.",
        "reset_done": "Server settings have been reset.",
        "ping_title": "Dynex Ping Status",
        "ping_description": "**Dynex**'s ping status",
        "voice_title": "Voice Channel Statistics",
        "voice_joined": "Joined channel",
        "voice_left": "Left channel",
        "voice_duration": "Time spent in voice",
        "voice_members": "Members when leaving",
        "voice_disable": "🔕 Disable Voice Notifications",
        "voice_enable": "🔔 Enable Voice Notifications",
        "voice_disabled": "Voice notifications have been disabled.",
        "voice_enabled": "Voice notifications have been enabled.",
        "welcome_default": "Welcome {member}!",
        "yes": "Yes",
        "no": "No"
    },

    "de": {
        "language_name": "Deutsch",
        "language_changed": "Deine Sprache wurde auf Deutsch eingestellt.",
        "already_language": "Du verwendest bereits Deutsch.",
        "language_title": "Dynex Sprachauswahl",
        "language_description": "Wähle die Sprache für Dynex.",
        "settings_title": "Dynex Einstellungen",
        "ticket": "🎫 Ticket",
        "logs": "📜 Logs",
        "welcome": "👋 Willkommen",
        "autorole": "👤 Autorolle",
        "moderation": "🛡️ Moderation",
        "refresh": "🔄 Aktualisieren",
        "reset": "♻️ Zurücksetzen",
        "enabled": "Aktiv",
        "disabled": "Deaktiviert",
        "ticket_open": "Ticket öffnen",
        "ticket_close": "Ticket schließen",
        "add_member": "Mitglied hinzufügen",
        "ticket_created": "Ticket erstellt.",
        "ticket_closed": "Das Ticket wird geschlossen.",
        "ticket_disabled": "Das Ticketsystem ist derzeit deaktiviert.",
        "ticket_name": "Ticket",
        "problem": "Problem",
        "problem_placeholder": "Beschreibe dein Problem",
        "member_id": "Mitglieds-ID",
        "member_id_placeholder": "Discord-ID des Mitglieds",
        "member_added": "Mitglied wurde hinzugefügt.",
        "invalid_member": "Kein gültiges Mitglied gefunden.",
        "permission": "Du hast keine Berechtigung.",
        "saved": "Einstellung gespeichert.",
        "reset_done": "Servereinstellungen wurden zurückgesetzt.",
        "ping_title": "Dynex Ping-Status",
        "ping_description": "Der Ping-Status von **Dynex**",
        "voice_title": "Sprachkanal-Statistiken",
        "voice_joined": "Beigetretener Kanal",
        "voice_left": "Verlassener Kanal",
        "voice_duration": "Zeit im Sprachkanal",
        "voice_members": "Mitglieder beim Verlassen",
        "voice_disable": "🔕 Sprachbenachrichtigungen deaktivieren",
        "voice_enable": "🔔 Sprachbenachrichtigungen aktivieren",
        "voice_disabled": "Sprachbenachrichtigungen wurden deaktiviert.",
        "voice_enabled": "Sprachbenachrichtigungen wurden aktiviert.",
        "welcome_default": "Willkommen {member}!",
        "yes": "Ja",
        "no": "Nein"
    },

    "fr": {
        "language_name": "Français",
        "language_changed": "Votre langue est maintenant le français.",
        "already_language": "Vous utilisez déjà le français.",
        "language_title": "Choix de la langue Dynex",
        "language_description": "Choisissez la langue de Dynex.",
        "settings_title": "Paramètres Dynex",
        "ticket": "🎫 Ticket",
        "logs": "📜 Logs",
        "welcome": "👋 Bienvenue",
        "autorole": "👤 Rôle automatique",
        "moderation": "🛡️ Modération",
        "refresh": "🔄 Actualiser",
        "reset": "♻️ Réinitialiser",
        "enabled": "Activé",
        "disabled": "Désactivé",
        "ticket_open": "Ouvrir un ticket",
        "ticket_close": "Fermer le ticket",
        "add_member": "Ajouter un membre",
        "ticket_created": "Ticket créé.",
        "ticket_closed": "Le ticket va être fermé.",
        "ticket_disabled": "Le système de tickets est actuellement désactivé.",
        "ticket_name": "Ticket",
        "problem": "Problème",
        "problem_placeholder": "Décrivez votre problème",
        "member_id": "ID du membre",
        "member_id_placeholder": "ID Discord du membre",
        "member_added": "Le membre a été ajouté.",
        "invalid_member": "Aucun membre valide trouvé.",
        "permission": "Vous n'avez pas la permission.",
        "saved": "Paramètre enregistré.",
        "reset_done": "Les paramètres du serveur ont été réinitialisés.",
        "ping_title": "État du ping Dynex",
        "ping_description": "État du ping de **Dynex**",
        "voice_title": "Statistiques vocales",
        "voice_joined": "Salon rejoint",
        "voice_left": "Salon quitté",
        "voice_duration": "Temps passé en vocal",
        "voice_members": "Membres au départ",
        "voice_disable": "🔕 Désactiver les notifications vocales",
        "voice_enable": "🔔 Activer les notifications vocales",
        "voice_disabled": "Les notifications vocales sont désactivées.",
        "voice_enabled": "Les notifications vocales sont activées.",
        "welcome_default": "Bienvenue {member}!",
        "yes": "Oui",
        "no": "Non"
    },

    "es": {
        "language_name": "Español",
        "language_changed": "Tu idioma ahora es español.",
        "already_language": "Ya estás usando español.",
        "language_title": "Idioma de Dynex",
        "language_description": "Selecciona el idioma de Dynex.",
        "settings_title": "Configuración de Dynex",
        "ticket": "🎫 Ticket",
        "logs": "📜 Registros",
        "welcome": "👋 Bienvenida",
        "autorole": "👤 Autorol",
        "moderation": "🛡️ Moderación",
        "refresh": "🔄 Actualizar",
        "reset": "♻️ Restablecer",
        "enabled": "Activado",
        "disabled": "Desactivado",
        "ticket_open": "Abrir ticket",
        "ticket_close": "Cerrar ticket",
        "add_member": "Añadir miembro",
        "ticket_created": "Ticket creado.",
        "ticket_closed": "El ticket se está cerrando.",
        "ticket_disabled": "El sistema de tickets está desactivado.",
        "ticket_name": "Ticket",
        "problem": "Problema",
        "problem_placeholder": "Describe tu problema",
        "member_id": "ID del miembro",
        "member_id_placeholder": "ID de Discord del miembro",
        "member_added": "El miembro fue añadido.",
        "invalid_member": "No se encontró un miembro válido.",
        "permission": "No tienes permiso.",
        "saved": "Configuración guardada.",
        "reset_done": "Configuración del servidor restablecida.",
        "ping_title": "Estado del Ping de Dynex",
        "ping_description": "Estado del ping de **Dynex**",
        "voice_title": "Estadísticas de voz",
        "voice_joined": "Canal al que entró",
        "voice_left": "Canal del que salió",
        "voice_duration": "Tiempo en voz",
        "voice_members": "Miembros al salir",
        "voice_disable": "🔕 Desactivar notificaciones de voz",
        "voice_enable": "🔔 Activar notificaciones de voz",
        "voice_disabled": "Notificaciones de voz desactivadas.",
        "voice_enabled": "Notificaciones de voz activadas.",
        "welcome_default": "¡Bienvenido {member}!",
        "yes": "Sí",
        "no": "No"
    },

    "it": {
        "language_name": "Italiano",
        "language_changed": "La tua lingua è stata impostata su Italiano.",
        "already_language": "Stai già usando Italiano.",
        "language_title": "Lingua Dynex",
        "language_description": "Seleziona la lingua di Dynex.",
        "settings_title": "Impostazioni Dynex",
        "ticket": "🎫 Ticket",
        "logs": "📜 Log",
        "welcome": "👋 Benvenuto",
        "autorole": "👤 Autorole",
        "moderation": "🛡️ Moderazione",
        "refresh": "🔄 Aggiorna",
        "reset": "♻️ Ripristina",
        "enabled": "Attivo",
        "disabled": "Disattivato",
        "ticket_open": "Apri ticket",
        "ticket_close": "Chiudi ticket",
        "add_member": "Aggiungi membro",
        "ticket_created": "Ticket creato.",
        "ticket_closed": "Il ticket verrà chiuso.",
        "ticket_disabled": "Il sistema ticket è disattivato.",
        "ticket_name": "Ticket",
        "problem": "Problema",
        "problem_placeholder": "Descrivi il problema",
        "member_id": "ID membro",
        "member_id_placeholder": "ID Discord del membro",
        "member_added": "Membro aggiunto.",
        "invalid_member": "Nessun membro valido trovato.",
        "permission": "Non hai il permesso.",
        "saved": "Impostazione salvata.",
        "reset_done": "Impostazioni del server ripristinate.",
        "ping_title": "Stato Ping Dynex",
        "ping_description": "Stato del ping di **Dynex**",
        "voice_title": "Statistiche canale vocale",
        "voice_joined": "Canale di ingresso",
        "voice_left": "Canale di uscita",
        "voice_duration": "Tempo in vocale",
        "voice_members": "Membri all'uscita",
        "voice_disable": "🔕 Disattiva notifiche vocali",
        "voice_enable": "🔔 Attiva notifiche vocali",
        "voice_disabled": "Notifiche vocali disattivate.",
        "voice_enabled": "Notifiche vocali attivate.",
        "welcome_default": "Benvenuto {member}!",
        "yes": "Sì",
        "no": "No"
    },

    "pt": {
        "language_name": "Português",
        "language_changed": "Seu idioma foi definido como Português.",
        "already_language": "Você já está usando Português.",
        "language_title": "Idioma do Dynex",
        "language_description": "Selecione o idioma do Dynex.",
        "settings_title": "Configurações do Dynex",
        "ticket": "🎫 Ticket",
        "logs": "📜 Logs",
        "welcome": "👋 Boas-vindas",
        "autorole": "👤 Autorole",
        "moderation": "🛡️ Moderação",
        "refresh": "🔄 Atualizar",
        "reset": "♻️ Redefinir",
        "enabled": "Ativado",
        "disabled": "Desativado",
        "ticket_open": "Abrir ticket",
        "ticket_close": "Fechar ticket",
        "add_member": "Adicionar membro",
        "ticket_created": "Ticket criado.",
        "ticket_closed": "O ticket está sendo fechado.",
        "ticket_disabled": "O sistema de tickets está desativado.",
        "ticket_name": "Ticket",
        "problem": "Problema",
        "problem_placeholder": "Descreva seu problema",
        "member_id": "ID do membro",
        "member_id_placeholder": "ID Discord do membro",
        "member_added": "Membro adicionado.",
        "invalid_member": "Nenhum membro válido encontrado.",
        "permission": "Você não tem permissão.",
        "saved": "Configuração salva.",
        "reset_done": "Configurações do servidor redefinidas.",
        "ping_title": "Status do Ping do Dynex",
        "ping_description": "Status do ping do **Dynex**",
        "voice_title": "Estatísticas de voz",
        "voice_joined": "Canal de entrada",
        "voice_left": "Canal de saída",
        "voice_duration": "Tempo em voz",
        "voice_members": "Membros ao sair",
        "voice_disable": "🔕 Desativar notificações de voz",
        "voice_enable": "🔔 Ativar notificações de voz",
        "voice_disabled": "Notificações de voz desativadas.",
        "voice_enabled": "Notificações de voz ativadas.",
        "welcome_default": "Bem-vindo {member}!",
        "yes": "Sim",
        "no": "Não"
    },

    "ru": {
        "language_name": "Русский",
        "language_changed": "Ваш язык установлен на русский.",
        "already_language": "Вы уже используете русский.",
        "language_title": "Язык Dynex",
        "language_description": "Выберите язык Dynex.",
        "settings_title": "Настройки Dynex",
        "ticket": "🎫 Тикет",
        "logs": "📜 Логи",
        "welcome": "👋 Приветствие",
        "autorole": "👤 Автороль",
        "moderation": "🛡️ Модерация",
        "refresh": "🔄 Обновить",
        "reset": "♻️ Сбросить",
        "enabled": "Включено",
        "disabled": "Выключено",
        "ticket_open": "Открыть тикет",
        "ticket_close": "Закрыть тикет",
        "add_member": "Добавить участника",
        "ticket_created": "Тикет создан.",
        "ticket_closed": "Тикет закрывается.",
        "ticket_disabled": "Система тикетов отключена.",
        "ticket_name": "Тикет",
        "problem": "Проблема",
        "problem_placeholder": "Опишите проблему",
        "member_id": "ID участника",
        "member_id_placeholder": "Discord ID участника",
        "member_added": "Участник добавлен.",
        "invalid_member": "Участник не найден.",
        "permission": "У вас нет прав.",
        "saved": "Настройка сохранена.",
        "reset_done": "Настройки сервера сброшены.",
        "ping_title": "Статус Ping Dynex",
        "ping_description": "Статус ping **Dynex**",
        "voice_title": "Статистика голосового канала",
        "voice_joined": "Канал входа",
        "voice_left": "Канал выхода",
        "voice_duration": "Время в голосовом канале",
        "voice_members": "Участников при выходе",
        "voice_disable": "🔕 Отключить голосовые уведомления",
        "voice_enable": "🔔 Включить голосовые уведомления",
        "voice_disabled": "Голосовые уведомления отключены.",
        "voice_enabled": "Голосовые уведомления включены.",
        "welcome_default": "Добро пожаловать, {member}!",
        "yes": "Да",
        "no": "Нет"
    },

    "ar": {
        "language_name": "العربية",
        "language_changed": "تم ضبط لغتك على العربية.",
        "already_language": "أنت تستخدم العربية بالفعل.",
        "language_title": "لغة Dynex",
        "language_description": "اختر لغة Dynex.",
        "settings_title": "إعدادات Dynex",
        "ticket": "🎫 تذكرة",
        "logs": "📜 السجلات",
        "welcome": "👋 الترحيب",
        "autorole": "👤 رتبة تلقائية",
        "moderation": "🛡️ الإشراف",
        "refresh": "🔄 تحديث",
        "reset": "♻️ إعادة ضبط",
        "enabled": "مفعّل",
        "disabled": "معطّل",
        "ticket_open": "فتح تذكرة",
        "ticket_close": "إغلاق التذكرة",
        "add_member": "إضافة عضو",
        "ticket_created": "تم إنشاء التذكرة.",
        "ticket_closed": "جارٍ إغلاق التذكرة.",
        "ticket_disabled": "نظام التذاكر معطّل حالياً.",
        "ticket_name": "تذكرة",
        "problem": "المشكلة",
        "problem_placeholder": "اكتب مشكلتك",
        "member_id": "معرّف العضو",
        "member_id_placeholder": "معرّف Discord للعضو",
        "member_added": "تمت إضافة العضو.",
        "invalid_member": "لم يتم العثور على عضو صالح.",
        "permission": "ليس لديك صلاحية.",
        "saved": "تم حفظ الإعداد.",
        "reset_done": "تمت إعادة ضبط إعدادات الخادم.",
        "ping_title": "حالة Ping لـ Dynex",
        "ping_description": "حالة Ping الخاصة بـ **Dynex**",
        "voice_title": "إحصائيات القناة الصوتية",
        "voice_joined": "القناة التي انضم إليها",
        "voice_left": "القناة التي غادرها",
        "voice_duration": "مدة البقاء في الصوت",
        "voice_members": "الأعضاء عند المغادرة",
        "voice_disable": "🔕 تعطيل إشعارات الصوت",
        "voice_enable": "🔔 تفعيل إشعارات الصوت",
        "voice_disabled": "تم تعطيل إشعارات الصوت.",
        "voice_enabled": "تم تفعيل إشعارات الصوت.",
        "welcome_default": "مرحباً {member}!",
        "yes": "نعم",
        "no": "لا"
    },

    "zh": {
        "language_name": "中文",
        "language_changed": "您的语言已设置为中文。",
        "already_language": "您已经在使用中文。",
        "language_title": "Dynex 语言选择",
        "language_description": "选择 Dynex 使用的语言。",
        "settings_title": "Dynex 设置",
        "ticket": "🎫 工单",
        "logs": "📜 日志",
        "welcome": "👋 欢迎",
        "autorole": "👤 自动身份组",
        "moderation": "🛡️ 管理",
        "refresh": "🔄 刷新",
        "reset": "♻️ 重置",
        "enabled": "已开启",
        "disabled": "已关闭",
        "ticket_open": "打开工单",
        "ticket_close": "关闭工单",
        "add_member": "添加成员",
        "ticket_created": "工单已创建。",
        "ticket_closed": "工单正在关闭。",
        "ticket_disabled": "工单系统目前已关闭。",
        "ticket_name": "工单",
        "problem": "问题",
        "problem_placeholder": "描述您的问题",
        "member_id": "成员 ID",
        "member_id_placeholder": "要添加成员的 Discord ID",
        "member_added": "成员已添加。",
        "invalid_member": "未找到有效成员。",
        "permission": "您没有权限。",
        "saved": "设置已保存。",
        "reset_done": "服务器设置已重置。",
        "ping_title": "Dynex Ping 状态",
        "ping_description": "**Dynex** 的 Ping 状态",
        "voice_title": "语音频道统计",
        "voice_joined": "加入的频道",
        "voice_left": "离开的频道",
        "voice_duration": "语音停留时间",
        "voice_members": "离开时成员数",
        "voice_disable": "🔕 关闭语音通知",
        "voice_enable": "🔔 开启语音通知",
        "voice_disabled": "语音通知已关闭。",
        "voice_enabled": "语音通知已开启。",
        "welcome_default": "欢迎 {member}！",
        "yes": "是",
        "no": "否"
    },

    "ja": {
        "language_name": "日本語",
        "language_changed": "言語を日本語に設定しました。",
        "already_language": "すでに日本語を使用しています。",
        "language_title": "Dynex 言語選択",
        "language_description": "Dynex の言語を選択してください。",
        "settings_title": "Dynex 設定",
        "ticket": "🎫 チケット",
        "logs": "📜 ログ",
        "welcome": "👋 ウェルカム",
        "autorole": "👤 自動ロール",
        "moderation": "🛡️ モデレーション",
        "refresh": "🔄 更新",
        "reset": "♻️ リセット",
        "enabled": "有効",
        "disabled": "無効",
        "ticket_open": "チケットを開く",
        "ticket_close": "チケットを閉じる",
        "add_member": "メンバーを追加",
        "ticket_created": "チケットを作成しました。",
        "ticket_closed": "チケットを閉じています。",
        "ticket_disabled": "チケットシステムは現在無効です。",
        "ticket_name": "チケット",
        "problem": "問題",
        "problem_placeholder": "問題を入力してください",
        "member_id": "メンバーID",
        "member_id_placeholder": "追加するメンバーのDiscord ID",
        "member_added": "メンバーを追加しました。",
        "invalid_member": "有効なメンバーが見つかりません。",
        "permission": "権限がありません。",
        "saved": "設定を保存しました。",
        "reset_done": "サーバー設定をリセットしました。",
        "ping_title": "Dynex Ping 状態",
        "ping_description": "**Dynex** の Ping 状態",
        "voice_title": "ボイスチャンネル統計",
        "voice_joined": "参加したチャンネル",
        "voice_left": "退出したチャンネル",
        "voice_duration": "ボイス滞在時間",
        "voice_members": "退出時のメンバー数",
        "voice_disable": "🔕 ボイス通知を無効化",
        "voice_enable": "🔔 ボイス通知を有効化",
        "voice_disabled": "ボイス通知を無効にしました。",
        "voice_enabled": "ボイス通知を有効にしました。",
        "welcome_default": "{member} さん、ようこそ！",
        "yes": "はい",
        "no": "いいえ"
    },

    "ko": {
        "language_name": "한국어",
        "language_changed": "언어가 한국어로 설정되었습니다.",
        "already_language": "이미 한국어를 사용하고 있습니다.",
        "language_title": "Dynex 언어 선택",
        "language_description": "Dynex에서 사용할 언어를 선택하세요.",
        "settings_title": "Dynex 설정",
        "ticket": "🎫 티켓",
        "logs": "📜 로그",
        "welcome": "👋 환영",
        "autorole": "👤 자동 역할",
        "moderation": "🛡️ 관리",
        "refresh": "🔄 새로고침",
        "reset": "♻️ 초기화",
        "enabled": "활성화",
        "disabled": "비활성화",
        "ticket_open": "티켓 열기",
        "ticket_close": "티켓 닫기",
        "add_member": "멤버 추가",
        "ticket_created": "티켓이 생성되었습니다.",
        "ticket_closed": "티켓을 닫는 중입니다.",
        "ticket_disabled": "티켓 시스템이 현재 비활성화되어 있습니다.",
        "ticket_name": "티켓",
        "problem": "문제",
        "problem_placeholder": "문제를 입력하세요",
        "member_id": "멤버 ID",
        "member_id_placeholder": "추가할 멤버의 Discord ID",
        "member_added": "멤버가 추가되었습니다.",
        "invalid_member": "유효한 멤버를 찾을 수 없습니다.",
        "permission": "권한이 없습니다.",
        "saved": "설정이 저장되었습니다.",
        "reset_done": "서버 설정이 초기화되었습니다.",
        "ping_title": "Dynex Ping 상태",
        "ping_description": "**Dynex**의 Ping 상태",
        "voice_title": "음성 채널 통계",
        "voice_joined": "참여한 채널",
        "voice_left": "나간 채널",
        "voice_duration": "음성 채널 체류 시간",
        "voice_members": "나갈 때의 멤버 수",
        "voice_disable": "🔕 음성 알림 끄기",
        "voice_enable": "🔔 음성 알림 켜기",
        "voice_disabled": "음성 알림이 비활성화되었습니다.",
        "voice_enabled": "음성 알림이 활성화되었습니다.",
        "welcome_default": "{member}님 환영합니다!",
        "yes": "예",
        "no": "아니요"
    },

    "nl": {
        "language_name": "Nederlands",
        "language_changed": "Je taal is ingesteld op Nederlands.",
        "already_language": "Je gebruikt al Nederlands.",
        "language_title": "Dynex Taalkeuze",
        "language_description": "Kies de taal van Dynex.",
        "settings_title": "Dynex Instellingen",
        "ticket": "🎫 Ticket",
        "logs": "📜 Logs",
        "welcome": "👋 Welkom",
        "autorole": "👤 Autorol",
        "moderation": "🛡️ Moderatie",
        "refresh": "🔄 Vernieuwen",
        "reset": "♻️ Resetten",
        "enabled": "Ingeschakeld",
        "disabled": "Uitgeschakeld",
        "ticket_open": "Ticket openen",
        "ticket_close": "Ticket sluiten",
        "add_member": "Lid toevoegen",
        "ticket_created": "Ticket aangemaakt.",
        "ticket_closed": "Het ticket wordt gesloten.",
        "ticket_disabled": "Het ticketsysteem is momenteel uitgeschakeld.",
        "ticket_name": "Ticket",
        "problem": "Probleem",
        "problem_placeholder": "Beschrijf je probleem",
        "member_id": "Lid-ID",
        "member_id_placeholder": "Discord-ID van het lid",
        "member_added": "Lid toegevoegd.",
        "invalid_member": "Geen geldig lid gevonden.",
        "permission": "Je hebt geen toestemming.",
        "saved": "Instelling opgeslagen.",
        "reset_done": "Serverinstellingen gereset.",
        "ping_title": "Dynex Ping-status",
        "ping_description": "De ping-status van **Dynex**",
        "voice_title": "Spraakkanaalstatistieken",
        "voice_joined": "Kanaal binnengekomen",
        "voice_left": "Kanaal verlaten",
        "voice_duration": "Tijd in spraak",
        "voice_members": "Leden bij vertrek",
        "voice_disable": "🔕 Spraakmeldingen uitschakelen",
        "voice_enable": "🔔 Spraakmeldingen inschakelen",
        "voice_disabled": "Spraakmeldingen uitgeschakeld.",
        "voice_enabled": "Spraakmeldingen ingeschakeld.",
        "welcome_default": "Welkom {member}!",
        "yes": "Ja",
        "no": "Nee"
    },

    "pl": {
        "language_name": "Polski",
        "language_changed": "Twój język został ustawiony na polski.",
        "already_language": "Już używasz języka polskiego.",
        "language_title": "Język Dynex",
        "language_description": "Wybierz język Dynex.",
        "settings_title": "Ustawienia Dynex",
        "ticket": "🎫 Zgłoszenie",
        "logs": "📜 Logi",
        "welcome": "👋 Powitanie",
        "autorole": "👤 AutoRola",
        "moderation": "🛡️ Moderacja",
        "refresh": "🔄 Odśwież",
        "reset": "♻️ Resetuj",
        "enabled": "Włączone",
        "disabled": "Wyłączone",
        "ticket_open": "Otwórz zgłoszenie",
        "ticket_close": "Zamknij zgłoszenie",
        "add_member": "Dodaj członka",
        "ticket_created": "Zgłoszenie utworzone.",
        "ticket_closed": "Zgłoszenie jest zamykane.",
        "ticket_disabled": "System zgłoszeń jest wyłączony.",
        "ticket_name": "Zgłoszenie",
        "problem": "Problem",
        "problem_placeholder": "Opisz swój problem",
        "member_id": "ID członka",
        "member_id_placeholder": "Discord ID członka",
        "member_added": "Członek został dodany.",
        "invalid_member": "Nie znaleziono członka.",
        "permission": "Nie masz uprawnień.",
        "saved": "Ustawienie zapisane.",
        "reset_done": "Ustawienia serwera zostały zresetowane.",
        "ping_title": "Status Ping Dynex",
        "ping_description": "Status ping **Dynex**",
        "voice_title": "Statystyki kanału głosowego",
        "voice_joined": "Kanał dołączony",
        "voice_left": "Kanał opuszczony",
        "voice_duration": "Czas na kanale głosowym",
        "voice_members": "Członkowie przy wyjściu",
        "voice_disable": "🔕 Wyłącz powiadomienia głosowe",
        "voice_enable": "🔔 Włącz powiadomienia głosowe",
        "voice_disabled": "Powiadomienia głosowe wyłączone.",
        "voice_enabled": "Powiadomienia głosowe włączone.",
        "welcome_default": "Witaj {member}!",
        "yes": "Tak",
        "no": "Nie"
    },

    "uk": {
        "language_name": "Українська",
        "language_changed": "Вашу мову встановлено українською.",
        "already_language": "Ви вже використовуєте українську.",
        "language_title": "Мова Dynex",
        "language_description": "Виберіть мову Dynex.",
        "settings_title": "Налаштування Dynex",
        "ticket": "🎫 Тікет",
        "logs": "📜 Логи",
        "welcome": "👋 Привітання",
        "autorole": "👤 Авто роль",
        "moderation": "🛡️ Модерація",
        "refresh": "🔄 Оновити",
        "reset": "♻️ Скинути",
        "enabled": "Увімкнено",
        "disabled": "Вимкнено",
        "ticket_open": "Відкрити тікет",
        "ticket_close": "Закрити тікет",
        "add_member": "Додати учасника",
        "ticket_created": "Тікет створено.",
        "ticket_closed": "Тікет закривається.",
        "ticket_disabled": "Система тікетів вимкнена.",
        "ticket_name": "Тікет",
        "problem": "Проблема",
        "problem_placeholder": "Опишіть проблему",
        "member_id": "ID учасника",
        "member_id_placeholder": "Discord ID учасника",
        "member_added": "Учасника додано.",
        "invalid_member": "Учасника не знайдено.",
        "permission": "У вас немає дозволу.",
        "saved": "Налаштування збережено.",
        "reset_done": "Налаштування сервера скинуто.",
        "ping_title": "Статус Ping Dynex",
        "ping_description": "Статус ping **Dynex**",
        "voice_title": "Статистика голосового каналу",
        "voice_joined": "Канал входу",
        "voice_left": "Канал виходу",
        "voice_duration": "Час у голосовому каналі",
        "voice_members": "Учасників при виході",
        "voice_disable": "🔕 Вимкнути голосові сповіщення",
        "voice_enable": "🔔 Увімкнути голосові сповіщення",
        "voice_disabled": "Голосові сповіщення вимкнено.",
        "voice_enabled": "Голосові сповіщення увімкнено.",
        "welcome_default": "Ласкаво просимо, {member}!",
        "yes": "Так",
        "no": "Ні"
    },

    "az": {
        "language_name": "Azərbaycan",
        "language_changed": "Diliniz Azərbaycan dili olaraq təyin edildi.",
        "already_language": "Artıq Azərbaycan dilindən istifadə edirsiniz.",
        "language_title": "Dynex Dil Seçimi",
        "language_description": "Dynex üçün dili seçin.",
        "settings_title": "Dynex Ayarları",
        "ticket": "🎫 Ticket",
        "logs": "📜 Loglar",
        "welcome": "👋 Qarşılama",
        "autorole": "👤 Avtorol",
        "moderation": "🛡️ Moderasiya",
        "refresh": "🔄 Yenilə",
        "reset": "♻️ Sıfırla",
        "enabled": "Aktiv",
        "disabled": "Deaktiv",
        "ticket_open": "Ticket Aç",
        "ticket_close": "Ticketi Bağla",
        "add_member": "Üzv Əlavə Et",
        "ticket_created": "Ticket yaradıldı.",
        "ticket_closed": "Ticket bağlanır.",
        "ticket_disabled": "Ticket sistemi hazırda deaktivdir.",
        "ticket_name": "Ticket",
        "problem": "Problem",
        "problem_placeholder": "Probleminizi yazın",
        "member_id": "Üzv ID-si",
        "member_id_placeholder": "Əlavə ediləcək üzvün Discord ID-si",
        "member_added": "Üzv ticketə əlavə edildi.",
        "invalid_member": "Etibarlı üzv tapılmadı.",
        "permission": "Bunu etmək üçün icazəniz yoxdur.",
        "saved": "Ayar yadda saxlanıldı.",
        "reset_done": "Server ayarları sıfırlandı.",
        "ping_title": "Dynex Ping vəziyyəti",
        "ping_description": "**Dynex** ping vəziyyəti",
        "voice_title": "Səs Kanalı Statistikası",
        "voice_joined": "Qoşulduğu kanal",
        "voice_left": "Ayrıldığı kanal",
        "voice_duration": "Səs kanalında qalma müddəti",
        "voice_members": "Çıxış zamanı üzv sayı",
        "voice_disable": "🔕 Səs bildirişlərini söndür",
        "voice_enable": "🔔 Səs bildirişlərini aktiv et",
        "voice_disabled": "Səs bildirişləri söndürüldü.",
        "voice_enabled": "Səs bildirişləri aktiv edildi.",
        "welcome_default": "Xoş gəlmisən {member}!",
        "yes": "Bəli",
        "no": "Xeyr"
    }
}


configs = {}
user_settings = {}
voice_sessions = {}


def load_data():
    global configs, user_settings

    if not os.path.exists(CONFIG_FILE):
        configs = {}
        user_settings = {}
        save_data()
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        configs = data.get("guilds", {})
        user_settings = data.get("users", {})

        for guild_id in list(configs.keys()):
            merged = DEFAULT_CONFIG.copy()
            merged.update(configs[guild_id])
            configs[guild_id] = merged

        for user_id in list(user_settings.keys()):
            old = user_settings[user_id]

            if isinstance(old, str):
                user_settings[user_id] = {
                    "language": old if old in LANGUAGES else "tr",
                    "voice_notifications": True
                }
            else:
                user_settings[user_id] = {
                    "language": old.get("language", "tr"),
                    "voice_notifications": old.get(
                        "voice_notifications",
                        True
                    )
                }

    except Exception:
        configs = {}
        user_settings = {}


def save_data():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "guilds": configs,
                "users": user_settings
            },
            f,
            ensure_ascii=False,
            indent=2
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


def get_language(user_id):
    settings = get_user_settings(user_id)
    language = settings.get("language", "tr")

    if language not in LANGUAGES:
        language = "tr"

    return language


def set_language(user_id, language):
    settings = get_user_settings(user_id)
    settings["language"] = language
    save_data()


def get_voice_notifications(user_id):
    return get_user_settings(user_id).get(
        "voice_notifications",
        True
    )


def set_voice_notifications(user_id, value):
    settings = get_user_settings(user_id)
    settings["voice_notifications"] = value
    save_data()


def t(user_id, key):
    language = get_language(user_id)

    if key in TEXTS.get(language, {}):
        return TEXTS[language][key]

    return TEXTS["en"].get(key, key)


class DynexBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=INTENTS
        )

    async def setup_hook(self):
        await self.tree.sync()


bot = DynexBot()


class LanguageSelect(discord.ui.Select):

    def __init__(self):
        options = []

        for code, name in LANGUAGES.items():
            options.append(
                discord.SelectOption(
                    label=name,
                    value=code
                )
            )

        super().__init__(
            placeholder="🌐 Dil seçin / Select language",
            options=options,
            custom_id="dynex_language_select"
        )

    async def callback(self, interaction):

        language = self.values[0]
        current = get_language(interaction.user.id)

        if current == language:
            await interaction.response.send_message(
                t(
                    interaction.user.id,
                    "already_language"
                ),
                ephemeral=True
            )
            return

        set_language(
            interaction.user.id,
            language
        )

        await interaction.response.send_message(
            t(
                interaction.user.id,
                "language_changed"
            ),
            ephemeral=True
        )


class LanguageView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(LanguageSelect())


@bot.tree.command(
    name="dil",
    description="Dynex dilini seç"
)
async def dil(interaction):

    language = get_language(
        interaction.user.id
    )

    embed = discord.Embed(
        title=TEXTS[language]["language_title"],
        description=TEXTS[language]["language_description"],
        color=discord.Color.blurple()
    )

    await interaction.response.send_message(
        embed=embed,
        view=LanguageView(),
        ephemeral=True
    )


@bot.tree.command(
    name="ping",
    description="Dynex ping durumunu gösterir"
)
async def ping(interaction):

    latency = round(
        bot.latency * 1000
    )

    embed = discord.Embed(
        title=t(
            interaction.user.id,
            "ping_title"
        ),
        description=t(
            interaction.user.id,
            "ping_description"
        ),
        color=discord.Color.from_rgb(
            0,
            0,
            0
        )
    )

    embed.add_field(
        name="",
        value=f"`{latency}ms`",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )


class VoiceNotificationView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(timeout=None)

        enabled = get_voice_notifications(
            user_id
        )

        self.toggle = discord.ui.Button(
            label=(
                t(
                    user_id,
                    "voice_disable"
                )
                if enabled
                else t(
                    user_id,
                    "voice_enable"
                )
            ),
            style=discord.ButtonStyle.secondary,
            custom_id=f"dynex_voice_toggle:{user_id}"
        )

        self.toggle.callback = self.toggle_callback
        self.add_item(self.toggle)

    async def toggle_callback(
        self,
        interaction
    ):

        if interaction.user.id != int(
            self.toggle.custom_id.split(":")[1]
        ):
            await interaction.response.send_message(
                t(
                    interaction.user.id,
                    "permission"
                ),
                ephemeral=True
            )
            return

        current = get_voice_notifications(
            interaction.user.id
        )

        set_voice_notifications(
            interaction.user.id,
            not current
        )

        new_state = not current

        self.toggle.label = (
            t(
                interaction.user.id,
                "voice_disable"
            )
            if new_state
            else t(
                interaction.user.id,
                "voice_enable"
            )
        )

        await interaction.response.edit_message(
            view=self
        )

        await interaction.followup.send(
            t(
                interaction.user.id,
                "voice_enabled"
                if new_state
                else "voice_disabled"
            ),
            ephemeral=True
        )


async def send_voice_statistics(
    member,
    before_channel,
    started_at
):

    if not get_voice_notifications(
        member.id
    ):
        return

    now = datetime.now(
        timezone.utc
    )

    duration = now - started_at
    total_seconds = int(
        duration.total_seconds()
    )

    hours = total_seconds // 3600
    minutes = (
        total_seconds % 3600
    ) // 60
    seconds = total_seconds % 60

    channel_name = (
        before_channel.name
        if before_channel
        else "-"
    )

    member_count = (
        len(before_channel.members)
        if before_channel
        else 0
    )

    embed = discord.Embed(
        title=t(
            member.id,
            "voice_title"
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=t(
            member.id,
            "voice_joined"
        ),
        value=channel_name,
        inline=False
    )

    embed.add_field(
        name=t(
            member.id,
            "voice_duration"
        ),
        value=(
            f"{hours}h "
            f"{minutes}m "
            f"{seconds}s"
        ),
        inline=False
    )

    embed.add_field(
        name=t(
            member.id,
            "voice_members"
        ),
        value=str(member_count),
        inline=False
    )

    try:
        dm = await member.create_dm()

        await dm.send(
            embed=embed,
            view=VoiceNotificationView(
                member.id
            )
        )

    except discord.Forbidden:
        pass

    except discord.HTTPException:
        pass

    except Exception as e:
        print(
            f"Voice DM error for {member}: {e}"
        )


@bot.event
async def on_voice_state_update(
    member,
    before,
    after
):

    key = (
        member.guild.id,
        member.id
    )

    if (
        before.channel is None
        and after.channel is not None
    ):

        voice_sessions[key] = {
            "channel_id": after.channel.id,
            "started_at": datetime.now(
                timezone.utc
            )
        }

    elif (
        before.channel is not None
        and after.channel is not None
        and before.channel.id != after.channel.id
    ):

        voice_sessions[key] = {
            "channel_id": after.channel.id,
            "started_at": datetime.now(
                timezone.utc
            )
        }

    elif (
        before.channel is not None
        and after.channel is None
    ):

        session = voice_sessions.pop(
            key,
            None
        )

        if session:

            await send_voice_statistics(
                member,
                before.channel,
                session["started_at"]
            )


def settings_embed(user_id):

    language = get_language(
        user_id
    )

    return discord.Embed(
        title=TEXTS[language]["settings_title"],
        description=(
            f"{TEXTS[language]['ticket']}\n"
            f"{TEXTS[language]['logs']}\n"
            f"{TEXTS[language]['welcome']}\n"
            f"{TEXTS[language]['autorole']}\n"
            f"{TEXTS[language]['moderation']}"
        ),
        color=discord.Color.blurple()
    )


class TicketProblemModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="Ticket"
        )

        self.problem = discord.ui.TextInput(
            label="Problem",
            placeholder="Sorununuzu yazın",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )

        self.add_item(
            self.problem
        )

    async def on_submit(
        self,
        interaction
    ):

        config = get_config(
            interaction.guild.id
        )

        category = None

        category_id = config.get(
            "ticket_category"
        )

        if category_id:

            category = interaction.guild.get_channel(
                int(category_id)
            )

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
                    read_message_history=True
                )
        }

        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        language = get_language(
            interaction.user.id
        )

        embed = discord.Embed(
            title=TEXTS[language]["ticket_name"],
            description=self.problem.value,
            color=discord.Color.blurple()
        )

        await channel.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketCloseView(language)
        )

        await interaction.response.send_message(
            f"{TEXTS[language]['ticket_created']} "
            f"{channel.mention}",
            ephemeral=True
        )


class AddMemberModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="Add Member"
        )

        self.member_id = discord.ui.TextInput(
            label="Member ID",
            placeholder="Discord ID",
            required=True,
            max_length=25
        )

        self.add_item(
            self.member_id
        )

    async def on_submit(
        self,
        interaction
    ):

        try:
            member_id = int(
                self.member_id.value
            )

            member = interaction.guild.get_member(
                member_id
            )

            if member is None:
                member = await interaction.guild.fetch_member(
                    member_id
                )

        except Exception:

            await interaction.response.send_message(
                t(
                    interaction.user.id,
                    "invalid_member"
                ),
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
            t(
                interaction.user.id,
                "member_added"
            )
        )


class TicketPanelView(discord.ui.View):

    def __init__(self, language="tr"):
        super().__init__(
            timeout=None
        )

        button = discord.ui.Button(
            label=TEXTS[language]["ticket_open"],
            style=discord.ButtonStyle.primary,
            emoji="🎫",
            custom_id="dynex_ticket_open"
        )

        async def callback(
            interaction
        ):

            config = get_config(
                interaction.guild.id
            )

            if not config.get(
                "ticket",
                True
            ):

                await interaction.response.send_message(
                    t(
                        interaction.user.id,
                        "ticket_disabled"
                    ),
                    ephemeral=True
                )

                return

            await interaction.response.send_modal(
                TicketProblemModal()
            )

        button.callback = callback

        self.add_item(
            button
        )


class TicketCloseView(discord.ui.View):

    def __init__(self, language="tr"):
        super().__init__(
            timeout=None
        )

        close_button = discord.ui.Button(
            label=TEXTS[language]["ticket_close"],
            style=discord.ButtonStyle.danger,
            emoji="🔒",
            custom_id="dynex_ticket_close"
        )

        add_button = discord.ui.Button(
            label=TEXTS[language]["add_member"],
            style=discord.ButtonStyle.secondary,
            emoji="👤",
            custom_id="dynex_ticket_add"
        )

        async def close_callback(
            interaction
        ):

            await interaction.response.send_message(
                t(
                    interaction.user.id,
                    "ticket_closed"
                )
            )

            await interaction.channel.delete(
                reason="Dynex ticket closed"
            )

        async def add_callback(
            interaction
        ):

            await interaction.response.send_modal(
                AddMemberModal()
            )

        close_button.callback = close_callback
        add_button.callback = add_callback

        self.add_item(
            close_button
        )

        self.add_item(
            add_button
        )


class SettingsView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(
            timeout=180
        )

        language = get_language(
            user_id
        )

        ticket = discord.ui.Button(
            label=TEXTS[language]["ticket"],
            style=discord.ButtonStyle.primary,
            row=0
        )

        logs = discord.ui.Button(
            label=TEXTS[language]["logs"],
            style=discord.ButtonStyle.secondary,
            row=0
        )

        welcome = discord.ui.Button(
            label=TEXTS[language]["welcome"],
            style=discord.ButtonStyle.secondary,
            row=1
        )

        autorole = discord.ui.Button(
            label=TEXTS[language]["autorole"],
            style=discord.ButtonStyle.secondary,
            row=1
        )

        moderation = discord.ui.Button(
            label=TEXTS[language]["moderation"],
            style=discord.ButtonStyle.secondary,
            row=2
        )

        refresh = discord.ui.Button(
            label=TEXTS[language]["refresh"],
            style=discord.ButtonStyle.success,
            row=2
        )

        reset = discord.ui.Button(
            label=TEXTS[language]["reset"],
            style=discord.ButtonStyle.danger,
            row=2
        )

        async def ticket_callback(
            interaction
        ):

            config = get_config(
                interaction.guild.id
            )

            config["ticket"] = not config["ticket"]

            save_data()

            await interaction.response.edit_message(
                embed=settings_embed(
                    interaction.user.id
                ),
                view=SettingsView(
                    interaction.user.id
                )
            )

        async def logs_callback(
            interaction
        ):

            config = get_config(
                interaction.guild.id
            )

            config["logs"] = not config["logs"]

            save_data()

            await interaction.response.edit_message(
                embed=settings_embed(
                    interaction.user.id
                ),
                view=SettingsView(
                    interaction.user.id
                )
            )

        async def welcome_callback(
            interaction
        ):

            config = get_config(
                interaction.guild.id
            )

            config["welcome"] = not config["welcome"]

            save_data()

            await interaction.response.edit_message(
                embed=settings_embed(
                    interaction.user.id
                ),
                view=SettingsView(
                    interaction.user.id
                )
            )

        async def autorole_callback(
            interaction
        ):

            config = get_config(
                interaction.guild.id
            )

            config["autorole"] = not config["autorole"]

            save_data()

            await interaction.response.edit_message(
                embed=settings_embed(
                    interaction.user.id
                ),
                view=SettingsView(
                    interaction.user.id
                )
            )

        async def moderation_callback(
            interaction
        ):

            config = get_config(
                interaction.guild.id
            )

            config["moderation"] = not config["moderation"]

            save_data()

            await interaction.response.edit_message(
                embed=settings_embed(
                    interaction.user.id
                ),
                view=SettingsView(
                    interaction.user.id
                )
            )

        async def refresh_callback(
            interaction
        ):

            await interaction.response.edit_message(
                embed=settings_embed(
                    interaction.user.id
                ),
                view=SettingsView(
                    interaction.user.id
                )
            )

        async def reset_callback(
            interaction
        ):

            configs[
                str(interaction.guild.id)
            ] = DEFAULT_CONFIG.copy()

            save_data()

            language = get_language(
                interaction.user.id
            )

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title=TEXTS[language]["settings_title"],
                    description=t(
                        interaction.user.id,
                        "reset_done"
                    ),
                    color=discord.Color.green()
                ),
                view=SettingsView(
                    interaction.user.id
                )
            )

        ticket.callback = ticket_callback
        logs.callback = logs_callback
        welcome.callback = welcome_callback
        autorole.callback = autorole_callback
        moderation.callback = moderation_callback
        refresh.callback = refresh_callback
        reset.callback = reset_callback

        self.add_item(ticket)
        self.add_item(logs)
        self.add_item(welcome)
        self.add_item(autorole)
        self.add_item(moderation)
        self.add_item(refresh)
        self.add_item(reset)


@bot.tree.command(
    name="ayarlar",
    description="Dynex sunucu ayarlarını açar"
)
@app_commands.checks.has_permissions(
    administrator=True
)
async def ayarlar(
    interaction
):

    await interaction.response.send_message(
        embed=settings_embed(
            interaction.user.id
        ),
        view=SettingsView(
            interaction.user.id
        ),
        ephemeral=True
    )


@ayarlar.error
async def ayarlar_error(
    interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        await interaction.response.send_message(
            t(
                interaction.user.id,
                "permission"
            ),
            ephemeral=True
        )


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
                int(role_id)
            )

            if role:

                try:
                    await member.add_roles(
                        role,
                        reason="Dynex autorole"
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
                int(channel_id)
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


@bot.event
async def on_ready():

    print(
        f"Dynex aktif: {bot.user} "
        f"| {len(LANGUAGES)} dil destekleniyor."
    )

    bot.add_view(
        TicketPanelView("tr")
    )


load_data()

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable bulunamadı."
    )

bot.run(TOKEN)
