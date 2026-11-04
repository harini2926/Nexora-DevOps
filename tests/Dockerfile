
FROM python:3.12-slim

WORKDIR /tests

RUN pip install --no-cache-dir pytest selenium

RUN mkdir -p /reports

COPY test_app.py .

CMD ["pytest", "-v", "--junitxml=/reports/results.xml", "test_app.py"]
