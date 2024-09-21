FROM python:3.10-alpine
RUN apk update && \
    apk add --virtual build-deps gcc zlib-dev && \
    apk add postgresql-dev
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8001"]