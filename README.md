# tournament

Проект турниров (Windows).

## Установка (Windows)

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка окружения

```cmd
copy .env.example .env
```

## Запуск проекта

```cmd
python app.py
```

Открой http://127.0.0.1:5000 в браузере.

## Как запушить в Git (пошагово)

```cmd
git init
git add .
git commit -m "init: tournament project"
git branch -M main
git remote add origin https://github.com/ТВОЙ_ЛОГИН/tournament.git
git push -u origin main
```
