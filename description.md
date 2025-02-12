**1.Работа с OCR:**
# Отправка файла на распознавание
curl -X POST http://localhost:8000/upload/ \
  -F "file=@path/to/image.png" \
  -F "lang=rus+eng"

# Получение списка поддерживаемых языков
curl http://localhost:8000/get_languages/

**2.Работа с записями:**
# Получить все записи
curl http://localhost:8000/records/

# Удалить записи по ID
curl -X POST http://localhost:8000/delete_records \
  -H "Content-Type: application/json" \
  -d '{"record_ids": [1, 2, 3]}'

**3.Работа с email:**
# Отправка текста на email
curl -X POST http://localhost:8000/send_email/ \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "recipient@mail.com",
    "text": "Распознанный текст"
  }'

# Настройки SMTP сервера для отправки e-mail
curl -X POST http://localhost:8000/admin/email_config \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465,
    "smtp_user": "user@gmail.com",
    "smtp_password": "password",
    "from_email": "user@gmail.com"
  }'


**4.Тестирование:**
# Запуск всех тестов
curl http://localhost:8000/run_test/all

# Запуск конкретной группы тестов
curl http://localhost:8000/run_test/endpoints
curl http://localhost:8000/run_test/ocr
curl http://localhost:8000/run_test/repository

**5.Логирование:**
# Получение последних 100 строк лога
curl http://localhost:8000/admin/logs

# Получение определенного количества строк
curl http://localhost:8000/admin/logs?lines=50

**Примеры использования микросервиса:**

_______________________________________
Описание endpoints микросервиса:

1.Основные страницы (GET):

  /                   - главная страница
  /OCR/               - страница распознавания текста
  /search/            - страница поиска с фильтрами
  /admin/             - панель администратора
  /tests/             - страница тестов

2. Работа с OCR:
  POST /upload/
      - загрузка и распознавание файла
      - параметры: 
          file: файл изображения
          lang: язык распознавания (например "rus+eng")
      - возвращает: {status: bool, text: str}

  GET /get_languages/
    - получение списка доступных языков
    - возвращает: список поддерживаемых языков

3. Работа с записями:
  GET /records/
      - получение всех записей
      - возвращает: список записей [{id, date_time, file_name, ocr_txt, status}, ...]

  POST /delete_records
      - удаление записей по ID
      - параметры: {record_ids: [int, int, ...]}
      - возвращает: {status: "success"} или ошибку

4. Работа с email:
  POST /send_email/
      - отправка текста на email
      - параметры: {to_email: str, text: str}
      - возвращает: {status: "success"} или ошибку

  POST /admin/email_config
    - сохранение настроек SMTP
    - параметры: {
        smtp_server: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str
    }
    - возвращает: {status: "success"} или ошибку

5. Тестирование:
  GET /run_test/{test_type}
      - запуск тестов
      - test_type: all, endpoints, repository, ocr
      - возвращает: {output: str} с результатами тестов

6. Логирование:
  GET /admin/logs
      - получение логов
      - параметры: lines (int, опционально) - количество строк
      - возвращает: {logs: str}
      
Все endpoints возвращают данные в формате JSON, кроме страниц с HTML-интерфейсом.