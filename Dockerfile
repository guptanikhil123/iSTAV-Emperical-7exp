FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Ensure requirements.txt includes: fastapi, uvicorn, httpx, openai, pandas, matplotlib, python-dotenv
RUN pip install --no-cache-dir -r requirements.txt
