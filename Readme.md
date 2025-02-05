
# Book Recommendation System
Этот проект представляет собой систему рекомендаций книг на основе графов. Проект включает:

-   **API**  для управления пользователями, книгами, авторами, жанрами и взаимодействиями.
    
-   **Веб-интерфейс**  для просмотра и управления данными.
***
## Установка и запуск
### 1. Требования

-   Python 3.11+
    
-   Redis (для кэширования)
    
-   PostgreSQL (как основная база данных)
    
-   Установленные зависимости из  `requirements.txt`
### 2. Установка зависимостей

1.  Создайте виртуальное окружение:
	```
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
	```
2.  Установите зависимости:
	```
    pip install -r requirements.txt
	```
### 3. Настройка Redis
1. Установите Redis (если ещё не установлен):

	- **Linux**:  `sudo apt install redis`
	- **Mac**:  `brew install redis`
	- **Windows**: Скачайте с  [официального сайта](https://redis.io/download).
2. Запустите Redis:
	```
	redis-server
	```
### 4. Подключение БД и Redis
1.  Создайте файл **.env** и заполните его по образцу **.env.sample**:
	```
    SECRET_KEY=django-insecure-12345!abcde67890!@#qwerty
    
    POSTGRES_DB=books_db
    POSTGRES_USER=books_user
    POSTGRES_PASSWORD=secure_password
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    
    LOCATION=redis://localhost:6379/0
	```
2. Примените миграции:
	```
	python manage.py migrate
	```
## Добавление тестовых данных
1. Запустите **!важно!** `generate_test_data`:
	```
	python manage.py generate_test_data
	```
	**Внимание!** `generate_test_data` удаляет старые записи, будье внимательны
	
2. Создайте суперпользователя:
	```
	python manage.py createsuperuser
	```
3. Используйте административную панель Django (`http://127.0.0.1:8000/admin/`) для добавления:
	-   Пользователей
	-   Книг
	-   Авторов
	-   Жанров
## Использование API
### 1. Регистрация и авторизация
 - **Регистрация**: `POST /api/users/register/`
	```
	{
		"email": "example@example.com"
		"password": "1234"
	}
	```
 - **Авторизация**: `POST /api/users/register/`
	```
	{
		"email": "example@example.com"
		"password": "1234"
	}
	```
	Ответ:
	```
	{
		"refresh": "your_refresh_token"
		"access": "your_access_token"
	}
	```
***
### 2. Управление данными
1. Добавление данных (с правами модератора `is_staff==True`):
	- **Жанры**: `POST api/genres/`, `PUT api/genres/`, `PATCH api/genres/<pk>/`
	- **Авторы**: `POST api/authors/`, `PUT api/authors/`, `PATCH api/genres/<pk>/`
	- **Книги**: `POST api/authors/`, `PUT api/authors/`, `PATCH api/genres/<pk>/`

2. Просмотр данных:
	- **Жанры**: `GET api/genres/`, `GET api/genres/<pk>/`
	- **Авторы**: `GET api/authors/`, `GET api/authors/<pk>/`
	- **Книги**: `GET api/genres/`, `GET api/genres/<pk>/`

3. Рекомендации:
	- **PageRank**: `GET api/users/me/pagerank/`
	- **Collaborative**: `GET api/users/me/collaborative/`
	- **k-NN**: `GET api/users/me/knn/`

4. Взаимодействия:
	- **Получить свои**: `GET api/interactions/pagerank/<int:user_id>/`
	- **Получить все**(с правами модератора `is_staff==True`): `GET api/interactions/pagerank/<int:user_id>/`
	- **Поставить/ изменить оценку**: `POST interactions/`, `PATCH interactions/<pk>/`
	```
		{
			"rating": 5.0
			"book": 733
		}
	```


5. Рекомендации(с правами модератора `is_staff==True`):
	- **PageRank**: `GET api/recommendations/pagerank/<int:user_id>/`
	- **Collaborative**: `GET recommendations/collaborative/<int:user_id>/`
	- **k-NN**: `GET recommendations/knn/<int:user_id>/`

6. Модерация (с правами модератора `is_staff==True`):
	- **Сменить статус `is_active` пользователя**: `POST api/users/<int:pk>/block/`

7. Статистика
	- **Получить статистику**: `GET api/statistics/`
## Использование веб-интерфейса
1. **Главная страница** `http://127.0.0.1:8000/books/`
	- навигация по основным разделам
2. **Рекомендации** `http://127.0.0.1:8000/books/recommendations/`
	- получение основных рекомендаций

## Авторы
[Ovechkin G.](https://github.com/goqwertys)