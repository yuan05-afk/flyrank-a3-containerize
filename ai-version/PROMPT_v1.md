# AI rematch — prompt v1 (from memory)

Containerize my FastAPI task CRUD API onto Postgres with Docker Compose.

- Use psycopg to talk to Postgres.
- tasks table: id, title, done. Create it if missing, seed 3 tasks if empty.
- Keep the 5 endpoints (GET /tasks, GET /tasks/{id}, POST, PUT, DELETE) with the same behaviour.
- Use parameterized queries.
- Give me a Dockerfile and a docker-compose file so `docker compose up` starts the app and the database.
- The database password should come from the environment.

Put it in ai-version/.
