FROM python:3.13-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install project dependencies
RUN pipenv install --system --deploy

# Install Playwright directly
RUN pip install playwright
RUN playwright install-deps
RUN playwright install

# Copy entire project
COPY . .

# Expose port 8000
EXPOSE 8000

# Default command to run the app
# Overriding this on Render to 1 because it may have OOM issues on free tier
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "app:app"]