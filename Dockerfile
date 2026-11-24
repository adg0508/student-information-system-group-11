FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --system sis
COPY app.py database.sql ./
COPY static/ static/
COPY templates/ templates/
USER sis
CMD ["sh", "-c", "exec gunicorn --preload --bind 0.0.0.0:${PORT:-5000} app:app"]
