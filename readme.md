# pokemon-league-api made with Flask

## Initial Setup

1. Virtual environment creation
 ```python3.11 -m venv .venv```

2. In ith VSCode, select .venv interpretor with [ Cmd+Shift+P / Ctrl+Shift+P ]

3. Install dependecies
 ```pip install -r requirements.txt```


## Server start up
Run with autoreload
```
flask --debug run
```

## Docker

```
docker build -t pokemon-league-api:latest . 
```
```
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" pokemon-league-api
```



## DB

Initialize db
```
flask db init
```

Detect and create migration
```
flask db migrate
```

Run migrations
```
flask db upgrade
```


### Others

Swagger URL
```http://localhost:5000/swagger-ui```