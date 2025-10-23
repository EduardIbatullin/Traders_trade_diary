
# **Техническое задание (ТЗ) по проекту: Онлайн-дневник сделок на Московской бирже (Сбер)**

*Версия: август 2025*

---

## **1. Общая концепция и назначение**

Веб-приложение для личного учёта, анализа и ведения **дневника сделок** на Московской бирже (Сбербанк).
Ключевая особенность — дневниковый подход: пользователь не просто фиксирует операции, а анализирует, делает пометки, строит план работы с позицией и возвращается к собственным записям для самоанализа.

---

## **2. Целевые сценарии и ключевые функции**

### **2.1. Импорт сделок**

* Импорт HTML-отчётов брокера Сбер (поддержка суточных и месячных; структура одинакова).
* Парсер реализован единым модулем.
* Предпросмотр импортированных сделок с возможностью исключения отдельных записей.
* Возможность сохранять оригинал файла отчёта (архитектурно поддерживается, реализуется по необходимости).

### **2.2. Ручной ввод сделок**

* Возможность ручного ввода сделки с подробной дневниковой информацией:

  * Причина покупки (идея, цель)
  * Уровни/триггеры для следующих покупок (по методике "Лесенка", стратегия САИ)
  * План ступенчатых продаж (цели, % от позиции, целевая цена)
  * Планируемый размер позиции в % от портфеля
* Возможность редактирования заметок после сохранения.

### **2.3. Сравнение при импорте**

* При импорте отчёта за даты, по которым уже есть сделки, работает механизм поиска “похожих” операций:

  * Сравнение по инструменту, типу операции, количеству и **времени с допустимым интервалом (±12/24 ч, настраиваемо)**
  * Все найденные совпадения показываются пользователю для ручного разрешения конфликта (сравнение полей, выбор источника, возможность частичного объединения)
  * Все операции проходят через “черновик импорта” — только после подтверждения пользователя записи вносятся в основную БД

### **2.4. Управление сделками и позициями**

* Сделки по одной бумаге объединяются в **позицию**.
* Главный экран — список текущих позиций/активов.
* Фильтры: дата, инструмент, тип операции (с расширяемостью набора фильтров).

### **2.5. Дневниковые заметки и методика "Лесенка"**

* Каждая сделка и каждая позиция может содержать:

  * Личную заметку (текст)
  * Причину покупки/продажи, целевую цену, стратегию, уровни для лесенки покупок и продаж, планируемый % портфеля
* В карточке позиции:

  * Основная информация о бумаге и позиции
  * Таблица уровней (ступеней) для покупок/продаж по методике "Лесенка"
  * Быстрый просмотр показателей: процент дохода до цели, текущий доход в %, рублях, средняя цена позиции, доход по продаже (FIFO и с учетом комиссий)
* Возможность категоризации/тегов для заметок (опционально)

### **2.6. Аналитика**

* В MVP: доходность по каждой позиции (FIFO, учёт комиссий), по сделкам, по текущей позиции, по отдельной сделке
* Закладывается расширяемость аналитики (добавление новых видов отчётов, графиков и др.)

### **2.7. Экспорт**

* Резервная копия данных (JSON/CSV/архив — уточняется по ходу)

### **2.8. Пользователи и роли**

* Полноценная регистрация, авторизация, восстановление пароля
* Роли: User (обычный пользователь), Admin (доп. права — управление пользователями, логирование)
* Логирование всех действий (импорт, редактирование, удаление и др.)
* Архитектурно заложена возможность авторизации через сторонние сервисы (Google, Яндекс и др.) — реализация в будущем.

### **2.9. Получение котировок**

* Подгрузка актуальных цен акций с MOEX по REST API
* Автоматическое обновление расчетов доходности по позициям/сделкам

### **2.10. Голосовой ввод заметок**

* Поддержка голосового ввода через Web Speech API (браузер)
* Кнопка 🎤 возле текстового поля заметки: пользователь диктует текст, который распознаётся и вставляется в заметку (аудио не хранится)
* Возможность редактировать текст перед сохранением
* Индикатор записи, обработка ошибок, поддержка русского языка

---

## **3. Ключевые бизнес-правила**

* Все вычисления (доходность, средняя цена, FIFO, учёт комиссий, лесенка продаж) реализуются на backend.
* Парсер HTML-отчётов строится на реальных шаблонах Сбер (образцы хранятся для тестирования).
* Система сравнения и разрешения конфликтов обязательна (никаких автоматических замен без решения пользователя).
* Учет часового пояса индивидуален для пользователя (важно для коррекции времени сделок).
* Все сущности и связи построены с прицелом на расширяемость (новые поля, виды аналитики, категории).

---

## **4. Архитектура данных (сущности и связи, кратко)**

* **User**
* **OAuthAccount** *(для расширения в будущем — авторизация через сторонние сервисы)*
* **UserSettings**
* **Position**
* **Trade**
* **Note**
* **BrokerReportFile**
* **ImportDraft**
* **ActionLog**

---

## **5. ER-диаграмма (описание связей)**

```
User
 ├─< OAuthAccount
 ├─< Trade
 │      ├─< Note
 │      └─< Position >─< Note
 ├─< BrokerReportFile >─< ImportDraft
 ├─< ActionLog
 └─< UserSettings
```

---

## **dbdiagram.io схема**

```dbml
Table users {
  id serial [primary key]
  email varchar [unique, not null]
  username varchar
  password_hash varchar [not null]
  role varchar [not null] // admin, user
  timezone varchar
  created_at timestamp
  updated_at timestamp
}

Table oauth_accounts {
  id serial [primary key]
  user_id int [ref: > users.id]
  provider varchar [not null] // google, yandex, vk и др.
  provider_user_id varchar [not null]
  provider_email varchar
  access_token varchar
  refresh_token varchar
  created_at timestamp
  updated_at timestamp
}

Table user_settings {
  id serial [primary key]
  user_id int [ref: > users.id, unique]
  compare_time_window_hours int
  other_settings jsonb
}

Table positions {
  id serial [primary key]
  user_id int [ref: > users.id]
  instrument varchar [not null]
  avg_price numeric
  quantity_total numeric
  total_commission numeric
  total_profit_loss_value numeric
  total_profit_loss_percent numeric
  note_id int [ref: - notes.id]
  created_at timestamp
  updated_at timestamp
}

Table trades {
  id serial [primary key]
  user_id int [ref: > users.id]
  position_id int [ref: > positions.id]
  instrument varchar [not null]
  trade_date timestamp
  operation varchar
  quantity numeric
  price numeric
  commission numeric
  profit_loss_value numeric
  profit_loss_percent numeric
  source varchar
  broker_report_file_id int [ref: > broker_report_files.id]
  note_id int [ref: - notes.id]
  created_at timestamp
  updated_at timestamp
}

Table notes {
  id serial [primary key]
  user_id int [ref: > users.id]
  trade_id int [ref: - trades.id]
  position_id int [ref: - positions.id]
  text text
  category varchar
  created_at timestamp
  updated_at timestamp
}

Table broker_report_files {
  id serial [primary key]
  user_id int [ref: > users.id]
  file_path varchar
  report_type varchar
  report_period_start date
  report_period_end date
  imported_at timestamp
  import_status varchar
}

Table import_drafts {
  id serial [primary key]
  user_id int [ref: > users.id]
  broker_report_file_id int [ref: > broker_report_files.id]
  draft_trades jsonb
  matching_candidates jsonb
  created_at timestamp
  resolved boolean
}

Table action_logs {
  id serial [primary key]
  user_id int [ref: > users.id]
  action_type varchar
  object_type varchar
  object_id int
  old_value jsonb
  new_value jsonb
  timestamp timestamp
}
```

---

## **6. Технологический стек**

* **Backend**: Python (FastAPI), SQLAlchemy + Alembic, PostgreSQL, BeautifulSoup/lxml для парсинга, JWT для авторизации, Pytest для тестов.
* **Frontend**: React/Next.js, Material UI/Ant Design, Web Speech API (для голосового ввода), Recharts/Chart.js (для аналитики).
* **DevOps**: Docker, GitHub, CI/CD (GitHub Actions).

---

## **7. Особые требования**

* Универсальный парсер под оба типа отчёта (суточный/месячный).
* "Черновик импорта" для безопасного слияния данных при импорте.
* Возможность добавления новых полей и логики без критической переделки архитектуры.
* Адаптивность интерфейса под разные устройства (ПК, смартфон).
* Фокус на UX: удобство ввода, дневниковые поля — всегда "на виду", быстрый доступ к аналитике, голосовой ввод.
* Заложена интеграция с OAuth (Google, Яндекс и др.), но реализация — на этапе расширения.

---

## **8. Подробное описание моделей (таблиц/сущностей) согласно ER-диаграмме**

Для каждой сущности указаны:

* Назначение
* Поля (имя, тип, ограничения)
* Описание поля и особенности
* Внешние ключи/связи
* Особые замечания (если есть)

---

### **1. User (`users`)**

| Поле           | Тип       | Ограничения              | Описание                                 |
| -------------- | --------- | ------------------------ | ---------------------------------------- |
| id             | serial    | PK, unique               | Уникальный идентификатор пользователя    |
| email          | varchar   | not null, unique         | E-mail, используется для входа           |
| username       | varchar   |                          | Отображаемое имя пользователя            |
| password\_hash | varchar   | not null                 | Хеш пароля                               |
| role           | varchar   | not null, default='user' | Роль пользователя: 'user', 'admin'       |
| timezone       | varchar   |                          | Часовой пояс (например, 'Europe/Moscow') |
| created\_at    | timestamp | default=now()            | Дата/время регистрации                   |
| updated\_at    | timestamp | on update                | Дата/время последнего обновления профиля |

**Связи:**

* 1 ко многим: trades, positions, notes, broker\_report\_files, import\_drafts, action\_logs, oauth\_accounts
* 1 к 1: user\_settings

---

### **2. OAuthAccount (`oauth_accounts`)** *(для будущего расширения)*

| Поле               | Тип       | Ограничения   | Описание                                         |
| ------------------ | --------- | ------------- | ------------------------------------------------ |
| id                 | serial    | PK, unique    | Уникальный ID записи                             |
| user\_id           | int       | not null, FK  | Ссылка на пользователя                           |
| provider           | varchar   | not null      | Провайдер авторизации (google, yandex, vk и др.) |
| provider\_user\_id | varchar   | not null      | ID пользователя у провайдера                     |
| provider\_email    | varchar   |               | Email у провайдера (если доступен)               |
| access\_token      | varchar   |               | Токен доступа                                    |
| refresh\_token     | varchar   |               | Refresh-токен (если доступен)                    |
| created\_at        | timestamp | default=now() | Когда добавлена запись                           |
| updated\_at        | timestamp | on update     | Когда обновлена запись                           |

**Связи:**

* Многие к одному с user

**Особенности:**

* В MVP таблица может существовать в БД, но логика OAuth не реализуется.

---

### **3. UserSettings (`user_settings`)**

| Поле                         | Тип    | Ограничения          | Описание                                              |
| ---------------------------- | ------ | -------------------- | ----------------------------------------------------- |
| id                           | serial | PK, unique           | Уникальный ID                                         |
| user\_id                     | int    | not null, unique, FK | Ссылка на пользователя                                |
| compare\_time\_window\_hours | int    | default=24           | Интервал сравнения сделок при импорте, в часах        |
| other\_settings              | jsonb  |                      | Прочие пользовательские настройки (для расширяемости) |

**Связи:**

* 1 к 1 с user

---

### **4. Position (`positions`)**

| Поле                         | Тип       | Ограничения   | Описание                               |
| ---------------------------- | --------- | ------------- | -------------------------------------- |
| id                           | serial    | PK, unique    | Уникальный ID позиции                  |
| user\_id                     | int       | not null, FK  | Владелец позиции                       |
| instrument                   | varchar   | not null      | Тикер или код бумаги                   |
| avg\_price                   | numeric   |               | Средняя цена входа (расчетное поле)    |
| quantity\_total              | numeric   |               | Текущий остаток по позиции (лоты/шт.)  |
| total\_commission            | numeric   |               | Общая комиссия по всем сделкам позиции |
| total\_profit\_loss\_value   | numeric   |               | Итоговая доходность в рублях           |
| total\_profit\_loss\_percent | numeric   |               | Итоговая доходность в %                |
| note\_id                     | int       | FK (nullable) | Основная заметка по позиции            |
| created\_at                  | timestamp | default=now() | Когда создана позиция                  |
| updated\_at                  | timestamp | on update     | Когда изменена позиция                 |

**Связи:**

* Многие к одному с user
* 1 ко многим с trades
* 1 ко многим с notes
* FK на note (главная заметка по позиции, опционально)

---

### **5. Trade (`trades`)**

| Поле                     | Тип       | Ограничения                | Описание                                           |
| ------------------------ | --------- | -------------------------- | -------------------------------------------------- |
| id                       | serial    | PK, unique                 | ID сделки                                          |
| user\_id                 | int       | not null, FK               | Владелец сделки                                    |
| position\_id             | int       | not null, FK               | К какой позиции относится сделка                   |
| instrument               | varchar   | not null                   | Тикер                                              |
| trade\_date              | timestamp | not null                   | Дата и время сделки (с учетом timezone)            |
| operation                | varchar   | not null                   | 'buy' / 'sell'                                     |
| quantity                 | numeric   | not null                   | Количество (лоты/шт.)                              |
| price                    | numeric   | not null                   | Цена за 1 лот/шт.                                  |
| commission               | numeric   |                            | Комиссия по сделке                                 |
| profit\_loss\_value      | numeric   |                            | Доходность по сделке в рублях (расчетное)          |
| profit\_loss\_percent    | numeric   |                            | Доходность по сделке в %                           |
| source                   | varchar   | not null, default='manual' | 'manual' / 'imported'                              |
| broker\_report\_file\_id | int       | FK (nullable)              | Ссылка на файл отчёта брокера (если импортирована) |
| note\_id                 | int       | FK (nullable)              | Основная заметка по сделке                         |
| created\_at              | timestamp | default=now()              | Когда добавлена                                    |
| updated\_at              | timestamp | on update                  | Когда изменена                                     |

**Связи:**

* Многие к одному с user
* Многие к одному с position
* 1 ко многим с notes
* FK на broker\_report\_file (если импортирована)
* FK на note (главная заметка по сделке, опционально)

---

### **6. Note (`notes`)**

| Поле         | Тип       | Ограничения   | Описание                                  |
| ------------ | --------- | ------------- | ----------------------------------------- |
| id           | serial    | PK, unique    | ID заметки                                |
| user\_id     | int       | not null, FK  | Владелец заметки                          |
| trade\_id    | int       | FK (nullable) | Ссылка на сделку, если заметка к сделке   |
| position\_id | int       | FK (nullable) | Ссылка на позицию, если заметка к позиции |
| text         | text      |               | Текст заметки                             |
| category     | varchar   |               | Категория/тег (опционально)               |
| created\_at  | timestamp | default=now() | Когда создана                             |
| updated\_at  | timestamp | on update     | Когда изменена                            |

**Связи:**

* Многие к одному с user
* Многие к одному с trade (опционально)
* Многие к одному с position (опционально)

---

### **7. BrokerReportFile (`broker_report_files`)**

| Поле                  | Тип       | Ограничения   | Описание                                 |
| --------------------- | --------- | ------------- | ---------------------------------------- |
| id                    | serial    | PK, unique    | ID файла отчёта                          |
| user\_id              | int       | not null, FK  | Владелец                                 |
| file\_path            | varchar   | not null      | Путь к файлу или имя в хранилище         |
| report\_type          | varchar   | not null      | Тип отчёта: 'monthly'/'daily'            |
| report\_period\_start | date      | not null      | Начало периода                           |
| report\_period\_end   | date      | not null      | Конец периода                            |
| imported\_at          | timestamp | default=now() | Дата/время импорта                       |
| import\_status        | varchar   |               | Статус импорта (например, 'ok', 'error') |

**Связи:**

* Многие к одному с user
* 1 ко многим с trades (импортированные сделки)
* 1 к 1 с import\_draft

---

### **8. ImportDraft (`import_drafts`)**

| Поле                     | Тип       | Ограничения          | Описание                                           |
| ------------------------ | --------- | -------------------- | -------------------------------------------------- |
| id                       | serial    | PK, unique           | ID черновика                                       |
| user\_id                 | int       | not null, FK         | Владелец                                           |
| broker\_report\_file\_id | int       | not null, FK, unique | К какому отчёту относится                          |
| draft\_trades            | jsonb     | not null             | Массив сделок из отчёта (до подтверждения импорта) |
| matching\_candidates     | jsonb     |                      | Кандидаты на совпадение (для сравнения)            |
| created\_at              | timestamp | default=now()        | Когда создан                                       |
| resolved                 | boolean   | default=false        | Черновик обработан? (да/нет)                       |

**Связи:**

* Многие к одному с user
* 1 к 1 с broker\_report\_file

---

### **9. ActionLog (`action_logs`)**

| Поле         | Тип       | Ограничения   | Описание                                       |
| ------------ | --------- | ------------- | ---------------------------------------------- |
| id           | serial    | PK, unique    | ID лог-записи                                  |
| user\_id     | int       | not null, FK  | Кто сделал действие                            |
| action\_type | varchar   | not null      | Тип действия ('import', 'edit', 'delete', ...) |
| object\_type | varchar   | not null      | Тип объекта ('trade', 'note', 'file', ...)     |
| object\_id   | int       | not null      | ID объекта                                     |
| old\_value   | jsonb     |               | Старое значение (для изменений/удалений)       |
| new\_value   | jsonb     |               | Новое значение                                 |
| timestamp    | timestamp | default=now() | Время действия                                 |

**Связи:**

* Многие к одному с user

---

## **9. Описание API и CRUD-сценариев**

---

### **9.1. Auth (Регистрация, Авторизация, OAuth)**

#### **POST /auth/register**

* **Назначение:** Регистрация нового пользователя.
* **Вход:**

  ```json
  {
    "email": "user@example.com",
    "username": "Trader",
    "password": "string"
  }
  ```
* **Выход:**

  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "Trader"
  }
  ```
* **Особенности:** Пароль хэшируется, email проверяется на уникальность.

---

#### **POST /auth/login**

* **Назначение:** Авторизация пользователя.
* **Вход:**

  ```json
  {
    "email": "user@example.com",
    "password": "string"
  }
  ```
* **Выход:**

  ```json
  {
    "access_token": "jwt-token",
    "token_type": "bearer"
  }
  ```
* **Особенности:** JWT с временем жизни (например, 24 ч).

---

#### **GET /auth/me**

* **Назначение:** Получение информации о текущем пользователе.
* **Выход:**

  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "Trader",
    "role": "user"
  }
  ```
* **Особенности:** Требуется авторизация.

---

#### **GET /auth/oauth/{provider}/login** *(MVP — заглушка)*

* **Назначение:** Начало OAuth-авторизации через `google`, `yandex` и др.
* **Выход:** Редирект на страницу провайдера.
* **Особенности:** Пока не реализуется.

---

#### **GET /auth/oauth/{provider}/callback** *(MVP — заглушка)*

* **Назначение:** Обработка ответа от OAuth-провайдера.
* **Выход:** JWT-токен (если успешная авторизация).
* **Особенности:** Пока не реализуется.

---

#### **POST /auth/logout**

* **Назначение:** Выход пользователя.
* **Особенности:** При использовании JWT может быть просто на фронтенде удаление токена.

---

## **9.2. User (Профиль пользователя)**

---

### **GET /users/{id}**

* **Назначение:** Получить данные профиля пользователя.

  * Пользователь может запросить только свой профиль.
  * Администратор может запросить профиль любого пользователя.

* **Выход:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "Trader",
  "role": "user",
  "timezone": "Europe/Moscow",
  "created_at": "2025-08-08T10:00:00Z"
}
```

* **Особенности:**

  * Требуется авторизация.
  * Для доступа к чужим данным — права администратора.

---

### **PATCH /users/{id}**

* **Назначение:** Обновить данные профиля пользователя (имя, часовой пояс, пароль).

* **Вход:**

```json
{
  "username": "NewName",
  "timezone": "Europe/Moscow",
  "password": "newsecurepassword"
}
```

* **Выход:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "NewName",
  "timezone": "Europe/Moscow",
  "updated_at": "2025-08-09T14:20:00Z"
}
```

* **Особенности:**

  * Требуется авторизация.
  * Изменение email в этой версии API не предусмотрено.
  * При смене пароля он хэшируется перед сохранением.

---

### **DELETE /users/{id}**

* **Назначение:** Удалить пользователя.

  * Пользователь может удалить свой аккаунт.
  * Администратор может удалить любой аккаунт.

* **Выход:**

```
204 No Content
```

* **Особенности:**

  * Требуется подтверждение действия (например, повторный ввод пароля).
  * Удаление необратимо — все данные (сделки, позиции, заметки) удаляются или помечаются как удалённые.

---

## **9.3. Trades (Сделки)**

---

### **POST /trades**

* **Назначение:** Добавить новую сделку вручную. Может быть привязана к существующей позиции или создать новую позицию автоматически.

* **Вход:**

```json
{
  "position_id": 101,            // необязательно
  "instrument": "SBER",
  "trade_date": "2025-08-08T12:00:00Z",
  "operation": "buy",            // "buy" или "sell"
  "quantity": 10,
  "price": 200.00,
  "commission": 1.50,
  "note": "Покупка по плану"
}
```

* **Выход:**

```json
{
  "id": 305,
  "position_id": 101,
  "instrument": "SBER",
  "trade_date": "2025-08-08T12:00:00Z",
  "operation": "buy",
  "quantity": 10,
  "price": 200.00,
  "commission": 1.50,
  "note": "Покупка по плану"
}
```

* **Особенности:**

  * Если `position_id` не передан, создаётся новая позиция.
  * Валидация: количество > 0, цена > 0.

---

### **GET /trades**

* **Назначение:** Получить список сделок пользователя с возможностью фильтрации.

* **Параметры запроса (Query):**

  * `instrument` (string) — фильтр по тикеру.
  * `from_date` (date) — дата начала периода.
  * `to_date` (date) — дата конца периода.
  * `operation` (string) — `"buy"` или `"sell"`.

* **Выход:**

```json
[
  {
    "id": 301,
    "position_id": 101,
    "instrument": "GAZP",
    "trade_date": "2025-08-05T10:15:00Z",
    "operation": "buy",
    "quantity": 100,
    "price": 149.00,
    "commission": 3.50,
    "note": "Вход по сигналу EMA"
  }
]
```

* **Особенности:**

  * Сортировка по дате по умолчанию — от новых к старым.

---

### **GET /trades/{id}**

* **Назначение:** Получить детальную информацию о конкретной сделке.

* **Выход:**

```json
{
  "id": 301,
  "position_id": 101,
  "instrument": "GAZP",
  "trade_date": "2025-08-05T10:15:00Z",
  "operation": "buy",
  "quantity": 100,
  "price": 149.00,
  "commission": 3.50,
  "profit_loss_value": null,
  "profit_loss_percent": null,
  "note": "Вход по сигналу EMA"
}
```

---

### **PATCH /trades/{id}**

* **Назначение:** Редактировать данные сделки.

* **Вход:**

```json
{
  "quantity": 120,
  "price": 150.00,
  "note": "Докупка по стратегии"
}
```

* **Выход:** Обновлённый объект сделки.

* **Особенности:**

  * Нельзя изменять `operation` после создания.
  * При изменении цены/количества перерассчитывается средняя цена позиции.

---

### **DELETE /trades/{id}**

* **Назначение:** Удалить сделку.

* **Выход:**

```
204 No Content
```

* **Особенности:**

  * Если после удаления сделки в позиции не останется сделок — позиция удаляется автоматически.

---

## **9.4. Positions (Позиции)**

---

### **GET /positions**

* **Назначение:** Получить список всех позиций пользователя с краткой сводкой.

* **Параметры запроса (Query):**

  * `instrument` (string) — фильтр по тикеру.
  * `from_date` (date) — дата открытия от.
  * `to_date` (date) — дата открытия до.
  * `sort_by` (string) — поле сортировки (`created_at`, `profit_loss_percent`).
  * `sort_dir` (string) — `asc` или `desc`.

* **Выход:**

```json
[
  {
    "id": 101,
    "instrument": "GAZP",
    "avg_price": 150.25,
    "quantity_total": 400,
    "total_profit_loss_value": 5000.00,
    "total_profit_loss_percent": 8.5,
    "note_preview": "Покупка на падении, цель 180...",
    "updated_at": "2025-08-07T15:45:00Z"
  }
]
```

---

### **GET /positions/{id}**

* **Назначение:** Получить детальную информацию по позиции, включая сделки, заметки и план действий (лесенку).

* **Выход:**

```json
{
  "id": 101,
  "instrument": "GAZP",
  "avg_price": 150.25,
  "quantity_total": 400,
  "total_commission": 120.50,
  "total_profit_loss_value": 5000.00,
  "total_profit_loss_percent": 8.5,
  "note": {
    "id": 15,
    "text": "Покупка на падении, цель 180, следующая докупка на 145",
    "category": null
  },
  "trades": [
    {
      "id": 301,
      "trade_date": "2025-08-05T10:15:00Z",
      "operation": "buy",
      "quantity": 100,
      "price": 149.00,
      "commission": 3.50,
      "profit_loss_value": null,
      "profit_loss_percent": null,
      "note": {
        "id": 22,
        "text": "Вход по сигналу EMA"
      }
    }
  ],
  "ladder_plan": [
    {
      "price": 145.00,
      "action": "buy",
      "percent_of_position": 20
    },
    {
      "price": 180.00,
      "action": "sell",
      "percent_of_position": 50
    }
  ]
}
```

---

### **POST /positions**

* **Назначение:** Создать новую позицию вручную (с возможностью сразу добавить первую сделку и заметку).

* **Вход:**

```json
{
  "instrument": "GAZP",
  "avg_price": 150.25,
  "quantity_total": 100,
  "note": {
    "text": "Первая покупка в рамках стратегии САИ",
    "category": "idea"
  }
}
```

* **Выход:**

```json
{
  "id": 101,
  "instrument": "GAZP",
  "avg_price": 150.25,
  "quantity_total": 100
}
```

---

### **PATCH /positions/{id}**

* **Назначение:** Обновить данные позиции, заметку и/или план действий.

* **Вход:**

```json
{
  "avg_price": 152.00,
  "note": {
    "text": "Обновил целевую цену до 185",
    "category": "update"
  },
  "ladder_plan": [
    { "price": 145.00, "action": "buy", "percent_of_position": 20 },
    { "price": 185.00, "action": "sell", "percent_of_position": 50 }
  ]
}
```

* **Выход:** Актуальная версия позиции.

---

### **DELETE /positions/{id}**

* **Назначение:** Удалить позицию и все связанные сделки и заметки.

* **Выход:**

```
204 No Content
```

* **Особенности:**

  * Удаление необратимо.
  * Перед удалением можно реализовать подтверждение на фронтенде.

---

## **9.5. Notes (Заметки)**

---

### **POST /notes**

* **Назначение:** Создать новую заметку, привязанную к позиции или сделке.

* **Вход:**

```json
{
  "trade_id": 123,       // либо position_id
  "position_id": null,   // можно оставить null
  "text": "Купил по стратегии лесенка, первая ступень",
  "category": "стратегия"
}
```

* **Выход:**

```json
{
  "id": 55,
  "trade_id": 123,
  "position_id": null,
  "text": "Купил по стратегии лесенка, первая ступень",
  "category": "стратегия",
  "created_at": "2025-08-08T10:20:00Z"
}
```

* **Особенности:**

  * Заметка принадлежит только одному пользователю.
  * Категория (`category`) опциональна.
  * Может быть добавлена вручную или через голосовой ввод (Web Speech API на фронтенде).

---

### **GET /notes**

* **Назначение:** Получить список заметок с возможностью фильтрации.

* **Параметры запроса (Query):**

  * `trade_id` (optional) — фильтр по сделке.
  * `position_id` (optional) — фильтр по позиции.
  * `category` (optional) — фильтр по категории.

* **Выход:**

```json
[
  {
    "id": 55,
    "trade_id": 123,
    "position_id": null,
    "text": "Купил по стратегии лесенка, первая ступень",
    "category": "стратегия",
    "created_at": "2025-08-08T10:20:00Z"
  },
  {
    "id": 56,
    "trade_id": null,
    "position_id": 12,
    "text": "Следующая цель — 180 руб.",
    "category": "цель",
    "created_at": "2025-08-08T10:30:00Z"
  }
]
```

---

### **PATCH /notes/{id}**

* **Назначение:** Редактировать текст и/или категорию заметки.

* **Вход:**

```json
{
  "text": "Цель 180 руб., стоп 150 руб.",
  "category": "план"
}
```

* **Выход:**

```json
{
  "id": 55,
  "text": "Цель 180 руб., стоп 150 руб.",
  "category": "план",
  "updated_at": "2025-08-08T12:00:00Z"
}
```

---

### **DELETE /notes/{id}**

* **Назначение:** Удалить заметку.

* **Выход:**

```
204 No Content
```

---

### **Особенности голосового ввода**

1. Пользователь нажимает кнопку 🎤 рядом с полем ввода заметки.
2. JS в браузере активирует распознавание речи (русский язык).
3. Распознанный текст подставляется в поле ввода.
4. Пользователь может отредактировать текст.
5. После нажатия **Сохранить** отправляется обычный POST-запрос `/notes`.

---

## **9.6. Import (Импорт отчётов брокера)**

---

### **POST /import**

* **Назначение:** Загрузить HTML-отчёт брокера (суточный или месячный) для последующего разбора и импорта.
* **Доступ:** Авторизованный пользователь.
* **Вход (multipart/form-data):**

  * `file` — HTML-файл отчёта брокера.
  * `report_type` *(optional)* — `daily` или `monthly` (если не указано — определяется автоматически).
* **Выход:**

```json
{
  "draft_id": 77,
  "broker_report_file_id": 54,
  "total_trades_found": 12,
  "potential_conflicts": 3
}
```

* **Особенности:**

  * Файл сохраняется в таблицу `broker_report_files`.
  * Создаётся черновик импорта (`import_drafts`).
  * Определяются потенциальные конфликты с уже существующими сделками.

---

### **GET /import/drafts**

* **Назначение:** Получить список всех активных черновиков импорта текущего пользователя.
* **Выход:**

```json
[
  {
    "id": 77,
    "report_type": "daily",
    "report_period_start": "2025-08-06",
    "report_period_end": "2025-08-06",
    "total_trades": 12,
    "potential_conflicts": 3,
    "created_at": "2025-08-06T12:00:00Z"
  }
]
```

---

### **GET /import/drafts/{id}**

* **Назначение:** Просмотр содержимого черновика импорта.
* **Выход:**

```json
{
  "id": 77,
  "broker_report_file_id": 54,
  "draft_trades": [
    {
      "draft_trade_id": "tmp-1",
      "instrument": "GAZP",
      "trade_date": "2025-08-06T10:15:00Z",
      "operation": "buy",
      "quantity": 100,
      "price": 149.00,
      "commission": 3.50,
      "match_status": "conflict",
      "existing_trade": {
        "id": 301,
        "price": 150.00,
        "commission": null
      }
    },
    {
      "draft_trade_id": "tmp-2",
      "instrument": "SBER",
      "trade_date": "2025-08-06T11:05:00Z",
      "operation": "sell",
      "quantity": 50,
      "price": 270.00,
      "commission": 2.70,
      "match_status": "new"
    }
  ]
}
```

* **Особенности:**

  * Каждая сделка из отчёта получает статус: `new`, `match` или `conflict`.
  * Для конфликтных сделок указывается существующая версия.

---

### **POST /import/drafts/{id}/resolve**

* **Назначение:** Разрешение конфликтов по сделкам.
* **Вход:**

```json
{
  "resolutions": [
    {
      "draft_trade_id": "tmp-1",
      "decision": "keep_draft"  // или "keep_existing", или "merge"
    },
    {
      "draft_trade_id": "tmp-2",
      "decision": "keep_draft"
    }
  ]
}
```

* **Правила `decision`:**

  * `keep_draft` — заменить существующую сделку данными из отчёта.
  * `keep_existing` — оставить без изменений.
  * `merge` — объединить данные.
* **Выход:**

```json
{
  "message": "Conflicts resolved. You can now confirm the import."
}
```

---

### **POST /import/drafts/{id}/confirm**

* **Назначение:** Применить черновик к основной базе (`trades` / `positions`).
* **Выход:**

```json
{
  "message": "Import completed successfully",
  "trades_imported": 12,
  "trades_updated": 3
}
```

---

### **DELETE /import/drafts/{id}**

* **Назначение:** Отменить импорт, удалить черновик и связанный файл отчёта.
* **Выход:**

```
204 No Content
```

---

## **9.7. Analytics (Аналитика)**

---

### **GET /analytics/positions**

* **Назначение:** Получить агрегированную аналитику по всем позициям пользователя.
* **Доступ:** Авторизованный пользователь.
* **Параметры (Query):**

  * `from_date` *(optional)* — начальная дата периода.
  * `to_date` *(optional)* — конечная дата периода.
  * `group_by` *(optional)* — способ группировки (`instrument`, `month`, `year`).
* **Выход:**

```json
{
  "total_positions": 12,
  "total_profit_loss_value": 15200.50,
  "total_profit_loss_percent": 8.7,
  "by_instrument": [
    {
      "instrument": "GAZP",
      "profit_loss_value": 5000.00,
      "profit_loss_percent": 8.5
    },
    {
      "instrument": "SBER",
      "profit_loss_value": 10200.50,
      "profit_loss_percent": 9.2
    }
  ]
}
```

* **Особенности:**

  * Можно фильтровать по дате и группировать по инструменту или периоду.
  * Рассчитывается на основе закрытых и открытых позиций.

---

### **GET /analytics/trades**

* **Назначение:** Получить статистику по сделкам за выбранный период.
* **Доступ:** Авторизованный пользователь.
* **Параметры (Query):**

  * `from_date` *(optional)* — начальная дата.
  * `to_date` *(optional)* — конечная дата.
  * `instrument` *(optional)* — фильтр по тикеру.
* **Выход:**

```json
{
  "total_trades": 35,
  "average_profit_loss_value": 420.75,
  "average_profit_loss_percent": 2.5,
  "win_rate_percent": 62.8,
  "profit_factor": 1.85,
  "max_drawdown_percent": -7.2,
  "best_trade": {
    "id": 301,
    "instrument": "GAZP",
    "profit_loss_value": 1500.00,
    "profit_loss_percent": 10.0
  },
  "worst_trade": {
    "id": 322,
    "instrument": "SBER",
    "profit_loss_value": -800.00,
    "profit_loss_percent": -5.5
  }
}
```

* **Особенности:**

  * Подсчёт win rate, profit factor и максимальной просадки.
  * Определение лучшей и худшей сделки в периоде.

---

## **9.8. Settings (Настройки)**

---

### **GET /settings**

* **Назначение:** Получить текущие настройки пользователя.
* **Доступ:** Авторизованный пользователь.
* **Выход:**

```json
{
  "timezone": "Europe/Moscow",
  "currency": "RUB",
  "language": "ru",
  "date_format": "DD.MM.YYYY",
  "notifications": {
    "email": true,
    "push": false
  },
  "default_trade_commission": 0.05
}
```

* **Особенности:**

  * Настройки хранятся в привязке к конкретному пользователю.
  * Используются при расчётах и отображении данных в интерфейсе.

---

### **PATCH /settings**

* **Назначение:** Обновить настройки пользователя.
* **Доступ:** Авторизованный пользователь.
* **Вход:**

```json
{
  "timezone": "Europe/Moscow",
  "currency": "USD",
  "language": "en",
  "notifications": {
    "email": false,
    "push": true
  },
  "default_trade_commission": 0.03
}
```

* **Выход:**

```json
{
  "timezone": "Europe/Moscow",
  "currency": "USD",
  "language": "en",
  "date_format": "DD.MM.YYYY",
  "notifications": {
    "email": false,
    "push": true
  },
  "default_trade_commission": 0.03
}
```

* **Особенности:**

  * Частичное обновление (только переданные поля изменяются).
  * Поля валидации:

    * `timezone` — должен соответствовать IANA.
    * `currency` — один из списка поддерживаемых валют (`RUB`, `USD`, `EUR` и др.).
    * `language` — один из поддерживаемых языков (`ru`, `en` и др.).
    * `default_trade_commission` — процент комиссии (0–100).

---

## **9.9. Logs (Журнал действий)**

---

### **GET /logs**

* **Назначение:** Получить историю действий пользователя или всех пользователей (для админа).
* **Доступ:**

  * Обычный пользователь — видит только свои действия.
  * Админ — видит все действия в системе.
* **Параметры (Query):**

  * `user_id` *(int, optional)* — фильтр по пользователю (только для админа).
  * `from_date` *(string, optional, формат YYYY-MM-DD)* — дата начала периода.
  * `to_date` *(string, optional, формат YYYY-MM-DD)* — дата конца периода.
  * `action_type` *(string, optional)* — фильтр по типу действия (`login`, `create_trade`, `delete_note`, и т.д.).
  * `limit` *(int, optional)* — количество записей на страницу.
  * `page` *(int, optional)* — номер страницы.
* **Выход:**

```json
[
  {
    "id": 501,
    "user_id": 1,
    "username": "TraderJoe",
    "action_type": "create_trade",
    "action_description": "Создана сделка по инструменту SBER",
    "created_at": "2025-08-08T10:30:00Z",
    "ip_address": "192.168.1.10",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  {
    "id": 502,
    "user_id": 1,
    "username": "TraderJoe",
    "action_type": "update_position",
    "action_description": "Обновлена позиция GAZP: изменена целевая цена",
    "created_at": "2025-08-08T12:15:00Z",
    "ip_address": "192.168.1.10",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  }
]
```

* **Особенности:**

  * Логи хранятся с метаданными: IP, user-agent, время.
  * Используются для аудита и безопасности.
  * Возможен экспорт логов в CSV/JSON (для админа).

---

### **DELETE /logs**

* **Назначение:** Очистка логов.
* **Доступ:**

  * Обычный пользователь — может очищать только свои логи.
  * Админ — может очищать логи любых пользователей или все сразу.
* **Параметры (Query):**

  * `user_id` *(optional)* — чьи логи удалять (только админ).
  * `before_date` *(optional)* — удалить все записи до указанной даты.
* **Выход:**

```json
{
  "message": "Логи успешно удалены",
  "deleted_count": 125
}
```

---

