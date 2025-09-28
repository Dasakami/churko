FROM python:3.11-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefer-binary -r requirements.txt

COPY . .
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "churko.asgi:application"]
