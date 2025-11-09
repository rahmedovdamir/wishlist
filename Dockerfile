FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    libpq-dev gcc gettext \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r celeryuser && useradd -r -g celeryuser celeryuser

RUN chown -R celeryuser:celeryuser /app

USER celeryuser

RUN python manage.py collectstatic --noinput

CMD ["sh", "-c", "python manage.py migrate && gunicorn wishlist.wsgi:application --bind 0.0.0.0:8000 --workers 3"]