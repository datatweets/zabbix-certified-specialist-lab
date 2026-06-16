# Mock Exam — Answer Key & Explanations

**Pass mark: 36 / 45 (80 %).** Each answer notes the **module to revisit** if you
missed it. Concepts are stable across Zabbix 7.0 (exam) and 7.4 (this course).

| Q | Ans | Why | Revisit |
|---|-----|-----|---------|
| 1 | **C** | The **database** stores config + history/trends; the server processes, the frontend displays. | M1, M4 |
| 2 | **B** | Server/trapper port is **10051**; the agent's *passive* port is 10050. | M1, M4, M6 |
| 3 | **C** | The **web service** renders dashboards to PDF for scheduled reports. | M33 |
| 4 | **B** | The **Java gateway** bridges Zabbix to **JMX** apps; the server doesn't speak JMX directly. | M22 |
| 5 | **B** | Compose runs each role as a **separate container** on a shared network. | M2 |
| 6 | **B** | **Passive** = the server/proxy connects *to* the agent (10050). Active = agent connects to server. | M6, M7 |
| 7 | **B** | Active checks are matched by the agent's **`Hostname`** = the Zabbix host name. A mismatch = no active data. | M7, M19 |
| 8 | **B** | **Trapper** items receive *pushed* values (`zabbix_sender`, traps). | M11 |
| 9 | **C** | `pused` = **percentage used**; `pfree` would be percent free. | M9 |
| 10 | **B** | A **dependent** item derives from a **master** item via preprocessing — one fetch, many metrics. | M9, M18 |
| 11 | **A** | A **UserParameter** runs a local command for a custom agent key. (Trapper is *push*, not custom-pull.) | M11 |
| 12 | **B** | **Change per second** turns an increasing counter into a **rate**. | M9 |
| 13 | **B** | 7.x uses **function-first** `last(/host/key)`. The `{host:key.last()}` form is pre-7.0. | M10 |
| 14 | **B** | A dependency **suppresses** the dependent trigger while the parent trigger is in PROBLEM (root-cause). | M10, M40 |
| 15 | **B** | The **recovery expression** defines when a problem is **resolved**. | M10 |
| 16 | **B** | `nodata(...,5m)=1` ⇒ **no data for 5 minutes** — the classic "is it alive?" check. | M10, M20 |
| 17 | **D** | Severity order: Not classified < Information < Warning < Average < High < **Disaster**. | M10 |
| 18 | **B** | Linking **inherits** items/triggers and keeps them **in sync** with the template. | M17, M18 |
| 19 | **B** | 7.x exports default to **YAML** (also XML/JSON). | M29 |
| 20 | **C** | Import matches by **UUID**, which makes imports idempotent and safe to re-run. | M29 |
| 21 | **B** | An LLD rule returns **JSON** of discovered entities with `{#MACRO}` keys. | M23 |
| 22 | **B** | Item prototypes use **`{#MACRO}`** LLD macros, expanded per discovered object. | M23 |
| 23 | **B** | An LLD **filter** includes/excludes objects by matching a macro against a **regex**. | M23 |
| 24 | **B** | A **proxy** collects data for remote/distributed sites and forwards it to the server. | M14 |
| 25 | **B** | An **active** proxy **connects to** the server; a passive proxy waits to be polled. | M14 |
| 26 | **B** | 7.x API auth = **`Authorization: Bearer <token>`**. The body `auth` field is deprecated. | M36 |
| 27 | **B** | No message template ⇒ "**No message defined for media type**" — the classic first-time alerting bug. | M27 |
| 28 | **B** | **Escalation steps** notify more people at **increasing intervals** as a problem persists. | M27 |
| 29 | **B** | A **recovery operation** fires when the problem is **resolved** (the "all clear"). | M27 |
| 30 | **B** | **User media** = the **address** and the **severity/time window** for notifying that user. | M27 |
| 31 | **B** | Scope actions with **conditions** (host group, severity, tag) to avoid alert storms. | M27, M32 |
| 32 | **B** | Permissions are granted through **user groups**, on **host groups** — never per user directly. | M25 |
| 33 | **B** | **Deny always wins** across multiple user groups. | M25, M32 |
| 34 | **B** | A **Super admin** always sees **all** host groups, regardless of permissions. | M25 |
| 35 | **A** | Agent↔server encryption uses **PSK** or **certificate (TLS)**. | M26 |
| 36 | **A** | The agent **`Server`** parameter is the **allow-list** of who may query it (passive). | M26, M31 |
| 37 | **B** | A host **map element changes colour** with the host's problem status. | M34 |
| 38 | **B** | **Top 100 triggers** ranks the most frequently firing triggers. | M33 |
| 39 | **B** | Scheduled PDFs need the **web service** + a reachable **Frontend URL**. | M33 |
| 40 | **B** | 7.x services map to problems by **tags** (problem tags), not host IDs. | M28, M35 |
| 41 | **B** | **SLI = uptime / (uptime + downtime)** over the reporting period, vs the SLO. | M35 |
| 42 | **B** | "Most critical of child services" ⇒ the parent **reflects its worst child**. | M28, M35 |
| 43 | **B** | **`zabbix_get -s <host> -k <key>`** tests the passive agent path directly. | M6, M31 |
| 44 | **B** | Maintenance **suppresses** problems (hidden unless "show suppressed"); it doesn't delete them. | M26 |
| 45 | **B** | "**Not supported**" = the server **can't collect** the item (bad key, missing dependency, permission). | M30, M31 |

## Scoring

- **41–45 (91 %+):** exam-ready. Skim weak topics and book the exam.
- **36–40 (80–89 %):** passing, but tighten the misses below.
- **27–35 (60–78 %):** close — revisit each missed module, then retake.
- **< 27:** rebuild fundamentals (Days 1–2) before retrying.

## Turn misses into a study plan

For every wrong answer, write down the **topic** and the **module** from the table,
then **redo that module's hands-on lab in the live Docker lab** — doing beats
re-reading. Group your misses:

- **Data collection** (Q6–12): Modules 6–9, 11
- **Triggers** (Q13–17): Module 10
- **Templates & LLD** (Q18–23): Modules 17, 18, 23, 29
- **Proxy** (Q24–25): Module 14
- **Alerting** (Q26–31): Module 27
- **Users & security** (Q32–36): Modules 25, 26
- **Visualization & reports** (Q37–39): Modules 33, 34
- **Services & SLA** (Q40–42): Modules 28, 35
- **Troubleshooting & ops** (Q43–45): Modules 26, 30, 31
