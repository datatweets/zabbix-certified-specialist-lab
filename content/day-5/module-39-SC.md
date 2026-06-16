# Module 39: What's Next

## Learning Objectives

By the end of this module participants can **plan their path beyond this course**: they
understand the Zabbix certification ladder past Specialist, can name the advanced
monitoring areas to grow into (HA, scale, cloud, Kubernetes, network, enterprise
alerting, automation/IaC), and have drafted a personal or organizational **monitoring
roadmap**.

## Topics

### You finished the Specialist course — here's what you built

It is worth pausing to take stock of the distance you have covered, because the
collection of things you now know how to do is larger than it feels in the moment.
Over 40 modules you built a complete, operating monitoring system for the **Online
Shop** on Docker: agents and items, triggers and dependencies, templates and LLD,
web/log/DB/SNMP/JMX monitoring, a proxy, alerting with escalation, users and security,
dashboards and maps, reports, a business service tree with an SLA, the API, and a full
troubleshooting capability. Each of those was not a stand-alone exercise but one more
capability bolted onto the same shop, which means you have practiced the way real
monitoring grows. **That is the Certified Specialist skill set.** This module
is about where to take it.

### The certification ladder beyond Specialist

Zabbix structures its credentials as a ladder, and knowing the rungs helps you aim. Each
level assumes the one below it and adds a distinct kind of competence — first the ability
to *design and implement* monitoring, then the ability to *install, scale, and secure* a
platform, and finally the ability to run one at *enterprise scale*. Here is the shape of
the climb and what each step buys you:

| Level | Certification | Prereq | What it adds |
|---|---|---|---|
| 2 | **Specialist (ZCS)** | none | design + implement monitoring *(you are here)* |
| 3 | **Professional (ZCP)** | ZCS | **install/scale/secure**: HA (server + proxy), encryption, advanced preprocessing & LLD, host prototypes, ODBC/SNMP discovery, autoregistration, VMware, **event correlation**, performance tuning *(3-day course)* |
| 4 | **Expert (ZCE)** | ZCP | **enterprise scale**: DB tuning for tens of thousands of hosts, near-zero-downtime upgrades, vault credentials, **LDAP/SAML/MFA**, TimescaleDB, SELinux *(5-day course)* |

The honest advice is to take the rungs in order rather than leaping ahead. **Natural
next step:** book the **ZCS exam** if you haven't (Modules 37–38), then aim
for **ZCP** — it turns "I can configure monitoring" into "I can install, scale, and
secure a Zabbix platform."

> **TO-VERIFY / external:** course/exam details, prices, and prerequisites can change —
> confirm on **zabbix.com/training** and **zabbix.com/exams**.

### Advanced monitoring areas to grow into

Several topics appeared in this course as a deliberately simplified version of the real
thing — a single server standing in for a cluster, one email action standing in for an
on-call platform. That was the right call for learning, but you should know where each
shortcut leads in production. The course covered each of these at a *foundational* level
(often as a lab shortcut); here is where they go in the real world:

- **High availability.** Zabbix has a native **server HA cluster** and **proxy HA /
  load balancing** — no single point of failure. (We ran a single server; production
  runs a cluster.)
- **Large-scale architecture.** Thousands of hosts and high **NVPS** push the
  **database** first: partitioning or **TimescaleDB**, tuned `Start*` processes and
  caches, and many **proxies** to distribute collection. (Module 30 is the doorway.)
- **Cloud monitoring.** Watch AWS/Azure/GCP via **HTTP agent** items against cloud
  APIs, plus cloud-native metrics and discovery that follows autoscaling.
- **Kubernetes & containers.** Official **Kubernetes** templates collect cluster, node,
  and pod metrics with service discovery — the modern equivalent of our LLD work.
- **Network monitoring at scale.** **SNMP low-level discovery** auto-creates an item
  per interface across switches and routers (Module 20 + 23 at scale), with traps and
  network maps.
- **Enterprise alerting.** On-call rotations (**PagerDuty/Opsgenie**), **ChatOps**
  (Slack/Teams), escalation policies, and **event correlation** to suppress noise — a
  big step beyond the single email action of Module 27.
- **Integrations.** Ticketing (**Jira/ServiceNow**), **Grafana**, data warehouses, and
  custom webhooks — Zabbix as part of a toolchain (Module 36's API is the door).
- **Automation & infrastructure as code.** Templates in **git**, hosts provisioned by
  **API/autoregistration**, configuration in **CI/CD**, and secrets in a **vault** —
  monitoring managed like application code (Modules 29, 36).

### Specialized monitoring use cases — setting them up

The reassuring thing about all those advanced areas is that you do not have to relearn
your craft for each one. The targets change, but the *method* you learned transfers
directly. When you tackle a new domain, walk the same five steps you have walked all week:

1. **Understand the source** — what does it expose (agent, SNMP, JMX, HTTP/JSON, logs)?
2. **Pick the collector** — agent item, HTTP agent + dependent items, SNMP, ODBC, JMX.
3. **Template it** — so every instance is monitored identically and reusably.
4. **Discover it** — LLD/host prototypes so it scales without manual work.
5. **Alert and report on it** — triggers, actions, services/SLA, dashboards.

That five-step pattern is the same whether the target is a Linux box, a Kubernetes
cluster, or a fleet of routers. Internalize it and a new monitoring domain stops being
intimidating; it becomes a checklist you already know how to run.

### A monitoring strategy for real organizations

It is tempting to think the tool is the hard part, but the tool is the easy part. What
separates monitoring that helps from monitoring that drowns its owners in noise is
strategy. Tools don't make good monitoring — **strategy** does:

- **Monitor what matters to the business**, not everything that emits a metric. Start
  from services and SLAs (Modules 28, 35), work down to components.
- **Alert on symptoms users feel**, route by severity, and use **dependencies/
  correlation** so one root cause pages once.
- **Make it reproducible** — config as code, reviewed and versioned.
- **Design for the audience** — ops vs management dashboards (Module 34).
- **Plan for scale and failure** — HA and proxies before you need them.
- **Iterate** — monitoring is never "done"; review coverage and noise regularly.

### Keep your skills alive

Skills decay when they go untouched, and monitoring skills decay faster than most because
the product keeps moving. A little deliberate practice keeps you sharp:

- **Keep the Docker lab.** Extend it, break it, fix it — the cheapest gym for these
  skills (Module 38).
- **Read the version-pinned docs**, follow the **Zabbix blog**, join the **forums/
  Telegram**, and attend a **meetup or the Zabbix Summit**.
- **Apply it at work** — even one well-built template or SLA dashboard compounds.

## Instructor-Led Discussion (Demonstration)

The instructor maps each advanced area back to where the course touched it (HA ⟵ single
server; scale ⟵ Module 30; LLD ⟵ Kubernetes/network discovery; API ⟵ integrations/IaC),
shows the official **certification path** and **documentation**, and shares how real
deployments grow from a lab like this one.

## Hands-On Lab — Design your monitoring roadmap

Vague good intentions evaporate within a week of finishing a course; a written, dated plan
survives. The point of this lab is to turn everything above into a document you will
actually act on, so work through it honestly rather than optimistically.

1. **Assess where you are.** Open `content/exam/monitoring-roadmap-worksheet.md` and
   fill in **§1 (skills)** and your weak areas from the mock exam/scenarios.
   **Expected:** an honest snapshot of your current skill set.

2. **Choose your next certification.** Complete **§2** — ZCP or ZCE, and a target date.
   **Expected:** a concrete certification goal.

3. **Pick advanced areas to learn.** In **§3**, check the topics relevant to your work
   (HA, cloud, Kubernetes, network, enterprise alerting, automation/IaC).
   **Expected:** a focused learning list, not "everything".

4. **Plan for your organization.** Fill **§4–§6** — what your org must monitor, the
   architecture (HA? proxies? database/scale?), and an automation/IaC plan.
   **Expected:** a realistic design sketch tied to real needs.

5. **Commit to a 30/90/180-day plan.** Complete **§7** with one concrete step per
   horizon (sit the exam · apply at work · ship a production improvement).
   **Expected:** a dated, actionable roadmap you'll actually follow.

## Expected Outcome

Participants know how to continue beyond the course: the certification path to
Professional and Expert, the advanced areas worth growing into, the transferable method
for new monitoring domains, and a written, dated **roadmap** for their skills and their
organization.
