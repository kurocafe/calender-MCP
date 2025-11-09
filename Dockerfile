FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY ./app/* .

# Create directory for credentials and tokens
RUN mkdir -p /mcp-data && \
    useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app /mcp-data

USER mcpuser

CMD ["python3", "google_calendar_mcp_server.py"]