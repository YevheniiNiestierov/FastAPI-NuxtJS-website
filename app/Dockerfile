FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./app
CMD ["sh", "-c", "until python -m app.create_admin; do echo 'Waiting for DB...'; sleep 3; done && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
