FROM python:3.11.3-alpine3.17

COPY requirements.txt .

RUN echo "Installing packages..." \
  && apk add --no-cache curl

RUN echo "Installing python libraries..." \
  && pip3 install --no-cache-dir -r requirements.txt

RUN addgroup -S app_group \
  && adduser -S app_user -G app_group

USER app_user

WORKDIR /app

COPY --chown=app_user:app_group . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8086"]

EXPOSE 8086

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8086/docs || exit 1
