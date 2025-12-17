# OpenLP → PDF (Web Converter)

Convert OpenLP service files (.osz) into beautifully themed PDF slides using OpenLP theme files (.otz) — all via a web interface.

currently active on https://openlp-to-pdf.duckdns.org/

## Built with

- Flask (web app)
- Redis + RQ (background jobs)
- Playwright (PDF rendering via Chromium)
- Tailwind CSS + Nord theme (frontend)
- Docker & Docker Compose (production-ready deployment)

## ✨ Features

- Upload OpenLP .osz and .otz files
- Auto-extract slides from services
- Render slides as themed PDFs
- Background image + gradient + color support
- Supports Unicode / Hindi / Devanagari / CJK / Emoji
- Live job status updates
- Clean Nord-themed frontend (light/dark mode)
- Automatic cleanup with daily housekeeper job
- Fully Dockerized
- Scales via background workers

## 📂 Project Structure

```
.
├── app.py
├── controllers
│   ├── __init__.py
│   ├── download_controller.py
│   └── upload_controller.py
├── docker-compose.yml
├── Dockerfile
├── jobs
│   ├── __init__.py
│   ├── housekeeper_job.py
│   └── uploader_job.py
├── README.md
├── requirements.txt
├── routes
│   ├── __init__.py
│   └── web.py
├── scripts
│   └── scheduler.py
├── services
│   ├── __init__.py
│   ├── openlp_service.py
│   └── pdf_service.py
├── templates
│   ├── 404.html
│   ├── base.html
│   ├── error.html
│   ├── index.html
│   └── job.html
└── tmp
```

## ⚙️ Requirements

You only need:

- Docker >= 20
- Docker Compose plugin

No local Python required.

## 🚀 Quick Start (Docker)

Clone the project:

```sh
git clone https://github.com/yourname/openlp-to-pdf-web.git
cd openlp-to-pdf-web
```

### 1️⃣ Build everything

```sh
docker-compose build
```

### 2️⃣ Run the stack

```sh
docker-compose up
```

(Use -d to run in background)

```sh
docker-compose up -d
```

### 3️⃣ Open the app

Visit:

http://localhost:5000


Upload:

✅ `.osz` → service file

✅ `.otz` → theme file

## 🧵 Background Jobs

Jobs run using Redis + RQ.

Active containers:

|Container|Purpose|
|---------|-------|
|`openlp_web`|Web server|
|`openlp_worker`|RQ workers|
|`openlp_scheduler`|Cron jobs|
|`openlp_redis`|Redis DB|

## 📂 Temp Files

PDFs and job artifacts live in:

```sh
/app/tmp/<job_id>/
```


Access inside container:

```sh
docker exec -it openlp_worker bash
cd /app/tmp
ls
```

## 💾 Optional: Persist tmp directory locally

Edit docker-compose.yml:

```yml
volumes:
  - ./tmp:/app/tmp
```

Now files appear locally:

```sh
ls tmp/
```

## 🧹 Cleanup Strategy

This system uses a housekeeper job:

- 📅 Runs every minute, deletes jobs which are to deleted, and also deletes the `tmp` directories associated with the job

## 🔎 Debugging Tips

### View logs

```sh
docker-compose logs -f openlp_worker
docker-compose logs -f openlp_web
```

### Restart everything

```sh
docker-compose down
docker-compose up --build
```

### Test Redis

```sh
docker exec -it openlp_redis redis-cli
keys *
```

### Check fonts

```ssh
docker exec -it openlp_worker fc-list
```

## ✍️ Environment Variables (Production)

add a `.env` at the root

```.env
# Flask
FLASK_SECRET_KEY=super-secret-change-me
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# OS
TMP_DIR=/app/tmp
```

## 🧪 Local Dev (optional, not required)

### Without Docker:

```sh
pip install -r requirements.txt
python app.py # main server

# on a second terminal
rq worker openlp-jobs # job server

# on a third terminal
PYTHONPATH=. python scripts/scheduler.py # housekeeper job
```

## 🎯 Limitations

- Video / livestream backgrounds are not supported in PDFs.
- PDFs are static.
- Some advanced OpenLP animations are ignored.
- Footer rendering can be added later.
- Font availability depends on Linux system.

## ✅ Supported Theme Features
|Feature|Supported|
|-------|---------|
|Background image|✅|
|Solid color|✅|
|Gradient|✅|
|Font size|✅|
|Alignment|✅|
|Unicode|✅|
|Hindi / Indic|✅|
|PDF output|✅|
|Video|❌|
|Animations|❌|

## ❤️ Credits
- OpenLP community (format + themes)
- Playwright (rock-solid PDF generation)
- Redis + RQ (job queue)
- Nord theme
- Flask + Tailwind CSS


## 🤝 Contributing

PRs welcome!
