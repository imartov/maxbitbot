CREATE TABLE users (
            chat_id SERIAL NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            login VARCHAR(100) NOT NULL,
            PRIMARY KEY (chat_id),
            UNIQUE (login)
);

CREATE TABLE task (
            id SERIAL NOT NULL,
            chat_id INTEGER NOT NULL,
            name VARCHAR(256) NOT NULL,
            description TEXT NOT NULL,
            PRIMARY KEY (id)
            FOREIGN KEY(chat_id) REFERENCES users (chat_id) ON DELETE CASCADE
);

CREATE TABLE completedtask (
            id SERIAL NOT NULL,
            chat_id INTEGER NOT NULL,
            name VARCHAR(256) NOT NULL,
            description TEXT NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(chat_id) REFERENCES users (chat_id) ON DELETE CASCADE
);