# Module 35: Business Service Monitoring

## Learning Objectives

By the end of this module participants can model and report on **business services**
in depth: refine the Online Shop **service tree**, map **technical triggers to
services** with tags, control **status calculation** with algorithms and **additional
rules**, observe **service impact** and **root cause** during a failure, and read a
**detailed SLA report** of uptime/downtime against a target — connecting a single
broken host to its business consequence.

## Topics

### From hosts to services — the business view

Module 28 introduced business services; this module goes deep. A **business service**
is something the company sells or depends on — *the Online Shop* — modelled
independently of the hosts that implement it. The value is translation: when
`demo-api` fails, an engineer sees a trigger; a manager needs to hear *"the API
Service is down, so the Online Shop is degraded, and we're breaching our SLA."*
Services provide that chain.

### Refining the service tree

The Online Shop tree has the components that matter. We **refine** it to match the
full architecture by adding the **Java Service** (`demo-java-jmx`) alongside Web
Frontend, API Service, Database, and Notification — five children under the Online
Shop root.

![The refined service tree: five components, with live status and SLA](assets/module-35/01-service-tree.png)

### Technical-trigger-to-service mapping

A leaf service connects to the infrastructure by **problem tags**: any problem event
carrying a matching tag counts against it. The **Database** service maps
`service = db`; because we tagged the `demo-postgres` **host** with `service:db`
(Module 28), every problem on that host flows to the service automatically — no
per-trigger wiring. This **technical-trigger → business-service mapping** is the
heart of the model.

![A service's problem-tag mapping (service = db) and status calculation rule](assets/module-35/02-service-config.png)

### Service dependencies and status calculation

A parent's status is derived from its children, and you control **how**:

- **Status calculation rule (algorithm):**
  - *Most critical of child services* — the parent is as bad as its worst child
    (right for "is the shop up?").
  - *Most critical if all children have problems* — only fails when every child does
    (for redundant components).
- **Status propagation rule** — *As is / Increase / Decrease / Fixed* — adjusts how a
  child's severity contributes to the parent, and **weight** lets some children
  matter more than others.
- **Additional rules** — override the algorithm in defined conditions.

We add an **additional rule** to the Online Shop root: *"If at least 2 child services
have Warning status or above → set the service to Disaster."* This encodes a real
business judgement — *multiple simultaneous failures are worse than the sum of their
parts*.

![The root's additional rule: two failing components escalate the shop to Disaster](assets/module-35/03-status-rules.png)

### Service impact and root cause

Now make it happen. With the web and API components both failing, watch the chain:
**Web Frontend** and **API Service** turn **High**; because two children are in
problem, the additional rule escalates the **Online Shop** root to **Disaster** — not
just High. The Services view names the **root cause** for each affected service
(*frontend is unavailable*, *API is unreachable*).

![Service impact: two High components escalate the root to Disaster, root causes named](assets/module-35/04-service-failure.png)

This is **business impact from a technical failure**, made explicit: two hosts down →
two services degraded → the whole Online Shop in Disaster → the SLA breaking.

### Uptime, downtime, and how the SLA is calculated

An **SLA** turns service status into a measured promise. Over a **reporting period**
(daily/weekly/monthly), Zabbix accumulates the time a service spent in **problem**
(**downtime**) versus healthy (**uptime**) and computes the **SLI** — the achieved
availability:

```text
SLI = uptime / (uptime + downtime) × 100%
```

compared against the **SLO** target (here **99.5%**). **Scheduled maintenance**
(Module 26) can be **excluded** from downtime, so planned work doesn't count against
you. Each service is evaluated independently and the root rolls up.

### Detailed SLA reports

The **SLA report** (Services → SLA report) shows the SLI per service per period,
coloured against the SLO. After our outage the Online Shop and its failed components
sit well below 99.5%, while the untouched Java and Notification services stay at 100%
— the report quantifies exactly which part of the business missed its target and by
how much.

![The detailed SLA report: SLI per service against the 99.5% target](assets/module-35/05-sla-report.png)

### Executive reporting

Managers don't open Zabbix. The **scheduled report** (Module 33) renders the Business
SLA Dashboard to **PDF** and emails it every Monday — the SLI and service health
delivered to the board without a login. Business service monitoring + SLA + scheduled
report is the full executive-reporting pipeline.

## Docker-Based Demonstration

Using the Online Shop services from Module 28, the instructor adds the Java Service,
shows the problem-tag mapping and the additional status rule, then stops two
components to escalate the root to Disaster — and opens the SLA report to show the
SLI fall against the 99.5% target.

## Hands-On Lab

1. **Refine the service tree.** Tag `demo-java-jmx` with `service:java`, add a trigger
   so it can fail, then **Monitoring → Services → (Edit) → Create service** `Java
   Service` under **Online Shop** with problem tag `service = java`.
   **Expected:** the Online Shop shows **five** child services.

2. **Inspect a mapping.** Open the **Database** service (Edit). Confirm **Problem
   tags** `service = db` and the **Status calculation rule**.
   **Expected:** the service is joined to `demo-postgres`'s problems by tag.

3. **Add an additional rule.** Edit the **Online Shop** root → **Advanced
   configuration → Additional rules → Add**: *If at least **2** child services have
   status **Warning** or above → set status to **Disaster***.
   **Expected:** the rule is listed under the root.

4. **Confirm the SLA target.** **Services → SLA** — `Online Shop SLA`, SLO **99.5%**,
   weekly, covering `tier = online-shop`.
   **Expected:** the SLA is enabled and covers all Online Shop services.

5. **Trigger a service failure.** Stop two components:
   ```bash
   docker stop demo-nginx demo-api
   ```
   **Expected:** within ~1 min **Web Frontend** and **API Service** go **High**; the
   additional rule escalates **Online Shop** to **Disaster**, with root causes named.

6. **Review the SLA calculation.** **Services → SLA report**, select `Online Shop
   SLA`.
   **Expected:** the SLI per service for the period — Online Shop and the failed
   components below **99.5%**, the untouched ones at **100%**. Explain the
   uptime/downtime math.

7. **Explain the business impact, then recover.** State the chain: *hosts down →
   services degraded → Online Shop in Disaster → SLA breached*. Then
   `docker start demo-nginx demo-api` and watch it recover.
   **Expected:** services return to OK; the breach remains recorded in the SLA history.

## Expected Outcome

Participants can build and refine a business service tree, map technical triggers to
services with tags, shape status with algorithms and additional rules, demonstrate
service impact and root cause from a real failure, and read a detailed SLA report —
fully connecting infrastructure monitoring to business outcomes.

## Instructor Notes

- **Lab vs production.** The model is identical; production trees are deeper
  (region → site → service → component) and SLAs map to **contractual** targets with
  penalties. Excluded **maintenance** windows (Module 26) matter a lot in real SLA
  math — planned work must not count as downtime.
- **Tags are the join — verify them first.** A service that never changes status has
  a **problem-tag mismatch**. Tag **hosts** (as we did) so every problem inherits the
  tag with no per-trigger work. Confirm the tag exists on the actual events.
- **Algorithms encode business meaning.** *Most critical of children* = "any failure
  shows". *If all children fail* = "redundant, one survivor is fine". The **additional
  rule** we added expresses "multiple failures are a bigger deal" — teach students to
  translate business rules into these settings, not to accept defaults blindly.
- **Root cause is the headline.** The Services view names the exact problem behind a
  red service — the fastest path from "the Online Shop is down" to "because the API is
  unreachable." Always drill in.
- **SLI swings while history is short.** Our services are days old, so a few minutes
  of downtime crater the SLI. Judge SLAs over a **full period**; don't panic at early
  numbers.
- **Close the loop to reporting.** Business service monitoring is only useful if
  someone sees it — pair it with the **scheduled PDF report** (Module 33) so the SLA
  reaches management automatically.
- **Timing (~45 min).** ~8 min concepts + refine the tree, ~10 min tag mapping +
  algorithms + additional rules, ~12 min trigger failure + impact + root cause, ~12
  min SLA calculation + detailed report, ~3 min executive reporting + recap.

## Lab-State Delta

Added in Module 35 (business service monitoring — kept):

- **Refined tree:** added **Java Service** (serviceid `6`) under Online Shop (root
  `1`), problem tag `service=java`, tier `online-shop`. Required: host tag
  `service:java` on `demo-java-jmx` (10795) and trigger **Online Shop Java service
  unreachable** (triggerid `33056`,
  `nodata(/demo-java-jmx/jmx["java.lang:type=Memory","HeapMemoryUsage.used"],5m)=1`,
  High). Tree now has **5 children**.
- **Additional status rule on root (1):** *type N≥, limit 2, status ≥ Warning(2) →
  Disaster(5)* — two failing components escalate Online Shop to Disaster.
- **Verified:** `docker stop demo-nginx demo-api` → Web Frontend + API Service High →
  rule escalated **Online Shop to Disaster** with root causes; **SLA report** showed
  SLI per service below the 99.5% SLO (Online Shop ~21.5%, Java/Notification 100%).
  Recovered with `docker start`. Screenshots in `content/day-5/assets/module-35/`.
  Lab at 8 hosts.
