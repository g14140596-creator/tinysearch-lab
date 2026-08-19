FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY tinysearch ./tinysearch
COPY data ./data
RUN pip install --no-cache-dir . && tinysearch --db /app/data/tinysearch.db index data/sample

ENV TINYSEARCH_DB=/app/data/tinysearch.db
EXPOSE 8000
CMD ["tinysearch", "--db", "/app/data/tinysearch.db", "serve", "--host", "0.0.0.0", "--port", "8000"]
