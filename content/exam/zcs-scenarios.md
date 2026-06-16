# Zabbix Certified Specialist — Scenario Discussion Cards

Open-ended, real-world scenarios for discussion (not multiple choice). For each:
**say the symptom, name the layer, state the most likely cause, and the fix.** A
strong answer reasons through the *chain*, not just a lucky guess. Model reasoning
follows each — discuss first, then read it.

---

### Scenario 1 — "Active items collect nothing"

**Situation.** A host's **passive** agent items work fine (CPU, memory), but its
**log** item and other *active* items stay empty. The agent container is up.

**Discuss:** what's the most likely cause, and how do you confirm it?

> **Model reasoning.** Passive works ⇒ network and the agent are fine; the problem is
> specific to **active** checks. Active checks are matched by the agent's **`Hostname`**
> and require **`ServerActive`** pointing at the server. The usual cause is a
> **`Hostname` mismatch** (agent name ≠ the Zabbix host name) or missing `ServerActive`.
> Confirm by comparing the agent config to the Zabbix host name, and check the server
> log for the host requesting active checks. *(Modules 7, 19.)*

### Scenario 2 — "A trigger fired but no email arrived"

**Situation.** *Monitoring → Problems* clearly shows a High problem, but the on-call
got nothing.

**Discuss:** how do you find the broken link?

> **Model reasoning.** Walk the **alerting chain** in order: is the **action** enabled
> and do its **conditions** match this event? does the **user** have **media**? does the
> user have **permission** to the problem's host? does the **media type** have a
> **message template** (the classic *"No message defined"*)? Read the action/alert
> status for the exact failure. Don't guess — the chain tells you which link is open.
> *(Modules 27, 32.)*

### Scenario 3 — "The database went down and we got 30 alerts"

**Situation.** PostgreSQL crashed; within a minute the on-call got DB, API, and web
alerts — a storm — and wasted time on the API before realising the DB was the cause.

**Discuss:** how do you make the *next* DB outage page once, with the root cause?

> **Model reasoning.** The API and web failures are **symptoms** of the DB being down.
> Configure **trigger dependencies**: make *API unreachable* (and *web*) **depend on**
> *Database unreachable*. While the DB trigger is in PROBLEM, the dependent symptom
> alerts are **suppressed**, so the on-call is paged about the **root cause** only. Get
> the *direction* right: symptom depends on cause. *(Modules 10, 40.)*

### Scenario 4 — "SNMP returns nothing"

**Situation.** A new network device is added with an SNMP interface, but every SNMP
item is "Not supported" / times out.

**Discuss:** how do you isolate the cause?

> **Model reasoning.** Test **from the command line first**: `snmpget -v2c -c <community>
> <host> <OID>`. If the CLI times out, the problem is the **device side** — wrong
> **community**, wrong **SNMP version** (v1/v2c/v3), a **firewall** blocking UDP 161, or
> the device's ACL not allowing the poller's IP. If the CLI works but Zabbix doesn't,
> it's the **item/interface config** (community macro, OID). The item **Test** shows the
> exact error. *(Module 20.)*

### Scenario 5 — "A user can't see any hosts"

**Situation.** You created a user with an **Admin** role and the correct password. They
log in, but *Monitoring → Hosts* is empty.

**Discuss:** what's wrong?

> **Model reasoning.** This is **capability vs visibility**. The role grants
> *capability* (what they can do), but *visibility* comes from **host-group permissions
> granted through a user group**. The user is in no group with **Read** on the relevant
> host group — so they see nothing. Fix it at the **user group**, not the user or the
> role. Remember **Deny wins** if they're in several groups. *(Module 25.)*

### Scenario 6 — "The queue keeps growing"

**Situation.** *Administration → Queue* shows a steadily rising backlog of values
waiting to be collected.

**Discuss:** what does it mean and what do you check?

> **Model reasoning.** A **growing** queue means the server **can't keep up**. Look at
> the **Zabbix server health** dashboard: a poller type pinned near 100 % (raise its
> `Start*` count), a full **history write cache** (the database can't absorb writes —
> tune the DB/partitioning), or **unreachable hosts** tying up pollers. A small steady
> queue is normal; a rising one is a capacity signal. *(Modules 13, 30.)*

### Scenario 7 — "Design: a new microservice exposes JSON metrics"

**Situation.** A new service publishes metrics at `http://svc:8080/metrics` as a JSON
object with a dozen fields. You must monitor several of them.

**Discuss:** how do you collect this efficiently?

> **Model reasoning.** Don't poll the endpoint a dozen times. Use **one HTTP agent
> master item** to fetch the JSON, then **dependent items** that each extract a field
> with **JSONPath** preprocessing. One request, many metrics — efficient and the
> standard pattern. Package it as a **template** so it's reusable. *(Modules 9, 18.)*

### Scenario 8 — "Design: 200 branch offices"

**Situation.** You must monitor servers in 200 remote sites with limited WAN links and
no direct access from the central server.

**Discuss:** outline the architecture.

> **Model reasoning.** Deploy a **Zabbix proxy** per site (or region): the proxy
> collects locally and forwards to the server, buffering if the WAN drops. Use **active
> proxies** (they connect out, friendlier to firewalls). Standardise with **templates**
> and **mass operations**, and onboard hosts automatically with **auto-registration /
> network discovery** rather than by hand. *(Modules 14, 15, 17.)*

### Scenario 9 — "The SLA says 60 % but everything is green now"

**Situation.** Management asks why the Online Shop SLA report shows 60 % when the
dashboard is all green.

**Discuss:** explain it.

> **Model reasoning.** The **SLI** is computed over the whole **reporting period**, not
> the current instant. Earlier outages this period accumulated **downtime** that counts
> against the SLO — *"green now"* doesn't erase *"down earlier."* If the downtime was
> **planned**, it should have been in a **maintenance** window (which can be excluded
> from SLA math). Judge SLAs over a full period, and use maintenance for planned work.
> *(Modules 26, 35.)*

### Scenario 10 — "An item is Not supported"

**Situation.** One item shows the red **Not supported** state.

**Discuss:** how do you diagnose it?

> **Model reasoning.** Open the item and **read its error** — Zabbix states the cause:
> a **bad key/parameters**, a **missing dependency** (e.g. a poller type not started, or
> a plugin/driver absent), or a **permission** problem. Reproduce with the item **Test**
> or `zabbix_get`. Fix the root cause or disable the check; don't leave unsupported
> items accumulating. *(Modules 30, 31.)*

---

*Use these to rehearse the exam's reasoning style and to practise explaining a design
to a team. If a scenario stumps you, redo the referenced module's hands-on lab.*
