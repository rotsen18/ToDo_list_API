# ToDo list API

API service for manage your todo tasks with email notification

## Installation and launch

Python must already be installed on your system

If you want to run locally, PostgreSQL server must be installed and 
a database must be created with the appropriate user

```shell
git clone https://github.com/rotsen18/ToDo_list_API.git
cd ToDo_list_API
python -m venv venv
venv/scripts/activate
pip install -r requirements.txt
set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your db username>
set DB_PASSWORD=<your db user password>
set SECRET_KEY=<your secret key>
python manage.py runserver
```

If you want to activate debug option you may set env
```shell
set DEBUG=True
```

## Run with docker

Docker should be installed
Fill required env variables in `.env` file

```shell
docker-compose build
docker-compose up
```

## Getting access

All documentation in two different styles is located at:
* /api/doc/swagger/
* /api/doc/redoc/

- create user at `/api/user/register/`
- get access token on `/api/user/token/`
- now every request should contain header:
`Authorisation: Bearer <your access token>`

for update access token you should post your refresh token at:
`/api/user/token/refresh/`

If you want to create admin user you should add superuser with command:
```shell
python manage.py createsuperuser
```

## Configure email

* Get an app key from Google (instructions: https://support.google.com/accounts/answer/185833?hl=en`)
* In settings.py `EMAIL_HOST_USER = "your@mail.adress"` add your real mail adress
* Create env variable with your app key
```shell
set "EMAIL_HOST_PASSWORD"=<your app key>
```

## Features

* Implemented JWT authorisation and permissions
* You can create todo task with title and description
* Every task may contain subscribers
* Email notification for subscriber. Your get mail when somebody has added you to task
* Task has 3 statuses: New, Active, Closed
* Editing and deleting task is allowed only by task author
* For every task you can add photos
* Tasks list may be filtered with selected status
