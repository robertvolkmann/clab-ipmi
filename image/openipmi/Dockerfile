FROM docker.io/library/debian:bookworm-slim

RUN apt-get update && \
    apt-get --no-install-recommends install --yes \
        ipmitool \
        iproute2 \
        openipmi \
        procps \
        python3 \
        telnet

COPY chassiscontrol.py lancontrol.py ipmisim1.emu lan.conf /

ENTRYPOINT ["/usr/bin/ipmi_sim", "-c", "/lan.conf", "-f", "/ipmisim1.emu"]
