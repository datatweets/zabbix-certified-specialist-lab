# Module 40: Final Capstone Project

> **Duration: 90 minutes.** This is the course capstone — an **assessment**, not a
> tutorial. You are given a brief and a set of **requirements**; you decide *how* to
> meet each one, drawing on everything from Modules 1–36. You then add the last
> required pieces (a trigger **dependency** and a **troubleshooting** drill), submit a
> set of **deliverables**, and **present** your design.
>
> Unlike every earlier module, this one gives you **goals and acceptance criteria, not
> click-by-click steps.** If you need the procedure for a requirement, the relevant
> module is named — but the point is to do it yourself.

## Learning Objectives

This is the module the whole course has been pointing at. For thirty-nine modules you
have been handed steps; here you are handed a problem. By the end of it you can
**design, build, operate, and troubleshoot a complete Zabbix monitoring environment**
on Docker — independently — covering hosts, templates, custom items,
web/log/DB/SNMP/JMX monitoring, triggers and dependencies, dashboards, alerting,
business services and SLAs, configuration export, the API, and incident
troubleshooting — and present the result as an engineer would to a team. The shift from
"follow the instructions" to "meet the bar however you see fit" is the whole point: a
Certified Specialist is measured by outcomes, not keystrokes.

## Topics

### The brief

Step into the role for a moment. You are the monitoring engineer for a small company's
**Online Shop**, running entirely on Docker — the same Online Shop you have been
building toward since Module 1. Management's ask is simple and it is the ask every
operations team eventually hears: *"Make sure the Online Shop is monitored end to end,
alert us before customers notice, tell us our SLA, and be able to fix it when it
breaks."* Your job is to deliver and prove a monitoring system that does exactly that,
for this environment:

```text
Online Shop
├── Nginx frontend        (demo-nginx)        — web monitoring
├── API application       (demo-api)          — HTTP agent + custom items
├── PostgreSQL database   (demo-postgres)     — ODBC monitoring
├── Java/JMX service      (demo-java-jmx)      — JMX via Java gateway
├── SNMP simulated device (demo-snmp-device)  — SNMP monitoring
├── Log-generating service(demo-log-app)      — log monitoring (via agent)
└── Notification channel  (demo-mailhog)      — local SMTP for email alerts
```

monitored by the Zabbix server, two agents, a proxy, the Java gateway, and the web
service — **8 hosts** in all. Notice that every tier in that tree wants a different
collection method; the breadth is the assessment.

### How this capstone works

The structure of this module is unlike anything you have done so far, so read this part
carefully before you start clicking. Everything that follows is framed as a goal you
must reach, with a clear test for whether you reached it — and nothing more.

- The build is expressed as **requirements** with **acceptance criteria** — the bar
  you must hit, not the keystrokes to hit it.
- **Build what's missing.** If you followed the course, most requirements are already
  satisfied in your lab — confirm them. **If any is missing or you started fresh,
  build it now** using the named module. *Knowing whether it's done and completing it
  is part of the assessment.*
- Each requirement maps to a **deliverable** — evidence you submit (a screenshot or
  output). The figures here show what a **passing** submission looks like.
- **Do not expect step-by-step instructions.** Reach for them only if stuck; a
  Certified Specialist works from goals.

### The deliverables

When you are done, you hand over a portfolio that an engagement would actually demand —
proof the system works, paired with proof you understand it. You submit: a
**dashboard** screenshot, the **host list**, the **custom items**, the **triggers**
(incl. the dependency), an **alerting summary**, the **business service tree**, an **SLA
result**, **API output**, **troubleshooting notes**, and a short **design explanation**
— evidence that the system works and that you understand it.

## Docker-Based Demonstration

Before the room scatters to work, the instructor sets the frame. They frame the project,
show one example of a finished deliverable (the dashboard), model the trigger dependency
and a single fault-and-fix, and demonstrate the 2-minute design presentation — then hand
the room the requirements. After that, the floor is yours.

## Hands-On Lab — The Project

> Meet each requirement, then capture its deliverable. Work in any order, but the
> phases below are a sensible 90-minute path. **Acceptance criteria are the test; how
> you satisfy them is up to you.** Where a requirement isn't yet in your lab, build it
> using the named module — that is part of the work.

### A. Foundation (≈10 min)

Everything else rests on the environment being up and every host onboarded, so confirm
that first.

**R1 — The environment is running and fully onboarded.**
- *Acceptance:* `docker compose -f compose_lab.yaml ps` shows every platform and demo
  container **Up**; **Data collection → Hosts** lists **8 hosts** (the frontend, API,
  database, Java, SNMP device, two agents, and the Zabbix server), each with correct
  interfaces, linked templates, and service tags.
- *If missing:* add hosts and link templates (Modules 2–6, 17–18, 22).
- *Deliverable:* **host list.**

![Passing deliverable — the 8-host monitored environment](assets/module-40/01-host-list.png)

### B. Data collection across every tier (≈12 min)

With the hosts in place, prove that each tier of the shop is actually producing numbers
— a host that exists but collects nothing is monitoring in name only.

**R2 — Every tier of the Online Shop is collecting data.**
- *Acceptance:* in **Monitoring → Latest data**, current values exist for **web**
  (demo-nginx scenario), **log** (agent `log[...]`), **database** (demo-postgres ODBC),
  **SNMP** (demo-snmp-device OIDs), and **Java/JMX** (demo-java-jmx heap/threads).
- *If missing:* configure the relevant check (Modules 19, 20, 21, 22).

**R3 — Custom metrics the templates don't provide are collected.**
- *Acceptance:* the Online Shop's business metrics (`app.shop[orders]` plus the
  LLD-discovered `queue_length`, `failed_payments`, `response_time_ms`) report values.
- *If missing:* build them (Modules 11, 23).
- *Deliverable:* **custom items.**

![Passing deliverable — custom items (UserParameter + LLD)](assets/module-40/03-custom-items.png)

### C. Triggers and a dependency (≈12 min)

Collecting data is half the job; the other half is teaching Zabbix when a number means
trouble — and which trouble is the real story when several alerts fire at once.

**R4 — At least five triggers protect the Online Shop.**
- *Acceptance:* five or more enabled triggers across multiple hosts and severities
  (e.g. web unavailable, API queue/response/failed-payments, DB unreachable, log ERROR,
  SNMP unreachable).
- *If missing:* author them with 7.x expressions (Module 10).

**R5 — A trigger dependency expresses root cause. *(new — you must build this)***
- *Goal:* when the database is down, the *API is unreachable* alert is a **symptom**,
  not a separate incident. Configure a **dependency** so the on-call is paged about the
  **root cause**, not the cascade.
- *Acceptance:* *Online Shop API is unreachable* (demo-api) **depends on** *Online Shop
  database is unreachable* (demo-postgres); with the DB trigger in problem, the API
  trigger is **suppressed**.
- *Think:* why is the direction API→DB and not DB→API? Be ready to justify it.
- *Deliverable:* **triggers + the dependency.**

![Passing deliverable — the trigger dependency (root-cause suppression)](assets/module-40/04-trigger-dependency.png)

### D. Visualization (≈10 min)

Numbers and triggers live deep in the menus; a dashboard is how a busy human sees the
whole shop's health in one glance, without knowing where anything is configured.

**R6 — One dashboard answers "is the Online Shop healthy?" at a glance.**
- *Acceptance:* a single dashboard combining the **infrastructure map**, an **SLA
  report**, **current problems**, and **host availability / severity** — readable by
  someone who doesn't use Zabbix daily.
- *If missing:* build it (Modules 12, 34).
- *Deliverable:* **dashboard.**

![Passing deliverable — a complete project dashboard](assets/module-40/02-final-dashboard.png)

### E. Alerting via local SMTP (≈8 min)

A dashboard helps the person who is already looking; alerting reaches the person who
isn't. Close the loop so a real problem finds a human.

**R7 — A real problem reaches a human by email.**
- *Acceptance:* a problem on an Online Shop host produces a **problem** email and, on
  recovery, a **recovery** email, both visible in Mailpit (`http://localhost:8025`);
  the media type points at the local SMTP server and the action is scoped (not every
  problem in Zabbix).
- *If missing:* configure media type, user media, and a trigger action (Module 27).
- *Deliverable:* **alerting summary.**

![Passing deliverable — email alerts via local SMTP](assets/module-40/07-alerting-mailpit.png)

### F. Business services and SLA (≈12 min)

Technical metrics speak to engineers; management thinks in services and promises. This
is where your monitoring rolls up into the language the business actually uses.

**R8 — The technical monitoring rolls up into a business view.**
- *Acceptance:* a service tree **Online Shop** with its components (Web Frontend, API
  Service, Database, Java Service, Notification Service), each **tag-mapped** to its
  host so it reacts to that host's problems and shows a **root cause**.
- *If missing:* build the tree and tag the hosts (Modules 28, 35).
- *Deliverable:* **business service tree.**

![Passing deliverable — the business service tree](assets/module-40/05-service-tree.png)

**R9 — There is a measurable SLA with a target.**
- *Acceptance:* an SLA (e.g. **99.5%**) covering the Online Shop services, and an **SLA
  report** showing the achieved **SLI** per service for the period.
- *If missing:* define the SLA (Modules 28, 35).
- *Deliverable:* **SLA result.**

![Passing deliverable — SLA report (SLI vs target)](assets/module-40/06-sla-report.png)

### G. Portability and automation (≈8 min)

A monitoring setup that lives only in one server's UI is fragile. Prove yours is
portable as code and operable from code, the way a real team would run it.

**R10 — Your monitoring is portable as code.**
- *Acceptance:* export at least one custom template (e.g. *Online Shop API by HTTP*) to
  a **YAML** file that could be re-imported on another server.
- *If missing:* export it (Module 29).

**R11 — You can operate Zabbix from code, not just the UI.**
- *Acceptance:* a **token-authenticated** API call returns real data — list the hosts
  and/or current problems (curl or a script).
- *If missing:* create a token and call the API (Module 36; the committed
  `content/lab/api/zbx_automation.py` is one way).
- *Deliverable:* **API output**, e.g.:
  ```text
  API version: 7.4.11
  Hosts (8): 10084 Zabbix server / 10783 demo-api / ... / 10781 zabbix-agent2-docker
  Current problems (2): [3] Linux: Zabbix agent is not available ; [4] ERROR in Online Shop app log
  ```

### H. Troubleshooting (≈12 min) — *applied, not pre-built*

Building a monitoring system is one skill; using it to chase down a fault under pressure
is another, and it is the one this drill measures. Here you do not pre-build anything —
you react to a break you did not cause.

**R12 — Diagnose and fix two injected failures, and document them.**
- *Setup:* have a partner (or the instructor) **inject two faults** without telling you
  the cause. *Self-paced option:* apply the two sealed "fault cards" below without
  reading their explanation first, then diagnose.
  - *Fault card 1:* `docker stop demo-nginx`
  - *Fault card 2:* set host macro `{$SNMP_COMMUNITY}` on `demo-snmp-device` to a wrong
    value
- *Acceptance:* for **each** fault you produce a note in the form **symptom → layer →
  root cause → fix → verification**, using the Module 31 method (`docker ps -a`,
  `zabbix_get`, the item **Test**, `Monitoring → Web`/`Problems`, the logs), and you
  **restore** the system to healthy.
- *Deliverable:* **troubleshooting notes** (and the problems you saw).

![Passing deliverable — the injected problems under diagnosis](assets/module-40/08-troubleshooting.png)

### I. Present the design (≈8 min)

The last requirement is the one that separates a technician from a specialist: you have
to explain what you built and why, out loud, to people who will judge the design on its
reasoning.

**R13 — Explain your monitoring design to the team.**
- *Acceptance:* a 2–3 minute walkthrough that covers: the tiers and **how each is
  monitored**, the **alerting** flow and the **trigger dependency** (and why its
  direction), the **service tree + SLA**, and the **two incidents** you resolved.
- *Deliverable:* **design explanation.**

## Expected Outcome

Participants demonstrate — largely independently — that they can **design, build,
operate, and troubleshoot a complete Zabbix monitoring environment using Docker**, the
full Certified Specialist skill set, and produce the evidence and explanation a real
engagement requires.
