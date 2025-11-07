# Инструкция по установке Python 3.11

## Windows

### Вариант 1: Через официальный сайт Python

1. Перейдите на https://www.python.org/downloads/
2. Скачайте Python 3.11.x (последняя версия 3.11)
3. Запустите установщик
4. **Важно**: Отметьте галочку "Add Python to PATH"
5. Выберите "Install Now" или "Customize installation"
6. После установки перезапустите терминал

### Вариант 2: Через Microsoft Store

1. Откройте Microsoft Store
2. Найдите "Python 3.11"
3. Нажмите "Установить"

### Вариант 3: Через pyenv (для продвинутых пользователей)

1. Установите pyenv-win: https://github.com/pyenv-win/pyenv-win
2. Установите Python 3.11:
```bash
pyenv install 3.11.10
pyenv local 3.11.10
```

## Проверка установки

После установки проверьте версию:
```bash
python --version
# Должно показать: Python 3.11.x
```

## Создание нового виртуального окружения

После установки Python 3.11:

1. Удалите старое виртуальное окружение (если есть):
```bash
# Windows
rmdir /s venv
# Linux/Mac
rm -rf venv
```

2. Создайте новое виртуальное окружение с Python 3.11:
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

4. Обновите pip:
```bash
python -m pip install --upgrade pip
```

5. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Если у вас установлено несколько версий Python

Если у вас установлено несколько версий Python, вы можете использовать:

- `python3.11` вместо `python`
- `py -3.11` (Windows) для выбора конкретной версии

Пример:
```bash
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```




