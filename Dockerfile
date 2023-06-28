FROM python:3.11.3-alpine3.17

WORKDIR /usr/src/app

COPY requirements.txt .

RUN echo "Installing packages..." \
  && apk add --no-cache curl

RUN echo "Installing python libraries..." \
  && pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8086"]

EXPOSE 8086

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8086/docs || exit 1
