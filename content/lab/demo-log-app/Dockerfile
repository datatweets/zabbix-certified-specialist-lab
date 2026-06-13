# demo-log-app — generates an application log stream for log monitoring (Module 19).
# Writes INFO / WARNING / ERROR lines to /var/log/demo/app.log on a shared volume
# that zabbix-agent-basic mounts read-only.
FROM alpine:3.20

COPY gen-logs.sh /usr/local/bin/gen-logs.sh
RUN chmod +x /usr/local/bin/gen-logs.sh

CMD ["/usr/local/bin/gen-logs.sh"]
