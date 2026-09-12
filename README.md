# Drink API

A small Flask + SQLite REST API for managing drinks.

## Features
- List drinks with search and pagination
- Get a single drink by ID
- Create, update, and delete drinks
- Basic input validation for safer requests

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python application.py
```

The server runs at `http://127.0.0.1:5000`.

## Endpoints
- `GET /` — API welcome message
- `GET /drinks?q=<keyword>&page=1&per_page=10` — list drinks
- `GET /drinks/<id>` — get one drink
- `POST /drinks` — create drink
- `PUT /drinks/<id>` — replace drink
- `PATCH /drinks/<id>` — partially update drink
- `DELETE /drinks/<id>` — delete drink

## Example Create Request
```bash
curl -X POST http://127.0.0.1:5000/drinks \
  -H "Content-Type: application/json" \
  -d '{"name":"Iced Tea","description":"Chilled black tea"}'
```
