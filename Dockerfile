FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Expose the HTTP and socket ports
EXPOSE 5000 5001

# Default command runs the Flask app. Ensure `app.py` binds 0.0.0.0 for container access.
CMD ["python", "app.py"]
