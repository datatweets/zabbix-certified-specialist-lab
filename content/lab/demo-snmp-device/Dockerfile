# demo-snmp-device — an SNMP-enabled container that simulates a network device
# (router/switch) for SNMP monitoring (Module 20). Runs net-snmp's snmpd with a
# read-only community string of "public", SNMP v2c, listening on UDP 161.
FROM alpine:3.20

RUN apk add --no-cache net-snmp net-snmp-tools

COPY snmpd.conf /etc/snmp/snmpd.conf

EXPOSE 161/udp

# -f = foreground, -Lo = log to stdout, listen on all interfaces UDP 161
CMD ["snmpd", "-f", "-Lo", "-c", "/etc/snmp/snmpd.conf", "udp:161"]
