# api_yamdb
#### Проект YaMDb
Проект YaMDb собирает отзывы пользователей на различные произведения.
# Подробное описание см. http://51.250.109.37/redoc/

Status of Last Deployment:<br>
<img src="https://github.com/ivan-khmara/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg"><br>

# шаблон наполнения env-файла
	DB_ENGINE=****                       # тип базы данных
	DB_NAME=****                         # имя базы данных
	POSTGRES_USER=****                   # логин для подключения к базе данных
	POSTGRES_PASSWORD=*******            # пароль для подключения к БД
	DB_HOST=****                         # название сервиса
	DB_PORT=****                         # порт для подключения к БД

	SECRET_KEY = '*****'                 # Секретный ключ Django проекта

# описание команд для запуска приложения в контейнерах
docker-compose up -d --build

# Лицензия
api_yamdb это программное обеспечение с открытым исходным кодом, распространяемое по лицензии MIT.

# Авторы:
	Иван Хмара
	Юрий Новиков
	Никита Новицкий
