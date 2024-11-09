# Base image with Python 3.10
FROM python:3.10.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
