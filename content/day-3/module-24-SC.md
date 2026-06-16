# Module 24: Practical Lab — Day 3

## Learning Objectives

By the end of this module participants can consolidate Day 3 end to end: **package**
a custom discovery rule into a **reusable, exportable template**, link it so items
and triggers are created by inheritance, **verify** SNMP and log monitoring, and add
an SNMP **availability trigger** — proving they can apply advanced templates, LLD,
SNMP, and log monitoring together.

## Topics

### What Day 3 built — and why we consolidate now

Day 3 was the day the Online Shop's monitoring grew teeth. You moved past the simple
"install an agent and watch CPU" world of Day 1 and learned the techniques that real
production monitoring leans on. Across those modules you added templates and mass
operations (Modules 17–18), so that monitoring becomes something you define once and
apply everywhere; log monitoring (Module 19), so the shop's application can tell you
in words when it is unhappy; SNMP (Module 20), so a network-like device can be
watched without an agent at all; web, performance, ODBC, and JMX checks (Modules
21–22), so you can measure response time, query a database directly, and reach inside
a Java process; and finally Low-Level Discovery (Module 23), so Zabbix finds things
to monitor on its own instead of you naming each one by hand.

Each of those was taught in isolation, one feature at a time, on its own corner of
the lab. That is the right way to *learn* a technique, but it is not how the work
actually feels on the job. A real engineer's day — and the Specialist exam — is
about making these pieces work **together** and making them **reusable**, so that the
monitoring you built for one host can be applied to the next host in seconds rather
than rebuilt from scratch.

This practical lab does exactly that. It is mostly *application*, not new theory:
you take the custom LLD you wrote in Module 23, **package it into a template** (the
Module 18 skill), link that template so a host inherits the discovery, **export** it
as YAML so it can be shared, then run **verification checkpoints** across SNMP and
log monitoring and harden the SNMP host with an availability trigger. Think of it as
the moment where the separate threads of Day 3 are braided into a single rope.

### From host configuration to a reusable template

In Module 23 the discovery rule lived **on the host** `zabbix-agent-basic`. That was
the natural place to build it the first time, because you only had one host in front
of you and you wanted to see the rule work before generalizing it. But a rule that
lives on a single host has a quiet cost: it can't be reused — every new host would
need it rebuilt by hand, click for click, with every chance for a typo to creep in.
Imagine the Online Shop growing to ten application servers; you would not want to
recreate the same discovery rule ten times.

The professional move is to put the rule, its item prototype, and its trigger
prototype into a **template**, then **link** the template. A template is a reusable
container of monitoring definitions; linking it to a host is how that host adopts
everything the template carries. The host then inherits the discovery; the items and
triggers it generates are identical, but now any host you link gets the same
monitoring for free. You define the capability once and hand it out as many times as
you like.

![The item prototype, now living in the template](assets/module-24/01-template-prototype.png)

When the template is linked, the host's discovered items show their origin — the
discovery rule's name prefixes each item — and the manual Module 11 `orders` item
sits beside them, untouched. That side-by-side is worth noticing: the inherited,
auto-discovered items and the one item you created by hand coexist cleanly, because
the discovery filter you wrote in Module 23 deliberately leaves `orders` alone.

![The host inherits the template's LLD: three discovered items plus the manual orders item](assets/module-24/02-host-inherited-items.png)

### Exporting for reuse and the exam

A template's real value is that it is *portable*. Once the capability lives in a
template rather than on a host, you can **export** it to YAML (Module 18) and that
file can be imported into any Zabbix 7.4 server, version-controlled in git alongside
your other infrastructure, or handed to a colleague who needs the same monitoring on
a different system. The exported file captures the discovery rule, its filter, and
both prototypes — the whole capability in one artifact. This is also the discipline
the certification rewards: monitoring that can be reproduced, reviewed, and shared,
not monitoring trapped inside one running server's database.

### Hardening SNMP with an availability trigger

Module 20 collected SNMP metrics but didn't alert. Collecting numbers is only half
the job; a number that nobody is watching the *absence* of is no better than no
number at all. If the `demo-snmp-device` quietly stopped answering, you would have a
flat graph and no warning. The practical adds the missing piece: a trigger that fires
when the device stops answering SNMP — `nodata()` on the SNMP item over a window — so
an unreachable network device raises a problem. `nodata()` is the availability
primitive of Zabbix: it watches whether a value arrived at all within a time window,
which is exactly the signal you want for "is this thing still reachable?"

![The SNMP unavailability trigger on demo-snmp-device](assets/module-24/03-snmp-trigger.png)

## Docker-Based Demonstration

The instructor creates the `Online Shop App by Zabbix agent` template, moves the
custom LLD into it, removes the host-level rule, links the template, and shows the
discovered items reappear by inheritance. Then they export the template to YAML, add
the SNMP availability trigger, and run the Day-3 verification checkpoints in Latest
data.

## Hands-On Lab

### Part A — Package the custom LLD into a reusable template

The work in Part A is a refactor: you are taking discovery that already works on a
host and relocating it into a template so it can be reused. The order matters —
build the template fully, then remove the host-level rule, then link — so that the
host never loses its discovery for long and its collected history stays continuous.

1. **Create the template.** **Data collection → Templates → Create template**:
   name `Online Shop App by Zabbix agent`, template group `Templates/Online Shop`.
   **Expected:** the template exists in that group.

2. **Add the discovery rule to the template.** On the template, create an LLD rule
   identical to Module 23: Name `Online Shop metric discovery`, Type **Zabbix
   agent**, Key `app.shop[discovery]`, interval `1m`, with the **filter** `{#FIELD}`
   does not match `^orders$`.
   **Expected:** the rule is saved on the template (no interface — templates have
   none).

3. **Add the prototypes.** Under the rule, add an **item prototype**
   `Online Shop: {#LABEL}` (key `app.shop[{#FIELD}]`, Numeric unsigned) and a
   **trigger prototype** `Online Shop: no data for {#LABEL}`
   (`nodata(/Online Shop App by Zabbix agent/app.shop[{#FIELD}],10m)=1`).
   **Expected:** one item prototype and one trigger prototype on the template.

4. **Remove the host-level rule and link the template.** On `zabbix-agent-basic`,
   **delete** the host-level `Online Shop metric discovery` rule (from Module 23),
   then **link** the `Online Shop App by Zabbix agent` template to the host.
   **Expected:** the host now lists both `Linux by Zabbix agent` and `Online Shop
   App by Zabbix agent` as linked templates.

5. **Verify inheritance.** Open **Data collection → Hosts → zabbix-agent-basic →
   Items**, filter key `app.shop`.
   **Expected:** the three discovered items (`queue_length`, `failed_payments`,
   `response_time_ms`) are re-created — now **via the template's** discovery rule —
   and `app.shop[orders]` remains the manual item. Values keep collecting.

6. **Export the template.** Select the template and **Export** as **YAML**.
   **Expected:** a YAML file containing the discovery rule, its filter, and both
   prototypes — a portable artifact (saved as
   `content/lab/templates/online-shop-app-by-zabbix-agent.yaml`).

### Part B — Harden SNMP monitoring

Now you give the SNMP device the alerting it has been missing. A single trigger using
`nodata()` turns a silent device into one that announces its own disappearance.

7. **Add an SNMP availability trigger.** On `demo-snmp-device`, create a trigger:
   Name `demo-snmp-device: no SNMP data (device unreachable)`, Severity **High**,
   Expression `nodata(/demo-snmp-device/snmp.sysname,5m)=1`.
   **Expected:** the trigger saves and shows **OK** while the device answers; it
   would fire if SNMP stopped responding (as it did when you broke the community in
   Module 20).

### Part C — Verify SNMP and log monitoring

The final part is a set of checkpoints. Rather than assume Day 3 still holds together
after the refactor, you confirm it: SNMP collecting, logs collecting and alerting,
and the whole Online Shop picture visible in one filtered view.

8. **Checkpoint SNMP.** **Monitoring → Latest data** for `demo-snmp-device`.
   **Expected:** `snmp.sysname`, `snmp.sysdescr`, `snmp.sysuptime`, `snmp.ifnumber`
   all collecting (Module 20).

9. **Checkpoint logs.** **Monitoring → Latest data** for `zabbix-agent-basic`, and
   **Monitoring → Problems**.
   **Expected:** the `log[...]` items are collecting and the `ERROR in Online Shop
   app log` trigger (Module 19) still raises problems as the app logs ERROR lines.

10. **See it consolidated.** In **Latest data**, filter to `zabbix-agent-basic` and
    `demo-snmp-device`, name `Online Shop`.
    **Expected:** the Online Shop's app metrics (discovered + manual) and log items
    collect together — the Day-3 picture in one view.

    ![The consolidated Online Shop app and log metrics](assets/module-24/04-consolidated.png)

## Expected Outcome

Participants have packaged the Online Shop's custom discovery into a reusable,
exported template; a host generating its app monitoring by inheritance; an SNMP
availability trigger; and verified, working SNMP and log monitoring — a complete,
portable Day-3 result they could rebuild on any Zabbix 7.4 server.
