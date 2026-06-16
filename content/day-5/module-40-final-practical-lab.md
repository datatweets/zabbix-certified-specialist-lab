# Module 40: Final Practical Lab (Capstone Project)

> **Duration: 90 minutes.** This is the course capstone. You assemble everything from
> Modules 1–36 into one complete, operating monitoring system for the Online Shop,
> add the last required pieces (a trigger **dependency** and a **troubleshooting**
> drill), produce a set of **deliverables**, and **present** your design.

## Learning Objectives

By the end of this module participants can **design, build, operate, and
troubleshoot a complete Zabbix monitoring environment** on Docker — covering hosts,
templates, custom items, web/log/DB/SNMP/JMX monitoring, triggers and dependencies,
dashboards, alerting, business services and SLAs, configuration export, the API, and
incident troubleshooting — and present the result as an engineer would to a team.

## Topics

### The project brief

You are the monitoring engineer for a small company's **Online Shop**, running
entirely on Docker. Your job: deliver a monitoring system that watches every tier,
alerts the on-call, reports SLA to management, and can be operated and debugged. The
environment is the one this whole course has built:

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

### The tasks

A complete build (each task maps to an earlier module):

1. Start the lab and **add all hosts** (M2–M6, M22) · 2. **Link templates** (M17–18)
· 3. **Custom items** (M11, M18, M23) · 4. **Web** (M21) · 5. **Log** (M19) · 6.
**Database/ODBC** (M22) · 7. **SNMP** (M20) · 8. **Java/JMX** (M22) · 9. **≥5
triggers** (M10) · 10. **≥1 trigger dependency** (this module) · 11. **Dashboard**
(M12, M34) · 12. **Email alerting via local SMTP** (M27) · 13. **Business service
tree** (M28, M35) · 14. **SLA** (M28, M35) · 15. **Export a template** (M29) · 16.
**Use the API** (M36) · 17. **Troubleshoot ≥2 injected problems** (M31) · 18.
**Present the design**.

### The deliverables

You submit evidence that it works: a **dashboard** screenshot, the **host list**, the
**custom items**, the **triggers** (incl. the dependency), an **alerting summary**, the
**business service tree**, an **SLA result**, **API output**, **troubleshooting notes**,
and a short **design explanation**. Each phase below produces one of these.

## Docker-Based Demonstration

The instructor walks the finished Online Shop end to end — host list, dashboard,
service tree, SLA, alerting — then adds the trigger dependency, injects two faults,
diagnoses and fixes them, and models the final presentation.

## Hands-On Lab

> Work the phases in order. Each ends with a **deliverable** to capture. Times are a
> guide for the 90-minute session.

### Phase 1 — Foundation: the environment (≈10 min)

1. **Start and verify the stack.**
   ```bash
   docker compose -f compose_lab.yaml ps
   ```
   **Expected:** all platform and demo containers **Up** (server, web, db, agents,
   proxy, java-gateway, web-service, and the seven demo systems).

2. **Confirm all hosts are monitored.** **Data collection → Hosts**.
   **Expected:** **8 hosts** — demo-nginx, demo-api, demo-postgres, demo-java-jmx,
   demo-snmp-device, the two agents, and the Zabbix server — each with the right
   interfaces, linked templates, and service tags. *(Deliverable: host list.)*

   ![Deliverable — the complete monitored host list (8 hosts)](assets/module-40/01-host-list.png)

### Phase 2 — Data collection across every tier (≈12 min)

3. **Verify each monitoring type is collecting** in **Monitoring → Latest data**:
   - **Web** (M21): `demo-nginx` web scenario *Online Shop Frontend* — OK.
   - **Log** (M19): `zabbix-agent-basic` `log[/var/log/demo/app.log]`.
   - **Database/ODBC** (M22): `demo-postgres` active connections, DB size.
   - **SNMP** (M20): `demo-snmp-device` sysName, ifNumber.
   - **Java/JMX** (M22): `demo-java-jmx` heap, threads, uptime.

   **Expected:** every tier reports current values.

4. **Confirm the custom items.** `zabbix-agent-basic`, filter key `app.shop`.
   **Expected:** the UserParameter item (`app.shop[orders]`) and the LLD-discovered
   metrics (`queue_length`, `failed_payments`, `response_time_ms`). *(Deliverable:
   custom items.)*

   ![Deliverable — custom items (UserParameter + LLD-discovered)](assets/module-40/03-custom-items.png)

### Phase 3 — Triggers and a dependency (≈12 min)

5. **Confirm at least five triggers** across the Online Shop (web unavailable, API
   queue/response/failed-payments, DB unreachable, log ERROR, SNMP unreachable, …).
   **Expected:** well over five, spanning multiple hosts and severities.

6. **Create a trigger dependency (required).** Make *Online Shop API is unreachable*
   (on `demo-api`) **depend on** *Online Shop database is unreachable* (on
   `demo-postgres`): open the API trigger → **Dependencies → Add** → select the DB
   trigger.
   **Expected:** the API trigger lists the DB trigger as a dependency. **Why:** if the
   database is down, the API failure is a *symptom* — the dependency **suppresses** the
   API alert so the on-call is paged about the **root cause** (the DB), not the
   cascade. *(Deliverable: triggers + dependency.)*

   ![Deliverable — the trigger dependency (API unreachable depends on DB unreachable)](assets/module-40/04-trigger-dependency.png)

### Phase 4 — Visualization (≈10 min)

7. **Build/confirm the project dashboard.** Assemble an *Online Shop — Final Project*
   dashboard with a **map** widget (the infrastructure map, M34), an **SLA report**, a
   **problems** widget, **host availability**, and **problems by severity**.
   **Expected:** one screen showing topology, SLA, and live health. *(Deliverable:
   dashboard.)*

   ![Deliverable — the Final Project dashboard](assets/module-40/02-final-dashboard.png)

### Phase 5 — Alerting via local SMTP (≈8 min)

8. **Confirm end-to-end alerting** (M27): the **Email (Mailpit)** media type → SMTP
   `demo-mailhog:1025`, Admin's email media, and the enabled trigger action on the
   Web Services group. Trigger a problem and check **http://localhost:8025**.
   **Expected:** problem and recovery emails arrive in Mailpit. *(Deliverable:
   alerting summary.)*

   ![Deliverable — email alerts delivered to the local SMTP server](assets/module-40/07-alerting-mailpit.png)

### Phase 6 — Business services and SLA (≈12 min)

9. **Confirm the business service tree** (M28/M35): **Monitoring → Services →** *Online
   Shop* with five components (Web Frontend, API Service, Database, Java Service,
   Notification Service), tag-mapped to their hosts, with the root status rule.
   **Expected:** the tree reflects component health and root cause. *(Deliverable:
   business service tree.)*

   ![Deliverable — the Online Shop business service tree](assets/module-40/05-service-tree.png)

10. **Review the SLA.** **Services → SLA report**, select *Online Shop SLA* (99.5%).
    **Expected:** SLI per service against the target. *(Deliverable: SLA result.)*

    ![Deliverable — the SLA report (SLI per service vs 99.5% target)](assets/module-40/06-sla-report.png)

### Phase 7 — Export and the API (≈8 min)

11. **Export a custom template** (M29). **Data collection → Templates**, select *Online
    Shop API by HTTP*, **Export → YAML**.
    **Expected:** a portable YAML file (config-as-code).

12. **Use the API** (M36). Run a token-authenticated call to list hosts or problems —
    e.g. the committed script:
    ```bash
    export ZBX_URL=http://localhost:8080/api_jsonrpc.php ZBX_TOKEN=<your token>
    python3 content/lab/api/zbx_automation.py
    ```
    **Expected:** the script prints the API version, the 8 hosts, current problems, and
    creates a host — proof you can automate Zabbix. *(Deliverable: API output.)*

    ```text
    API version: 7.4.11
    Hosts (8): 10084 Zabbix server / 10783 demo-api / ... / 10781 zabbix-agent2-docker
    Current problems (2): [3] Linux: Zabbix agent is not available ; [4] ERROR in Online Shop app log
    Created host api-automation-demo -> hostid 10798
    ```

### Phase 8 — Troubleshooting two injected problems (≈12 min)

The instructor injects two faults. Diagnose each with the Module 31 method —
*symptom → layer → test → fix → verify* — and write a note.

13. **Problem 1 — the website is down.** `demo-nginx` is stopped.
    **Diagnose:** **Monitoring → Web** / **Problems** shows *Online Shop frontend is
    unavailable*; `docker ps -a` shows the container exited. **Fix:** `docker start
    demo-nginx`. **Verify:** the scenario returns to OK.

14. **Problem 2 — the SNMP device went silent.** The `{$SNMP_COMMUNITY}` is wrong.
    **Diagnose:** the SNMP item **Test → Get value** returns *Timeout while connecting
    to "demo-snmp-device:161"*; the community is `wrongcommunity`. **Fix:** set it back
    to `public`. **Verify:** SNMP items collect again.

    ![Deliverable — troubleshooting: the injected problems in Monitoring → Problems](assets/module-40/08-troubleshooting.png)

15. **Write troubleshooting notes** for each: *symptom → layer → root cause → fix →
    verification.* *(Deliverable: troubleshooting notes.)*

### Phase 9 — Present the design (≈8 min)

16. **Present your monitoring design** (2–3 minutes): walk the dashboard, name the
    tiers and how each is monitored, show the service tree and SLA, explain the
    alerting flow and the trigger dependency, and summarise the two incidents you
    fixed. *(Deliverable: design explanation.)*

## Expected Outcome

Participants demonstrate that they can **design, build, operate, and troubleshoot a
complete Zabbix monitoring environment using Docker** — the full Certified Specialist
skill set — and produce the evidence and explanation a real engagement requires.

## Instructor Notes

### Grading rubric (self-assessment or instructor)

| Deliverable | Evidence | ✓ |
|---|---|---|
| Monitored hosts | 8 hosts, correct interfaces + templates | |
| Data collection | web, log, DB, SNMP, JMX all collecting | |
| Custom items | UserParameter + LLD metrics present | |
| Triggers (≥5) + **dependency** | five+ triggers; one dependency configured | |
| Dashboard | one screen with map/SLA/problems | |
| Alerting | email in Mailpit on problem + recovery | |
| Business service tree | Online Shop + ≥4 children, tag-mapped | |
| SLA | SLA report shows SLI vs 99.5% | |
| Template export | a YAML export produced | |
| API | token call lists hosts/problems | |
| Troubleshooting | two faults diagnosed + fixed, with notes | |
| Presentation | clear walkthrough of the design | |

A pass is **all twelve** demonstrated end to end.

### Coaching notes

- **Assemble, don't rebuild.** Most of this exists from Modules 1–36; the project is
  to make it work **together** and to prove it. Spend time on the **dependency**, the
  **troubleshooting**, and the **presentation** — the genuinely new work.
- **The dependency is the teaching moment.** *API depends on DB* means the on-call
  gets one root-cause page, not a storm of symptoms. Make students articulate *why*
  the direction is API→DB and not the reverse.
- **Insist on troubleshooting notes.** "It works now" is not a deliverable; the
  *symptom → layer → root cause → fix → verify* note is. The audit log (M26) often
  reveals who/what changed.
- **The presentation matters.** A Certified Specialist must explain a design to a team,
  not just click. Score clarity: tiers, monitoring method per tier, alerting flow,
  SLA, and the incidents.
- **Lab vs production.** Everything here maps to production: real hosts/cloud/k8s
  instead of containers, HTTPS + secrets, LTS releases, a real SMTP relay and on-call
  rotation, and the same API/templates-in-git workflow. The *thinking* is identical.
- **Timing (90 min):** ~5 brief · ~10 foundation · ~12 data collection · ~12 triggers
  + dependency · ~10 visualization · ~8 alerting · ~12 services + SLA · ~8 export +
  API · ~12 troubleshooting · ~8 presentation. Adjust to the group; the dependency,
  troubleshooting, and presentation are non-negotiable.

## Lab-State Delta

Added in Module 40 (capstone — kept):

- **Trigger dependency (new required element):** *Online Shop API is unreachable*
  (triggerid `32832`, demo-api) now **depends on** *Online Shop database is
  unreachable* (`33052`, demo-postgres) — root-cause suppression.
- **Dashboard:** `Online Shop — Final Project` (dashboardid `414`) — map (sysmap 3) +
  SLA report (slaid 1) + host availability + problems by severity + current problems.
  KEPT.
- **Verified the full build** as deliverables: 8 hosts; web/log/DB/SNMP/JMX collecting;
  custom items; ≥5 triggers + the dependency; service tree (5 children) + SLA 99.5%;
  email alerting via Mailpit; template export; API (`zbx_automation.py`).
- **Troubleshooting drill (demonstrate-then-revert):** stopped `demo-nginx` (web
  outage) and set `{$SNMP_COMMUNITY}` to `wrongcommunity` (SNMP failure) → diagnosed →
  **restored both** (nginx started, community `public`) → recovered. Lab at **8 hosts**.
  Screenshots in `content/day-5/assets/module-40/`. **Course content complete.**
