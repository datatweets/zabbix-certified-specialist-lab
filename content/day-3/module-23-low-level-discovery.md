# Module 23: Low-Level Discovery (LLD)

## Learning Objectives

By the end of this module participants can explain **Low-Level Discovery**, read a
built-in discovery rule and its **prototypes**, write a **custom LLD rule** that
returns discovery JSON, use **LLD macros** and a **filter** to control what is
created, and let Zabbix **auto-generate items and triggers** instead of adding them
by hand.

## Topics

### Why LLD exists

In Module 11 you added each Online Shop metric **by hand** — one item per number.
That does not scale: a host has an unknown number of network interfaces,
filesystems, CPUs, or services, and they change over time. **Low-Level Discovery**
solves this: Zabbix asks the host *"what do you have?"*, gets back a list, and
**creates an item (and trigger, and graph) for each discovered thing automatically**
— then keeps that list up to date.

### The two halves: a discovery rule and its prototypes

LLD has exactly two pieces:

1. **A discovery rule** — a special item whose value is **JSON**: a list of objects,
   each describing one discovered entity with **LLD macros** (names in `{#...}`):

   ```json
   [
     {"{#IFNAME}":"eth0"},
     {"{#IFNAME}":"lo"}
   ]
   ```

2. **Prototypes** — templates for items, triggers, graphs, and even hosts, written
   **with the macros** instead of real values. For every object the rule returns,
   Zabbix substitutes the macros and creates a real entity:

   ```text
   item prototype  net.if.in[{#IFNAME}]   ->  net.if.in[eth0], net.if.in[lo]
   ```

### Built-in LLD is already running

The `zabbix-agent-basic` host is linked to **Linux by Zabbix agent** (Module 6),
which ships ready-made discovery rules — *Network interface discovery*
(`net.if.discovery`), *Block devices discovery*, *Mounted filesystem discovery*.
They have already discovered this host's interfaces and created per-interface items
like `net.if.in["eth0"]`. That is LLD working for you out of the box.

![Discovery rules on the host: three built-in plus our custom rule](assets/module-23/01-discovery-rules.png)

### A custom LLD rule for the Online Shop

Built-in rules cover the OS; for the **Online Shop's own metrics** we write a
**custom** rule. We extend the Module 11 UserParameter script with a `discovery`
mode that returns LLD JSON listing the Online Shop's metrics, each with two macros
— the API field and a human label:

```json
[
  {"{#FIELD}":"orders","{#LABEL}":"Total orders"},
  {"{#FIELD}":"queue_length","{#LABEL}":"Queue length"},
  {"{#FIELD}":"failed_payments","{#LABEL}":"Failed payments"},
  {"{#FIELD}":"response_time_ms","{#LABEL}":"API response time"}
]
```

The discovery rule's key is `app.shop[discovery]` — the **same UserParameter**
(`app.shop[*]`) that already serves the metric values, just called with a
different argument.

### LLD macros and the filter

The macros `{#FIELD}` and `{#LABEL}` come straight from the JSON. A **filter** then
decides which discovered objects are kept, by matching a macro against a regular
expression. We already monitor `orders` manually (Module 11), so we **exclude** it
— *"`{#FIELD}` does not match `^orders$`"* — and let LLD create the rest. This is
how you avoid duplicates and scope discovery to what you care about.

![The LLD filter: keep every metric except orders](assets/module-23/02-lld-filter.png)

### Automating item and trigger creation

One **item prototype** — `app.shop[{#FIELD}]`, named `Online Shop: {#LABEL}` —
becomes one real item per kept metric. One **trigger prototype** —
`nodata(/zabbix-agent-basic/app.shop[{#FIELD}],10m)=1` — becomes one real "no data"
trigger per item. You author the pattern **once**; Zabbix multiplies it.

![The item prototype with {#FIELD} and {#LABEL} macros](assets/module-23/03-item-prototype.png)

When the rule runs, the items appear with live values — `queue_length`,
`failed_payments`, `response_time_ms` — while `orders` stays the original manual
item, untouched by discovery.

![Discovered Online Shop items collecting alongside the manual orders item](assets/module-23/04-discovered-items.png)

### Lifecycle: lost resources

A discovery rule re-runs on its interval. If a discovered object **disappears**
(an interface is removed), Zabbix doesn't delete its items immediately — the rule's
**"Keep lost resources period"** marks them lost and removes them after a grace
window, so you keep history. New objects are added automatically on the next run.

## Docker-Based Demonstration

The instructor opens the host's discovery rules to show the built-in Linux LLD and
its per-interface items, then extends the Online Shop UserParameter script with a
`discovery` mode, confirms the JSON with `zabbix_get`, creates the custom discovery
rule with a filter that excludes `orders`, adds an item prototype and a trigger
prototype, runs the rule, and shows the new items and triggers appear by themselves.

## Hands-On Lab

1. **Look at built-in LLD.** On `zabbix-agent-basic`, open **Data collection →
   Hosts → Discovery rules**. Open *Network interface discovery* and its **Item
   prototypes**.
   **Expected:** prototypes like `net.if.in["{#IFNAME}"]`; in **Latest data** you
   already see real items such as `Interface eth0: Bits received` — created by LLD,
   not by hand.

2. **Add a discovery mode to the UserParameter script.** Extend
   `content/lab/agent-userparams/online_shop.sh` so `online_shop.sh discovery`
   prints the LLD JSON above, then restart the agent so the bind-mounted script
   reloads:
   ```bash
   docker restart zabbix-agent-basic
   docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k 'app.shop[discovery]'
   ```
   **Expected:** the JSON array of four `{#FIELD}`/`{#LABEL}` objects. *(Restart is
   needed because editing a single bind-mounted file replaces its inode.)*

3. **Create the custom discovery rule.** On `zabbix-agent-basic`, **Create
   discovery rule**: Name `Online Shop metric discovery`, Type **Zabbix agent**,
   Key `app.shop[discovery]`, Update interval `1m`.
   **Expected:** the rule is saved and lists under Discovery rules.

4. **Add a filter to exclude `orders`.** On the rule's **Filters** tab, add
   `{#FIELD}` **does not match** `^orders$`.
   **Expected:** the filter is saved; `orders` will be skipped (already monitored
   in Module 11).

5. **Add an item prototype.** Under the rule → **Item prototypes → Create item
   prototype**: Name `Online Shop: {#LABEL}`, Type **Zabbix agent**, Key
   `app.shop[{#FIELD}]`, *Type of information* **Numeric (unsigned)**, interval `1m`.
   **Expected:** one prototype that will expand per discovered metric.

6. **Add a trigger prototype.** Under the rule → **Trigger prototypes → Create
   trigger prototype**: Name `Online Shop: no data for {#LABEL}`, Severity
   **Average**, Expression
   `nodata(/zabbix-agent-basic/app.shop[{#FIELD}],10m)=1`.
   **Expected:** one trigger prototype.

7. **Run discovery and verify.** Click **Execute now** on the rule (or wait one
   interval), then open **Monitoring → Latest data** (filter `zabbix-agent-basic`,
   name `Online Shop`).
   **Expected:** three new items — `Online Shop: Queue length`, `Failed payments`,
   `API response time` — collecting values; `orders` remains the original manual
   item. Three matching "no data" triggers now exist under the host. You added
   **one** prototype and got **three** items and **three** triggers.

## Expected Outcome

Participants can read and write LLD: understand the rule-plus-prototype model, use
the built-in OS discovery, author a custom discovery rule fed by a UserParameter,
shape results with macros and a filter, and have Zabbix auto-create and maintain
items and triggers — the technique that makes large environments manageable.

## Instructor Notes

- **Lab vs production.** The mechanics are identical at any scale — the payoff just
  grows: one filesystem prototype covers a server with 2 mounts or 200; one SNMP
  interface prototype (Module 20) covers a 48-port switch. LLD is *the* answer to
  "we have hundreds of these."
- **Tie it back to Module 11.** Those hand-made `app.shop[...]` items are exactly
  what a prototype generates. Make the contrast explicit: manual = one at a time and
  it drifts; LLD = author once, stays current.
- **The discovery rule is just an item that returns JSON.** Debug it like any item:
  `zabbix_get` the key and read the JSON. Most "nothing was discovered" problems are
  malformed JSON or a filter that matched nothing.
- **Filters include *and* exclude.** "Matches" keeps; "does not match" drops. Anchor
  your regex (`^...$`) or it will match more than you expect. Combine conditions
  with And/Or for precise scoping.
- **Bind-mount gotcha (lab-specific).** Editing the single mounted script changes
  its inode, so the container keeps the old file until you `docker restart` it. In
  production the script lives on the host filesystem and this doesn't arise.
- **Built-in macros vary by source.** `{#IFNAME}`, `{#FSNAME}/{#FSTYPE}`,
  `{#SNMPINDEX}` for SNMP LLD — check the rule's **LLD macros** tab or the template
  to learn what a given rule exposes before writing prototypes.
- **Don't over-discover.** Every discovered object is real load. Filter out loopback
  and virtual interfaces, pseudo-filesystems, and metrics you already collect — as
  we excluded `orders`.
- **Timing (~45 min).** ~10 min concept + built-in LLD tour, ~10 min custom JSON +
  `zabbix_get`, ~15 min rule + filter + item/trigger prototypes, ~10 min execute,
  verify auto-creation, lifecycle + recap.

## Lab-State Delta

Added in Module 23 (kept — custom LLD for the Online Shop):

- **Script change:** `content/lab/agent-userparams/online_shop.sh` gained a
  `discovery` mode emitting LLD JSON (`{#FIELD}`,`{#LABEL}` for the four Online Shop
  metrics). Served by the existing `app.shop[*]` UserParameter as
  `app.shop[discovery]`. (Agent restart required to reload the bind-mounted script.)
- **Custom discovery rule on `zabbix-agent-basic` (10780):** `Online Shop metric
  discovery` (ruleid `71510`, key `app.shop[discovery]`, Zabbix agent, 1m), with a
  **filter** `{#FIELD}` does not match `^orders$`.
- **Item prototype** `Online Shop: {#LABEL}` (`71511`, key `app.shop[{#FIELD}]`) and
  **trigger prototype** `Online Shop: no data for {#LABEL}` (`33042`,
  `nodata(.../app.shop[{#FIELD}],10m)=1`).
- **Auto-created (flags=discovered):** items `app.shop[queue_length]`,
  `app.shop[failed_payments]`, `app.shop[response_time_ms]` + their three "no data"
  triggers. `app.shop[orders]` stays the manual Module 11 item (excluded by filter).
  Built-in Linux LLD (net.if/vfs) already present via the linked template.
  Screenshots in `content/day-3/assets/module-23/`.
