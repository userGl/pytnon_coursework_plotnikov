# pytnon_coursework_plotnikov
Курсовая работа студента ТГУ Плотникова Г.А. по предмету "Программирование на Python: углубленный курс"
"Микросервис для анализа текста на изображениях (OCR)"

______________________________________________________
Из задания на курсовой проект:
Решаемые задачи:
• Использование библиотеки  Tesseract для OCR.
• Создание API с использованием FastAPI.
• Валидация данных (Проверка, что изображение содержит текст).
• Хранение результатов в базе данных и отображение их через frontend.
_______________________________________________________

Сервис организован на базе web фреймворка FastAPI и Tesseract



Администратор
1.Добавление/изменение/удаление данных пользователя:
1.1 Авторизуется под учётными данными администратора;
1.2 Заходит на страницу "Пользователи";
1.3 Добавляет/изменяет/удаляет учётные данные пользователя (login, password, e-mail);
1.4 Сервис сохраняет/изменяет/удаляет учётные данные пользователя. При удалении пользователя удаляются файлы пользователя из хранилища.

Администратор
2.Просмотр служебной информации администратором:
2.2 см 1.1;
2.3 Администратор заходит на страницу "Журнал";
2.4 Сервис отображает названия загруженных документов, размер документа, дату и время загрузки, время обработки документа, имя пользователя и почту на которую был выслан результат.

Пользователь
3. Распознование документа:
3.1. Пользователь открывает страницу сервиса и авторизуется;
3.2. Пользователь переходит на страницу загрузки документа для распознавания текста;
3.3. Пользователь загружает документ с изображения в формате jpg;
3.4. Сервис сохраняет загруженный документ в директорию "temp";
3.5. Сервис выполняет проверку документа на корректность и в случае успеха запускает процесс распознавания текста;
3.6. Сервис помещает файл распознаный документ в папку пользователя в хранилище (формат docx). Файл в папке "temp" удаляется.
3.7. В результате обработки документа пользователь получает на почту тестовый документ в формате ".docx" в котором находится распознанный текст загруженного документа.

4. Просмотр документа:
4.1 См. 3.1
4.2 Пользователь переходит на страницу сохранённых документов;
4.3 Сервер отображает список документов пользователя;
4.4 Пользователь выбирает документ для просмотра/повторной отправки на mail.
4.5 Сервис отображает/отправляет на mail выбранный документ из хранилища;

5. Удаление документов
5.1 Пользователь выполняет пункты 4.1 и 4.2
5.2 Пользователь выбирает файлы для удаления и подтверждает удаление.
5.3 Сервис удаляет выбранные файлы из хранилища.







Действия администратора:
1.


Пользователь подключившись к web странице сервера может:
1.Просмотреть ранее загруженные документы и результаты сканирования;
2.Загрузить документы в графическом формате (jpg, png, bmp) на сервер;
3.Удалить не нужные документы в графическом / текстовом формате;
4.Выбрать язык/языки распознования;
5.Производить распознование графического файла;
6.Произвести редактирование распознаного текста в ручном режиме;
7.Отправить распознанный / отредактированный текстовый документ на указанный e-mail.

Для работы программы необходимо установить соответствующий бинарный файл программы. Для деталей см:
https://github.com/tesseract-ocr/tessdoc?tab=readme-ov-file#binaries

Так же необходимо установить зависимости из файла requirements.txt

Для запуска web сервера наберите в командной строке: uvicorn app:app