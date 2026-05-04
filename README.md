## Parser auto.ria

Fast and asynchronous service for scraping AUTO.RIA listings, storing them in PostgreSQL, and managing parsing via API. It supports manual parsing and scheduled tasks through Celery.

### Features

- Parse listings from the AUTO.RIA search page.
- Store listings in the database (duplicate checks).
- Retrieve listings by different filters.
- Scheduled parsing jobs (Celery Beat).
- Export to CSV and VCF.

### Stack

- FastAPI
- PostgreSQL + SQLAlchemy (async)
- Celery + RabbitMQ
- Alembic

### Quick Start (Docker Compose)

1. Create a `.env` file from the example:

```bash
cp env.example .env
```

2. Start services:

```bash
docker-compose up --build
```

API will be available at `http://localhost:8000`, and Swagger at `http://localhost:8000/docs`.

### Environment Variables

Minimum set (see [env.example](env.example)):

- `DATABASE_URL`
- `CELERY_BROKER_URL`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

### Main Endpoints

#### Parsing

- `POST /parse/` — start parsing by URL
  - Parameters: `url` (str), `max_pages` (int, default 1)
- `GET /parse/get_csv_file` — export all to CSV
- `GET /parse/get_vcf_file` — export all to VCF

#### Listings

- `GET /adverts/all`
- `GET /adverts/id/{advert_id}`
- `GET /adverts/auto_id/{auto_id}`
- `GET /adverts/phone/{phone_number}`

#### Jobs

- `GET /jobs/` — list jobs
- `POST /jobs/` — create a job
- `PATCH /jobs/{job_id}` — update a job
- `POST /jobs/{job_id}/disable` — disable a job
- `POST /jobs/{job_id}/run` — run a job now (enqueue)

Example of creating a job:

```bash
curl -X POST "http://localhost:8000/jobs/" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://auto.ria.com/uk/search/?category_id=1", "max_pages": 2, "interval_hours": 6, "active": true}'
```

### Migrations

```bash
alembic upgrade head
```

### Notes

- Celery Beat checks jobs every 5 minutes.
- This service is not intended for multi-user usage yet. It can be easily added later.
- Please contact me if you find a bug or the parser stops working.
- Planned: add parsing via a Telegram bot.