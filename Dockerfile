FROM python:3.12-slim

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install system dependencies (Tesseract + OpenCV requirements)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port (Render uses 10000)
EXPOSE 10000

# Start server
CMD ["gunicorn", "medisync_360.wsgi:application", "--bind", "0.0.0.0:10000"]