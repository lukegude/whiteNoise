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
        -v /run/user/$(id -u)/pulse:/run/user/$(id -u)/pulse \
        -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
        -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
        -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
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