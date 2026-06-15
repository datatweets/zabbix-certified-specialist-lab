# Zabbix server (MySQL, Alpine 7.4) extended with the PostgreSQL ODBC driver
# so the course can do ODBC database monitoring (Module 22) out of the box.
FROM zabbix/zabbix-server-mysql:alpine-7.4-latest

USER root
# unixODBC + PostgreSQL ODBC driver (psqlodbcw.so)
RUN apk add --no-cache unixodbc psqlodbc
# Register the driver and a DSN for the Online Shop database (demo-postgres)
COPY odbcinst.ini /etc/odbcinst.ini
COPY odbc.ini     /etc/odbc.ini

USER 1997
