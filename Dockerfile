FROM python:3.11.3-alpine3.17

WORKDIR /usr/src/app

COPY requirements.txt .

RUN echo "Installing python libraries..." \
  && pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8086"]

EXPOSE 8086