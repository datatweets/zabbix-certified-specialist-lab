# Module 11: Custom Data Collection

## Learning Objectives

By the end of this module participants can extend Zabbix beyond built-in
templates: collect a custom metric with an agent **UserParameter** (a script you
write), **push** a metric into Zabbix with **zabbix_sender** and a **trapper**
item, recognise when to use HTTP agent items instead, parameterise checks with
**user macros**, and choose the right collection method for a given metric.

## Topics

### Why custom collection — the Online Shop's own numbers

Templates monitor CPU, memory, and disk — but they know nothing about *your*
business. How many **orders**? What is today's **revenue**? Those numbers come
from your application, and you teach Zabbix to collect them. This module adds the
Online Shop's own KPIs to the lab.

### Four ways to collect a custom metric

| Method | Direction | Best for |
|---|---|---|
| **UserParameter** (agent runs a script) | agent → server | metrics a script on the host can produce |
| **Zabbix sender → trapper item** | external → server (push) | values produced elsewhere (cron jobs, CI, batch) |
| **HTTP agent item** | server → endpoint (pull) | JSON/Prometheus APIs (Module 9) |
| **Custom Zabbix agent 2 plugin** | agent → server | reusable Go plugins (advanced) |

### UserParameters and custom scripts

A **UserParameter** maps a new **item key** to a shell command the agent runs.
A **flexible** UserParameter uses `[*]` to accept arguments. Ours runs a small
script that returns one field of the Online Shop API:

```ini
# /etc/zabbix/zabbix_agentd.d/online_shop.conf
UserParameter=app.shop[*],/usr/local/bin/online_shop.sh $1
```

```sh
# /usr/local/bin/online_shop.sh  (returns one numeric field)
field="$1"
wget -qO- http://demo-api:5000/metrics | grep -oE "\"${field}\":[0-9]+" | grep -oE '[0-9]+'
```

So `app.shop[orders]` runs the script with `orders`, and the agent returns the
number. The agent must **reload** the configuration to pick up a new
UserParameter. In our Docker lab the script and `.conf` are mounted into the
agent and you **recreate the container**; on a traditional host you would drop the
files in place and restart the agent service — the same idea.

### Zabbix sender and trapper items (the push model)

Sometimes the value is produced *somewhere else* — a nightly job, a CI pipeline, a
payment processor. A **trapper** item (type *Zabbix trapper*) does not poll; it
**waits** to be *sent* a value with **`zabbix_sender`**:

```bash
zabbix_sender -z zabbix-server -s demo-api -k app.revenue.daily -o 14820
```

This is the most flexible method: anything that can run one command can feed
Zabbix. The trapper item's **Allowed hosts** field restricts who may send.

### Active vs passive, applied to custom checks

A UserParameter can be polled **passively** (server asks, as we do here) or run as
an **active** check (agent pushes on a schedule) — the same active/passive choice
from Module 7. Trapper items are inherently push; HTTP agent items are pull. Match
the direction to where the data lives and how your network is shaped.

### Macros in custom checks

**User macros** (`{$NAME}`) are named, reusable values. They keep checks and
triggers generic: define a threshold once on the host (or template) and reference
it everywhere. We add `{$REVENUE.MIN}` on `demo-api` and use it in a trigger so
the target revenue is configurable per host without editing the expression.

## Docker-Based Demonstration

The instructor shows all three live paths for the Online Shop's KPIs: a
**UserParameter** (`app.shop[orders]`) returning the order count from a script on
the agent, a **trapper** item (`app.revenue.daily`) fed a value with
`zabbix_sender`, and a reminder that the Module 9 **HTTP agent** items are a third
custom method. All three land in **Latest data** and on a dashboard, tagged by
their `source`.

## Hands-On Lab

1. **Review the custom script and UserParameter.** In the repo, open
   `content/lab/agent-userparams/online_shop.sh` and `online_shop.conf`. The
   `compose_lab.yaml` file mounts them into `zabbix-agent-basic` at
   `/usr/local/bin/online_shop.sh` and `/etc/zabbix/zabbix_agentd.d/online_shop.conf`.
   **Expected:** you understand that the agent will run `online_shop.sh <field>`
   for the key `app.shop[<field>]`.

2. **Load the UserParameter (recreate the agent).**
   ```bash
   docker compose -f compose_lab.yaml up -d zabbix-agent-basic
   ```
   **Expected:** the agent restarts with the new configuration. *(On a real host
   you would instead copy the files and run `zabbix_agentd -R userparameter_reload`
   or restart the service.)*

3. **Test the UserParameter directly** — before involving Zabbix at all:
   ```bash
   docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k 'app.shop[orders]'
   ```
   **Expected:** a number (the current order count). If this works, the agent side
   is correct and any remaining problem is in Zabbix configuration.

4. **Create the matching item.** On host `zabbix-agent-basic`, create an item:
   - **Name:** `Online Shop: orders (UserParameter)`
   - **Type:** `Zabbix agent`
   - **Key:** `app.shop[orders]`
   - **Type of information:** `Numeric (unsigned)`
   - **Tags:** `component=business`, `source=userparameter`

   **Expected:** within ~1 minute the item shows the order count in Latest data.

   ![A UserParameter item is a normal Zabbix agent item with your custom key](assets/module-11/01-userparameter-item.png)

5. **Push a metric with zabbix_sender (trapper item).** On host `demo-api`, create
   a **Zabbix trapper** item:
   - **Name:** `Online Shop: daily revenue (trapper)`
   - **Key:** `app.revenue.daily`
   - **Type of information:** `Numeric (unsigned)`, **Units** `$`

   Then push a value:
   ```bash
   docker exec zabbix-server zabbix_sender -z zabbix-server -s demo-api -k app.revenue.daily -o 14820
   ```
   **Expected:** `zabbix_sender` reports `processed: 1; failed: 0`, and the value
   appears in Latest data. A trapper item has no interval and **Test/Execute now
   are disabled** — it only receives.

   ![A trapper item waits to be sent values; note the Allowed hosts field](assets/module-11/03-trapper-item.png)

6. **See both custom metrics in Latest data.** Go to **Monitoring → Latest data**
   and filter **Name** to `Online Shop:`.
   **Expected:** the UserParameter `orders` (on `zabbix-agent-basic`) and the
   trapper `daily revenue` (on `demo-api`), each tagged with its `source`.

   ![Both custom metrics, tagged by collection source](assets/module-11/02-latest-custom.png)

7. **Add a macro and a trigger on a custom metric.** On host `demo-api`, open the
   **Macros** tab and add `{$REVENUE.MIN}` = `10000`. Then create a trigger:
   - **Name:** `Online Shop: daily revenue below target ({$REVENUE.MIN})`
   - **Severity:** **Warning**
   - **Expression:** `last(/demo-api/app.revenue.daily)<{$REVENUE.MIN}`

   **Expected:** the trigger uses the macro for its threshold, so the target is
   configurable per host without touching the expression. (At `14820 > 10000` it
   stays OK; send a smaller value to see it fire.)

   ![A user macro keeps the threshold configurable](assets/module-11/04-macro.png)

8. **Show the metrics on a dashboard.** Create a dashboard
   `Online Shop — Custom Metrics` with two **Item value** widgets — one for the
   `orders` UserParameter item, one for the `daily revenue` trapper item.
   **Expected:** a dashboard displaying your business KPIs alongside everything
   else Zabbix collects.

   ![The Online Shop's own KPIs on a dashboard](assets/module-11/05-dashboard.png)

## Expected Outcome

Participants can extend Zabbix with their own metrics three ways — a UserParameter
script run by the agent, values pushed with `zabbix_sender` into a trapper item,
and HTTP agent items (Module 9) — parameterise checks and triggers with user
macros, and decide which method fits a given source.

## Instructor Notes

- **Lab vs production.** In our Docker lab the UserParameter script and config are
  **mounted** and you recreate the container; on a VM/bare-metal host you place the
  files and reload/restart the agent. The UserParameter mechanism is identical —
  only the delivery differs. `zabbix_sender` runs anywhere with network access to
  the server's port 10051.
- **Test the agent side first.** `zabbix_get -k 'app.shop[orders]'` proves the
  script and UserParameter work *before* you create the Zabbix item — the same
  isolation habit from Module 6. If `zabbix_get` returns the value but the item is
  unsupported, the problem is the item config, not the script.
- **Security of UserParameters.** A UserParameter runs arbitrary commands as the
  agent user — review scripts carefully, avoid passing unsanitised arguments
  (`UnsafeUserParameters` is off by default), and never enable `system.run`
  blindly. This is why production agents restrict keys (Module 7's
  `AllowKey`/`DenyKey`).
- **When to use which.** Script on the host → UserParameter. Value generated
  elsewhere (cron, CI, batch) → `zabbix_sender` + trapper. A JSON/Prometheus
  endpoint → HTTP agent (Module 9). Make students justify a choice for a given
  metric.
- **Macros scale.** Putting `{$REVENUE.MIN}` on the host (or a template) lets the
  same trigger serve hundreds of hosts with different thresholds — the foundation
  of good template design (Module 18).
- **Timing (~45 min).** ~12 min methods overview + UserParameters, ~13 min build +
  test UserParameter + item, ~10 min sender/trapper, ~7 min macro + trigger +
  dashboard, ~3 min when-to-use recap.

## Lab-State Delta

Added in Module 11 (all kept):

- **Lab infra:** `compose_lab.yaml` now mounts a UserParameter script + config into
  `zabbix-agent-basic` (`content/lab/agent-userparams/online_shop.sh`,
  `online_shop.conf`) — key `app.shop[*]` (flexible).
- **Item (UserParameter):** `Online Shop: orders (UserParameter)` (itemid `70989`)
  on `zabbix-agent-basic` (10780) — Zabbix agent, key `app.shop[orders]`, unsigned,
  tags `component:business`, `source:userparameter`.
- **Item (trapper):** `Online Shop: daily revenue (trapper)` (itemid `70990`) on
  `demo-api` (10783) — Zabbix trapper, key `app.revenue.daily`, unsigned, `$`,
  tags `component:business`, `source:trapper`; value `14820` pushed via
  `zabbix_sender`.
- **User macro:** `{$REVENUE.MIN}` = `10000` on `demo-api`.
- **Trigger:** `Online Shop: daily revenue below target ({$REVENUE.MIN})`
  (triggerid `32836`) — `last(/demo-api/app.revenue.daily)<{$REVENUE.MIN}`,
  **Warning**.
- **Dashboard:** `Online Shop — Custom Metrics` (dashboardid `409`) — Item value
  widgets for the orders and revenue items. Screenshots in
  `content/day-2/assets/module-11/`.
