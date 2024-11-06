#!/usr/bin/python3
import fcntl
import logging
import math
import os
import signal
import socket
import struct
import subprocess
import sys
import time
import yaml

BASE_IMG = '/ubuntu.img'


class Qemu:
    def __init__(self, name: str, smp: str, memory: str, interfaces: int):
        self._name = name
        self._smp = smp
        self._memory = memory
        self._interfaces = interfaces
        self._p = None
        self._disk = '/overlay.img'
        self._iso = '/cloud-init.iso'

    def prepare_overlay(self, base: str) -> None:
        cmd = [
            'qemu-img',
            'create',
            '-f', 'qcow2',
            '-F', 'qcow2',
            '-b', base,
            self._disk,
        ]
        subprocess.run(cmd, check=True)

    # https://github.com/hellt/vrnetlab/blob/master/ubuntu/docker/launch.py
    def create_cloud_init_configuration(self):
        hostname = socket.gethostname()

        bootstrap_config = {
            'hostname': hostname,
            'fqdn': hostname,
            'users': [{
                'name': 'ansible',
                'groups': ['sudo'],
                'lock_passwd': False,
                'passwd': '$6$FK09vnVRTO.BxLwN$.RuqxV8BmY.J8r6qrXtn7WCr6WL0TD1M7wELEWQun8v1fEHIEMIpz0GzL8f2pMZkftklF1aecgLZ0UWVmww9m.',
                'shell': '/bin/bash',
                'sudo': ['ALL=(ALL) NOPASSWD:ALL'],
            }],
            'ssh_pwauth': True,
            'timezone': 'Europe/Berlin',
            'runcmd': [
                'touch /etc/cloud/cloud-init.disabled',
            ]
        }

        bootstrap_config_path = "/bootstrap_config.yaml"

        with open(bootstrap_config_path, 'w') as f:
            f.write("#cloud-config\n")
            yaml.dump(bootstrap_config, f, default_flow_style=False, width=math.inf)

        network_config = {
            'version': 2,
            'ethernets': {
                'eth0': {
                    'match': {
                        'macaddress': get_mac_address('eth0'),
                    },
                    'set-name': 'eth0',
                    'addresses': [get_ip_address('eth0') + '/16'],
                    'routes': [{
                        'to': 'default',
                        'via': get_default_gateway(),
                    }],
                    'nameservers': {
                        'addresses': ['9.9.9.9'],
                    }
                }
            }
        }

        network_config_path = "/network_config.yaml"

        with open(network_config_path, 'w') as f:
            yaml.dump(network_config, f, default_flow_style=False)

        cloud_localds_args = [
            "cloud-localds",
            "-v",
            f"--network-config={network_config_path}",
            self._iso,
            bootstrap_config_path,
        ]
        subprocess.run(cloud_localds_args, check=True)

    def start(self) -> None:
        cmd = [
            'qemu-system-x86_64',
            '-cpu', 'host',
            '-smp', self._smp,
            '-display', 'none',
            '-enable-kvm',
            '-nodefaults',
            '-machine', 'q35',
            '-name', self._name,
            '-m', self._memory,
            '-cdrom', self._iso,
            '-drive', 'if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd',
            '-drive', 'if=pflash,format=raw,file=/usr/share/OVMF/OVMF_VARS.fd',
            '-drive', f'if=virtio,format=qcow2,file={self._disk}',
            '-chardev', 'socket,id=ipmi0,host=127.0.0.1,port=9002,reconnect=10',
            '-device', 'ipmi-bmc-extern,id=bmc0,chardev=ipmi0',
            '-device', 'isa-ipmi-kcs,bmc=bmc0,irq=5',
            '-serial', 'telnet:127.0.0.1:5000,server,nowait',
        ]

        for i in range(self._interfaces):
            with open(f'/sys/class/net/eth{i}/address', 'r') as f:
                mac = f.read().strip()
            cmd.append('-device')
            cmd.append(f'virtio-net-pci,netdev=hn{i},mac={mac},romfile=""')
            cmd.append(f'-netdev')
            cmd.append(f'tap,id=hn{i},ifname=tap{i},script=/mirror_tap_to_eth.sh,downscript=remove_mirror.sh')

        self._p = subprocess.Popen(cmd)

    def wait(self) -> None:
        self._p.wait()


def main():
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger()

    name = os.getenv('CLAB_LABEL_CLAB_NODE_NAME', default='switch')
    smp = os.getenv('QEMU_SMP', default='4')
    memory = os.getenv('QEMU_MEMORY', default='8192')
    interfaces = int(os.getenv('CLAB_INTFS', 0)) + 1  # containerlab doesn't include eth0

    vm = Qemu(name, smp, memory, interfaces)

    logger.info('Prepare disk')
    vm.prepare_overlay(BASE_IMG)

    logger.info('Create cloud-init configuration')
    vm.create_cloud_init_configuration()

    logger.info(f'Waiting for {interfaces} interfaces to be connected')
    wait_until_interfaces_are_connected(interfaces)

    logger.info('Start QEMU')
    vm.start()

    logger.info('Wait until QEMU is terminated')
    vm.wait()


def handle_exit(signal, frame):
    sys.exit(0)


def wait_until_interfaces_are_connected(interfaces: int) -> None:
    while True:
        i = 0
        for iface in os.listdir('/sys/class/net/'):
            if iface.startswith('eth'):
                i += 1
        if i == interfaces:
            break
        time.sleep(1)


def get_ip_address(iface: str) -> str:
    # Source: https://bit.ly/3dROGBN
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', iface.encode('utf_8'))
    )[20:24])


def get_mac_address(iface: str) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mac = fcntl.ioctl(
        s.fileno(),
        0x8927,  # SIOCGIFHWADDR
        struct.pack('256s', iface.encode('utf-8'))
    )[18:24]
    return ':'.join('%02x' % b for b in mac)


def get_default_gateway() -> str:
    # Source: https://splunktool.com/python-get-default-gateway-for-a-local-interfaceip-address-in-linux
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                # If not default route or not RTF_GATEWAY, skip it
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


if __name__ == '__main__':
    main()
