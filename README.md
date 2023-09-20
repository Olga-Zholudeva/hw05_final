# hw05_final

## Добавляем новые опции в [социальную сеть Yatube](https://github.com/Olga-Zholudeva/hw03_forms)

### Описание проекта:

- Реализована система подписок на авторов
- Выведены иллюстрации к постам:
  - в шаблон главной страницы
  - в шаблон профайла автора
  - в шаблон страницы группы
  - на отдельную страницу поста
- Написаны тесты, которые проверяют, что при выводе поста с картинкой изображение передаётся:
  - в словаре context
  - на главную страницу,
  - на страницу профайла,
  - на страницу группы,
  - на отдельную страницу поста;
  - при отправке поста с картинкой через форму PostForm создаётся запись в базе данных;
- Создана система комментариев
- Реализована система комментирования записей. На странице поста под текстом записи выводится форма для отправки комментария, а ниже — список комментариев. Комментировать могут только авторизованные пользователи. 
- Реализовано кеширование главной страницы


### Технологии:

Python 3.7
Django 2.2.19

### Запуск проекта:

- Клонируем репозиторий: **git clone [hw05_final](https://github.com/Olga-Zholudeva/hw05_final)**
- Cоздаем и активировируем виртуальное окружение: **python3 -m venv env source env/bin/activate**
- Устанавливаем зависимости из файла requirements.txt: **pip install -r requirements.txt**
- Переходим в папку yatube: **cd yatube**
- Применяем миграции: **python manage.py makemigrations**
- Создаем супер пользователя: **python manage.py createsuperuser**
- Применяем статику: **python manage.py collectstatic**
- Запускаем проект на локальном устройстве: **python3 manage.py runserver**

### Проект выполнила:

**Ольга Жолудева**
