# Use an official Python runtime as a parent image
FROM python:3.8.18-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# RUN ls
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r backend/flask/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable

# Run app.py when the container launches
CMD ["uvicorn", "backend.flask.app:app", "--host", "0.0.0.0", "--port", "80"]
