# Тестовое задание
``` 
git clone https://github.com/Sosylka19/test.git
``` 

```
cd test
```
Установить бота в зулипе и скопировать zuliprc в директорию src.model

Также сделать .env файл со след полями:
>ZULIP_EMAIL = "<BOT_NAME>@<Домен зулипа или вашего сервера>"

>ZULIP_API_KEY = "<BOT_API_KEY>"

Инструкция по установке бота в зулипе [instruction](https://zulip.com/api/configuring-python-bindings#download-a-zuliprc-file)

```
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```
Команда ниже выполняется ~7 минут, загружая 90+% CPU
```
python -m src.parser.parser && python -m src.model.model
```

Поля в отчете по пользователям, которые не имеют аватарку в `data/no_avatars.txt`:
> emails, last_time_active

Поля в отчете по пользователям, у которых аватар не валидный(процент лица на фото меньше заданного threshold или нет лица на фото) в `data/faces_summary.csn`:
>url, email, face_area_percantage, last_time_active
