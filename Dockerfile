FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    cron \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libasound2 \
    fonts-liberation \
    fonts-noto-core \
    fonts-noto-extra \
    fonts-noto-unhinted \
    fonts-noto-ui-core \
    fonts-noto-color-emoji \
    fonts-noto-cjk \
    fonts-indic \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install chromium

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "--timeout", "120", "-b", "0.0.0.0:5000", "app:create_app()"]
