FROM python:3.13.12-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip==26.0.1 \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["sh", "/app/scripts/start.sh"]
