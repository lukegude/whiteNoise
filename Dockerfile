# Use an official Python runtime as the parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
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



# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask to run in production mode
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["flask", "run"]

