# Stage 1: Build Frontend
FROM node:18-alpine as frontend_builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Backend & Runtime
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies (Chrome for Selenium/Puppeteer)
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl ca-certificates \
    libxss1 libappindicator1 libgconf-2-4 \
    fonts-liberation libasound2 libnspr4 libnss3 \
    libx11-xcb1 libxtst6 lsb-release xdg-utils libgbm1 \
    --no-install-recommends \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.com.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build from stage 1
# Backend expects static files at ../frontend/dist
COPY --from=frontend_builder /app/frontend/dist /app/frontend/dist

# Set permissions for Chrome (optional but good practice)
RUN useradd -m appuser
USER appuser

# Environment variables
ENV PORT=8000
ENV HEADLESS_MODE=true
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
