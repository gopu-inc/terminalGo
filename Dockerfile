# Image dédiée au terminal
FROM ubuntu:22.04

# Installer apt complet + outils de base
RUN apt-get update && apt-get install -y \
    git curl build-essential python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier le serveur terminal
COPY terminal_server.py ./terminal_server.py
COPY requirements.txt ./requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 9000

CMD ["uvicorn", "terminal_server:app", "--host", "0.0.0.0", "--port", "9000"]
