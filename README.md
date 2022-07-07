# Auth-sprint-2

# Запуск контейнеров
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
