# AI rematch — prompt v2 (improved)

Containerize a FastAPI task CRUD API onto PostgreSQL with Docker Compose. Hard rules:

1. Two services: `api` (built from a Dockerfile) and `db` (official `postgres:16` image).
2. `db` MUST have a named **volume** so data survives `docker compose down && up`.
3. The api reaches the db by the service name **`db`**, never `localhost`.
4. The Postgres password comes from **`.env`** (`${POSTGRES_PASSWORD}`); it is NEVER hardcoded in the compose file or the app. Commit a `.env.example`, git-ignore `.env`.
5. `db` has a **healthcheck** (`pg_isready`) and `api` uses `depends_on: condition: service_healthy`.
6. All SQL uses psycopg `%s` **parameterized** placeholders — no f-strings.
7. `tasks` table (id SERIAL PK, title TEXT, done BOOLEAN) created if missing; seed 3 rows ONLY when the table is empty.
8. Endpoints and status codes identical to A1/A2: 200/201/204/400/404 with JSON `{"error": ...}`.

Quarantine under ai-version/.
