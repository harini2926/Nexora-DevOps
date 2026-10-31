FROM python:3.12-slim

WORKDIR /app

COPY front2/ /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m compileall -q /app

RUN mkdir -p /app/database

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "wsgi:app"]
