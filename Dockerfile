# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (optional, you can set them during runtime)
ENV API_KEY 74b2ebd6f711129dff3c39688dba89da
ENV SECRET_KEY 3353f4d802a8e3b8dd9d15af2704be13
ENV PI42_API_KEY 74b2ebd6f711129dff3c39688dba89da
ENV PI42_API_SECRET 3353f4d802a8e3b8dd9d15af2704be13

# Run the bot
CMD ["python3", "run.py"]
