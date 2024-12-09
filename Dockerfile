FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y \
    libasound2-dev \
    pulseaudio \
    sox \
    libsox-fmt-all \
    bluez \
    bluez-tools \
    pulseaudio-module-bluetooth \
    expect \
    libbluetooth-dev \
    build-essential \
    dbus-x11 \
    dbus


RUN gcc whitenoise.c -o out


RUN usermod -a -G audio root
RUN usermod -a -G pulse root
RUN usermod -a -G pulse-access root
RUN usermod -a -G bluetooth root
RUN usermod -a -G lp root



EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

CMD ["flask", "run"]

