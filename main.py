# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import telebot
from telebot import types

from config import Config
from services.database import DataBase, FileData
from models.User import User
from enums.StatusEnum import Status

bot = telebot.TeleBot(Config.TOKEN)

# Создаем экземпляр базы данных
db = DataBase()


def register_command():
    from handlers import common, admin

    common.register_handlers(bot)
    #admin.register_handlers(bot)


@bot.message_handler(commands=['start'])
def start(message):
    # Проверяем, есть ли пользователь в базе данных
    user_exists = db.has_user(message.from_user.id)

    if not user_exists:
        # Если пользователя нет, добавляем его
        new_user = User(
            id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        db.add_user(new_user)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    btn1 = types.KeyboardButton("Мой расписание")
    btn2 = types.KeyboardButton("Все мероприятия")
    btn3 = types.KeyboardButton("FQA")
    btn4 = types.KeyboardButton("Мой QR")

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=markup)


# --- Слайдер мероприятий ---
from services.database import DataBase, FileData
from models.Workshop import Workshop

# Состояние слайдера для каждого пользователя (user_id: {index, message_id})
user_slider_state = {}


def get_workshops_list():
    db = DataBase()
    db._read_data(FileData.WORKSHOPS)
    workshops = []
    for w in db.data.values():
        workshops.append(Workshop.from_dict(w))
    return workshops


def send_workshop_slider(chat_id, user_id, workshops, idx, message_id=None):
    workshop = workshops[idx]
    text = f"<b>{workshop.title}</b>\n\n{workshop.description}\n\nДата: {workshop.start.strftime('%d.%m.%Y %H:%M')} — {workshop.end.strftime('%d.%m.%Y %H:%M')}"
    db = DataBase()
    db._read_data(FileData.WORKSHOPS)
    is_registered = str(user_id) in workshop.waiting_user_ids
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_prev = types.InlineKeyboardButton("⬅️ Предыдущее", callback_data="workshop_prev")
    btn_next = types.InlineKeyboardButton("Следующее ➡️", callback_data="workshop_next")
    if is_registered:
        btn_reg = types.InlineKeyboardButton("❌ Отменить регистрацию", callback_data="workshop_unregister")
        btn_exit = types.InlineKeyboardButton("↖️ Выйти в главное меню", callback_data="workshop_exit")
        markup.add(btn_prev, btn_next)
        markup.add(btn_reg)
        markup.add(btn_exit)
    else:
        btn_reg = types.InlineKeyboardButton("Зарегистрироваться", callback_data="workshop_register")
        markup.add(btn_prev, btn_next)
        markup.add(btn_reg)
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='HTML')
        except Exception:
            msg = bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')
            user_slider_state[user_id] = {'idx': idx, 'message_id': msg.message_id}
            return
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')
        user_slider_state[user_id] = {'idx': idx, 'message_id': msg.message_id}
        return
    user_slider_state[user_id]['idx'] = idx


@bot.message_handler(func=lambda message: message.text == "Все мероприятия")
def handle_all_workshops(message):
    workshops = get_workshops_list()
    if not workshops:
        bot.send_message(message.chat.id, "Нет доступных мероприятий.")
        return
    send_workshop_slider(message.chat.id, message.from_user.id, workshops, 0)


@bot.callback_query_handler(func=lambda call: call.data.startswith("workshop_"))
def handle_workshop_slider(call):
    user_id = call.from_user.id
    workshops = get_workshops_list()
    state = user_slider_state.get(user_id, {'idx': 0, 'message_id': call.message.message_id})
    idx = state.get('idx', 0)
    message_id = state.get('message_id', call.message.message_id)
    if call.data == "workshop_next":
        idx = (idx + 1) % len(workshops)
        send_workshop_slider(call.message.chat.id, user_id, workshops, idx, message_id)
    elif call.data == "workshop_prev":
        idx = (idx - 1) % len(workshops)
        send_workshop_slider(call.message.chat.id, user_id, workshops, idx, message_id)
    elif call.data == "workshop_register":
        db = DataBase()
        db._read_data(FileData.WORKSHOPS)
        workshop = workshops[idx]
        if str(user_id) not in workshop.waiting_user_ids:
            workshop.waiting_user_ids.append(str(user_id))
            db.data[str(workshop.id)] = workshop.to_dict()
            db._write_data(FileData.WORKSHOPS)
        send_workshop_slider(call.message.chat.id, user_id, workshops, idx, message_id)
    elif call.data == "workshop_unregister":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Да", callback_data="workshop_confirm_unreg"),
            types.InlineKeyboardButton("Нет", callback_data="workshop_cancel_unreg")
        )
        bot.send_message(call.message.chat.id, "Точно отменить регистрацию?", reply_markup=markup)
    elif call.data == "workshop_exit":
        user_slider_state.pop(user_id, None)
        bot.send_message(call.message.chat.id, "Вы вышли из режима просмотра мероприятий.")
    elif call.data == "workshop_confirm_unreg":
        db = DataBase()
        db._read_data(FileData.WORKSHOPS)
        workshop = workshops[idx]
        if str(user_id) in workshop.waiting_user_ids:
            workshop.waiting_user_ids.remove(str(user_id))
            db.data[str(workshop.id)] = workshop.to_dict()
            db._write_data(FileData.WORKSHOPS)
        bot.send_message(call.message.chat.id, "Регистрация отменена.")
        send_workshop_slider(call.message.chat.id, user_id, workshops, idx, message_id)
    elif call.data == "workshop_cancel_unreg":
        send_workshop_slider(call.message.chat.id, user_id, workshops, idx, message_id)


if __name__ == "__main__":
    register_command()
    print("Бот запущен")
    bot.polling(none_stop=True)
