
FROM python:3.12-slim

WORKDIR /app

# Copy Flask frontend
COPY front2/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create persistent database directory
RUN mkdir -p /app/database

# Flask port
EXPOSE 5000

# Start Flask using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "wsgi:app"]
