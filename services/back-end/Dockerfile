FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/back-end/src

WORKDIR /app/back-end

COPY back-end/pyproject.toml ./pyproject.toml
COPY back-end/src ./src
COPY back-end/institution-profile.md ./institution-profile.md

RUN pip install --upgrade pip && pip install .

COPY datasets /app/datasets

EXPOSE 8000

CMD ["uvicorn", "app.main:create_application", "--factory", "--host", "0.0.0.0", "--port", "8000"]
