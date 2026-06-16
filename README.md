# Zabbix Certified Specialist — Docker Lab & Course

A self-contained, **Docker-based Zabbix 7.4 lab** and a **complete 40-module
hands-on course** for the Zabbix Certified Specialist path. Clone this
repository, start one Docker Compose stack, and you have a full monitoring
playground — a Zabbix platform plus a small fictional **"Online Shop"** (web
frontend, API, database, Java/JMX service, SNMP device, logs, and a mail sink)
to monitor end to end.

The whole course follows one storyline: *we build the monitoring for the Online
Shop, one capability per module, using Docker.* Difficulty builds across five
days, from first principles to API automation, exam preparation, and a final
capstone project.

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

The training stack is defined entirely in
[`compose_lab.yaml`](compose_lab.yaml) (MySQL is the canonical database) and runs
**15 containers**:

**Zabbix platform (8):** `zabbix-server`, `zabbix-db` (MySQL 8.4),
`zabbix-web`, `zabbix-agent-basic`, `zabbix-agent2-docker`,
`zabbix-proxy-branch`, `zabbix-java-gateway`, `zabbix-web-service`.

**Online Shop — the systems you monitor (7):** `demo-nginx` (web),
`demo-api` (JSON metrics), `demo-postgres` (database), `demo-java-jmx` (JMX),
`demo-snmp-device` (SNMP), `demo-log-app` (logs), `demo-mailhog` (SMTP sink,
Mailpit).

The demo build assets live under [`content/lab/`](content/lab/).

## The course

Course modules live under [`content/`](content/), organised by day. The course
is **complete — all 40 modules**, plus exam materials and a final project.

| Day | Theme |
|-----|-------|
| 1 | Fundamentals & Docker-based setup |
| 2 | Data collection, triggers, dashboards, proxy, discovery |
| 3 | Advanced monitoring (templates, logs, SNMP, web, DB, JMX, LLD) |
| 4 | Administration, security, alerting, business monitoring, troubleshooting |
| 5 | Reporting, API automation, exam prep, final project |

### Module index

**Day 1 — Fundamentals & Docker setup** ([`content/day-1/`](content/day-1/))

- **1.** [Introduction to Zabbix](content/day-1/module-01-introduction.md)
- **2.** [Deploying Zabbix with Docker Compose](content/day-1/module-02-deploy-compose.md)
- **3.** [Zabbix User Interface](content/day-1/module-03-user-interface.md)
- **4.** [Zabbix Data Flow](content/day-1/module-04-data-flow.md)
- **5.** [Configuring Basic Data Collection](content/day-1/module-05-basic-data-collection.md)
- **6.** [Basic Zabbix Agent Setup](content/day-1/module-06-agent-setup.md)
- **7.** [Agent Configuration Best Practices](content/day-1/module-07-agent-best-practices.md)
- **8.** [Practical Lab — Day 1](content/day-1/module-08-practical-lab.md)

**Day 2 — Data collection, triggers, dashboards, proxy, discovery** ([`content/day-2/`](content/day-2/))

- **9.** [Advanced Data Collection](content/day-2/module-09-advanced-data-collection.md)
- **10.** [Triggers and Alerts](content/day-2/module-10-triggers-and-alerts.md)
- **11.** [Custom Data Collection](content/day-2/module-11-custom-data-collection.md)
- **12.** [Visualization Tools](content/day-2/module-12-visualization-tools.md)
- **13.** [Understanding Zabbix Queue](content/day-2/module-13-zabbix-queue.md)
- **14.** [Working with Zabbix Proxy](content/day-2/module-14-zabbix-proxy.md)
- **15.** [Network Discovery](content/day-2/module-15-network-discovery.md)
- **16.** [Practical Lab — Day 2](content/day-2/module-16-practical-lab.md)

**Day 3 — Advanced monitoring** ([`content/day-3/`](content/day-3/))

- **17.** [Mass Operations](content/day-3/module-17-mass-operations.md)
- **18.** [Advanced Templates](content/day-3/module-18-advanced-templates.md)
- **19.** [Monitoring Logs](content/day-3/module-19-monitoring-logs.md)
- **20.** [SNMP Monitoring](content/day-3/module-20-snmp-monitoring.md)
- **21.** [Web Monitoring](content/day-3/module-21-web-monitoring.md)
- **22.** [Performance Monitoring](content/day-3/module-22-performance-monitoring.md)
- **23.** [Low-Level Discovery (LLD)](content/day-3/module-23-low-level-discovery.md)
- **24.** [Practical Lab — Day 3](content/day-3/module-24-practical-lab-day-3.md)

**Day 4 — Administration, security, alerting, business monitoring** ([`content/day-4/`](content/day-4/))

- **25.** [User Management](content/day-4/module-25-user-management.md)
- **26.** [Security Best Practices](content/day-4/module-26-security-best-practices.md)
- **27.** [Alerting and Notifications](content/day-4/module-27-alerting-and-notifications.md)
- **28.** [Inventory and Business Monitoring](content/day-4/module-28-inventory-and-business-monitoring.md)
- **29.** [Configuring Zabbix Import/Export](content/day-4/module-29-import-export.md)
- **30.** [Optimization Techniques](content/day-4/module-30-optimization-techniques.md)
- **31.** [Troubleshooting Zabbix](content/day-4/module-31-troubleshooting.md)
- **32.** [Practical Lab — Day 4](content/day-4/module-32-practical-lab-day-4.md)

**Day 5 — Reporting, API automation, exam prep, final project** ([`content/day-5/`](content/day-5/))

- **33.** [System Reports](content/day-5/module-33-system-reports.md)
- **34.** [Advanced Visualization](content/day-5/module-34-advanced-visualization.md)
- **35.** [Business Service Monitoring](content/day-5/module-35-business-service-monitoring.md)
- **36.** [Zabbix API and Automation](content/day-5/module-36-api-automation.md)
- **37.** [Exam Preparation](content/day-5/module-37-exam-preparation.md)
- **38.** [Exam Discussion & Strategy](content/day-5/module-38-exam-discussion.md)
- **39.** [What's Next](content/day-5/module-39-whats-next.md)
- **40.** [Final Capstone Project](content/day-5/module-40-final-capstone.md) — guided [Final Practical Lab](content/day-5/module-40-final-practical-lab.md)

**Extra modules — optional advanced topics** ([`content/extra/`](content/extra/)) — production-grade enrichments beyond the core ZCS scope; each runs in the same `compose_lab.yaml` stack

- **41.** [Advanced SNMP — SNMPv3 and bulk walks](content/extra/module-41-advanced-snmp.md)
- **43.** [Monitoring Docker with Zabbix agent 2](content/extra/module-43-docker-monitoring.md)
- **44.** [Predictive and Trend Triggers](content/extra/module-44-predictive-triggers.md)
- **45.** [Proxy High Availability with Proxy Groups](content/extra/module-45-proxy-ha.md)
- **46.** [Encrypting Zabbix — PSK and Database TLS](content/extra/module-46-encryption.md)
- **47.** [Directory Authentication with OpenLDAP and JIT](content/extra/module-47-openldap-auth.md)
- **48.** [External Alerting with Slack](content/extra/module-48-slack-alerting.md)
- **49.** [Backup, Restore, and Database Partitioning](content/extra/module-49-backup-and-partitioning.md)
- **50.** [LLD Host Prototypes and Interactive Frontend Scripts](content/extra/module-50-host-prototypes-and-scripts.md)

> These are **additive** — they don't change the baseline. The two extra
> containers (`zabbix-proxy-branch-2` for proxy HA, `lab-openldap` for LDAP) sit
> behind a Compose `extra` profile, so the default `docker compose up -d` still
> starts the baseline 15 containers; each extra module starts what it needs (e.g.
> `docker compose -f compose_lab.yaml up -d lab-openldap`). Module 48 (Slack)
> needs your own workspace + bot token; Module 42 (browser items) is omitted —
> not functional on Zabbix 7.4.11.

### Exam preparation

Self-study materials live under [`content/exam/`](content/exam/):

- [ZCS mock exam](content/exam/zcs-mock-exam.md) and
  [answer key](content/exam/zcs-mock-exam-answers.md) (45 questions)
- [Scenario cards](content/exam/zcs-scenarios.md) for applied reasoning
- [Monitoring roadmap worksheet](content/exam/monitoring-roadmap-worksheet.md)

New here? Start with
[Module 1: Introduction to Zabbix](content/day-1/module-01-introduction.md) and
[Module 2: Deploying Zabbix with Docker Compose](content/day-1/module-02-deploy-compose.md).

## Repository layout

```text
zabbix-docker/
├── compose_lab.yaml             # the training stack (MySQL + demo systems)
├── CLAUDE.md                    # authoring rules for the course content
├── content/
│   ├── outline/                 # source curriculum (reference)
│   ├── lab-state.md             # living record of what exists in the lab
│   ├── lab/                     # demo-system build assets (Dockerfiles, apps)
│   ├── verification/
│   │   ├── api/                 # reusable Zabbix API helper scripts
│   │   └── browser/             # Playwright capture scripts for screenshots
│   ├── exam/                    # mock exam, scenarios, worksheet
│   ├── day-1/ … day-5/          # the 40 modules, plus assets/ per day
│   └── …
└── compose*.yaml, Dockerfiles/, … # upstream zabbix-docker tooling
```

The remaining top-level files (`compose.yaml`, `compose_pgsql.yaml`,
`Dockerfiles/`, `kubernetes.yaml`, `Makefile`, etc.) are upstream
zabbix-docker assets and are **not** used by the course; only
`compose_lab.yaml` is.

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
