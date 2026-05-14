# Задача 1. Управление учетными данными пользователя

## Решение

В архитектуру BionicPRO добавлен IAM/SSO слой на базе Keycloak.

Keycloak используется как единая точка входа и federation broker для внешних удостоверяющих служб разных стран. Учетные записи пользователей запрашиваются из внешних IdP/LDAP/AD, расположенных в стране представительства компании. 
Медицинские и персональные данные пользователей продолжают храниться локально в региональных хранилищах BionicPRO и не переносятся в Keycloak.

Для защиты токенов добавлен Session API. 
Фронтенд не получает access_token и refresh_token от внешнего IdP. После входа пользователя Keycloak выпускает внутренние токены BionicPRO, а BFF хранит их на серверной стороне. Фронтенду возвращается только защищённая HttpOnly Secure SameSite cookie.

Для frontend-клиента используется OAuth 2.0 Authorization Code Flow with PKCE. Implicit Flow и Direct Access Grants отключены. PKCE защищает систему от атаки с перехватом authorization code.

Доступ к отчётам ограничивается на уровне API: пользователь может получить только отчеты, связанные с его user_id и prosthesis_id.

## Задача 2. Замена Code Grant на PKCE

Для frontend-клиента `reports-frontend` включён Authorization Code Flow with PKCE.

Изменения:
- клиент остался публичным: `publicClient: true`;
- включен стандартный Authorization Code Flow: `standardFlowEnabled: true`;
- отключен Implicit Flow: `implicitFlowEnabled: false`;
- отключен Direct Access Grants: `directAccessGrantsEnabled: false`;
- включен PKCE с методом S256: `pkce.code.challenge.method: S256`;
- во фронтенде Keycloak adapter настроен с `pkceMethod: 'S256'`.

PKCE повышает безопасность, потому что перехваченный authorization code нельзя обменять на токены без `code_verifier`.