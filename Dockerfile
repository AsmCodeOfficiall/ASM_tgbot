FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app



COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

COPY bot/requirements.txt ./bot/
RUN pip install --no-cache-dir -r bot/requirements.txt

COPY . .

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/app

CMD ["python", "run.py"]
