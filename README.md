# 📡 SensorsAPI

Python Async RESTful API built using FastAPI and Tortoise ORM,
designed to manage sensor data with PostgreSQL database.

## ❇️ Key features:

- good api documentation (Swagger UI made by FastAPI) 📄
- transactional operations and support for different databases (Tortoise ORM) 🗄
- easy deployment and scalability with Docker and Docker Compose 🚚
- models fields verification (Pydantics) 🖊
- user authentication (OAuth2) 🔑
- passwords encryption (Argon2) 🔒
- Docker container healthcheck :heart:
- testing with PyTest in test SQLite DB (not on production DB) ✅

## 🛂 Requirements:

- Internet connection (to build) 📶
- Docker 📦
- Docker Compose 🚛
- WSL (on Windows) 💻

## ⚙️ Build and run

1. set enviromental variables like:

- DB_NAME
- DB_USER
- DB_PASSWORD
- JWT_SECRET

2. Run command:

```bash
docker compose up
```

## ✅ Testing

Run this command in project files inside docker container:

```bash
python3 -m pytest
```
