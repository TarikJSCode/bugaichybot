
import logging
import re
import os
import json
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ChatMemberHandler

# Словник для відмінювання українських імен (розширена бібліотека)
MALE_NAMES_DECLENSION = {
    'Андрій': 'Андрія', 'Олександр': 'Олександра', 'Володимир': 'Володимира',
    'Дмитро': 'Дмитра', 'Сергій': 'Сергія', 'Максим': 'Максима',
    'Артем': 'Артема', 'Роман': 'Романа', 'Іван': 'Івана',
    'Петро': 'Петра', 'Микола': 'Миколу', 'Павло': 'Павла',
    'Bogdan': 'Богдана', 'Тарас': 'Тараса', 'Юрій': 'Юрія',
    'Віктор': 'Віктора', 'Ігор': 'Ігоря', 'Олег': 'Олега',
    'Віталій': 'Віталія', 'Денис': 'Дениса', 'Антон': 'Антона',
    'Олексій': 'Олексія', 'Василь': 'Василя', 'Григорій': 'Григорія',
    'Михайло': 'Михайла', 'Ярослав': 'Ярослава', 'Владислав': 'Владислава',
    'Станіслав': 'Станіслава', 'Богуслав': 'Богуслава', 'Мирослав': 'Мирослава',
    'Святослав': 'Святослава', 'Ростислав': 'Ростислава', 'Вячеслав': 'Вячеслава',
    'Костянтин': 'Костянтина', 'Валентин': 'Валентина', 'Валерій': 'Валерія',
    'Геннадій': 'Геннадія', 'Леонід': 'Леоніда', 'Едуард': 'Едуарда',
    'Євген': 'Євгена', 'Арсен': 'Арсена', 'Руслан': 'Руслана',
    'Назар': 'Назара', 'Остап': 'Остапа', 'Орест': 'Ореста',
    'Богдан': 'Богдана', 'Степан': 'Степана', 'Ілля': 'Іллю',
    'Матвій': 'Матвія', 'Данило': 'Данила', 'Марко': 'Марка',
    'Тимофій': 'Тимофія', 'Захар': 'Захара', 'Елеазар': 'Елеазара',
    'Федір': 'Федора', 'Гліб': 'Гліба', 'Аркадій': 'Аркадія',
    'Анатолій': 'Анатолія', 'Борис': 'Бориса', 'Вадим': 'Вадима',
    'Георгій': 'Георгія', 'Дамян': 'Дамяна', 'Емиль': 'Емиля',
    'Жора': 'Жору', 'Заур': 'Заура', 'Кирило': 'Кирила',
    'Левко': 'Левка', 'Мирон': 'Мирона', 'Нестор': 'Нестора',
    'Онуфрій': 'Онуфрія', 'Прохор': 'Прохора', 'Ричард': 'Ричарда',
    'Савелій': 'Савелія', 'Тимур': 'Тимура', 'Ульрих': 'Ульриха',
    'Феодосій': 'Феодосія', 'Христофор': 'Христофора', 'Цезар': 'Цезара',
    'Шмуель': 'Шмуеля', 'Ярема': 'Ярему', 'Яків': 'Якова'
}

FEMALE_NAMES_DECLENSION = {
    'Анна': 'Анну', 'Марія': 'Марію', 'Катерина': 'Катерину',
    'Олена': 'Олену', 'Наталія': 'Наталію', 'Світлана': 'Світлану',
    'Тетяна': 'Тетяну', 'Ірина': 'Ірину', 'Людмила': 'Людмилу',
    'Галина': 'Галину', 'Валентина': 'Валентину', 'Лариса': 'Ларису',
    'Оксана': 'Оксану', 'Юлія': 'Юлію', 'Вікторія': 'Вікторію',
    'Дарина': 'Дарину', 'Софія': 'Софію', 'Емілія': 'Емілію',
    'Поліна': 'Поліну', 'Діана': 'Діану', 'Альона': 'Альону',
    'Богдана': 'Богдану', 'Владислава': 'Владиславу', 'Василина': 'Василину',
    'Гелена': 'Гелену', 'Дарія': 'Дарію', 'Єлизавета': 'Єлизавету',
    'Жанна': 'Жанну', 'Зоя': 'Зою', 'Ія': 'Ію',
    'Кристина': 'Кристину', 'Лілія': 'Лілію', 'Маргарита': 'Маргариту',
    'Ніна': 'Ніну', 'Ольга': 'Ольгу', 'Полина': 'Полину',
    'Роксолана': 'Роксолану', 'Стефанія': 'Стефанію', 'Тамара': 'Тамару',
    'Уляна': 'Уляну', 'Фаїна': 'Фаїну', 'Христина': 'Христину',
    'Ціна': 'Ціну', 'Шарлотта': 'Шарлотту', 'Ярослава': 'Ярославу',
    'Аліна': 'Аліну', 'Бажена': 'Бажену', 'Вера': 'Веру',
    'Гліб': 'Гліба', 'Данна': 'Данну', 'Ева': 'Еву',
    'Ілона': 'Ілону', 'Калина': 'Калину', 'Лада': 'Ладу',
    'Мирослава': 'Мирославу', 'Надія': 'Надію', 'Оріана': 'Оріану',
    'Роксана': 'Роксану', 'Соломія': 'Соломію', 'Таїсія': 'Таїсію',
    'Устина': 'Устину', 'Феодора': 'Феодору', 'Христя': 'Христю',
    'Ця': 'Цю', 'Шанна': 'Шанну', 'Ява': 'Яву',
    'Агата': 'Агату', 'Божена': 'Божену', 'Віра': 'Віру',
    'Горислава': 'Гориславу', 'Добромила': 'Добромилу', 'Есфір': 'Есфір',
    'Іванна': 'Іванну', 'Кіра': 'Кіру', 'Любов': 'Любов',
    'Мілена': 'Мілену', 'Неля': 'Нелю', 'Орися': 'Орисю',
    'Руслана': 'Руслану', 'Слава': 'Славу', 'Тіана': 'Тіану',
    'Ульяна': 'Ульяну', 'Фелісія': 'Фелісію', 'Хрістя': 'Хрістю',
    'Цвітана': 'Цвітану', 'Шура': 'Шуру', 'Яна': 'Яну'
}

# Дані для зберігання стосунків (зберігаються у файлі relationships.json)
RELATIONSHIPS_FILE = 'relationships.json'

# Системи рівнів стосунків
RELATIONSHIP_LEVELS = {
    0: {"name": "Знайомство", "emoji": "👋", "required_actions": 0},
    1: {"name": "Симпатія", "emoji": "😊", "required_actions": 5},
    2: {"name": "Закоханість", "emoji": "😍", "required_actions": 15},
    3: {"name": "Кохання", "emoji": "💕", "required_actions": 30},
    4: {"name": "Глибоке кохання", "emoji": "💖", "required_actions": 50},
    5: {"name": "Готовність до шлюбу", "emoji": "💍", "required_actions": 75}
}

# Команди пар для стосунків з очками (прибрано cuddle)
COUPLE_COMMANDS = {
    'kiss': {'action': 'поцілував', 'points': 2, 'emoji': '💋'},
    'hug': {'action': 'обійняв', 'points': 1, 'emoji': '🤗'},
    'love': {'action': 'кохає', 'points': 3, 'emoji': '💕'},
    'date': {'action': 'ходить на побачення з', 'points': 3, 'emoji': '🌹'},
    'flirt': {'action': 'фліртує з', 'points': 1, 'emoji': '😏'},
    'gift': {'action': 'дарує подарунок', 'points': 2, 'emoji': '🎁'},
    'dance': {'action': 'танцює з', 'points': 2, 'emoji': '💃'},
    'hold': {'action': 'тримає за руку', 'points': 1, 'emoji': '👫'},
    'propose': {'action': 'робить пропозицію', 'points': 0, 'emoji': '💍'},
    'accept': {'action': 'приймає пропозицію від', 'points': 0, 'emoji': '✅'},
    'reject': {'action': 'відхиляє пропозицію від', 'points': 0, 'emoji': '❌'},
    'start': {'action': 'розпочинає стосунки з', 'points': 1, 'emoji': '💫'},
    'marry': {'action': 'одружується з', 'points': 0, 'emoji': '💒'},
    'divorce': {'action': 'розлучається з', 'points': 0, 'emoji': '💔'},
    'breakup': {'action': 'розстається з', 'points': 0, 'emoji': '😢'}
}

# Валідні команди
VALID_COMMANDS = [
    'start', 'help', 'relationships', 'myrelationships', 'flipcoin', 'proposals',
    *COUPLE_COMMANDS.keys()
]

def load_relationships():
    """Завантажує стосунки з файлу"""
    try:
        with open(RELATIONSHIPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_relationships(relationships):
    """Зберігає стосунки у файл"""
    with open(RELATIONSHIPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, ensure_ascii=False, indent=2)

def decline_name(name):
    """Відмінює ім'я з називного у знахідний відмінок"""
    if name in MALE_NAMES_DECLENSION:
        return MALE_NAMES_DECLENSION[name]
    elif name in FEMALE_NAMES_DECLENSION:
        return FEMALE_NAMES_DECLENSION[name]

    # Автоматичне відмінювання
    if name.endswith(('ій', 'ей')):
        return name[:-2] + 'я'
    elif name.endswith('о'):
        return name[:-1] + 'а'
    elif name.endswith(('н', 'м', 'р', 't', 'к', 'л', 'с')):
        return name + 'а'
    elif name.endswith('а'):
        return name[:-1] + 'у'
    elif name.endswith('я'):
        return name[:-1] + 'ю'

    return name

def get_relationship_level(total_actions):
    """Визначає рівень стосунків за кількістю дій"""
    for level in reversed(range(len(RELATIONSHIP_LEVELS))):
        if total_actions >= RELATIONSHIP_LEVELS[level]["required_actions"]:
            return level
    return 0

def format_duration(start_date):
    """Форматує тривалість стосунків"""
    start = datetime.fromisoformat(start_date)
    duration = datetime.now() - start
    total_seconds = duration.total_seconds()
    days = duration.days
    hours = (duration.seconds // 3600)
    minutes = (duration.seconds % 3600) // 60

    if total_seconds < 60:
        return "менше хвилини"
    elif total_seconds < 3600:  # менше години
        return f"{minutes} хвилин"
    elif days == 0:  # менше дня
        if hours == 1:
            return f"1 година {minutes} хвилин"
        else:
            return f"{hours} годин {minutes} хвилин"
    elif days == 1:
        return f"1 день {hours} годин"
    elif days < 7:
        return f"{days} днів"
    elif days < 30:
        weeks = days // 7
        remaining_days = days % 7
        if weeks == 1:
            if remaining_days > 0:
                return f"1 тиждень {remaining_days} днів"
            else:
                return "1 тиждень"
        else:
            if remaining_days > 0:
                return f"{weeks} тижнів {remaining_days} днів"
            else:
                return f"{weeks} тижнів"
    elif days < 365:
        months = days // 30
        remaining_days = days % 30
        if months == 1:
            if remaining_days > 0:
                return f"1 місяць {remaining_days} днів"
            else:
                return "1 місяць"
        else:
            if remaining_days > 0:
                return f"{months} місяців {remaining_days} днів"
            else:
                return f"{months} місяців"
    else:
        years = days // 365
        remaining_days = days % 365
        if years == 1:
            if remaining_days > 30:
                months = remaining_days // 30
                return f"1 рік {months} місяців"
            elif remaining_days > 0:
                return f"1 рік {remaining_days} днів"
            else:
                return "1 рік"
        else:
            if remaining_days > 30:
                months = remaining_days // 30
                return f"{years} років {months} місяців"
            elif remaining_days > 0:
                return f"{years} років {remaining_days} днів"
            else:
                return f"{years} років"

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не знайдено в змінних середовища! Додайте його в Secrets.")

def create_user_link(name, user_id=None, is_sender=False):
    """Створює посилання на користувача"""
    if is_sender:
        # Відправник без символів, звичайний текст
        return name
    else:
        # Адресант з одним тематичним емодзі та жирним шрифтом
        if user_id:
            # Створюємо посилання на профіль користувача з блакитним підсвічуванням
            return f"[💖**{name}**💖](tg://user?id={user_id})"
        else:
            return f"💖**{name}**💖"

async def setup_bot_commands(application):
    """Налаштовує команди бота"""
    from telegram import BotCommandScope, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats

    private_commands = [
        BotCommand("start", "Головне меню бота"),
        BotCommand("help", "Довідка")
    ]

    group_commands = [
        BotCommand("start", "💫 Розпочати роботу з ботом"),
        BotCommand("flipcoin", "🪙 Кинути монету"),
        BotCommand("relationships", "💕 Показати всі стосунки"),
        BotCommand("myrelationships", "❤️ Показати ваші стосунки"),
        BotCommand("commands", "📋 Список всіх команд стосунків")
    ]

    await application.bot.set_my_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
    await application.bot.set_my_commands(group_commands, scope=BotCommandScopeAllGroupChats())

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробляє команду /start"""
    keyboard = [
        [InlineKeyboardButton("📖 Інструкція", callback_data='instructions')],
        [InlineKeyboardButton("📞 Зв'язок", callback_data='contact')],
        [InlineKeyboardButton("ℹ️ Про бота", callback_data='about')],
        [InlineKeyboardButton("💡 Приклади", callback_data='examples')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🎭 Привіт! Я бот для створення веселих дій та управління стосунками!\n\n"
        "💕 **Система рівнів стосунків:**\n"
        "👋 Знайомство → 😊 Симпатія → 😍 Закоханість → 💕 Кохання → 💖 Глибоке кохання → 💍 Готовність до шлюбу\n\n"
        "**Нові можливості:**\n"
        "• Жирні ніки з спеціальними символами\n"
        "• Слова в **\"лапках\"** після крапки\n"
        "• Система пропозицій 💍\n"
        "• Розширена бібліотека імен\n\n"
        "**Команди:**\n"
        "`/дія @користувач додаткові дії. зі словами`\n"
        "`/start @партнер` - розпочати стосунки\n"
        "`/propose @партнер` - зробити пропозицію\n"
        "`/accept/@reject @партнер` - прийняти/відхилити\n\n"
        "Вибери опцію з меню нижче! 👇"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def flipcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для кидання монети"""
    result = random.choice(["🪙 Орел", "🪙 Решка"])
    await update.message.reply_text(f"🎲 Результат: {result}")

async def relationships_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показує всі стосунки"""
    relationships = load_relationships()

    if not relationships:
        await update.message.reply_text("💔 Поки що немає активних стосунків!")
        return

    text = "💕 **Активні стосунки:**\n\n"
    for couple_id, data in relationships.items():
        parts = couple_id.split('_')
        if len(parts) >= 2:
            partner1, partner2 = parts[0], parts[1]
            duration = format_duration(data['start_date'])
            total_actions = data.get('total_actions', 0)
            level = get_relationship_level(total_actions)
            level_info = RELATIONSHIP_LEVELS[level]
            status = data.get('status', 'dating')

            status_emoji = "💒" if status == 'married' else "💕"

            partner1_link = create_user_link(partner1, is_sender=False)
            partner2_link = create_user_link(partner2, is_sender=False)

            text += f"{status_emoji} {partner1_link} ❤️ {partner2_link}\n"
            text += f"📊 Рівень: {level_info['emoji']} {level_info['name']}\n"
            text += f"⚡ Дії: {total_actions}\n"
            text += f"📅 Тривалість: {duration}\n\n"

    await update.message.reply_text(text, parse_mode='Markdown')

async def my_relationships_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показує стосунки користувача"""
    user_name = update.message.from_user.first_name
    relationships = load_relationships()

    user_relationships = []
    for couple_id, data in relationships.items():
        parts = couple_id.split('_')
        if len(parts) >= 2:
            partner1, partner2 = parts[0], parts[1]
            if partner1 == user_name or partner2 == user_name:
                partner = partner2 if partner1 == user_name else partner1
                duration = format_duration(data['start_date'])
                total_actions = data.get('total_actions', 0)
                level = get_relationship_level(total_actions)
                level_info = RELATIONSHIP_LEVELS[level]
                status = data.get('status', 'dating')

                status_text = "💒 Одружені" if status == 'married' else "💕 У стосунках"
                partner_link = create_user_link(partner, is_sender=False)

                user_relationships.append(
                    f"{status_text}\n"
                    f"❤️ Партнер: {partner_link}\n"
                    f"📊 Рівень: {level_info['emoji']} {level_info['name']}\n"
                    f"⚡ Дії: {total_actions}\n"
                    f"📅 Тривалість: {duration}"
                )

    if not user_relationships:
        text = "💔 У вас поки немає активних стосунків!"
    else:
        user_link = create_user_link(user_name, is_sender=True)
        text = f"💕 **Ваші стосунки, {user_link}:**\n\n" + "\n\n".join(user_relationships)

    await update.message.reply_text(text, parse_mode='Markdown')

async def proposals_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показує активні пропозиції"""
    user_name = update.message.from_user.first_name
    relationships = load_relationships()

    user_proposals = []

    # Пропозиції ДО користувача
    proposals_to_user = []
    # Пропозиції ВІД користувача
    proposals_from_user = []

    for couple_id, data in relationships.items():
        if 'proposal' in data and data['proposal']['status'] == 'pending':
            proposal = data['proposal']
            if proposal['to'] == user_name:
                from_user_link = create_user_link(proposal['from'], is_sender=False)
                proposals_to_user.append(f"💍 Від {from_user_link}")
            elif proposal['from'] == user_name:
                to_user_link = create_user_link(proposal['to'], is_sender=False)
                proposals_from_user.append(f"💌 До {to_user_link}")

    text = f"💌 **Активні пропозиції для {create_user_link(user_name, is_sender=True)}:**\n\n"

    if proposals_to_user:
        text += "📨 **Пропозиції до вас:**\n" + "\n".join(proposals_to_user) + "\n\n"
        text += "Використайте /accept @username або /reject @username\n\n"

    if proposals_from_user:
        text += "📤 **Ваші пропозиції:**\n" + "\n".join(proposals_from_user) + "\n\n"

    if not proposals_to_user and not proposals_from_user:
        text += "💔 Немає активних пропозицій!"

    await update.message.reply_text(text, parse_mode='Markdown')

async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показує список всіх команд стосунків"""
    commands_text = (
        "📋 **Список команд стосунків:**\n\n"
        "**Основні дії (+очки):**\n"
        "💋 `/kiss @партнер` - поцілувати (+2 очки)\n"
        "🤗 `/hug @партнер` - обійняти (+1 очко)\n"
        "💕 `/love @партнер` - кохати (+3 очки)\n"
        "🌹 `/date @партнер` - піти на побачення (+3 очки)\n"
        "😏 `/flirt @партнер` - фліртувати (+1 очко)\n"
        "🎁 `/gift @партнер` - подарувати подарунок (+2 очки)\n"
        "💃 `/dance @партнер` - танцювати (+2 очки)\n"
        "👫 `/hold @партнер` - тримати за руку (+1 очко)\n\n"
        "**Управління стосунками:**\n"
        "💫 `/start @партнер` - розпочати стосунки\n"
        "💍 `/propose @партнер` - зробити пропозицію\n"
        "✅ `/accept @партнер` - прийняти пропозицію\n"
        "❌ `/reject @партнер` - відхилити пропозицію\n"
        "💒 `/marry @партнер` - одружитися\n"
        "💔 `/divorce @партнер` - розлучитися\n"
        "😢 `/breakup @партнер` - розстатися\n\n"
        "**Інформаційні команди:**\n"
        "💕 `/relationships` - показати всі стосунки\n"
        "❤️ `/myrelationships` - показати ваші стосунки\n"
        "💌 `/proposals` - показати активні пропозиції\n\n"
        "**Приклад використання:**\n"
        "`/kiss @username` або `/вдарив @username. зі словами`"
    )

    await update.message.reply_text(commands_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробляє натискання кнопок"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔙 Назад до меню", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.data == 'instructions':
        instructions_text = (
            "📖 **Інструкція по використанню бота:**\n\n"
            "**Формат команди дій:**\n"
            "`/дія @імя, додаткові слова` - звичайна дія\n\n"
            "**Команди для стосунків:**\n"
            "💋 `/kiss @партнер` - поцілувати (+2 очки)\n"
            "🤗 `/hug @партнер` - обійняти (+1 очко)\n"
            "❤️ `/love @партнер` - кохати (+3 очки)\n"
            "🌹 `/date @партнер` - піти на побачення (+3 очки)\n"
            "😏 `/flirt @партнер` - фліртувати (+1 очко)\n"
            "🎁 `/gift @партнер` - подарувати подарунок (+2 очки)\n"
            "💃 `/dance @партнер` - танцювати (+2 очки)\n\n"
            "**Особливі команди:**\n"
            "💒 `/marry @партнер` - одружитися (потрібен 5 рівень)\n"
            "💔 `/divorce @партнер` - розлучитися\n"
            "😢 `/breakup @партнер` - розстатися\n\n"
            "**Рівні стосунків:**\n"
            "👋 Знайомство (0 дій)\n"
            "😊 Симпатія (5 дій)\n"
            "😍 Закоханість (15 дій)\n"
            "💕 Кохання (30 дій)\n"
            "💖 Глибоке кохання (50 дій)\n"
            "💍 Готовність до шлюбу (75 дій)"
        )
        await query.edit_message_text(instructions_text, reply_markup=reply_markup, parse_mode='Markdown')

    elif query.data == 'examples':
        examples_text = (
            "💡 **Приклади використання:**\n\n"
            "**Прості дії:**\n"
            "• `/поцілував @Олена` → ✨ ♦**Тарас**♦ поцілував ♥**Олену**♥\n"
            "• `/вдарив @Андрій, сильно` → ✨ ♠**Тарас**♠ вдарив ♣**Андрія**♣ зі словами сильно\n\n"
            "**Команди для стосунків:**\n"
            "• `/kiss @Марія` → 💋 створює/покращує стосунки\n"
            "• `/date @Олена` → 🌹 піти на романтичне побачення\n"
            "• `/marry @Анна` → 💒 одружитися (якщо 5 рівень)\n"
            "• `/divorce @Анна` → 💔 розлучитися\n\n"
            "**Інші команди:**\n"
            "• `/flipcoin` → 🪙 Орел або Решка\n"
            "• `/relationships` → 💕 список всіх пар\n"
            "• `/myrelationships` → ❤️ ваші стосунки з рівнями"
        )
        await query.edit_message_text(examples_text, reply_markup=reply_markup, parse_mode='Markdown')

    elif query.data == 'contact':
        contact_text = (
            "📞 **Контакти та підтримка:**\n\n"
            "👨‍💻 Розробник: @shadow\\_tar\n"
            "💬 Для питань та пропозицій звертайтесь до розробника\n\n"
            "🐛 Знайшли помилку? Повідомте нам!\n"
            "💡 Є ідеї для покращення? Ми слухаємо!"
        )
        await query.edit_message_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown')

    elif query.data == 'about':
        about_text = (
            "ℹ️ **Про бота:**\n\n"
            "🎭 Бот для створення веселих дій та управління прогресивними стосунками\n"
            "💕 Система рівнів стосунків з прогресією\n"
            "💒 Можливість одруження та розлучення\n"
            "🎯 Призначений для розваг у групових чатах\n"
            "⚡ Швидко обробляє команди\n"
            "🎨 Красиво форматує результат\n\n"
            "**Версія:** 3.0\n"
            "**Створено:** 2024"
        )
        await query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')

    elif query.data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("📖 Інструкція", callback_data='instructions')],
            [InlineKeyboardButton("📞 Зв'язок", callback_data='contact')],
            [InlineKeyboardButton("ℹ️ Про бота", callback_data='about')],
            [InlineKeyboardButton("💡 Приклади", callback_data='examples')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = (
            "🎭 Привіт! Я бот для створення веселих дій та управління стосунками!\n\n"
            "💕 **Нова система рівнів стосунків:**\n"
            "👋 Знайомство → 😊 Симпатія → 😍 Закоханість → 💕 Кохання → 💖 Глибоке кохання → 💍 Готовність до шлюбу\n\n"
            "**Команди:**\n"
            "`/дія @користувач, додатковий текст`\n"
            "`/kiss @партнер` - поцілувати (+2 очки)\n"
            "`/marry @партнер` - одружитися (потрібен 5 рівень)\n"
            "`/divorce @партнер` - розлучитися\n"
            "`/breakup @партнер` - розстатися\n\n"
            "Вибери опцію з меню нижче! 👇"
        )
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

def find_user_partner(user_name, relationships):
    """Знаходить партнера користувача в активних стосунках"""
    for couple_id, data in relationships.items():
        parts = couple_id.split('_')
        if len(parts) >= 2:
            partner1, partner2 = parts[0], parts[1]
            if partner1 == user_name:
                return partner2, data
            elif partner2 == user_name:
                return partner1, data
    return None, None

async def handle_couple_command(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str, target: str = None) -> None:
    """Обробляє команди для пар"""
    user_name = update.message.from_user.first_name
    bot_username = context.bot.username
    relationships = load_relationships()

    # Видаляємо повідомлення з командою
    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"Не вдалося видалити повідомлення: {e}")

    # Перевіряємо чи не намагаються виконати команду на боті
    if target and (target.lower() == bot_username.lower() if bot_username else False):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🤖 На мені не можна виконувати команди стосунків!",
            parse_mode='Markdown'
        )
        return

    # Якщо target не вказано, шукаємо існуючого партнера
    if target is None:
        partner, partner_data = find_user_partner(user_name, relationships)
        if partner is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 У вас немає партнера! Для створення нових стосунків згадайте користувача (наприклад: /kiss @username)",
                parse_mode='Markdown'
            )
            return
        target = partner

    # Створюємо унікальний ID для пари
    couple_id = '_'.join(sorted([user_name, target]))

    # Перевіряємо особливі команди
    if command == 'propose':
        if couple_id not in relationships:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Ви не у стосунках! Спочатку почніть стосунки командою /start.",
                parse_mode='Markdown'
            )
            return

        total_actions = relationships[couple_id].get('total_actions', 0)
        if total_actions < RELATIONSHIP_LEVELS[5]["required_actions"]:
            current_level = get_relationship_level(total_actions)
            needed = RELATIONSHIP_LEVELS[5]["required_actions"] - total_actions
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"💍 Для пропозиції потрібен 5 рівень стосунків!\n📊 Ваш рівень: {RELATIONSHIP_LEVELS[current_level]['emoji']} {RELATIONSHIP_LEVELS[current_level]['name']}\n⚡ Потрібно ще {needed} дій для пропозиції!",
                parse_mode='Markdown'
            )
            return

        relationships[couple_id]['proposal'] = {'from': user_name, 'to': target, 'status': 'pending'}
        save_relationships(relationships)

        user_link = create_user_link(user_name, is_sender=True)
        target_link = create_user_link(target, is_sender=False)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💍 {user_link} робить пропозицію {target_link}! 💕\n\n{target_link}, використайте /accept @{user_name} або /reject @{user_name}",
            parse_mode='Markdown'
        )
        return

    elif command == 'accept':
        if couple_id not in relationships or 'proposal' not in relationships[couple_id]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Немає пропозиції для прийняття!",
                parse_mode='Markdown'
            )
            return

        proposal = relationships[couple_id]['proposal']
        if proposal['to'] != user_name or proposal['status'] != 'pending':
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Ви не можете прийняти цю пропозицію!",
                parse_mode='Markdown'
            )
            return

        relationships[couple_id]['status'] = 'married'
        del relationships[couple_id]['proposal']
        save_relationships(relationships)

        user_link = create_user_link(user_name, is_sender=True)
        target_link = create_user_link(target, is_sender=False)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💒 Вітаємо! {target_link} та {user_link} тепер одружені! 🎉👰🤵💕",
            parse_mode='Markdown'
        )
        return

    elif command == 'reject':
        if couple_id not in relationships or 'proposal' not in relationships[couple_id]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Немає пропозиції для відхилення!",
                parse_mode='Markdown'
            )
            return

        proposal = relationships[couple_id]['proposal']
        if proposal['to'] != user_name or proposal['status'] != 'pending':
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Ви не можете відхилити цю пропозицію!",
                parse_mode='Markdown'
            )
            return

        del relationships[couple_id]['proposal']
        save_relationships(relationships)

        user_link = create_user_link(user_name, is_sender=True)
        target_link = create_user_link(target, is_sender=False)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💔 {user_link} відхилив(ла) пропозицію від {target_link}... 😢",
            parse_mode='Markdown'
        )
        return

    elif command == 'marry':
        if couple_id not in relationships:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Ви не у стосунках! Спочатку почніть стосунки командою /start.",
                parse_mode='Markdown'
            )
            return

        # Перевіряємо чи є прийнята пропозиція
        if relationships[couple_id].get('status') != 'married':
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💍 Спочатку зробіть пропозицію командою /propose та отримайте згоду!",
                parse_mode='Markdown'
            )
            return

        user_link = create_user_link(user_name, is_sender=True)
        target_link = create_user_link(target, is_sender=False)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💒 {user_link} та {target_link} вже одружені! 💕",
            parse_mode='Markdown'
        )
        return

    elif command == 'divorce':
        if couple_id not in relationships or relationships[couple_id].get('status') != 'married':
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Ви не одружені! Неможливо розлучитися.",
                parse_mode='Markdown'
            )
            return

        del relationships[couple_id]
        save_relationships(relationships)

        user_link = create_user_link(user_name, is_sender=True)
        target_link = create_user_link(target, is_sender=False)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💔 {user_link} та {target_link} розлучилися... 😢",
            parse_mode='Markdown'
        )
        return

    elif command == 'breakup':
        if couple_id not in relationships:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💔 Ви не у стосунках! Немає з ким розставатися.",
                parse_mode='Markdown'
            )
            return

        del relationships[couple_id]
        save_relationships(relationships)

        user_link = create_user_link(user_name, is_sender=True)
        target_link = create_user_link(target, is_sender=False)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"😢 {user_link} та {target_link} розсталися... 💔",
            parse_mode='Markdown'
        )
        return

    # Звичайні команди стосунків
    command_info = COUPLE_COMMANDS[command]
    action = command_info['action']
    points = command_info['points']
    emoji = command_info['emoji']

    # Додаємо або оновлюємо стосунки
    if couple_id not in relationships:
        relationships[couple_id] = {
            'start_date': datetime.now().isoformat(),
            'total_actions': 0,
            'actions': [],
            'status': 'dating'
        }

    # Перевіряємо та додаємо відсутні поля для старих записів
    if 'total_actions' not in relationships[couple_id]:
        relationships[couple_id]['total_actions'] = 0
    if 'actions' not in relationships[couple_id]:
        relationships[couple_id]['actions'] = []
    if 'status' not in relationships[couple_id]:
        relationships[couple_id]['status'] = 'dating'

    # Додаємо дію та очки
    relationships[couple_id]['total_actions'] += points
    relationships[couple_id]['actions'].append({
        'action': f"{user_name} {action} {target}",
        'date': datetime.now().isoformat(),
        'points': points
    })

    total_actions = relationships[couple_id]['total_actions']
    current_level = get_relationship_level(total_actions)
    level_info = RELATIONSHIP_LEVELS[current_level]

    save_relationships(relationships)

    # Перевіряємо чи це нові стосунки
    if total_actions == points:
        user_link = create_user_link(user_name, is_sender=True)
        target_link = create_user_link(target, is_sender=False)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"💕 Вітаємо! {user_link} та {target_link} тепер у стосунках! ❤️",
            parse_mode='Markdown'
        )

    # Виконуємо дію
    target_declined = decline_name(target)
    user_link = create_user_link(user_name, is_sender=True)
    target_link = create_user_link(target_declined, is_sender=False)

    response = f"{emoji} {user_link} {action} {target_link}"

    # Додаємо інформацію про рівень
    if points > 0:
        response += f"\n📊 Рівень стосунків: {level_info['emoji']} {level_info['name']} ({total_actions} дій)"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        parse_mode='Markdown'
    )

async def handle_action_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробляє звичайні команди дій"""
    message_text = update.message.text.strip()
    user_name = update.message.from_user.first_name
    bot_username = context.bot.username

    # Видаляємо повідомлення з командою
    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"Не вдалося видалити повідомлення: {e}")

    # Розбираємо команду: /дія @ім'я додаткові дії, зі словами текст
    # Приклад: /вдарив @Жирного після чого вдарив в печінку вдарив по хребту, я тебе люблю
    pattern = r'^/([^@\s]+)\s*@(\w+)(.*)$'
    match = re.match(pattern, message_text)

    if not match:
        return

    action = match.group(1).strip()
    target_username = match.group(2).strip()
    rest_text = match.group(3).strip() if match.group(3) else ""

    # Перевіряємо чи це не команда для пар
    if action in COUPLE_COMMANDS:
        return

    # Перевіряємо чи не намагаються виконати команду на боті
    if target_username.lower() == bot_username.lower() if bot_username else False:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🤖 На мені не можна виконувати дії!",
            parse_mode='Markdown'
        )
        return

    # Спробуємо знайти користувача за username для отримання user_id
    target_user_id = None
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        reply_user = update.message.reply_to_message.from_user
        if reply_user.username and reply_user.username.lower() == target_username.lower():
            target_user_id = reply_user.id
            target_display_name = reply_user.first_name or reply_user.username
        else:
            target_display_name = target_username
    else:
        # Якщо це username (англійські букви), використовуємо його
        if target_username.isascii():
            target_display_name = target_username
        else:
            target_display_name = target_username

    user_link = create_user_link(user_name, is_sender=True)
    target_declined = decline_name(target_display_name)
    target_link = create_user_link(target_declined, target_user_id, is_sender=False)

    # Розділяємо додаткові дії та слова по крапці (новий тригер)
    additional_actions = ""
    words = ""

    if rest_text:
        if '.' in rest_text:
            parts = rest_text.split('.', 1)
            additional_actions = parts[0].strip()
            words = parts[1].strip()
        else:
            additional_actions = rest_text

    # Формуємо відповідь
    response = f"✨ {user_link} {action} {target_link}"

    if additional_actions:
        response += f" {additional_actions}"

    if words:
        response += f" зі словами 💬**\"{words}\"**✨"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response,
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробляє всі повідомлення і шукає команди"""
    message_text = update.message.text

    if message_text.startswith('/'):
        # Витягуємо команду
        command_match = re.match(r'^/(\w+)', message_text)
        if command_match:
            command = command_match.group(1)

            # Перевіряємо чи це команда для пар
            if command in COUPLE_COMMANDS:
                # Шукаємо згаданого користувача
                target = None
                if '@' in message_text:
                    target_match = re.search(r'@(\w+)', message_text)
                    if target_match:
                        target = target_match.group(1)

                await handle_couple_command(update, context, command, target)
            else:
                # Звичайна дія
                await handle_action_command(update, context)

async def main() -> None:
    """Запускає бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Налаштування команд бота
    await setup_bot_commands(application)

    # Додаємо обробники команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("flipcoin", flipcoin_command))
    application.add_handler(CommandHandler("relationships", relationships_command))
    application.add_handler(CommandHandler("myrelationships", my_relationships_command))
    application.add_handler(CommandHandler("proposals", proposals_command))
    application.add_handler(CommandHandler("commands", commands_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Обробники для повідомлень
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.COMMAND, handle_message))

    print("🤖 Бот запущений у polling режимі з новою системою стосунків...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
