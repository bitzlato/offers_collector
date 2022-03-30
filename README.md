# Offers-collector

## Setup

### source
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### docker
```bash
docker-compose build
```

#### RUN postgres
```bash
docker run --name postgres_server -e POSTGRES_PASSWORD=1 -p 0.0.0.0:5432:5432 -d postgres
```

## Сonfiguration
create .env file and update variables
```bash
cp .env.example .env
```

create .api_key.json file and update
```bash
cp .api_key.json.example .api_key.json
```


## Start
### source
```bash
python app.py
```

### docker
```docker

```

# offers_collector
