FROM python:3.13

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose frontend (Gradio) port
EXPOSE 7860
# Use `bash -c` to launch both in background
CMD bash -c "uvicorn backend.main:app --port 8000 & \
             python frontend/app.py --server-name 0.0.0.0 --server-port 7860 && wait"