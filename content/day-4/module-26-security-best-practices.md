# Module 26: Security Best Practices

## Learning Objectives

By the end of this module participants can harden a Zabbix deployment: explain the
core hardening steps, use the **audit log** to track who changed what, schedule
**maintenance mode** so planned work doesn't generate false alerts, and describe
**agent allowed-server** restrictions and **PSK/certificate encryption** — plus the
Docker-specific secret-handling concerns for this lab.

## Topics

### What "securing Zabbix" actually means

Zabbix sits in a privileged position — it can reach every host you monitor and
holds credentials, topology, and alerting. Hardening it is layered:

- **Accounts:** change defaults, use named least-privilege users (Modules 2 and 25),
  never share `Admin`.
- **Accountability:** keep an **audit trail** of configuration and login activity.
- **Operations:** use **maintenance mode** so expected downtime doesn't page anyone.
- **Transport:** restrict which server may talk to each agent, and **encrypt** the
  agent↔server channel.
- **Platform:** protect the frontend, the database, backups, and — here — Docker
  secrets.

This module walks the layers that are new, building on the access control from
Module 25.

### Audit logging and event tracking

Every configuration change and login is recorded in **Reports → Audit log**: the
time, the **user**, their **IP**, the **resource** affected, the **action**
(add/update/delete/login), and a **details** diff of what changed. When a trigger
mysteriously stops firing or a host disappears, the audit log answers *who did it
and when* — essential for incident review and for any compliance regime.

![The audit log: who changed what, when — real records from this lab](assets/module-26/01-audit-log.png)

In our lab the audit log already shows the Module 25 work — the `Online Shop
Viewers` group and `shop.viewer` user being added, with full details. Audit logging
is on by default; in production you also forward these records to a SIEM and protect
them from tampering.

### Maintenance mode

When you patch a server or restart the Online Shop's web tier, its checks will fail
— and without warning Zabbix would raise problems and **page the on-call for work
you already know about**. A **maintenance period** tells Zabbix "expected downtime
here": problems for those hosts are **suppressed** (hidden unless you opt to show
them), so alerts stay meaningful.

A maintenance period has:

- **Maintenance type** — *With data collection* (keep collecting, just suppress) or
  *No data collection* (stop polling those hosts entirely during the window).
- An **active window** (`Active since`/`Active till`) and one or more **Periods**
  (one-time, daily, weekly, monthly) that define *when* it actually applies.
- The **hosts or host groups** it covers, optionally narrowed by **tags**.

![A maintenance period for the web frontend: type, window, period, host](assets/module-26/02-maintenance-config.png)

Once the server's timer applies it, the host shows an **orange wrench** in
**Monitoring → Hosts**, and its problems are suppressed for the window.

![demo-nginx marked in maintenance (the wrench icon)](assets/module-26/03-maintenance-active.png)

### Agent security: the allowed server

A Zabbix agent should answer **only** the server you trust. The agent's
**`Server`** parameter (in this lab the `ZBX_SERVER_HOST` env value, which becomes
`Server=zabbix-server`) is an allow-list of who may query it passively;
**`ServerActive`** is where it sends active checks. Anything else is refused. In
production you pin these to your server/proxy IPs and firewall port **10050** so the
agent isn't an open data source.

### Encryption and certificate management (concept)

By default the lab's agent↔server traffic is **unencrypted** — fine on an isolated
Docker network, not for production. Zabbix supports two encryption modes, configured
per host on the **Encryption** tab (and matched in the agent config):

- **PSK (pre-shared key)** — a shared identity + key on both ends. Simple, good for
  a handful of hosts.
- **Certificate (TLS)** — X.509 certificates signed by your CA. Scales to many
  hosts and integrates with PKI, at the cost of certificate management.

![The host Encryption tab: No encryption / PSK / Certificate](assets/module-26/04-encryption-tab.png)

> **TO-VERIFY / concept only:** enabling PSK or certificates requires matching TLS
> settings in each agent's config (and, for certs, a CA and signed certs). Doing it
> wrong silently drops the connection, so this lab leaves encryption **off** and
> teaches the model and where it is set. The Encryption tab and the `tls_connect`/
> `tls_accept` fields are real; only the rollout is out of scope here.

### Frontend, backups, and Docker secrets

- **Frontend security:** serve the web UI over **HTTPS**, set a session timeout, and
  restrict access — it is the front door to everything.
- **Backups:** the configuration and history live in the **database**; a real
  deployment takes regular DB dumps (and stores templates in git, as this course
  does) so it can be restored.
- **Docker secrets vs `.env`:** this lab passes passwords as **plain environment
  values** in `compose_lab.yaml` for clarity. That is a **lab shortcut** — in
  production use **Docker/Swarm secrets** or a vault so credentials aren't sitting in
  an env file or visible in `docker inspect`.

## Docker-Based Demonstration

The instructor reviews the audit log (pointing at the Module 25 changes), creates a
maintenance period for `demo-nginx` and shows the wrench icon appear, opens the host
**Encryption** tab to explain PSK vs certificate, shows the agent's allowed-server
setting, and contrasts the lab's plain `.env` values with Docker secrets.

## Hands-On Lab

1. **Confirm the basics are already hardened.** Verify the `Admin` password was
   changed from the default (Module 2) and that a least-privilege user exists
   (`shop.viewer`, Module 25).
   **Expected:** no account uses the default `Admin`/`zabbix` password; named users
   exist with scoped roles.

2. **Review the audit log.** Open **Reports → Audit log**.
   **Expected:** entries for the recent changes — the `shop.viewer` user and `Online
   Shop Viewers` group **Add** actions, with user, IP, and a details diff. Click
   **Details** on one to read the exact change.

3. **Create a maintenance period.** **Data collection → Maintenance → Create
   maintenance period**: Name `Online Shop web maintenance`, type **With data
   collection**, an active window covering now, add a **One time only** period of
   `1h`, and add host **demo-nginx**. **Add.**
   **Expected:** the period is saved and listed.

4. **See maintenance take effect.** Wait up to a minute, then open **Monitoring →
   Hosts** (filter host group `Web Services`).
   **Expected:** **demo-nginx** shows the **orange wrench** maintenance icon; any
   problems it raises during the window are **suppressed** (tick *Show suppressed
   problems* to reveal them). `demo-api` is unaffected.

5. **Inspect agent security.** Look at the agent's allowed server:
   ```bash
   docker exec zabbix-agent-basic sh -c 'printenv | grep ZBX_SERVER_HOST'
   ```
   **Expected:** `ZBX_SERVER_HOST=zabbix-server` — the agent answers only the lab
   server. In a non-container agent this is the `Server=` line in
   `zabbix_agentd.conf`.

6. **Open the Encryption tab (concept).** Edit `zabbix-agent-basic` → **Encryption**.
   **Expected:** *Connections to/from host* offer **No encryption / PSK /
   Certificate**; the lab uses **No encryption**. Note where PSK identity/key or a
   certificate would go — do **not** enable it (it would drop the agent connection
   without matching agent config).

7. **Discuss Docker secrets.** Inspect how a password reaches a container:
   ```bash
   docker inspect zabbix-db --format '{{json .Config.Env}}'
   ```
   **Expected:** the DB password is visible in plain environment values — a lab
   shortcut. Discuss replacing it with **Docker secrets** or a vault in production.

8. **Clean up.** Delete the maintenance period (so it doesn't suppress alerts in the
   next module).
   **Expected:** demo-nginx leaves maintenance (the wrench disappears).

## Expected Outcome

Participants can articulate and apply Zabbix hardening: named least-privilege
accounts, an audit trail they can read, maintenance windows that prevent false
alerts, agent allowed-server restrictions, the PSK/certificate encryption model, and
the difference between lab `.env` shortcuts and production secret management.

## Instructor Notes

- **Lab vs production — this whole module.** The lab is intentionally permissive:
  unencrypted agents, plain `.env`, HTTP frontend, single shared network. Be explicit
  that each is a teaching shortcut and state the production counterpart: TLS/PSK,
  secrets/vault, HTTPS, network segmentation, firewalled ports.
- **Audit log is your incident timeline.** Teach students to reach for it first when
  "something changed." Note that it captures **failed logins** too — a brute-force
  signal. In production, ship it to a SIEM and make it append-only.
- **Maintenance suppresses, it doesn't blind you.** *With data collection* keeps
  history flowing (so graphs have no gap) and only hides problems; *No data
  collection* stops polling. Choose deliberately. Suppressed problems are still there
  under *Show suppressed problems* — maintenance is not an excuse to ignore real
  failures that outlast the window.
- **Always set the maintenance window before the work, and remove it after.** A
  forgotten maintenance that stays active silently hides real outages — we delete
  ours in step 8 for exactly this reason.
- **Encryption is all-or-nothing per connection.** If you set the host to require PSK
  but the agent isn't configured to match, the link goes dark with no data — which is
  why we keep it concept-only here. Roll it out host-by-host with the agent config
  changed in lockstep.
- **Don't share Admin.** Every human gets a named account (Module 25); `Admin` is
  break-glass only. Combined with the audit log, named accounts make actions
  attributable.
- **Timing (~45 min).** ~10 min hardening overview + audit log, ~15 min maintenance
  mode (create, observe, clean up), ~10 min agent allowed-server + encryption concept,
  ~10 min frontend/backups/Docker secrets discussion + recap.

## Lab-State Delta

Added in Module 26 (security practices — mostly demonstration):

- **Audit log:** confirmed live (Reports → Audit log) with real records from Module
  25 (user/group/role changes). No object created — it is always-on.
- **Maintenance mode:** created `Online Shop web maintenance` (maintenanceid `1`,
  *With data collection*, host `demo-nginx`), verified `demo-nginx` entered
  maintenance (maintenance_status=1, wrench icon), then **deleted** it so it does not
  suppress alerts in Module 27. (Demonstrated then reverted.)
- **Agent security:** documented the allowed-server setting (`ZBX_SERVER_HOST=
  zabbix-server` → `Server=`); no change.
- **Encryption:** concept only — host `tls_connect`/`tls_accept` remain `1` (No
  encryption); Encryption tab shown. No change to live connections.
- Screenshots in `content/day-4/assets/module-26/`. Lab unchanged (8 hosts).
