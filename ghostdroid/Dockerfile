FROM python:3.11-slim

LABEL maintainer="GhostDroid Team"
LABEL description="GhostDroid CLI - Ethical Android Security Testing Framework"
LABEL version="2.0.1"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    android-tools-adb \
    android-tools-fastboot \
    usbutils \
    nmap \
    net-tools \
    iputils-ping \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ghostdroid

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p reports logs database payloads/generated

RUN chmod +x main.py

RUN useradd -m -s /bin/bash ghostdroid && \
    chown -R ghostdroid:ghostdroid /opt/ghostdroid

USER ghostdroid

ENTRYPOINT ["python3", "main.py"]
CMD ["--help"]
