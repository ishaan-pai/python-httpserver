FROM python:3.11-slim

WORKDIR /app

COPY ./src ./src

WORKDIR /app/src

EXPOSE 8000

CMD ["python", "main.py", "functions.py"]
