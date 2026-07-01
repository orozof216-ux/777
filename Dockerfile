# Python image
FROM python:3.10

# рабочая папка
WORKDIR /app

# зависимости
COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# копируем проект
COPY . /app/

# порт
EXPOSE 8000

# запуск
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]