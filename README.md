# Offers-collector

## Setup

### source
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
or
### docker
```bash
docker-compose build
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
python app.py   # run web ui
python collector.py # run collector
```
or

### docker
```bash
docker-compose up db web collector
```