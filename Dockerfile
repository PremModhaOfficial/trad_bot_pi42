# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (optional, you can set them during runtime)
# ENV API_KEY your_api_key
# ENV SECRET_KEY your_secret_key

# Run the bot
CMD ["python", "run.py"]