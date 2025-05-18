from enums.BotState import BotState
from enums.StatusEnum import Status
from utils.decorators import admin_only, admin_only_event_callback
from services.database import DataBase
db = DataBase()
from telebot import types
from models.Event import Event

def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "Мои мероприятия")
    @admin_only(event_id=100)
    def show_admin_events(message):
        """
        Обработчик команды "Мои мероприятия" для администраторов.

        Получает список мероприятий, на которые у пользователя есть права администратора,
        и отображает первую карточку с возможностью листания.

        Параметры:
            message (telebot.types.Message): сообщение Telegram от пользователя
        """
        print("Обработчик сработал!")

        user_id = message.from_user.id
        events = db.get_admin_events(user_id)  # ← вот тут вызывается

        if not events:
            bot.send_message(message.chat.id, "У вас пока нет мероприятий.")
            return

        with bot.retrieve_data(user_id, message.chat_id) as data:
            data["admin_event_index"] = 0

        show_event_card(message.chat.id, user_id, events)

    def show_event_card(chat_id, user_id, events: list[Event], message_id=None):
        """
        Отображает карточку мероприятия по текущему индексу для пользователя.

        Если указан `message_id`, сообщение редактируется. Иначе — создаётся новое.

        Аргументы:
            chat_id (int): ID чата, в который отправляется сообщение
            user_id (int): Telegram ID пользователя
            events (list[Event]): Список мероприятий, где пользователь админ
            message_id (Optional[int]): ID сообщения, если нужно отредактировать
        """

        with bot.retrieve_data(user_id, chat_id) as data:
            index = data.get('admin_event_index', 0)
            event = events[index]

        text = (
            f"<b>{event.title}</b>\n"
            f"Мастер-классов: {len(event.workshop_ids)}\n"
            f"Зарегистрировано: {len(event.registered_user_ids)}\n"
            f"Дата проведения: {event.start.date()} — {event.end.date()}"
        )

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("⬅️", callback_data="event_prev"),
            types.InlineKeyboardButton("➡️", callback_data="event_next")
        )
        markup.add(types.InlineKeyboardButton("✏️ Редактировать", callback_data="event_edit"))
        markup.add(types.InlineKeyboardButton("➕ Создать новое", callback_data="event_create"))

        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


        @bot.callback_query_handler(func=lambda call: call.data in ["event_prev", "event_next"])
        def paginate_events(call):
            """
            Обработчик нажатий на кнопки листания мероприятий (⬅️, ➡️).

            Изменяет текущий индекс мероприятия и перерисовывает карточку.

            Параметры:
                call (telebot.types.CallbackQuery): объект колбэка от Telegram
            """
            user_id = call.from_user.id
            chat_id = call.message.chat.id

            events = db.get_admin_events(user_id)
            total = len(events)

            if total == 0:
                bot.answer_callback_query(call.id, "Нет мероприятий.")
                return

            # Работа с состоянием
            with bot.retrieve_data(user_id, chat_id) as data:
                current = data.get("admin_event_index", 0)

                if call.data == "event_prev":
                    current = (current - 1) % total
                else:
                    current = (current + 1) % total

                data["admin_event_index"] = current

            # Обновляем сообщение
            show_event_card(
                chat_id=chat_id,
                user_id=user_id,
                events=events,
                message_id=call.message.message_id
            )

            bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("event_edit:"))
    @admin_only_event_callback
    def handle_event_edit(call, event_id):
        """
        Показывает подменю редактирования мероприятия.
        """
        bot.answer_callback_query(call.id)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🕒 Изменить дату", callback_data=f"event_edit_time:{event_id}"))
        markup.add(types.InlineKeyboardButton("🔗 Ссылка на чат", callback_data=f"event_edit_chat:{event_id}"))
        markup.add(types.InlineKeyboardButton("🧩 Мастер-классы", callback_data=f"event_edit_workshops:{event_id}"))
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="event_edit_back"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🔧 Вы редактируете мероприятие #{event_id}",
            reply_markup=markup
        )

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="event_edit_back"))

    @bot.callback_query_handler(func=lambda call: call.data.startswith("event_edit_time:"))
    @admin_only_event_callback
    def handle_edit_time(call, event_id):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Введите дату начала и окончания в формате:\n\n`дд.мм.гггг дд.мм.гггг`",
                         parse_mode="Markdown")
        bot.set_state(call.from_user.id, BotState.AWAIT_EVENT_TIME, call.message.chat.id)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data["event_id"] = event_id

    @bot.message_handler(state=BotState.AWAIT_EVENT_TIME)
    def receive_event_time(message):
        from datetime import datetime
        user_id = message.from_user.id
        chat_id = message.chat.id

        try:
            start_str, end_str = message.text.strip().split()
            start = datetime.strptime(start_str, "%d.%m.%Y")
            end = datetime.strptime(end_str, "%d.%m.%Y")
        except:
            bot.send_message(chat_id, "❌ Неверный формат. Попробуйте снова.")
            return

        with bot.retrieve_data(user_id, chat_id) as data:
            event_id = data["event_id"]

        res = db.get_event(event_id)
        if res.status != Status.OK:
            bot.send_message(chat_id, "❌ Ошибка загрузки мероприятия.")
            return

        event = Event.from_dict(res.value)
        event.start = start
        event.end = end

        db.update_event(event)  # ты должен реализовать update_event в DataBase

        bot.send_message(chat_id, "✅ Даты обновлены!")
        bot.delete_state(user_id, chat_id)

    @bot.message_handler(state=BotState.AWAIT_EVENT_TIME)
    def receive_event_time(message):
        from datetime import datetime
        user_id = message.from_user.id
        chat_id = message.chat.id

        try:
            start_str, end_str = message.text.strip().split()
            start = datetime.strptime(start_str, "%d.%m.%Y")
            end = datetime.strptime(end_str, "%d.%m.%Y")
        except:
            bot.send_message(chat_id, "❌ Неверный формат. Попробуйте снова.")
            return

        with bot.retrieve_data(user_id, chat_id) as data:
            event_id = data["event_id"]

        res = db.get_event(event_id)
        if res.status != Status.OK:
            bot.send_message(chat_id, "❌ Ошибка загрузки мероприятия.")
            return

        event = Event.from_dict(res.value)
        event.start = start
        event.end = end

        db.update_event(event)  # ты должен реализовать update_event в DataBase

        bot.send_message(chat_id, "✅ Даты обновлены!")
        bot.delete_state(user_id, chat_id)

    @bot.callback_query_handler(func=lambda call: call.data == "event_edit_back")
    def handle_back_to_event(call):
        user_id = call.from_user.id
        events = db.get_admin_events(user_id)
        with bot.retrieve_data(user_id, call.message.chat.id) as data:
            index = data.get("admin_event_index", 0)

        show_event_card(call.message.chat.id, user_id, events, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "event_create")
    def handle_event_create(call):
        user_id = call.from_user.id
        bot.send_message(call.message.chat.id, "Введите название нового мероприятия:")
        bot.set_state(user_id, BotState.AWAIT_NAME, call.message.chat.id)
