FROM python:3.10-slim

COPY hello-app.py ./

RUN pip install fastapi uvicorn[standard] >/dev/null 2>&1

CMD uvicorn hello-app:app --host 0.0.0.0
