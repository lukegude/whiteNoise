#!/bin/bash

IMAGE_NAME="whitenoise"

build_image() {
    echo "Building Docker image..."
    docker build -t $IMAGE_NAME .
}

run_container() {
    echo "Running Docker container..."
    docker run -it --rm \
        -p 5000:5000 \
        --device /dev/snd \
        -e PULSE_SERVER=unix:/run/pulse/native \
        -v /run/pulse:/run/pulse \
        -v /etc/asound.conf:/etc/asound.conf:ro \
        -v /dev/shm:/dev/shm \
        -v /var/run/dbus:/var/run/dbus \
        -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
        --group-add $(getent group audio | cut -d: -f3) \
        --privileged \
        $IMAGE_NAME
}

if [ "$1" = "build" ]; then
    build_image
    exit 0
fi

if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
    echo "Docker image not found. Building first..."
    build_image
fi

run_container