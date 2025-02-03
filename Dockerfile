# Use the official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]
