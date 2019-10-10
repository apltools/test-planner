# Test planner

## How to deploy

### Create a `.env`-file

```shell script
SECRET_KEY=
DATABASE=postgres
SQL_ENGINE=django.db.backends.postgresql
SQL_NAME=postgres
SQL_USER=postgres
SQL_HOST=db
SQL_PORT=5432
```

Please add a `SECRET_KEY`, to this file


### Generate `SECRET_KEY`
```python
import random
''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])
```

### Start the server
```shell script
# Start containers
docker-compose -f docker-compose.prod.yml up -d
# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```