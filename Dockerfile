# Slim, single-stage image for the FastAPI app.
FROM python:3.12-slim

WORKDIR /app

# Install deps first so Docker can cache this layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
