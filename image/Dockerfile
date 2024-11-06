FROM docker.io/library/debian:bookworm-slim

RUN apt-get update && \
    apt-get --no-install-recommends install --yes \
        cloud-image-utils \
        dhcpcd-base \
        ipmitool \
        iproute2 \
        openipmi \
        ovmf \
        procps \
        python3 \
        python3-yaml \
        qemu-utils \
        qemu-system-x86 \
        telnet

ARG UBUNTU_VERSION=noble
ARG UBUNTU_IMG_URL="https://cloud-images.ubuntu.com/$UBUNTU_VERSION/current/$UBUNTU_VERSION-server-cloudimg-amd64.img"

ADD "${UBUNTU_IMG_URL}" /ubuntu.img

COPY . /

ENTRYPOINT ["/entrypoint.sh"]
