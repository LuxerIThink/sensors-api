FROM python:3.12.2-alpine3.19

COPY src/requirements.txt .

RUN echo "Installing packages..." \
  && apk update \
  && apk add --no-cache curl

RUN echo "Installing python libraries..." \
  && pip3 install --no-cache-dir -r requirements.txt

RUN addgroup -S app_group \
  && adduser -S app_user -G app_group
USER app_user

WORKDIR /app

COPY --chown=app_user:app_group src/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086"]

EXPOSE 8086
