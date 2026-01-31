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

# Install system dependencies (Chromium from official Debian repos)
# "chromium" package includes the browser
# "chromium-driver" package includes the WebDriver matches the browser version
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget curl unzip \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build from stage 1
COPY --from=frontend_builder /app/frontend/dist /app/frontend/dist

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Environment variables
ENV PORT=8000
ENV HEADLESS_MODE=true
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend
# Command to run (Shell form to allow $PORT expansion)
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
