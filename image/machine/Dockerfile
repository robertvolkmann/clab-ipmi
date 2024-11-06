FROM docker.io/library/debian:bookworm-slim

RUN apt-get update && \
    apt-get --no-install-recommends install --yes \
        cloud-image-utils \
        iproute2 \
        ovmf \
        python3 \
        python3-yaml \
        qemu-utils \
        qemu-system-x86 \
        telnet

ARG UBUNTU_VERSION=noble
ARG UBUNTU_IMG_URL="https://cloud-images.ubuntu.com/$UBUNTU_VERSION/current/$UBUNTU_VERSION-server-cloudimg-amd64.img"

ADD "${UBUNTU_IMG_URL}" /ubuntu.img

RUN qemu-img resize /ubuntu.img 50G

ENTRYPOINT ["/launch.py"]

COPY mirror_tap_to_eth.sh remove_mirror.sh launch.py /
