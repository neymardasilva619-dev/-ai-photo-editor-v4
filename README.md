# AI Photo Editor v4

AI-фоторедактор с загрузкой фото, маской, AI-редактированием, фильтрами, Undo/Redo и экспортом PNG.

## Важно
GitHub хранит код, но сам по себе не запускает Python/Flask-сервер. Для рабочей онлайн-версии этот репозиторий нужно подключить к хостингу, например Render, и добавить секрет `OPENAI_API_KEY` в настройках сервиса.

## Файлы
- `index.html` — интерфейс редактора
- `server.py` — Flask-сервер и AI API
- `requirements.txt` — зависимости Python
- `Procfile` — команда запуска на хостинге
- `render.yaml` — конфигурация Render

## Переменная окружения
На сервере создайте:

`OPENAI_API_KEY=ваш_ключ`

Не вставляйте API-ключ в `index.html` и не загружайте `.env` в GitHub.

## Локальный запуск
```bash
pip install -r requirements.txt
python server.py
```
Затем откройте `http://127.0.0.1:8787`.
