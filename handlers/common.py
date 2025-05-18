from datetime import datetime
from telebot import TeleBot, types
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery

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

    # === FSM-регистрация (AWAIT_*) ===
    if state == BotState.AWAIT_FIRST_NAME:
        with bot.retrieve_data(user_id) as data:
            data['first_name'] = text
        bot.set_state(user_id, BotState.AWAIT_LAST_NAME, message.chat.id)
        return bot.send_message(message.chat.id, "Введите вашу *фамилию*:", parse_mode='Markdown')

    if state == BotState.AWAIT_LAST_NAME:
        with bot.retrieve_data(user_id) as data:
            data['last_name'] = text
        bot.set_state(user_id, BotState.AWAIT_PATRONYMIC, message.chat.id)
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(KeyboardButton("Пропустить"))
        return bot.send_message(
            message.chat.id,
            "Введите *отчество* (или «Пропустить»):",
            parse_mode='Markdown',
            reply_markup=kb
        )

    if state == BotState.AWAIT_PATRONYMIC:
        patronymic = None if text.lower() == "пропустить" else text
        with bot.retrieve_data(user_id) as data:
            data['patronymic'] = patronymic
        bot.set_state(user_id, BotState.AWAIT_BIRTH_DATE, message.chat.id)
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(KeyboardButton("Пропустить"))
        return bot.send_message(
            message.chat.id,
            "Введите дату рождения в формате *ГГГГ-ММ-ДД* (или «Пропустить»):",
            parse_mode='Markdown',
            reply_markup=kb
        )

    if state == BotState.AWAIT_BIRTH_DATE:
        if text.lower() == "пропустить":
            birth_date = None
        else:
            try:
                birth_date = datetime.fromisoformat(text).date()
            except ValueError:
                return bot.send_message(
                    message.chat.id,
                    "Неверный формат! Введите *ГГГГ-ММ-ДД*:",
                    parse_mode='Markdown'
                )

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
            return bot.send_message(message.chat.id, "Ошибка при сохранении, попробуйте позже.")

        # регистрация завершена — показываем главное меню
        bot.set_state(user_id, BotState.USER, message.chat.id)
        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        kb.add(
            KeyboardButton(Commands.CommonEnum.MY_SCHEDULE.value),
            KeyboardButton(Commands.CommonEnum.ALL_EVENTS.value),
            KeyboardButton(Commands.CommonEnum.FAQ.value),
            KeyboardButton(Commands.CommonEnum.MY_QR.value),
            KeyboardButton(Commands.CommonEnum.SELECT_EVENT.value)
        )
        return bot.send_message(
            message.chat.id,
            f"Спасибо, {fn}! Регистрация завершена.\nВыберите действие:",
            reply_markup=kb
        )

    if state == BotState.USER and text == Commands.CommonEnum.SELECT_EVENT.value:
        db = DataBase()
        evs_req = db.get_events()
        if evs_req.status != Status.OK or not evs_req.value:
            return bot.send_message(message.chat.id, "Событий нет.")

        kb = types.InlineKeyboardMarkup()
        for ev in evs_req.value:
            kb.add(types.InlineKeyboardButton(
                text=f"{ev['id']}: {ev['start']}–{ev['end']}",
                callback_data=f"select_event:{ev['id']}"
            ))
        return bot.send_message(message.chat.id, "Выберите мероприятие:", reply_markup=kb)

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


def register_callbacks(bot: TeleBot):
    @bot.callback_query_handler(func=lambda cq: cq.data and cq.data.startswith("select_event:"))
    def on_event_selected(cq: CallbackQuery):
        event_id = int(cq.data.split(":", 1)[1])
        db = DataBase()
        ws_req = db.get_workshops(event_id)
        if ws_req.status != Status.OK or not ws_req.value:
            bot.answer_callback_query(cq.id, "Нет воркшопов")
            return bot.send_message(cq.message.chat.id, "В этом событии нет воркшопов.")

        kb = types.InlineKeyboardMarkup()
        text = f"Workshops для Event {event_id}:"
        for ws in ws_req.value:
            text += f"\n\n• {ws['id']}: {ws['title']} ({ws['start']}–{ws['end']})"
            kb.add(types.InlineKeyboardButton(
                text=f"Зарегистрироваться на {ws['id']}",
                callback_data=f"reg_ws:{ws['id']}"
            ))
        bot.answer_callback_query(cq.id)
        bot.send_message(cq.message.chat.id, text, reply_markup=kb)

    @bot.callback_query_handler(func=lambda cq: cq.data and cq.data.startswith("reg_ws:"))
    def on_workshop_reg(cq: CallbackQuery):
        ws_id = int(cq.data.split(":", 1)[1])
        user_id = cq.from_user.id
        db = DataBase()
        req = db.get_workshops(ws_id)
        if req.status == Status.OK:
            req.value.add_registration(user_id)
