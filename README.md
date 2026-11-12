# Автоматизация UI-тестирования формы регистрации

Учебная практика: МВЕК, ИСП, 4 курс.  
Дисциплина: Тестирование веб-приложений.  
Занятие 11: Проект воркшопа 1.

Проект автоматизированного UI-тестирования модуля регистрации веб-приложения на базе **Python**, **Selenium WebDriver**, **pytest** и **Allure Report**.

В качестве целевого стенда используется полигон: `https://demowebshop.tricentis.com/register` (или `https://practicesoftwaretesting.com/auth/register`).

---

## 1. Системные требования

* Python 3.10+
* Браузер Google Chrome и/или Mozilla Firefox
* Утилита командной строки `allure` (для генерации интерактивных веб-отчетов)

---

## 2. Развертывание и установка

```bash
# 1. Создание виртуального окружения
python -m venv .venv

# Активация окружения:
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 2. Обновление pip и установка зависимостей
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Базовый запуск
python -m pytest

# Запуск только в Google Chrome
python -m pytest --test-browser=chrome

# Запуск только в Mozilla Firefox
python -m pytest --test-browser=firefox

# 4. Запуск в фоновом (Headless) режиме
# Windows
$env:HEADLESS="true"; python -m pytest --test-browser=chrome

# Linux
HEADLESS=true python -m pytest --test-browser=chrome

# 5. Формирование и просмотр Allure-отчета
allure serve allure-results
