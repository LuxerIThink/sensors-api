# 📡 SensorsAPI

Python Async RESTful API built using FastAPI and Tortoise ORM,
designed to manage sensor data with PostgreSQL database.

## 📦 DB Structure:

![Sensors API DB Strudture](docs%2FSensorsAPI.drawio.svg)

## ❇️ Key features:

- FastAPI async RESTful API 📄
- Tortoise ORM async transactional PostgreSQL management 🗄
- Docker and Docker Compose easy deployment 🚚
- Pydantics models fields verification 🖊
- OAuth2 user authentication 🔑
- Argon2 passwords encryption 🔒
- Docker container healthcheck :heart:
- PyTest automatic tests with mock SQLite3 database ✅
- Extended searching options by parameters for GET requests 🔎
- Preview shared devices and their children 🔗

## 🛂 Requirements:

- Internet connection (to build) 📶
- Docker 📦
- Docker Compose 🚛
- WSL and Docker Desktop (on Windows) 💻

## ⚙️ Build and run

1. Set environmental variables:

- DB_NAME
- DB_USER
- DB_PASSWORD
- JWT_SECRET

2. Run command:

```bash
docker compose up
```

## ✅ Testing and Coverage

Run this command inside docker container:

```bash
pytest --cov=.
```
