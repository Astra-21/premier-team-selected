FROM python:3.10

WORKDIR /app

COPY ./app /app/app
COPY .env /app/.env
COPY requirements.txt /app/

RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


