# Use the official lightweight Python image
FROM python:3.10.8

# Set the working directory inside the container
WORKDIR /app

# Copy the application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8080

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

#Permission for uploads folder
RUN mkdir -p /app/uploads && chmod -R 777 /app/uploads

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]


