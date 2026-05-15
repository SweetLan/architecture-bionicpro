# Задание 1. Повышение безопасности системы

# Задача 1.1. Управление учетными данными пользователя

## Решение

В архитектуру BionicPRO добавлен IAM/SSO слой на базе Keycloak.

Keycloak используется как единая точка входа и federation broker для внешних удостоверяющих служб разных стран. Учетные записи пользователей запрашиваются из внешних IdP/LDAP/AD, расположенных в стране представительства компании. 
Медицинские и персональные данные пользователей продолжают храниться локально в региональных хранилищах BionicPRO и не переносятся в Keycloak.

Для защиты токенов добавлен Session API. 
Фронтенд не получает access_token и refresh_token от внешнего IdP. После входа пользователя Keycloak выпускает внутренние токены BionicPRO, а BFF хранит их на серверной стороне. Фронтенду возвращается только защищённая HttpOnly Secure SameSite cookie.

Для frontend-клиента используется OAuth 2.0 Authorization Code Flow with PKCE. Implicit Flow и Direct Access Grants отключены. PKCE защищает систему от атаки с перехватом authorization code.

Доступ к отчётам ограничивается на уровне API: пользователь может получить только отчеты, связанные с его user_id и prosthesis_id.

[Архитектура решения](Task1.1&1.2/BionicPRO_C4_model.drawio.xml)

## Задача 1.2. Замена Code Grant на PKCE

Для frontend-клиента `reports-frontend` включён Authorization Code Flow with PKCE.

Изменения:
- клиент остался публичным: `publicClient: true`;
- включен стандартный Authorization Code Flow: `standardFlowEnabled: true`;
- отключен Implicit Flow: `implicitFlowEnabled: false`;
- отключен Direct Access Grants: `directAccessGrantsEnabled: false`;
- включен PKCE с методом S256: `pkce.code.challenge.method: S256`;
- во фронтенде Keycloak adapter настроен с `pkceMethod: 'S256'`.

PKCE повышает безопасность, потому что перехваченный authorization code нельзя обменять на токены без `code_verifier`.


# Задание 2. Разработка сервиса отчётов

## Описание проекта

В рамках задания была разработана архитектура платформы подготовки и получения отчетов по телеметрии бионических протезов.

Решение включает:
- ETL-процесс на Apache Airflow;
- OLAP-хранилище на ClickHouse;
- backend API для получения готовых отчетов;
- frontend UI для запроса отчетов;
- аутентификацию и ограничение доступа пользователей.

---

# Задача 2.1. Архитектура решения

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

Архитектурная схема подготовлена [в draw.io](Task2.1&2.2/BionicPRO_C4_model.drawio.xml)

---

# Задача 2.2. Airflow DAG и ETL

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
Ссылка на [airflow](Task2.1&2.2/airflow/dags/prosthesis_reports_dag.py)
Скриншоты 
[Screenshot1](Task2.1&2.2/airflow/Screenshot1.png)
[Screenshot2](Task2.1&2.2/airflow/Screenshot2.png)
[Архитектура](Task2.1&2.2/BionicPRO_C4_model.drawio.xml)
---

# Задача 2.3. Backend API

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
[Ссылка на backend](Task2.3/backend/)
[Скриншот](Task2.3/Screenshot1.png)
---

# Задача 2.4. Ограничение доступа

Реализовано ограничение доступа к отчетам.

Backend:
- не принимает `user_id` через query-параметры;
- получает пользователя только из заголовка `X-User-Id`.

Это предотвращает получение чужих отчётов.

Неавторизованный запрос возвращает ошибку:

```text
422 Unprocessable Entity
```
[Скриншот](Task2.4/Screenshot1.png)
---

# Задача 2.5. UI для получения отчётов

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

[Скриншот](Task2.5/Screenshot.png)
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

