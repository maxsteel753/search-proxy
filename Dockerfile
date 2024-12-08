# Use the official Python image from the DockerHub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app/

# Copy the requirements file and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --retries 5 --timeout 30

# Copy the content of the app to the container
COPY . .

# Specify the command to run on container start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#CMD ["fastapi", "run", "app/main.py", "--port", "80"]
