# Инструкция по развертыванию проекта

1. **Клонируйте репозиторий и перейдите в его папку:**
   ```bash
   git clone git@github.com:karanovon/api_yamdb.git
   cd api_yamdb
   ```

2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Установите зависимости из файла `requirements.txt`:**
   ```bash
   python3 -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Выполните миграции для настройки базы данных:**
   ```bash
   python3 manage.py migrate
   ```

5. **Запустите сервер разработки:**
   ```bash
   python3 manage.py runserver
   ```

---

## Загрузка данных в базу

Этот проект поддерживает загрузку данных из CSV-файлов с помощью специальной команды Django. Для наполнения базы данных выполните следующую команду:

```bash
python manage.py import_csv_to_db
```