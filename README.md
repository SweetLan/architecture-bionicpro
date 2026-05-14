# BionicPRO Reports Platform

## Описание проекта

В рамках задания была разработана архитектура платформы подготовки и получения отчетов по телеметрии бионических протезов.

Решение включает:
- ETL-процесс на Apache Airflow;
- OLAP-хранилище на ClickHouse;
- backend API для получения готовых отчетов;
- frontend UI для запроса отчетов;
- аутентификацию и ограничение доступа пользователей.

---

# Задача 1. Архитектура решения

Подготовлена архитектура системы подготовки отчетов.

Реализованы следующие компоненты:
- CRM-система с данными клиентов;
- поток телеметрии протезов;
- Apache Airflow для ETL-обработки;
- ClickHouse как OLAP-база;
- backend `reports-api` (на схеме как Api);
- frontend UI;
- Keycloak для аутентификации пользователей.

ETL-процесс:
1. Извлекает данные из CRM.
2. Извлекает телеметрию протезов.
3. Агрегирует данные.
4. Формирует витрину `prosthesis_report_mart`.
5. Backend API предоставляет готовые отчёты без realtime-вычислений.

Архитектурная схема подготовлена [в draw.io](Task2/BionicPRO_C4_model.drawio.xml)

---

# Задача 2. Airflow DAG и ETL

Реализован DAG:
- `prosthesis_reports_etl`

DAG выполняет:
- чтение данных CRM;
- чтение телеметрии;
- агрегацию показателей;
- загрузку витрины отчётности в ClickHouse.

Созданы таблицы:
- `crm_clients`
- `telemetry_events`
- `prosthesis_report_mart`

В витрине реализованы:
- количество телеметрических событий;
- среднее время ответа;
- максимальное время ответа;
- средний уровень батареи;
- минимальный уровень батареи.

Настроено расписание запуска DAG.

Витрина оптимизирована для быстрого доступа по `user_id`.
Ссылка на [airflow](Task2/airflow/dags/prosthesis_reports_dag.py)
Скриншоты 
[Screenshot1](Task2/airflow/Screenshot1.png)
[Screenshot2](Task2/airflow/Screenshot2.png)
[Архитектура](Task2/BionicPRO_C4_model.drawio.xml)
---

# Задача 3. Backend API

Реализован backend-сервис на FastAPI.

Добавлен endpoint:

```http
GET /reports
```

API:
- получает готовые данные из ClickHouse;
- не выполняет тяжёлые вычисления в realtime;
- возвращает отчеты пользователя.

Пример запроса:

```bash
curl.exe -H "X-User-Id: user-1" http://localhost:8000/reports
```
[Ссылка на backend](Task3/backend/)
[Скриншот](Task3/Screenshot1.png)
---

# Задача 4. Ограничение доступа

Реализовано ограничение доступа к отчетам.

Backend:
- не принимает `user_id` через query-параметры;
- получает пользователя только из заголовка `X-User-Id`.

Это предотвращает получение чужих отчётов.

Неавторизованный запрос возвращает ошибку:

```text
422 Unprocessable Entity
```
[Скриншот](Task4/Screenshot1.png)
---

# Задача 5. UI для получения отчётов

Во frontend реализована кнопка:
- `Download Report`

Frontend:
- вызывает backend endpoint `/reports`;
- передаёт идентификатор пользователя;
- отображает результат запроса.

---

# Используемые технологии

- React
- FastAPI
- Apache Airflow
- ClickHouse
- Docker Compose
- Keycloak
- PostgreSQL

[Скриншот](Task5/Screenshot.png)
---

# Проверка работы

## Запуск проекта

```bash
docker compose up -d
```

## Frontend

```text
http://localhost:3000
```

## Backend API

```text
http://localhost:8000/docs
```

## Airflow

```text
http://localhost:8081
```

Логин:
- admin
- admin

---

# Проверка ETL

Запустить DAG:
- `prosthesis_reports_etl`

Проверить данные в ClickHouse:

```sql
SELECT * FROM prosthesis_report_mart;
```

---

# Проверка безопасности

Без заголовка:

```bash
curl.exe http://localhost:8000/reports
```

Результат:
- ошибка 422.

С заголовком:

```bash
curl.exe -H "X-User-Id: user-1" http://localhost:8000/reports
```

Результат:
- возвращается только отчёт пользователя `user-1`.

