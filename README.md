# Containerlab IPMI

OpenIPMI: https://github.com/cminyard/openipmi

Build images:
```bash
docker build -t localhost/machine image
```

Show BMC info:
```bash
docker exec -it clab-ipmi-machine ipmitool -I lanplus -U ipmiusr -P test -p 9001 -H 127.0.0.1 mc info
```

Show channel informations:
```bash
docker exec -it clab-ipmi-machine ipmitool -I lanplus -U ipmiusr -P test -p 9001 -H 127.0.0.1 lan print 1
```

Power on the VM:
```bash
docker exec -it clab-ipmi-machine ipmitool -I lanplus -U ipmiusr -P test -p 9001 -H 127.0.0.1 power on
```
