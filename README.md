# Proga2moon

UNIT.HACK 2025. Кейс приложение/бот от NAUMEN

---

## Getting a bot token

---

Before launching, you need to get a Telegram Bot Token:

1. Open Telegram and find [@BotFather](https://t.me/BotFather)

2. Use the "`/newbot`" command to create a new bot.

3. Specify the name of the bot (for example: `MyEventBot`)

4. Get a token like: `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi`

5. Save the received file to `config.py` in the root directory of the project

---

## Installation

--- 

1. Clone the repository:
    ```bash
    git clone https://github.com/Barkosss/Proga2moon.git
    ```

2. Installing Python:

   Make sure that you have Python 3.12 or higher installed. To do this, you can run the following command in the
   terminal:

   #### For Windows:
    1. Go to [Python download page](https://www.python.org/downloads/)
    2. Download and install the latest version of Python
    3. Important: When installing, do not forget to check the option **"Add Python to PATH"**

   #### Python on macOS and Linux:
   Python should already be pre-installed on these systems, but to upgrade or install the latest version, you can use
   the package manager:

   #### For macOS (via Homebrew):
    ```bash
    brew install python
    ```

   #### For Linux (Debian/Ubuntu):
    ```bash
    sudo apt update
    sudo apt install python3
    ```

3. Install the dependencies:
    ```bash
    poetry install
    ```

4. Start the bot:
   ```bash
   python3 main.py
   ```
   or use
   ```bash
   poetry run python3 main.py
   ```

---

## Project structure

---

```
Proga2moon/
    │
    ├── main.py                  # Главный файл для запуска бота
    ├── config.py                # Конфигурационные параметры (токен)
    ├── database/                # База данных
    │   ├── __init__.py
    │   ├── users.json           # База данных участников
    │   ├── events.json          # База данных ивентов
    │   └── workshops.json       # База данных мастер классов
    │
    ├── handlers/                # Обработчики сообщений и команд
    │   ├── __init__.py
    │   ├── admin.py             # Админ-функции (рассылки, управление событиями)
    │   └── common.py            # Общие команды (help, info, feedback)
    │
    ├── services/                # Дополнительные сервисы
    │   ├── __init__.py
    │   ├── notifications.py     # Система уведомлений
    │   ├── database.py          # Управление базой данных
    │   └── secutiry.py          # Система безопасности (Создание и чтение QR-код)
    │
    ├── utils/                   # Утилиты
    │   ├── decorators.py        # Декоратор для проверки прав доступа к командам
    │   └── validators.py        # Валидатор
    │
    └── pyproject.toml           # Зависимости
```