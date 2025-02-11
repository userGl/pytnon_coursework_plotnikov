**1.Работа с OCR:**
# Загрузка и распознавание файла
POST /upload/
Content-Type: multipart/form-data
file: <файл>
lang: rus+eng

# Получение списка доступных языков
GET /get_languages/

**2.Работа с записями:**
# Получение всех записей
GET /records/

# Удаление выбранных записей
POST /delete_records
Content-Type: application/json
{
    "filenames": ["file1.txt", "file2.txt"]
}

**3.Работа с email:**
# Отправка результата на email
POST /send_email/
Content-Type: application/json
{
    "to_email": "example@mail.com",
    "text": "Распознанный текст"
}

# Сохранение настроек SMTP
POST /admin/email_config
Content-Type: application/json
{
    "smtp_server": "smtp.mail.ru",
    "smtp_port": 465,
    "smtp_user": "user@mail.ru",
    "smtp_password": "password",
    "from_email": "user@mail.ru"
}

**4.Тестирование:**
# Запуск тестов
GET /run_test/{test_type}
где test_type может быть: all, endpoints, repository, ocr

**5.Логирование:**
# Получение логов
GET /admin/logs?lines=100

**Примеры использования микросервиса:**
# Получить все записи
curl http://localhost:8000/records/

# Запустить все тесты
curl http://localhost:8000/run_test/all

# Получить логи
curl http://localhost:8000/admin/logs

# Отправить файл на распознавание
curl -X POST http://localhost:8000/upload/ \
  -F "file=@image.png" \
  -F "lang=rus+eng"

# Отправить результат на email
curl -X POST http://localhost:8000/send_email/ \
  -H "Content-Type: application/json" \
  -d '{"to_email":"user@mail.ru","text":"Распознанный текст"}'

