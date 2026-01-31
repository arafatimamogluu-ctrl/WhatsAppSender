# Base image
FROM python:3.9-slim

# Install system dependencies (Chrome, libs)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    # Chrome dependencies
    libxss1 \
    libappindicator1 \
    libgconf-2-4 \
    fonts-liberation \
    libasound2 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.com.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Build frontend (requires Node)
# Multi-stage build is better, but for simplicity let's install node here or just assume we commit 'dist' (User hasn't committed dist usually).
# Let's install Node to build frontend.
# Install Node.js 18 (required for Vite)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs
WORKDIR /app/frontend
RUN npm install && npm run build

# Go back to backend
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Environment variables
ENV PORT=8000
ENV HEADLESS_MODE=true

# Command to run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
