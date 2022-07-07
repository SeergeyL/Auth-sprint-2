# Auth-sprint-2

# Запуск контейнеров
Адрес проверки авторизации пользователя в Async-API
```
AUTH_SERVICE_URL='http://127.0.0.1:80/v1/check-auth'
```
Оба сервиса (Async-API и Auth) запускаются по отдельности:
```
docker-compose up -d
```
В сервисе Auth необходимо выполнить все миграции:
```
make migrate
```
Если нужно создать админа
```
make superuser
```
