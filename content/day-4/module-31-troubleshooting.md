# Module 31: Troubleshooting Zabbix

## Learning Objectives

By the end of this module participants can follow a **structured troubleshooting
process**: read the symptom in the UI, isolate the failing layer, use the diagnostic
toolchain (`docker logs`, the Zabbix logs, `zabbix_get`, network and DNS checks, the
item **Test**), fix the root cause, and verify recovery — applied to the most common
Zabbix failures.

## Topics

### A method, not a guess

Most Zabbix problems are not mysterious — they are one broken link in a known chain.
The fix is a **repeatable method**:

1. **Read the symptom** — what does the UI actually say? (a red availability icon, a
   "not supported" item, a missing alert).
2. **Isolate the layer** — frontend, server, database, network, agent, or config?
3. **Test that layer directly** — from the component that talks to it, with the
   smallest possible check.
4. **Read the logs** — the server/agent log usually states the cause in plain text.
5. **Fix the root cause, then verify** — confirm with the same test that first failed.

Work **outside-in** (is the container even up? can we reach the port? does the name
resolve? does the check return a value?) and the cause falls out quickly.

### The diagnostic toolchain

- **`docker ps -a`** — is the container running, exited, or restarting?
- **`docker logs <container>`** — the dockerized Zabbix server/agent log to stdout;
  this is your **Zabbix log**. Grep it for the host name.
- **`zabbix_get -s <host> -k <key>`** — ask the agent for one value, exactly as the
  server does. The fastest agent test.
- **Network/DNS** — `nc -zv <host> 10050` (port reachable?), `getent hosts <host>`
  (does the name resolve?).
- **The UI** — a host's **availability** icon carries the exact error on hover; an
  item's **Test → Get value** reproduces the failure with the precise message.

### The Zabbix data path (where things break)

```text
frontend ──HTTP──> server ──poll/trap──> agent/device
   │                  │
   └── needs DB ──────┴── needs DB (zabbix-db)
```

Each arrow is a failure point, and each maps to a symptom:

| Symptom | Likely layer | First check |
|---|---|---|
| Frontend "cannot connect to server" | frontend ↔ server | `ZBX_SERVER_HOST`, server up (`docker ps`) |
| Server won't start / no data at all | server ↔ database | server log "cannot connect to database", DB up |
| One host's agent icon is red | server ↔ agent | `zabbix_get`, port 10050, `Server=` allow-list |
| Active checks missing only | agent `Hostname` | must match the Zabbix host name (Module 7) |
| Item "not supported" | item config | read the item error (Module 30) |
| Alert never arrives | action/media chain | media type template, user media, perms (Module 27) |
| User can't see hosts | permissions | user group host-group rights (Module 25) |

### DNS vs IP, and Docker networking

In this lab every container talks by **name** on the `zabbix-lab` network. A subtle
trap: when a container **stops**, Docker removes its name from DNS, so the failure
shows as a **name-resolution** error (`getaddrinfo() failed`, `NXDOMAIN`), not a
plain "connection refused". In production the equivalents are a wrong/locked-down
**DNS** entry or a host that only answers on its **IP** — when DNS is unreliable,
configure the interface with an **IP** instead. Containers must also share a
**network**; a host on a different Docker network simply can't be reached.

## Docker-Based Demonstration

The instructor breaks things on purpose and diagnoses each with the toolchain:
**stop the database**, **stop an agent**, **change an agent's hostname**, **break the
web endpoint**, **break the SMTP settings**, **break the SNMP community** — showing
that the *method* is the same every time. Below is the worked example for an agent.

### Worked example: "Zabbix agent is not available"

**Break it** — stop the agent container:

```bash
docker stop zabbix-agent-basic
```

**1 — is the container up?**

```bash
docker ps -a --format '{{.Names}} {{.Status}}' | grep zabbix-agent-basic
# zabbix-agent-basic   Exited (0) ...        <-- not running
```

**2 — can the server reach it on the network / does the name resolve?**

```bash
docker exec zabbix-server nc -zv zabbix-agent-basic 10050
# nc: bad address 'zabbix-agent-basic'
docker exec zabbix-server getent hosts zabbix-agent-basic
# (empty)  -> NXDOMAIN: the stopped container left DNS
```

**3 — ask the agent directly:**

```bash
docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k agent.ping
# zabbix_get: Get value error: getaddrinfo() failed for 'zabbix-agent-basic'
```

**4 — read the server log:**

```bash
docker logs --since 2m zabbix-server | grep zabbix-agent-basic
# ...failed: another network error, wait for 15 seconds
# temporarily disabling Zabbix agent checks on host "zabbix-agent-basic": interface unavailable
```

**In the UI**, the host's availability icon turns red; hovering it shows the exact
error — *Cannot establish TCP connection … Host is unreachable* — so you can diagnose
without the CLI at all.

![The agent host's availability error, shown on hover](assets/module-31/01-agent-unavailable.png)

A trigger also raises a problem, so the failure is alerted, not just visible:

![The "agent is not available" problem in Monitoring → Problems](assets/module-31/02-agent-problem.png)

The item **Test → Get value** reproduces the failure at the item level with the
precise message — the fastest way to confirm a single check:

![The item Test reproduces the connection error](assets/module-31/03-item-test-error.png)

**Fix and verify:**

```bash
docker start zabbix-agent-basic
docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k agent.ping
# 1                              <-- recovered
```

![The host availability is green again after the fix](assets/module-31/04-recovered.png)

## Hands-On Lab

Work each scenario with the **same method**: symptom → isolate → test → log → fix →
verify.

1. **Agent not available.** `docker stop zabbix-agent-basic`. Diagnose with
   `docker ps -a`, `zabbix_get`, the availability error, and the server log; then
   `docker start` it.
   **Expected:** the red availability icon and `getaddrinfo`/`unreachable` error,
   then green after restart.

2. **Web scenario failing.** `docker stop demo-nginx` (Module 21). Check **Monitoring
   → Web**.
   **Expected:** the scenario names the failed step — *Step "Home page" failed:
   Could not resolve host*. Start the container to recover.

3. **Database unavailable.** Inspect the dependency: `docker logs zabbix-server | grep
   -i database`.
   **Expected:** with `zabbix-db` healthy, no errors; understand that stopping it
   would log *cannot connect to database* and halt the server. (Don't stop the DB in
   a shared lab.)

4. **Unsupported item.** **Data collection → Hosts → Items**, filter **State: Not
   supported** (Module 30), open one and read its **error**.
   **Expected:** the error states the cause (bad key, missing process, permission).

5. **Email alert not sent.** Re-check the Module 27 chain: action enabled & matching,
   user media present, media type **has a message template**.
   **Expected:** the *"No message defined for media type"* class of error is found by
   walking the chain.

6. **SNMP check failing.** Recall Module 20: test from the CLI
   `docker exec demo-snmp-device snmpget -v2c -c <community> localhost 1.3.6.1.2.1.1.5.0`
   and the item **Test**.
   **Expected:** a wrong community produces an SNMP **timeout**; the correct one
   returns the value.

## Expected Outcome

Participants can troubleshoot Zabbix methodically: map a symptom to a layer, test
that layer with the right tool, confirm the cause in the logs, fix it, and verify —
rather than guessing. They know the common failures and where each one is diagnosed.

## Instructor Notes

- **Teach the method, not a list of fixes.** The scenarios change; the
  outside-in process does not. Make students state *which layer* they are testing
  before they run a command.
- **The log usually just tells you.** `docker logs zabbix-server` (and the agent log)
  states "cannot connect to database", "interface unavailable", "cannot resolve" in
  plain English. Read it before theorizing.
- **`zabbix_get` is the single best agent tool.** It isolates the server↔agent path
  from everything else. If `zabbix_get` works but the item doesn't, the problem is
  config (key, interface, permissions), not connectivity.
- **Docker-specific traps.** A stopped container disappears from DNS (`NXDOMAIN`),
  not just refuses connections; containers must share a network to talk; names, not
  `localhost`, address other services. Call these out — they confuse newcomers.
- **Active vs passive.** A red availability icon is a **passive** path failure
  (server → agent). Missing **active** items with the agent up is almost always a
  **Hostname mismatch** (Module 7) — a different diagnosis entirely.
- **Change one thing, then re-test.** Don't fix three things at once; you won't know
  which mattered. Verify with the exact check that first failed.
- **Lab vs production.** Here we `docker stop`/`start`; in production the same
  symptoms come from crashed services, firewalls, full disks, expired certificates,
  or DNS changes — but the layered method and the tools (`systemctl status`, service
  logs, `zabbix_get`, `nc`, `dig`) are identical.
- **Timing (~45 min).** ~10 min the method + toolchain + data path, ~15 min the
  worked agent example end to end, ~15 min students run 2–3 scenarios, ~5 min recap
  of the symptom→layer table.

## Lab-State Delta

Module 31 (troubleshooting — demonstrate then revert, no permanent changes):

- **Worked example verified:** stopped `zabbix-agent-basic` → diagnosed via
  `docker ps -a` (Exited), `nc`/`getent` (NXDOMAIN), `zabbix_get` (`getaddrinfo()
  failed`), server log ("temporarily disabling Zabbix agent checks … interface
  unavailable"), UI availability error ("Cannot establish TCP connection … Host is
  unreachable"), and item **Test** → **started it again** and verified `agent.ping`=1,
  interface available. Lab restored.
- No objects created. Other failure modes reference earlier modules (Web M21, DB M22,
  Unsupported M30, Email M27, SNMP M20). Screenshots in
  `content/day-4/assets/module-31/`. Lab unchanged (8 hosts).
