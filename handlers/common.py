from datetime import datetime
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton

from enums.CommandsEnum import Commands
from enums.BotState import BotState
from enums.StatusEnum import Status
from services.database import DataBase
from models.User import User

import qrcode
from io import BytesIO

def common_handler(bot: TeleBot, message: Message, state):
    text = message.text.strip()
    user_id = message.from_user.id

    if state == BotState.AWAIT_FIRST_NAME:
        with bot.retrieve_data(user_id) as data:
            data['first_name'] = text
        bot.set_state(user_id, BotState.AWAIT_LAST_NAME, message.chat.id)
        bot.send_message(message.chat.id, "Введите вашу *фамилию*:", parse_mode='Markdown')
        return

    if state == BotState.AWAIT_LAST_NAME:
        with bot.retrieve_data(user_id) as data:
            data['last_name'] = text
        bot.set_state(user_id, BotState.AWAIT_PATRONYMIC, message.chat.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("Пропустить"))
        bot.send_message(
            message.chat.id,
            "Введите *отчество* (или «Пропустить»):",
            parse_mode='Markdown',
            reply_markup=markup
        )
        return

    if state == BotState.AWAIT_PATRONYMIC:
        patronymic = None if text.lower() == "пропустить" else text
        with bot.retrieve_data(user_id) as data:
            data['patronymic'] = patronymic
        bot.set_state(user_id, BotState.AWAIT_BIRTH_DATE, message.chat.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("Пропустить"))
        bot.send_message(
            message.chat.id,
            "Введите дату рождения в формате *ГГГГ-ММ-ДД* (или «Пропустить»):",
            parse_mode='Markdown',
            reply_markup=markup
        )
        return

    if state == BotState.AWAIT_BIRTH_DATE:
        if text.lower() == "пропустить":
            birth_date = None
        else:
            try:
                birth_date = datetime.fromisoformat(text).date()
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    "Неверный формат! Введите *ГГГГ-ММ-ДД*:",
                    parse_mode='Markdown'
                )
                return

        with bot.retrieve_data(user_id) as data:
            fn = data['first_name']
            ln = data['last_name']
            patr = data.get('patronymic')

        db = DataBase()
        new_user = User(
            id=user_id,
            first_name=fn,
            last_name=ln,
            patronymic=patr,
            birth_date=birth_date
        )
        res = db.add_user(new_user)
        if res.status != Status.OK:
            bot.send_message(message.chat.id, "Ошибка при сохранении, попробуйте позже.")
            return

        bot.set_state(user_id, BotState.USER, message.chat.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(
            KeyboardButton(Commands.CommonEnum.MY_SCHEDULE.value),
            KeyboardButton(Commands.CommonEnum.ALL_EVENTS.value),
            KeyboardButton(Commands.CommonEnum.FAQ.value),
            KeyboardButton(Commands.CommonEnum.MY_QR.value),
        )
        bot.send_message(
            message.chat.id,
            f"Спасибо, {fn}! Регистрация завершена.\nВыберите действие:",
            reply_markup=markup
        )
        return

    try:
        command = Commands.CommonEnum(text)
    except ValueError:
        return bot.reply_to(message, "Неправильный ввод!")

    with bot.retrieve_data(user_id) as data:
        data['is_admin'] = False

    db = DataBase()

    if command == Commands.CommonEnum.MY_SCHEDULE:
        user_id = message.from_user.id
        user_req = db.get_user(user_id)
        if user_req.status != Status.OK:
            new_user = User(
                id=user_id,
                first_name=message.from_user.first_name or "",
                last_name=message.from_user.last_name or ""
            )
            add_req = db.add_user(new_user)
            if add_req.status != Status.OK:
                bot.send_message(message.chat.id, "Ошибка при добавлении пользователя.")
                return
            user = new_user
        else:
            user = user_req.value

        if not user.registered_event_ids:
            bot.send_message(message.chat.id, "У вас нет зарегистрированных мероприятий.")
        else:
            resp = "Ваше расписание:"
            for event_id in user.registered_event_ids:
                ev_req = db.get_event(event_id)
                if ev_req.status == Status.OK:
                    ev = ev_req.value
                    resp += f"\n- Мероприятие {ev['id']} с {ev['start']} по {ev['end']}"
                else:
                    resp += f"\n- Мероприятие {event_id} (не найдено)"
            bot.send_message(message.chat.id, resp)

    elif command == Commands.CommonEnum.ALL_EVENTS:
        ev_req = db.get_events()
        if ev_req.status == Status.OK:
            events = ev_req.value
            resp = "Все мероприятия:"
            for ev in events:
                resp += f"\n- ID: {ev['id']}, начало: {ev['start']}, конец: {ev['end']}"
            bot.send_message(message.chat.id, resp)
        else:
            bot.send_message(message.chat.id, "Ошибка при получении мероприятий.")

    elif command == Commands.CommonEnum.FAQ:
        faqs = [
            ("Как зарегистрироваться?", "Нажмите кнопку 'Зарегистрироваться' рядом с мероприятием."),
            ("Как отменить регистрацию?", "Нажмите 'Отменить регистрацию' в вашем расписании."),
        ]
        resp = "FAQ:"
        for q, a in faqs:
            resp += f"\n\n*{q}*\n{a}"
        bot.send_message(message.chat.id, resp, parse_mode='Markdown')

    elif command == Commands.CommonEnum.MY_QR:
        from services.security import Security
        user_id = message.from_user.id
        req = Security.create_qr(user_id)

        bot.send_photo(message.chat.id, photo=req.value)

    else:
        return
