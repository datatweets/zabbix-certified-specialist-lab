# Module 22: Performance Monitoring

## Learning Objectives

By the end of this module participants can collect performance data from sources
that are not plain agents: query a database over **ODBC**, read a Java
application's JVM over **JMX** (through the Zabbix **Java gateway**), and derive new
metrics with **calculated** and **aggregate** items — rounding out the Online
Shop's database and Java tiers.

## Topics

### Three ways to reach "deeper" performance data

The Online Shop's slow moments usually live below the agent: a saturated database,
a JVM running out of heap, or a number you must *compute* from several others.
Zabbix has a purpose-built collector for each:

- **ODBC** — run SQL against a database and store the result as an item.
- **JMX** — read a Java app's managed beans (memory, threads, uptime) via the
  **Java gateway**.
- **Calculated / aggregate items** — build new metrics from existing ones,
  on one host or across many.

### Database monitoring with ODBC

An **ODBC item** (item type **Database monitor**) lets the Zabbix **server** open a
database connection and run a `SELECT`, storing the first value of the result. It
needs three things on the server:

1. An **ODBC driver** for the database (here the PostgreSQL driver
   `psqlodbcw.so`).
2. A **driver registration** in `/etc/odbcinst.ini`.
3. A **DSN** (data source name) in `/etc/odbc.ini` describing the target.

In this lab those are **baked into the server image** (`content/lab/zabbix-server/`)
so ODBC works out of the box; the DSN is named **`shopdb`** and points at
`demo-postgres` / database `shop`:

```ini
# /etc/odbcinst.ini
[PostgreSQL]
Driver = /usr/lib/psqlodbcw.so

# /etc/odbc.ini
[shopdb]
Driver     = PostgreSQL
Servername = demo-postgres
Port       = 5432
Database   = shop
```

The item key is `db.odbc.select[<unique-id>,<dsn>]`; the **SQL** lives in the
item's *SQL query* field and the login in *User name* / *Password*:

![An ODBC Database monitor item: DSN key, SQL query, credentials](assets/module-22/01-odbc-item.png)

We collect two database performance metrics for the Online Shop:

- **Active connections** — `SELECT count(*) FROM pg_stat_activity WHERE
  state='active';`
- **Database size** — `SELECT pg_database_size('shop');`

### Java application monitoring with JMX

Java apps expose internals through **JMX** (Java Management Extensions) — MBeans
for heap, threads, GC, uptime. Zabbix does **not** speak JMX directly; it asks the
**Java gateway** (the `zabbix-java-gateway` container), which connects to the app
and returns the value. The server is already wired to it (`ZBX_JAVAGATEWAY` and
`ZBX_STARTJAVAPOLLERS` are set in `compose_lab.yaml`).

`demo-java-jmx` is a Tomcat app started with JMX on port **12345** (no auth, lab
only). The host carries a **JMX interface** (`demo-java-jmx:12345`), and items are
type **JMX agent** with a key naming the MBean and attribute:

```text
jmx["java.lang:type=Memory","HeapMemoryUsage.used"]
jmx["java.lang:type=Threading","ThreadCount"]
jmx["java.lang:type=Runtime","Uptime"]
```

![A JMX agent item: jmx[] key, JMX interface, JMX endpoint](assets/module-22/02-jmx-item.png)

The **JMX endpoint** `service:jmx:rmi:///jndi/rmi://{HOST.CONN}:{HOST.PORT}/jmxrmi`
is filled in by default and resolves from the host's JMX interface.

### Calculated and aggregate items

Sometimes the metric you want isn't collected anywhere — you **compute** it.

- A **calculated item** (type **Calculated**) holds a **formula** referencing other
  items by `/host/key`. It runs on the server, no polling of the device. Example —
  database size in MB instead of bytes:

  ```text
  last(/demo-postgres/db.odbc.select[pg.db.size,shopdb])/1048576
  ```

  ![A calculated item deriving MB from the ODBC byte value](assets/module-22/03-calculated-item.png)

- An **aggregate** is a calculated item using a **`*_foreach`** function to roll up
  **many** items into one — averages, sums, counts across a host group. Example —
  average JVM heap across every host in *Java Applications*:

  ```text
  avg(last_foreach(/*/jmx["java.lang:type=Memory","HeapMemoryUsage.used"]?[group="Java Applications"]))
  ```

  (In Zabbix 7.x the old `aggregate` item type is gone — aggregation is just a
  calculated item with `avg/sum/count/min/max` over `*_foreach`.)

All of these are ordinary items afterward: they show in Latest data, draw graphs,
and drive triggers.

![ODBC, JMX, and calculated values side by side in Latest data](assets/module-22/04-latest-data.png)

## Docker-Based Demonstration

The instructor shows the ODBC driver and DSN already present on the server, creates
the two ODBC database items, adds the `demo-java-jmx` host with a JMX interface and
three JVM items (collected through the Java gateway), then builds a calculated item
(bytes → MB) and an aggregate (`avg` heap across the Java group), and views them all
arriving together in Latest data.

## Hands-On Lab

1. **Confirm ODBC works on the server.** The PostgreSQL driver and the `shopdb`
   DSN are baked into the lab image — prove the connection:
   ```bash
   docker exec zabbix-server sh -c "echo 'SELECT count(*) FROM pg_stat_activity;' | isql -v shopdb shop shop"
   ```
   **Expected:** `Connected!` and a row count. If this fails, ODBC is misconfigured
   — fix it here before touching Zabbix.

2. **Create the host `demo-postgres`.** **Data collection → Hosts → Create host**,
   name `demo-postgres`, groups `Databases` and `Docker Lab`. No interface is
   needed — ODBC items run on the server.
   **Expected:** the host exists.

3. **Add the ODBC items.** On `demo-postgres` create two items, Type **Database
   monitor**, *User name* `shop`, *Password* `shop`:
   - `DB active connections` — key `db.odbc.select[pg.active.connections,shopdb]`,
     SQL `SELECT count(*) FROM pg_stat_activity WHERE state='active';`
   - `Online Shop database size` — key `db.odbc.select[pg.db.size,shopdb]`, SQL
     `SELECT pg_database_size('shop');`, Units `B`

   **Expected:** within a minute both collect values (a small connection count; a
   size of a few MB).

4. **Create the host `demo-java-jmx` with a JMX interface.** Create a host,
   groups `Java Applications` and `Docker Lab`, and add a **JMX interface**: DNS
   `demo-java-jmx`, port `12345`.
   **Expected:** the host has one JMX interface.

5. **Add the JVM items.** On `demo-java-jmx` create three items, Type **JMX agent**,
   on the JMX interface:
   - `JVM heap memory used` — `jmx["java.lang:type=Memory","HeapMemoryUsage.used"]`,
     Units `B`
   - `JVM thread count` — `jmx["java.lang:type=Threading","ThreadCount"]`
   - `JVM uptime` — `jmx["java.lang:type=Runtime","Uptime"]`, Units `ms`

   **Expected:** the Java gateway collects them within a minute — heap of tens of
   MB, a couple dozen threads, a climbing uptime.

6. **Build a calculated item.** On `demo-postgres`, create an item Type
   **Calculated**, key `pg.db.size.mb`, *Type of information* **Numeric (float)**,
   Units `MB`, Formula:
   ```text
   last(/demo-postgres/db.odbc.select[pg.db.size,shopdb])/1048576
   ```
   **Expected:** it reports the same size as the ODBC item, in MB.

7. **Build an aggregate item.** On `demo-java-jmx`, create an item Type
   **Calculated**, key `jvm.heap.avg`, Units `B`, Formula:
   ```text
   avg(last_foreach(/*/jmx["java.lang:type=Memory","HeapMemoryUsage.used"]?[group="Java Applications"]))
   ```
   **Expected:** with one Java host it equals that host's heap; add more Java hosts
   and it averages them — no edit required.

8. **View everything together.** **Monitoring → Latest data**, filter to
   `demo-postgres` and `demo-java-jmx`.
   **Expected:** ODBC, JMX, and calculated metrics side by side — the Online Shop's
   database and Java tiers now report performance.

## Expected Outcome

Participants can monitor a database over ODBC, a Java application over JMX via the
Java gateway, and compute derived metrics with calculated and aggregate items —
extending the Online Shop to its data and application tiers and setting up the
performance triggers and dashboards of later modules.

## Instructor Notes

- **Lab vs production.** The ODBC driver and DSN are pre-baked here
  (`content/lab/zabbix-server/`); in production you install the driver on the
  **server (or proxy)** doing the polling and define the DSN there. JMX is real —
  the only lab shortcut is **no authentication/TLS** on the JMX port; production
  JMX uses credentials and often TLS (set them on the item / gateway).
- **ODBC runs on the server, JMX runs through the gateway.** Neither needs an agent
  on the target. A "Database monitor" item failing is almost always the **DSN,
  driver, or credentials** — test with `isql` first. A JMX item failing is almost
  always the **gateway not running, not configured (`ZBX_JAVAGATEWAY`), or the app
  not exposing JMX** on that port.
- **Least privilege for DB monitoring.** Don't monitor as a superuser. In
  production create a read-only user with just the grants the queries need; we use
  `shop` here for simplicity.
- **Keep ODBC queries cheap and infrequent.** Each ODBC item is a real query on a
  real interval — a heavy `SELECT` every 10 s can hurt the very database you watch.
  Prefer fast catalog/stat views (`pg_stat_*`) and modest intervals.
- **Calculated ≠ dependent.** A **calculated** item *pulls* from other items by a
  formula on its own schedule; a **dependent** item (Module 9) is *pushed* from one
  master value by preprocessing. Use calculated for math across items, dependent
  for extracting from one payload.
- **Aggregate quirk.** `*_foreach` evaluates over whatever matches the filter at
  run time, so new hosts join the aggregate automatically — powerful, but it also
  means an empty match returns "not supported". Scope the filter to a real group.
- **Timing (~45 min).** ~15 min ODBC (drivers/DSN + two items), ~15 min JMX
  (gateway + interface + JVM items), ~12 min calculated + aggregate, ~3 min recap.

## Lab-State Delta

Added in Module 22 (all kept — database and Java performance tiers):

- **Lab image change:** `zabbix-server` now builds from
  `content/lab/zabbix-server/` (official image + `psqlodbc`/`unixodbc` +
  `odbcinst.ini`/`odbc.ini`); DSN **`shopdb`** → `demo-postgres`/`shop`.
  `compose_lab.yaml` updated to `build:` it.
- **Host group:** `Java Applications` (groupid `28`).
- **Host `demo-postgres` (10794)** — groups Databases + Docker Lab, no interface.
  ODBC items: `DB active connections` (`71503`,
  `db.odbc.select[pg.active.connections,shopdb]`), `Online Shop database size`
  (`71504`, `db.odbc.select[pg.db.size,shopdb]`, B). Calculated:
  `Online Shop database size (MB)` (`71508`, key `pg.db.size.mb`).
- **Host `demo-java-jmx` (10795)** — groups Java Applications + Docker Lab, **JMX
  interface** `demo-java-jmx:12345` (interfaceid `88`). JMX items: `JVM heap memory
  used` (`71505`), `JVM thread count` (`71506`), `JVM uptime` (`71507`). Aggregate:
  `Average JVM heap used (Java Applications)` (`71509`, key `jvm.heap.avg`,
  `avg(last_foreach(...?[group="Java Applications"]))`).
- All collecting green. Screenshots in `content/day-3/assets/module-22/`. Lab at
  8 hosts.
