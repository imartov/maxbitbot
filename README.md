# Telegram Task Manager Bot

## Overview

The Telegram Task Manager Bot is a Python-based bot that helps users manage their tasks efficiently on the Telegram platform. Users can register, add tasks, modify them, mark them as complete, and delete them.

## Features

- **User Registration**: Users can register with the bot to create their accounts.
- **Task Management**: Users can add tasks, view their tasks, modify task details, mark tasks as complete, and delete tasks.
- **Finite State Machine (FSM)**: The bot uses FSM to guide users through different steps of task management, providing a smooth and intuitive user experience.
- **Cancellation and Navigation**: Users can cancel ongoing actions or navigate back to the previous step using dedicated commands.
- **Error Handling**: The bot handles errors gracefully and provides informative messages to users in case of invalid input or unexpected issues.

## Dependencies

- **Python 3**: The bot is written in Python 3.
- **aiogram**: A powerful asynchronous library for building Telegram bots.
- **SQLAlchemy**: For interacting with the PostgreSQL database.
- **asyncpg**: An asynchronous PostgreSQL database driver for Python.
- **PostgreSQL**: A relational database used to store user data and task information.

## Project Structure
```bash
telegram-task-manager-bot/
├── common/
│   └── bot_cmds_list.py          
├── database/
│   ├── sql_query/
│   │   └── create_tables.sql
│   ├── conn.py
│   ├── models.py
│   └── sql_query.py
├── handlers/
│   ├── fsm.py
│   └── private.py
├── kbrds/
│   ├── inline.py
│   └── reply.py
├── messages/
│   ├── choose_login.txt
│   ├── no_register.txt
│   ├── prev_step.txt
│   └── success_register.txt.py
├── .dockerignore
├── .env
├── .gitignore
├── app.py
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Setup

1. **Clone the Repository**: Clone this repository to your local machine.
   ```bash
   git clone https://github.com/imartov/maxbitbot.git
   ```
2. **Install Dependencies**: Install the required Python dependencies using pip.
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up Configuration**: Create a `.env` file and specify the required environment variables such as Telegram bot token, database connection details, etc.
   ```plaintext
   TG_ROKEN=<your-telegram-bot-token>
   DB_USER=<your-postgres-username>
   DB_PASSWORD=<your-postgres-password>
   DB_HOST=<your-postgres-host>
   DB_PORT=<your-postgres-port>
   DB_NAME=<your-postgres-db-name>
   ```

## Usage

1. **Start the Bot**: Run the bot application using the following command.
   ```bash
   python app.py
   ```
2. **Interacting with the Bot**: Users can interact with the bot by sending commands and following the bot's prompts for task management.

## Architectural description
This section contains an architectural description of the solution, including a diagram of components and interactions.

### Entities
- **User**. It contains the following properties:  
    - ***chat_id*** - the user's ID in the telegram
    - ***user_name*** - the user name entered
    - ***login*** - a unique logic selected by the user

- **Task**. It contains the following properties:  
    - ***id*** - unique task ID
    - ***chat_id*** - the user's ID in the telegram related to ***User.chat_id***
    - ***name*** - a short task name
    - ***description*** - a longer description of the task

- **Completedtask**. It contains the following properties:  
    - ***id*** - unique task ID
    - ***chat_id*** - the user's ID in the telegram related to ***User.chat_id***
    - ***name*** - a short task name
    - ***description*** - a longer description of the task

### Diagram of components and interactions
![alt text](comp_dia.jpg)

## Description of the main classes and functions, their purpose and interaction

The main classes and functions:

### app.main
| Purpose | Interaction |
|:---:|:---:|
| The method contains methods that are called when the bot is launched | dp - `aiogram.Dispatcher()` and bot - `aiogram.Bot()` |

### kbrds.reply.main_kb
| Purpose | Interaction |
|:---:|:---:|
| The variable that forms the main navigation menu | `aiogram.types.ReplyKeyboardMarkup()` and `aiogram.types.KeyboardButton()` |

### kbrds.inline.get_callback_btns
| Purpose | Interaction |
|:---:|:---:|
| The method dynamically generates an inline menu сallback_data is used as an additional mandatory argument | `aiogram.utils.keyboard.InlineKeyboardBuilder()` and `aiogram.types.KeyboardButton()` |

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-new-feature`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-new-feature`).
5. Create a new pull request.

## License

The MIT License (MIT)
Copyright (c) 2024 Alexandr Kozyrev, https://github.com/imartov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

## Contact

For any inquiries or issues, please contact:  
alexandr.kosyrew@mail.ru  
[Telegram](https://t.me.alr_ks)