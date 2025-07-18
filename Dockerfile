FROM python:3.8

WORKDIR /home/debater

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

# Install test dependencies
RUN pip install pytest requests redis

COPY . .

EXPOSE 8000

# Production command (no reload) - use shell to expand $PORT
CMD uvicorn debater.app:app --host 0.0.0.0 --port ${PORT:-8000}
