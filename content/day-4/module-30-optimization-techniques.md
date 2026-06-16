# Module 30: Optimization Techniques

## Learning Objectives

By the end of this module participants can reason about Zabbix performance: read the
**internal health metrics** (NVPS, process utilization, cache, queue), tune **item
intervals** and **housekeeping/retention**, clean up **unsupported items**, apply
**database** and **template** design principles, and place all this against Zabbix's
**release lifecycle** and the lab's **Docker** resource model.

## Topics

### The one number that matters: NVPS

Zabbix performance starts with **NVPS — new values per second**: how many metric
values the server ingests every second. **Reports → System information** shows the
**Required server performance** for your config — our lab is **~6.8 NVPS** with 8
hosts and ~500 items. A real deployment might be thousands. Almost every tuning
decision is about keeping NVPS sustainable for your hardware.

![System information: NVPS, item/trigger counts, version status](assets/module-30/01-system-info.png)

### How the server spends its time: internal processes

The server is a pipeline of specialized processes, each of which can become a
bottleneck:

- **Pollers** actively fetch passive checks; **unreachable pollers** handle
  down hosts; **JMX/HTTP/ICMP** pollers for those types.
- **Trappers** receive pushed data (active agents, `zabbix_sender`, traps).
- **Preprocessing workers** run the preprocessing steps (Module 9).
- **History syncers** write incoming values to the database.
- **Housekeeper** deletes old data.

The **Zabbix server health** dashboard graphs each process's **% utilization**, the
**cache usage**, the **value cache effectiveness**, and the **queue** — the live
view of where time goes. A process pinned near 100% is your bottleneck; raise its
`Start…` count in the server config.

![The Zabbix server health dashboard: NVPS, process utilization, cache, queue](assets/module-30/02-server-health.png)

### The queue

The **queue** (Module 13) is the count of values waiting to be collected. A small,
steady queue is healthy; a **growing** queue means the server can't keep up —
too few pollers, an overloaded database, or unreachable hosts holding pollers.
**Administration → Queue** and the health dashboard both surface it. The queue is
the earliest warning that you are out of headroom.

### Caches

The server keeps hot data in memory to avoid hitting the database:

- **Configuration cache** — hosts/items/triggers definitions.
- **Value cache** — recent history for trigger evaluation.
- **History write cache** — buffers values before the history syncers flush them.

Each has a **% used** metric. A cache filling toward 100% (especially the history
write cache) signals the database can't absorb writes fast enough — tune the cache
size **and** the database.

### Housekeeping, history, trends, and database growth

The **database** is usually the first thing to hurt at scale, and **history** and
**trends** are the biggest tables:

- **History** — every raw value (per the item's history period; lab default **31d**).
- **Trends** — hourly min/avg/max rollups, kept far longer (lab default **365d**).

**Administration → Housekeeping** sets retention and whether to **override** every
item's per-item setting with a global one. The **housekeeper** process then deletes
expired data. Shorter retention = smaller, faster database.

![Housekeeping: history 31d, trends 365d, and the override toggles](assets/module-30/03-housekeeping.png)

### Tuning item intervals

Every item at interval *N* contributes `1/N` to NVPS. Collecting CPU every **1s**
when **1m** would do multiplies load 60×. Right-size intervals to how fast the
metric actually changes; use **trends** for long-term graphs instead of keeping raw
1s history for a year. Fewer items and sensible intervals are the cheapest
optimization there is.

### Unsupported items

An **unsupported** item is one the server cannot collect (bad key, missing
dependency, a poller type not started). They are dead weight — config the server
still processes — and usually flag a real misconfiguration. **Data collection →
Hosts → Items**, filtered to **State: Not supported**, lists them. In our lab the
unsupported items are internal checks for **processes this deployment doesn't run**
(IPMI, SNMP trapper, VMware, connectors) — harmless, but in production you fix or
disable them so they stop generating noise and load.

![Items in the Not supported state — review and clean these up](assets/module-30/04-unsupported-items.png)

### Template design, releases, and Docker limits

- **Template design** affects performance: prefer **dependent items** (one request,
  many metrics — Module 9/18) over many separate polls, and reasonable intervals in
  the template so every linked host inherits good defaults.
- **Release lifecycle:** Zabbix ships **LTS** releases (e.g. 7.0, ~5 years support)
  for stable production, and **standard** releases (7.2, **7.4** — this course) with
  the newest features but a short support window. System information shows your
  version and whether it is **up to date**. Plan upgrades around LTS for production.
- **Docker resource limits:** in this lab the containers run unconstrained; in
  production you set `deploy.resources.limits` (CPU/memory) per service in Compose so
  the server, database, and proxies get guaranteed, bounded resources.

## Docker-Based Demonstration

The instructor opens **System information** (NVPS, counts, version), tours the
**Zabbix server health** dashboard (process utilization, cache, queue), shows the
**Housekeeping** retention settings, and filters the items list to **Not supported**
— then discusses interval tuning and Docker resource limits.

## Hands-On Lab

1. **Read the capacity number.** Open **Reports → System information**.
   **Expected:** *Required server performance, new values per second* (~**6.8** here),
   plus host/item/trigger counts and whether the version is up to date.

2. **View internal process usage.** Open the **Zabbix server health** dashboard
   (**Dashboards → All dashboards → Zabbix server health**).
   **Expected:** graphs for **values processed per second**, **utilization of data
   collectors** and **internal processes**, **cache usage**, and **queue size** — all
   low in this small lab.

3. **Review the queue.** **Administration → Queue**.
   **Expected:** few or zero delayed items (a healthy lab). A growing queue would
   mean the server is under-provisioned (Module 13).

4. **Review unsupported items.** **Data collection → Hosts → Items**, set **State:
   Not supported**.
   **Expected:** the internal checks for processes this deployment doesn't run (IPMI,
   SNMP trapper, VMware, connectors). Read one item's error to see *why*.

5. **Adjust an item's update interval.** Open any high-frequency item and change its
   **Update interval** (e.g. from `30s` to `1m`).
   **Expected:** the item collects half as often — directly lowering NVPS. Multiply
   across thousands of items to see why intervals matter.

6. **Inspect retention.** **Administration → Housekeeping**.
   **Expected:** **History** `31d` and **Trends** `365d`, with the **Override**
   toggles off (per-item settings apply). Discuss shortening history to shrink the
   database.

7. **Discuss Docker limits.** Look at the lab's `compose_lab.yaml`.
   **Expected:** no hard CPU/memory limits in the lab; discuss adding
   `deploy.resources.limits` for the server and database in production.

## Expected Outcome

Participants can locate and interpret Zabbix's performance signals — NVPS, process
utilization, cache, and queue — and apply the main levers: item intervals,
history/trends retention, unsupported-item cleanup, template design, and (in
production) database tuning and Docker resource limits. They understand that
**design decisions drive performance**.

## Instructor Notes

- **Lab vs production.** A 6.8-NVPS lab never strains anything — say so, then scale
  the thinking: at thousands of NVPS the database and history syncers dominate, and
  you tune `Start*` process counts, cache sizes, and DB storage. The **metrics to
  watch are identical**; only the numbers change.
- **Tune by evidence, not guesswork.** Find the pinned process / full cache /
  growing queue on the health dashboard first, then change the matching parameter.
  Raising every `Start*` count blindly wastes memory.
- **The database is the usual ceiling.** History/trends growth and slow deletes are
  the classic pain. In production: shorten retention, and use **partitioning**
  (MySQL) or **TimescaleDB** (PostgreSQL) so housekeeping drops whole partitions
  instead of row-by-row deletes.
- **Intervals and dependent items are free wins.** Right-sizing intervals and
  collecting many metrics from one request (dependent items, Module 9/18) cut NVPS
  without losing visibility — do these before adding hardware.
- **Unsupported ≠ ignore.** Each unsupported item is either a real misconfiguration
  to fix or a check to disable. Left alone they accumulate and mislead. Ours are
  benign (disabled poller types) — show students how to read the error to decide.
- **Pick your release deliberately.** Production should track an **LTS** (7.0) for
  stability; standard releases (7.4) are for the newest features and short-lived
  support. Don't chase every release on critical infrastructure.
- **Right-size Docker.** Without limits, one runaway container can starve the others.
  Production Compose sets CPU/memory limits and reservations per service.
- **Timing (~45 min).** ~10 min NVPS + internal processes, ~10 min health dashboard +
  queue + caches, ~10 min housekeeping/history/trends + DB strategy, ~8 min item
  intervals + unsupported cleanup, ~7 min release lifecycle + Docker limits + recap.

## Lab-State Delta

Module 30 (optimization — read-only review, no permanent changes):

- **Reviewed (no objects created):** System information (NVPS **~6.8**, 8 hosts, 507
  items / 28 not supported, 233 triggers, version 7.4.11 up to date); **Zabbix
  server health** dashboard (process utilization, cache, queue); **Housekeeping**
  (history `31d`, trends `365d`, overrides off); **unsupported items** on Zabbix
  server (disabled poller types — benign).
- Tuning techniques (item intervals, retention, dependent items, DB partitioning,
  Docker limits, LTS vs standard releases) taught as concepts. No lab objects added.
  Screenshots in `content/day-4/assets/module-30/`. Lab unchanged (8 hosts).
