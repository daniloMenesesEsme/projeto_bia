FROM python:3.9-slim-buster

WORKDIR /app

# Copy web_app's requirements.txt
COPY web_app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire web_app directory into the container's /app
COPY web_app/ .

# Copy the chatbot directory from project root
COPY chatbot/ ./chatbot/

CMD ["python", "app.py"]
