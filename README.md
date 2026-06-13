# Zabbix Certified Specialist — Docker Lab & Course

A self-contained, **Docker-based Zabbix 7.4 lab** and a **40-module hands-on
course** for the Zabbix Certified Specialist path. Clone this repository, start
one Docker Compose stack, and you have a complete monitoring playground — a Zabbix
platform plus a small fictional **"Online Shop"** (web frontend, API, database,
Java/JMX service, SNMP device, logs, and a mail sink) to monitor end to end.

The whole course follows one storyline: *we build the monitoring for the Online
Shop, one capability per module, using Docker.*

---

## Requirements

- **Docker Desktop** (or Docker Engine + the Compose v2 plugin)
- **Git**
- **8 GB RAM minimum** (16 GB recommended), 4 CPU cores, ~20 GB free disk
- A web browser and a terminal

## Quick start

```bash
# 1. Clone and enter the repo
git clone https://github.com/datatweets/zabbix-certified-specialist-lab.git
cd zabbix-certified-specialist-lab

# 2. Start the whole lab (first run builds the demo images — a few minutes)
docker compose -f compose_lab.yaml up -d

# 3. Check everything is up (15 containers)
docker compose -f compose_lab.yaml ps
```

Then open the Zabbix frontend:

- **URL:** <http://localhost:8080>
- **Login:** `Admin` / `zabbix`  *(change this in Module 2)*

Mail sent by the lab's alerting is caught locally by Mailpit:

- **Mailpit UI:** <http://localhost:8025>

## What's in the lab

**Zabbix platform:** `zabbix-server`, `zabbix-db` (MySQL), `zabbix-web`,
`zabbix-agent-basic`, `zabbix-agent2-docker`, `zabbix-proxy-branch`,
`zabbix-java-gateway`, `zabbix-web-service`.

**Online Shop (the systems you monitor):** `demo-nginx` (web), `demo-api`
(JSON metrics), `demo-postgres` (database), `demo-java-jmx` (JMX), `demo-snmp-device`
(SNMP), `demo-log-app` (logs), `demo-mailhog` (SMTP sink).

Everything is defined in [`compose_lab.yaml`](compose_lab.yaml); the demo build
assets live under [`content/lab/`](content/lab/).

## The course

Course modules live under [`content/`](content/), organised by day:

| Day | Theme |
|-----|-------|
| 1 | Fundamentals & Docker-based setup |
| 2 | Data collection, triggers, dashboards, proxy, discovery |
| 3 | Advanced monitoring (templates, logs, SNMP, web, DB, JMX, LLD) |
| 4 | Administration, security, alerting, business monitoring, troubleshooting |
| 5 | Reporting, API automation, exam prep, final project |

Start with [Module 1: Introduction to Zabbix](content/day-1/module-01-introduction.md)
and [Module 2: Deploying Zabbix with Docker Compose](content/day-1/module-02-deploy-compose.md).

## Resetting the lab

```bash
# Stop the lab (keeps the database)
docker compose -f compose_lab.yaml down

# Wipe everything, including the database, for a clean slate
docker compose -f compose_lab.yaml down -v
docker compose -f compose_lab.yaml up -d
```

> **Security note:** this is a *training* lab. Passwords are deliberately simple
> and the frontend is plain HTTP on port 8080. Do **not** use this configuration
> in production — the course explains what changes for real deployments.

## Credits

The Zabbix platform containers and base Compose tooling are derived from the
official [`zabbix/zabbix-docker`](https://github.com/zabbix/zabbix-docker) project
(AGPL-3.0); see [`README.zabbix-docker.md`](README.zabbix-docker.md) and
[`LICENSE`](LICENSE). The course content, the `compose_lab.yaml` training stack,
and the Online Shop demo systems are additions for this course.
