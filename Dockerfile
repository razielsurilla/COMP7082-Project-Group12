FROM python:3.11-slim

# System deps (optional but recommended)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# NiceGUI runs uvicorn internally, but we expose 9090 for Fly.io
EXPOSE 9090

ENV PYTHONUNBUFFERED=1
ENV PORT=9090

# Run your NiceGUI app (modify path to your main file)
CMD ["python", "main.py"]
