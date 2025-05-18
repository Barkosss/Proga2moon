import telebot
from telebot import types
from services.database import DataBase
db = DataBase()
from config import Config
from enums.BotState import BotState
from enums.StatusEnum import Status

bot = telebot.TeleBot(Config.TOKEN)


def register_command():
    from handlers import common, admin

    common.register_handlers(bot)
    admin.register_handlers(bot)

def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("Кнопка 1")
    btn2 = types.KeyboardButton("Кнопка 2")

    markup.row(btn1, btn2)


@bot.message_handler(commands=["start"])
def handle_start(message):
    user_first_name = message.from_user.first_name

    text = (
        f"👋 Привет, {user_first_name}!\n\n"
        "Добро пожаловать в бота мероприятия. Здесь ты можешь:\n"
        "• 📅 просматривать мастер-классы\n"
        "• 📝 регистрироваться на мероприятия\n"
        "• ❓ задавать вопросы\n"
        "• 💬 получать актуальную информацию\n\n"
        "Если ты организатор — нажми кнопку ниже, чтобы перейти в панель управления 👑"
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Мои мероприятия", "Часто задаваемые вопросы")
    markup.add("Связаться с организатором", "Я организатор")

    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Я организатор")
def handle_admin_entry(message):
    user_id = message.from_user.id
    res = db.get_user(user_id)

    if res.status != Status.OK or not res.value.admin_event_ids:
        bot.send_message(message.chat.id, "❌ У вас нет доступа администратора.")
        return

    bot.set_state(user_id, BotState.ADMIN, message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Мои мероприятия", "Вопросы от участников")
    markup.add("Стать обычным пользователем")

    bot.send_message(
        message.chat.id,
        "👑 Вы вошли в режим администратора.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: msg.text == "Стать обычным пользователем")
def handle_become_user(message):
    bot.set_state(message.from_user.id, BotState.USER, message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Мои мероприятия", "Часто задаваемые вопросы")
    markup.add("Связаться с организатором", "Я организатор")

    bot.send_message(
        message.chat.id,
        "🚪 Вы вернулись в обычный режим.",
        reply_markup=markup
    )


if __name__ == "__main__":
    register_command()
    print("Bot is init")
    bot.polling(none_stop=True)

