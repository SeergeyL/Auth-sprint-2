# Сервис авторизации для онлайн кинотеатра
Сервис необходим для регистрации и авторизации пользователей по логину и паролю. 

Также реализована OAuth авторизация через сервисы Яндекс и VK

# Запуск контейнеров
Необходмо указать адрес проверки авторизации пользователя в Async-API
```
AUTH_SERVICE_URL='http://{ADDRESS}:81/v1/check-auth'
```

Копируется репозиторий вместе с сабмодулями
```
git clone https://github.com/SeergeyL/Auth-sprint-2.git
git submodule update --init
```

Необходимо запустить оба сервиса (Async-API и Auth). Каждый запускается своей командой:
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

При запросах к Async-API в заголовках необходимо указать `access_token`.

Получить токен можно воспользовавшись созданным суперюзером:
```
curl -H 'Content-Type: application/json' --data '{"email": "admin@admin.ru", "password": "123456"}' http://{ADDRESS}:81/v1/login
```
