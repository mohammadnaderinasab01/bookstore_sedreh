FROM python:3.11.4-slim-buster

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY . code
WORKDIR /code

EXPOSE 8000

# runs the production server
CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000