import uuid
from datetime import datetime
from services.questionDB import QuestionDB

from pyexpat.errors import messages
from telebot.types import Message

from enums.BotState import BotState
from enums.StatusEnum import Status
from models.Question import Question
from utils.decorators import admin_only, admin_only_event_callback
from services.database import DataBase
db = DataBase()
from telebot import types
from models.Event import Event

def register_handlers(bot):
    @bot.message_handler(func=lambda msg: msg.text == "Мои мероприятия")
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
        print("Обработчик сработал!")
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

    @bot.callback_query_handler(func=lambda call: call.data == "event_create")
    def handle_event_create(call):
        user_id = call.from_user.id
        bot.set_state(user_id, BotState.AWAIT_EVENT_TITLE, call.message.chat.id)
        bot.send_message(call.message.chat.id, "Введите название мероприятия:")

        with bot.retrieve_data(user_id, call.message.chat.id) as data:
            data["event_data"] = {}

    @bot.message_handler(state=BotState.AWAIT_EVENT_TITLE)
    def receive_event_title(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["event_data"]["title"] = message.text

        bot.set_state(message.from_user.id, BotState.AWAIT_EVENT_DESC, message.chat.id)
        bot.send_message(message.chat.id, "Введите описание мероприятия:")

    @bot.message_handler(state=BotState.AWAIT_EVENT_DESC)
    def receive_event_desc(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["event_data"]["description"] = message.text

        bot.set_state(message.from_user.id, BotState.AWAIT_EVENT_START, message.chat.id)
        bot.send_message(message.chat.id, "Введите дату начала (ДД.ММ.ГГГГ):")

    @bot.message_handler(state=BotState.AWAIT_EVENT_START)
    def receive_start_date(message):
        try:
            start = datetime.strptime(message.text, "%d.%m.%Y")
        except:
            bot.send_message(message.chat.id, "❌ Неверный формат. Повторите.")
            return

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["event_data"]["start"] = start.isoformat()

        bot.set_state(message.from_user.id, BotState.AWAIT_EVENT_END, message.chat.id)
        bot.send_message(message.chat.id, "Введите дату окончания (ДД.ММ.ГГГГ):")

    @bot.message_handler(state=BotState.AWAIT_EVENT_END)
    def receive_end_date(message):
        try:
            end = datetime.strptime(message.text, "%d.%m.%Y")
        except:
            bot.send_message(message.chat.id, "❌ Неверный формат. Повторите.")
            return

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["event_data"]["end"] = end.isoformat()

        bot.set_state(message.from_user.id, BotState.AWAIT_EVENT_LOCATION, message.chat.id)
        bot.send_message(message.chat.id, "Введите место проведения:")

    @bot.message_handler(state=BotState.AWAIT_EVENT_LOCATION)
    def receive_location(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["event_data"]["location"] = message.text

        bot.set_state(message.from_user.id, BotState.AWAIT_EVENT_CHAT, message.chat.id)
        bot.send_message(message.chat.id, "Введите ссылку на чат (или - если не нужно):")

    @bot.message_handler(state=BotState.AWAIT_EVENT_CHAT)
    def receive_chat(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["event_data"]["chat_link"] = message.text if message.text != "-" else ""

            # Теперь можно создать Event-объект
            event_id = generate_event_id()  # реализуй как хочешь (UUID или счётчик)
            event = Event(
                id=event_id,
                start=datetime.fromisoformat(data["event_data"]["start"]),
                end=datetime.fromisoformat(data["event_data"]["end"]),
                workshop_ids=[],
                admin_ids=[message.from_user.id],
                chat_link=data["event_data"]["chat_link"]
            )
            db.add_event(event, [])  # без воркшопов пока

        bot.send_message(message.chat.id, "✅ Мероприятие создано!")
        bot.delete_state(message.from_user.id, message.chat.id)

    def generate_event_id() -> str:
        return str(uuid.uuid4())

    @bot.message_handler(func=lambda msg: msg.text == "Вопросы от участников")
    def handle_question_list(message):
        user_id = message.from_user.id
        res = db.get_user(user_id)

        if res.status != Status.OK or not res.value.admin_event_ids:
            bot.send_message(message.chat.id, "❌ У вас нет доступа к вопросам.")
            return

        event_id = res.value.admin_event_ids[0]  # пока берём первый (или выбираем активный)
        questions = db.get_questions(event_id)

        if not questions:
            bot.send_message(message.chat.id, "Нет новых вопросов.")
            return

        with bot.retrieve_data(user_id, message.chat.id) as data:
            data["question_index"] = 0
            data["questions"] = [q.to_dict() for q in questions]
            data["event_id"] = event_id

        show_question(message.chat.id, user_id, questions, index=0)

    def show_question(chat_id, user_id, questions, index):
        q = questions[index]
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Ответить", callback_data=f"admin_answer:{q['id']}"),
            types.InlineKeyboardButton("Далее ➡️", callback_data="admin_next_question")
        )

        text = (
            f"<b>Вопрос {index + 1} из {len(questions)}</b>\n\n"
            f"📍 Мероприятие: ПИК-АЙТИ\n"
            f"❓ <i>{q['text']}</i>"
        )

        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call: call.data == "admin_next_question")
    def handle_next_question(call):
        user_id = call.from_user.id
        with bot.retrieve_data(user_id, call.message.chat.id) as data:
            index = data.get("question_index", 0)
            questions = data.get("questions", [])

            if index + 1 >= len(questions):
                bot.answer_callback_query(call.id, "Больше вопросов нет.")
                return

            index += 1
            data["question_index"] = index

        bot.answer_callback_query(call.id)
        show_question(call.message.chat.id, user_id, questions, index)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin_answer:"))
    def ask_for_answer(call):
        question_id = call.data.split(":")[1]

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data["answering_question_id"] = question_id

        bot.set_state(call.from_user.id, BotState.AWAIT_ADMIN_ANSWER, call.message.chat.id)
        bot.send_message(call.message.chat.id, "✍️ Напишите ответ на вопрос:")

    @bot.message_handler(state=BotState.AWAIT_ADMIN_ANSWER)
    def receive_answer_text(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["answer_text"] = message.text

        bot.set_state(message.from_user.id, BotState.AWAIT_ADMIN_CONFIRMATION, message.chat.id)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Отправить", callback_data="admin_send_answer"))
        markup.add(types.InlineKeyboardButton("✏️ Изменить", callback_data="admin_edit_answer"))

        bot.send_message(message.chat.id, f"Вы ответили:\n\n<i>{message.text}</i>", parse_mode="HTML",
                         reply_markup=markup)

    @bot.message_handler(state=BotState.AWAIT_ADMIN_ANSWER)
    def receive_answer_text(message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["answer_text"] = message.text

        bot.set_state(message.from_user.id, BotState.AWAIT_ADMIN_CONFIRMATION, message.chat.id)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Отправить", callback_data="admin_send_answer"))
        markup.add(types.InlineKeyboardButton("✏️ Изменить", callback_data="admin_edit_answer"))

        bot.send_message(message.chat.id, f"Вы ответили:\n\n<i>{message.text}</i>", parse_mode="HTML",
                         reply_markup=markup)

    @bot.message_handler(func=lambda msg: msg.text == "Часто задаваемые вопросы")
    def show_faq(message):
        faq_text = (
            "📌 <b>FAQ</b>\n\n"
            "• Как записаться на мастер-класс?\n"
            "Ответ: Нажмите 'Записаться' в карточке воркшопа.\n\n"
            "• Можно ли отменить регистрацию?\n"
            "Ответ: Да, через кнопку 'Отменить регистрацию'.\n\n"
            "• Где найти расписание?\n"
            "Ответ: В разделе 'Моё расписание'."
        )
        bot.send_message(message.chat.id, faq_text, parse_mode="HTML")

    from uuid import uuid4
    from datetime import datetime

    @bot.message_handler(func=lambda msg: msg.text == "Связаться с организатором")
    def ask_question_text(message):
        bot.set_state(message.from_user.id, BotState.AWAIT_NAME, message.chat.id)
        bot.send_message(message.chat.id, "✍️ Напиши свой вопрос организатору:")

    @bot.message_handler(state=BotState.AWAIT_NAME)
    def receive_question(message):
        user_id = message.from_user.id
        user = db.get_user(user_id).value
        event_id = user.registered_event_ids[0] if user.registered_event_ids else None

        if not event_id:
            bot.send_message(message.chat.id, "❌ Вы не зарегистрированы ни на одно мероприятие.")
            return

        question = Question(
            id=str(uuid4()),
            event_id=event_id,
            user_id=user_id,
            text=message.text,
            created_at=datetime.now()
        )

        db_questions.add_question(question)
        bot.send_message(message.chat.id, "✅ Ваш вопрос передан организаторам. Спасибо!")
        bot.delete_state(user_id, message.chat.id)
