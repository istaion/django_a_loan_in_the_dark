FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential \
    curl \
    apt-utils \
    gnupg2 && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && \
    env ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN apt-get update && \
    apt-get install -y redis-server

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONUNBUFFERED 1
ENV ODBCINI=/etc/odbc.ini

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app/

EXPOSE 80

CMD service redis-server start && python manage.py migrate && python init_db.py && daphne -b 0.0.0.0 -p 80 djangoApp.asgi:application



