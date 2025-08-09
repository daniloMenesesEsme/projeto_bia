FROM python:3.9-slim-buster

WORKDIR /app

COPY web_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "web_app/app.py"]
