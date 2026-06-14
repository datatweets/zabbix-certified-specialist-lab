# Module 5: Configuring Basic Data Collection

## Learning Objectives

By the end of this module participants can create a monitored host in Zabbix,
give it a Zabbix agent interface (and explain when to use DNS vs IP), organise it
with host groups, link a template to collect dozens of metrics instantly, read
the resulting data in Latest data, and create, tag, and test their own manual
item. This is the first module where you add real, reachable monitoring to the
Online Shop lab.

## Topics

### From concepts to configuration

In Module 4 you traced how data flows; now you build the first piece of it. We
turn the running `zabbix-agent-basic` container into a proper **monitored host**
so Zabbix collects its CPU, memory, disk, filesystem, and network metrics — and
then we add one custom item that checks the Online Shop web frontend. Everything
here is done in **Data collection → Hosts**.

### Creating a host

A **host** is the unit you monitor. Creating one requires, at minimum, a **host
name**, at least one **host group**, and usually an **interface** for Zabbix to
reach it. The host name is significant: for agent **active checks** it must match
the agent's configured `Hostname`, and it is how the host is referenced in
trigger expressions later (e.g. `/zabbix-agent-basic/agent.ping`). We name our
host exactly after the container: **`zabbix-agent-basic`**.

### Host interfaces and the agent interface

An **interface** tells Zabbix *how to reach* a host. A host can have several
interface types — **Agent**, **SNMP**, **JMX**, and **IPMI** — and we add the one
matching how we collect. For a Zabbix agent we add an **Agent interface** with a
port (default **10050**, the agent's passive-check port).

### DNS vs IP — and why DNS wins in Docker

Each interface can connect by **IP address** or **DNS name** (the "Connect to"
toggle). In Docker, container IP addresses are assigned dynamically and can change
when the stack restarts, but the **container name is a stable DNS name** on the
`zabbix-lab` network. So we set **Connect to: DNS** and **DNS name:
`zabbix-agent-basic`**. The server resolves that name to whatever IP the container
currently has — robust across restarts. (In production you would typically use a
stable IP or a real DNS record; the principle "prefer the stable address" is the
same.)

### Host groups

A **host group** is a label that collects related hosts. Groups drive
**permissions** (Module 25) and make **filtering** and **dashboards** scopeable.
A host must belong to at least one group and may belong to several. We put our
host in two course groups: **Docker Lab** (everything in the lab) and **Linux
Servers** (all Linux hosts). *(Zabbix also ships a stock group named "Linux
servers" — note the lowercase "s"; we use our own course groups from the canonical
naming so the Online-Shop hosts are grouped intentionally.)*

### Items and item keys

An **item** is one thing you measure; its **item key** specifies exactly what to
collect. Keys can take parameters in square brackets, e.g.
`vm.memory.size[available]`, `net.if.in[eth0]`, `vfs.fs.size[/,pused]`. Rather than
hand-creating dozens of items, we **link a template** that brings a curated set
all at once — but you can always add your own.

### Templates (a first taste)

A **template** is a reusable bundle of items, triggers, and graphs. Linking
**Linux by Zabbix agent** to our host instantly gives it ~150 items (CPU, memory,
filesystems, network interfaces, and more) with sensible intervals — no manual
work. Templates are covered in depth in Module 18; here we simply consume one.

### Update intervals, history, and trends

Every item has three time settings you will set constantly:

- **Update interval** — how often the value is collected (e.g. `1m`). Shorter =
  more resolution and more load.
- **History** — how long *raw* values are kept (lab default **31d**). History
  powers detailed, recent graphs.
- **Trends** — how long hourly **min/avg/max** roll-ups are kept (lab default
  **365d**). Trends power long-term graphs cheaply after history expires.

Choosing these well is the core of capacity and performance planning (Module 30).

### Item tags and timeouts

- **Item tags** are `name: value` labels on an item (e.g. `component: web`).
  Tags are how 7.x filters Latest data, groups problems, and routes alerts —
  they replace the old "applications" concept. You will tag deliberately.
- **Timeout** is how long Zabbix waits for the item's value before giving up. In
  7.4 it defaults to the **Global** timeout (3s) but can be **Override**-n per
  item for slow checks.

### Testing item values

Before trusting an item, **test** it. The item form's **Test** button asks the
server (or a proxy) to fetch the value *right now* and shows you the raw and
processed result — invaluable for catching a wrong key or an unreachable host
before you build triggers on top of it.

## Docker-Based Demonstration

The instructor turns the `zabbix-agent-basic` container into a monitored host and
shows data arriving. The container is already running and already trusts the
server (its config sets `Server=zabbix-server`), so a quick protocol-level check
proves the agent answers before we touch the UI:

```bash
# The server can already reach the agent (passive check, port 10050):
docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k agent.ping
# -> 1
```

Then, in the frontend, the instructor creates the host, links the template, and
opens **Monitoring → Latest data** to watch ~150 metrics begin to populate within
a minute.

## Hands-On Lab

> If you are doing this on your own clone, the host does not exist yet — you
> create it here. (In a shared classroom lab it may already exist; your
> instructor will tell you whether to create a new one, e.g. `zabbix-agent-basic-2`.)

1. **Start creating the host.** Go to **Data collection → Hosts** and click
   **Create host** (top-right).
   **Expected:** the **Host** configuration dialog opens on the **Host** tab.

2. **Name the host.** In **Host name**, enter `zabbix-agent-basic`.
   **Expected:** the name is accepted; the Visible name auto-fills to match.

3. **Add host groups.** In **Host groups**, type `Docker Lab` and select it (or
   create it by typing the name and choosing "(new)"), then add `Linux Servers`
   the same way.
   **Expected:** two group chips appear: *Docker Lab* and *Linux Servers*.

4. **Add the agent interface.** Next to **Interfaces**, click **Add → Agent**.
   - Leave **IP address** as `127.0.0.1` (a value is required even when using
     DNS).
   - Set **DNS name** to `zabbix-agent-basic`.
   - Set **Connect to** to **DNS**.
   - Leave **Port** as `10050`.

   **Expected:** an Agent interface row shows DNS `zabbix-agent-basic`, Connect to
   **DNS**, port 10050.

   ![The configured host: agent interface (DNS), groups, and linked template](assets/module-05/02-host-form.png)
   *Connect to is set to DNS so the server resolves the container name instead of
   pinning a volatile IP.*

5. **Link the Linux template.** In **Templates**, type `Linux by Zabbix agent`
   and select it.
   **Expected:** *Linux by Zabbix agent* appears in the Templates list.

6. **Save the host.** Click **Add**.
   **Expected:** the host appears in the **Hosts** list. Within a minute its
   **Availability** column shows a green **ZBX** (the server reached the agent).

   ![The new host in the Hosts list](assets/module-05/01-hosts-list.png)

7. **Check Latest data.** Go to **Monitoring → Latest data**, set the **Hosts**
   filter to `zabbix-agent-basic`, and click **Apply**.
   **Expected:** ~150 items populate (e.g. *Available memory* ≈ several GB, CPU
   utilization, filesystem usage), each with a **Last check** time and **Last
   value**. The data is real and updates on each item's interval.

   ![Latest data flowing for the new host](assets/module-05/03-latest-data.png)

8. **Create a manual item** that checks the Online Shop web frontend. In **Data
   collection → Hosts**, click **Items** on the `zabbix-agent-basic` row, then
   **Create item**, and set:
   - **Name:** `Online Shop web port reachable`
   - **Type:** `Zabbix agent`
   - **Key:** `net.tcp.service[http,demo-nginx,80]`
   - **Type of information:** `Numeric (unsigned)`
   - **Update interval:** `1m`
   - Leave **History** (`31d`) and **Trends** (`365d`) at their defaults.

   **Expected:** the form accepts the key; History shows `31d`, Trends `365d`, and
   Timeout shows **Global**.

   ![The manual item form (key, interval, history, trends, timeout)](assets/module-05/04-item-form.png)
   *Note the History (31d), Trends (365d), and Timeout (Global) fields — the time
   settings every item has — and the Tags and Preprocessing tabs at the top.*

9. **Tag the item.** Switch to the item's **Tags** tab and add two tags:
   - `component` = `web`
   - `target` = `demo-nginx`

   **Expected:** two tag rows appear.

   ![Item tags](assets/module-05/05-item-tags.png)

10. **Test the item before saving.** Click **Test → Get value and test**.
    **Expected:** the **Value** field shows **`1`** (the demo-nginx HTTP port is
    answering; `0` would mean down). This confirms the key and host are correct.

    ![Test item — live value 1 returned from the agent](assets/module-05/06-item-test.png)

11. **Save the item** (click **Add**). After up to a minute, find it in **Latest
    data** for the host.
    **Expected:** *Online Shop web port reachable* shows **Last value 1** with the
    tags `component: web` and `target: demo-nginx`.

## Expected Outcome

Participants have added `zabbix-agent-basic` as a fully monitored host — in the
*Docker Lab* and *Linux Servers* groups, reached over its agent interface by DNS,
linked to *Linux by Zabbix agent* and collecting ~150 metrics — and have created,
tagged, and tested a custom item that confirms the Online Shop web frontend is
reachable. The Online Shop now has its first real monitoring.

## Instructor Notes

- **Lab vs production.** We connect by **DNS = container name** because Docker IPs
  are dynamic. In production you would use a host's real IP or DNS record; the
  lesson — *target a stable address* — transfers directly. Port 10050 and the
  agent's `Server=` allow-list are identical in production.
- **Why a value is still required in the IP field.** Zabbix keeps both IP and DNS
  on an interface and uses whichever **Connect to** selects. Leaving the IP at
  `127.0.0.1` while connecting by DNS is fine and intentional.
- **Choosing the manual key.** All the obvious simple keys (`system.uptime`,
  `agent.ping`, `system.users.num`) are *already provided by the template*, and a
  host cannot have two items with the same key. We deliberately chose
  `net.tcp.service[http,demo-nginx,80]` — unique, and it teaches that an agent can
  check *other* hosts (here, the web frontend), foreshadowing real service checks.
- **Test before you trust.** Encourage students to always use **Test** on a new
  item. It isolates "is the key/host right?" from "is my trigger right?", saving
  enormous time later (Module 31).
- **Tags, not applications.** Students from older Zabbix will look for
  "Applications." In 7.x that concept is gone — **tags** do the grouping/filtering.
- **The green ZBX may take a minute.** Availability flips to green only after the
  server's next config sync and a successful poll. If it is grey, wait or check
  the agent container is up.
- **Timing (~45 min).** ~10 min concepts (host/interface/DNS/groups), ~15 min
  create host + template + Latest data, ~15 min manual item + tags + test, ~5 min
  recap and Q&A.

## Lab-State Delta

Added in Module 5 (created via the API for verification; identical to the UI
steps above):

- **Host groups:** `Linux Servers` (groupid 22), `Docker Lab` (groupid 23).
- **Host:** `zabbix-agent-basic` (hostid 10780) — groups *Linux Servers* +
  *Docker Lab*; **Agent interface** DNS `zabbix-agent-basic:10050`, Connect to
  **DNS** (`useip=0`), availability **green**; linked template **Linux by Zabbix
  agent** (templateid 10001) → ~150 items collecting (152 supported).
- **Manual item:** `Online Shop web port reachable` (itemid 69696), key
  `net.tcp.service[http,demo-nginx,80]`, type Zabbix agent, unsigned, interval
  `1m`, history `31d`, trends `365d`, tags `component:web` + `target:demo-nginx`,
  current value **1**.
