# Module 14: Working with Zabbix Proxy

## Learning Objectives

By the end of this module participants can explain what a Zabbix **proxy** is and
when to use one, tell **active** from **passive** proxies, register the lab's
`zabbix-proxy-branch` proxy, **assign a host to it** so data is collected through
the proxy, check **proxy health**, and demonstrate what happens when a proxy goes
down and recovers.

## Topics

### What is a Zabbix proxy?

A **Zabbix proxy** is a lightweight collector that does data gathering **on behalf
of the server** for a set of hosts, then forwards the results to the server in
bulk. The proxy has its **own small database** (SQLite, MySQL, or PostgreSQL)
where it **buffers** data, so if the link to the server drops, nothing is lost —
the proxy stores values and ships them when the connection returns. Our lab runs
`zabbix-proxy-branch` (a **SQLite** proxy).

### Why use a proxy? (use cases)

A proxy is the answer whenever the server should not — or cannot — poll hosts
directly:

- **Branch / remote office** — one proxy per site collects locally and sends a
  single, compressed stream to HQ instead of the server reaching across the WAN to
  every host.
- **DMZ / firewall** — hosts behind a firewall are polled by a proxy inside the
  DMZ; only the proxy→server connection crosses the boundary (one hole, not many).
- **Scale** — proxies offload collection and preprocessing from the server, so one
  server can monitor far more hosts.
- **Unstable links** — the proxy's buffer rides out network outages without data
  loss.

In our storyline, `zabbix-proxy-branch` is the **branch office** collector: it
monitors the Online Shop's web frontend (`demo-nginx`) locally and forwards to the
central server.

### Active vs passive proxy

The difference is **who initiates the connection** (like agents in Module 7):

| | **Active** proxy | **Passive** proxy |
|---|---|---|
| Connection | proxy → server (10051) | server → proxy (10051) |
| Good for | proxy behind NAT/firewall (outbound only) | server reaches into a controlled network |
| Config | server just needs the proxy's **name** | server needs the proxy's **address** |

`zabbix-proxy-branch` runs in **active** mode (it connects out to the server), set
via `ZBX_PROXYMODE=0` in `compose_lab.yaml`.

### Proxy health and queue

The server tracks each proxy under **Administration → Proxies**: its **mode**,
**state** (Online/Offline), **version**, **last seen** age, **item count**, and
**required VPS**. A proxy that is Offline or whose "last seen" keeps growing is not
forwarding data. Each proxy also has its **own queue** (the buffered values waiting
to be sent); a growing proxy queue means the proxy cannot keep up or the link to
the server is down. Proxy tuning is the same idea as server tuning (Module 13):
enough pollers and `DataSenderFrequency` for the load.

## Docker-Based Demonstration

`zabbix-proxy-branch` is already running and *connecting* to the server, but until
it is **registered** the server rejects it (`proxy "zabbix-proxy-branch" not
found`). The instructor registers it, assigns `demo-nginx` to it, shows the
`demo-nginx` data arriving **through the proxy** in Latest data, then
`docker stop zabbix-proxy-branch` to show the proxy going **Offline** and the data
stalling — and `docker start` to show recovery (and the buffered data catching up).

## Hands-On Lab

1. **Confirm the proxy is running.**
   ```bash
   docker compose -f compose_lab.yaml ps zabbix-proxy-branch
   docker logs zabbix-proxy-branch --tail 3
   ```
   **Expected:** the container is `Up`; the log shows it trying to reach the server
   (and, until registered, the server logs `proxy "zabbix-proxy-branch" not found`).

2. **Register the proxy.** Go to **Administration → Proxies → Create proxy**:
   - **Proxy name:** `zabbix-proxy-branch` (must match the proxy's `ZBX_HOSTNAME`)
   - **Proxy mode:** **Active**

   **Add.**
   **Expected:** within ~1 minute the proxy appears with **State: Online**, a
   version, and a recent "last seen".

   ![Registering the active proxy](assets/module-14/02-proxy-config.png)

3. **Check proxy health.** Look at **Administration → Proxies**.
   **Expected:** `zabbix-proxy-branch` — **Active**, **Online**, version 7.4.11,
   "Last seen" a few seconds, item/host counts.

   ![The proxy is Online and healthy](assets/module-14/01-proxies-list.png)

4. **Assign a host to the proxy.** Create a host `demo-nginx` (groups *Web
   Services* + *Docker Lab*, **no interface**). Set **Monitored by → Proxy →
   `zabbix-proxy-branch`**. Add an **HTTP agent** item, e.g.
   `Nginx: active connections` → URL `http://demo-nginx/stub_status`, with a
   regular-expression preprocessing step `Active connections: ([0-9]+)` → `\1`.
   Save.
   **Expected:** the host is now collected by the proxy, not the server.

   ![demo-nginx is Monitored by the proxy](assets/module-14/03-host-monitored-by-proxy.png)

5. **Verify data comes through the proxy.** Go to **Monitoring → Latest data**,
   filter to `demo-nginx`.
   **Expected:** the item values appear — the **proxy** did the HTTP request to
   `demo-nginx` and forwarded the result to the server. Same data, collected one
   hop away.

   ![demo-nginx data collected via the proxy](assets/module-14/04-latest-via-proxy.png)

6. **Stop the proxy and observe.**
   ```bash
   docker stop zabbix-proxy-branch
   ```
   **Expected:** within a minute or two **Administration → Proxies** shows the
   proxy **Offline** with a growing "Last seen", and `demo-nginx`'s Latest data
   stops updating — the proxy is no longer forwarding.

   ![The proxy goes Offline; its data stalls](assets/module-14/05-proxy-down.png)

7. **Restart and confirm recovery.**
   ```bash
   docker start zabbix-proxy-branch
   ```
   **Expected:** the proxy returns to **Online**, and `demo-nginx` data resumes —
   including any values the proxy **buffered** in its SQLite database while it was
   cut off (no gap from a brief outage).

## Expected Outcome

Participants can explain proxy architecture and use cases, distinguish active and
passive proxies, register a proxy, move a host's collection onto a proxy, verify
data flows through it, read proxy health, and demonstrate the proxy's
buffer-and-forward behaviour across an outage.

## Instructor Notes

- **Lab vs production.** Our proxy and its "branch" host run on one Docker network;
  in production the proxy sits at the remote site/DMZ and the **only** connection
  to HQ is proxy↔server on 10051 — which is exactly why proxies simplify
  firewalls. SQLite suits a small proxy; busy proxies use MySQL/PostgreSQL.
- **The name must match.** Active-proxy registration hinges on the proxy's
  `Hostname` (here `ZBX_HOSTNAME=zabbix-proxy-branch`) equalling the **Proxy name**
  in Zabbix — the same gotcha as active agents (Module 7). Show the "proxy not
  found" log so students recognise it.
- **Why move a host to a proxy at all.** Emphasise the data path changes
  (server→host becomes proxy→host→…→server) but the *configuration* is identical —
  you just pick "Monitored by: Proxy". Great for "lift a whole site behind one
  collector".
- **Buffering is the headline feature.** The proxy's local DB means a flaky WAN
  does not lose data. Demo the short outage in step 6–7 and point out there is no
  gap after recovery.
- **Agent allow-lists still apply.** We monitored `demo-nginx` with **HTTP agent**
  checks (agentless) so the proxy could collect immediately. If you move an
  *agent* host to a proxy, the agent's `Server=` allow-list must include the
  **proxy's** address, or it will refuse the proxy's polls (Module 7).
- **Timing (~45 min).** ~12 min what/why + active vs passive, ~10 min register +
  health, ~12 min assign host + verify data, ~8 min stop/recover + buffering, ~3
  min recap.

## Lab-State Delta

Added in Module 14 (kept — the proxy is now part of the architecture):

- **Proxy registered:** `zabbix-proxy-branch` (proxyid `1`) — **Active** mode,
  SQLite, Online.
- **Host:** `demo-nginx` (hostid `10785`) — groups *Web Services* + *Docker Lab*,
  **no interface**, **Monitored by proxy** `zabbix-proxy-branch`. HTTP agent items:
  `Nginx: active connections` (itemid `71083`, regex-extracted from
  `/stub_status`) and `Nginx: home page (HTTP 200 check)` (itemid `71084`).
- **Verified lifecycle:** data flows server-less (via proxy); stopping the proxy
  turned it **Offline** (last seen grew to 1m 38s) and stalled `demo-nginx`;
  restarting recovered it (lastclock advanced). Proxy left **running**.
  Screenshots in `content/day-2/assets/module-14/`.
