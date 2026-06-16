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

By the end of this module participants can **design, build, operate, and troubleshoot
a complete Zabbix monitoring environment** on Docker — independently — covering hosts,
templates, custom items, web/log/DB/SNMP/JMX monitoring, triggers and dependencies,
dashboards, alerting, business services and SLAs, configuration export, the API, and
incident troubleshooting — and present the result as an engineer would to a team.

## Topics

### The brief

You are the monitoring engineer for a small company's **Online Shop**, running
entirely on Docker. Management's ask is simple: *"Make sure the Online Shop is
monitored end to end, alert us before customers notice, tell us our SLA, and be able
to fix it when it breaks."* Your job is to deliver and prove a monitoring system that
does exactly that, for this environment:

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
service — **8 hosts** in all.

### How this capstone works

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

You submit: a **dashboard** screenshot, the **host list**, the **custom items**, the
**triggers** (incl. the dependency), an **alerting summary**, the **business service
tree**, an **SLA result**, **API output**, **troubleshooting notes**, and a short
**design explanation** — evidence that the system works and that you understand it.

## Docker-Based Demonstration

The instructor frames the project, shows one example of a finished deliverable (the
dashboard), models the trigger dependency and a single fault-and-fix, and demonstrates
the 2-minute design presentation — then hands the room the requirements.

## Hands-On Lab — The Project

> Meet each requirement, then capture its deliverable. Work in any order, but the
> phases below are a sensible 90-minute path. **Acceptance criteria are the test; how
> you satisfy them is up to you.** Where a requirement isn't yet in your lab, build it
> using the named module — that is part of the work.

### A. Foundation (≈10 min)

**R1 — The environment is running and fully onboarded.**
- *Acceptance:* `docker compose -f compose_lab.yaml ps` shows every platform and demo
  container **Up**; **Data collection → Hosts** lists **8 hosts** (the frontend, API,
  database, Java, SNMP device, two agents, and the Zabbix server), each with correct
  interfaces, linked templates, and service tags.
- *If missing:* add hosts and link templates (Modules 2–6, 17–18, 22).
- *Deliverable:* **host list.**

![Passing deliverable — the 8-host monitored environment](assets/module-40/01-host-list.png)

### B. Data collection across every tier (≈12 min)

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

**R6 — One dashboard answers "is the Online Shop healthy?" at a glance.**
- *Acceptance:* a single dashboard combining the **infrastructure map**, an **SLA
  report**, **current problems**, and **host availability / severity** — readable by
  someone who doesn't use Zabbix daily.
- *If missing:* build it (Modules 12, 34).
- *Deliverable:* **dashboard.**

![Passing deliverable — a complete project dashboard](assets/module-40/02-final-dashboard.png)

### E. Alerting via local SMTP (≈8 min)

**R7 — A real problem reaches a human by email.**
- *Acceptance:* a problem on an Online Shop host produces a **problem** email and, on
  recovery, a **recovery** email, both visible in Mailpit (`http://localhost:8025`);
  the media type points at the local SMTP server and the action is scoped (not every
  problem in Zabbix).
- *If missing:* configure media type, user media, and a trigger action (Module 27).
- *Deliverable:* **alerting summary.**

![Passing deliverable — email alerts via local SMTP](assets/module-40/07-alerting-mailpit.png)

### F. Business services and SLA (≈12 min)

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

## Instructor Notes

### Grading rubric (self-assessment or instructor)

| # | Requirement | Acceptance evidence | ✓ |
|---|---|---|---|
| R1 | Environment onboarded | 8 hosts, correct interfaces + templates | |
| R2 | Data collection | web, log, DB, SNMP, JMX all collecting | |
| R3 | Custom items | UserParameter + LLD metrics present | |
| R4 | Triggers (≥5) | five+ enabled, multi-host, multi-severity | |
| R5 | **Trigger dependency** | API→DB dependency; suppression understood | |
| R6 | Dashboard | one screen: map + SLA + problems + availability | |
| R7 | Alerting | problem **and** recovery email in Mailpit | |
| R8 | Business service tree | Online Shop + ≥4 tag-mapped children | |
| R9 | SLA | SLA report shows SLI vs target | |
| R10 | Template export | a YAML export produced | |
| R11 | API | token call returns hosts/problems | |
| R12 | Troubleshooting | two faults diagnosed + fixed, with notes | |
| R13 | Presentation | clear, correct design walkthrough | |

A pass is **all thirteen** demonstrated end to end.

### Coaching notes

- **This is an assessment — resist re-teaching.** Give goals, not clicks. Point a stuck
  learner at the named module rather than walking them through it; the gap they fill is
  the thing being measured.
- **Most of it already exists — that's fine.** A learner who did the course confirms
  most requirements and *builds the few new/missing ones* (the dependency, the
  dashboard if they want a fresh one, the troubleshooting). A learner starting cold
  builds the lot — both are valid; the acceptance criteria are identical.
- **The dependency is the headline reasoning check.** *API depends on DB* → one
  root-cause page, not a symptom storm. Make them justify the **direction**; reversing
  it is the classic mistake.
- **Insist on troubleshooting notes.** "It works now" fails R12. The *symptom → layer →
  root cause → fix → verify* note is the deliverable; the audit log (M26) often reveals
  *who/what* changed.
- **Score the presentation seriously.** A Specialist explains a design to a team, not
  just clicks. Listen for: monitoring method per tier, alerting flow, the dependency
  rationale, SLA meaning, and incident handling.
- **Self-paced fault injection.** Without an instructor, have learners pair up to inject
  each other's faults, or apply the sealed fault cards (R12) and diagnose before reading
  the cause. The skill is the diagnosis, so don't peek.
- **Lab vs production.** Everything maps up: real hosts/cloud/k8s instead of containers,
  HTTPS + secrets + LTS releases, a real SMTP relay and on-call rotation, and the same
  API/templates-in-git workflow. The *thinking* is identical.
- **Timing (90 min):** ~5 brief · ~10 R1 · ~12 R2–R3 · ~12 R4–R5 · ~10 R6 · ~8 R7 · ~12
  R8–R9 · ~8 R10–R11 · ~12 R12 · ~8 R13. The dependency, troubleshooting, and
  presentation are non-negotiable.

## Lab-State Delta

Capstone objects (kept; identical environment to the Module 40 reference lab):

- **Trigger dependency (R5, new):** *Online Shop API is unreachable* (triggerid `32832`,
  demo-api) **depends on** *Online Shop database is unreachable* (`33052`,
  demo-postgres) — root-cause suppression. Set via `trigger.update`.
- **Dashboard:** `Online Shop — Final Project` (dashboardid `414`) — map (sysmap 3) +
  SLA report (slaid 1) + host availability + problems by severity + current problems.
- **Verified the full build** against the acceptance criteria: 8 hosts;
  web/log/DB/SNMP/JMX collecting; custom items; ≥5 triggers + dependency; 5-child
  service tree + SLA 99.5%; email alerting via Mailpit; template export; API.
- **Troubleshooting (R12, demonstrate-then-revert):** stopped `demo-nginx` and set
  `{$SNMP_COMMUNITY}` to `wrongcommunity` → diagnosed → restored both → recovered. Lab
  at **8 hosts**. Deliverable screenshots reused from `content/day-5/assets/module-40/`.
