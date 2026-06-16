# Module 28: Inventory and Business Monitoring

## Learning Objectives

By the end of this module participants can connect technical monitoring to business
impact: populate **host inventory** (manual and automatic), build a **business
service tree** for the Online Shop, map services to problems with **tags**, watch a
failure roll up to **service status** and surface a **root cause**, and define an
**SLA** with a target and read its **SLA report**.

## Topics

### Two questions this module answers

Everything you have built so far has been aimed at a single question, asked over and
over for each host and each metric: *"is this host or item healthy?"* That is the
right question for an engineer staring at a console, but it is not the question your
manager, your customer, or the person who signed the uptime contract is asking. They
care about the Online Shop as a whole, not about whether `eth0` on `demo-postgres`
dropped a packet. Business monitoring is the layer that translates between those two
worlds, and it answers two higher-level questions that the rest of the course has not
yet touched:

- **"What do we have?"** — **host inventory**: an asset register inside Zabbix.
- **"Is the *business service* healthy, and are we meeting our promises?"** —
  **business service monitoring** and **SLA**.

Together these turn a wall of green and red triggers — informative to you, baffling to
everyone else — into something a manager can read at a glance: *is the Online Shop up,
and what is our uptime against the SLA we promised?* That single sentence is the
payoff of the entire module, and everything below is the machinery that produces it.

### Host inventory

Before you can talk about the *health* of an asset, it helps to have a record that the
asset exists at all, along with who owns it, where it lives, and what it is. Zabbix
gives every host an **inventory** record for exactly this purpose: a structured form
with fields for type, name, location, contact, serial number, OS, and dozens more
besides. Think of it as a lightweight CMDB (configuration management database) that
lives right next to the monitoring data, so the question "what is this thing, and who
do I call when it breaks?" has an answer in the same tool that just told you it broke.

Inventory operates in one of three **modes**, and the choice is per host:

- **Disabled** — no inventory.
- **Manual** — you fill the fields in (what we do for the Online Shop hosts).
- **Automatic** — a field is **populated from an item**: e.g. map the *system
  information* item to the OS field, and it updates itself.

The manual mode is the natural starting point because you are typing in facts a human
already knows — that `demo-nginx` is the web server contacted at `ops@online-shop.lab`.
Automatic mode is where inventory stops being paperwork and starts maintaining itself:
you point a field at an item, and from then on the field tracks whatever that item
reports. Once the records exist, **Inventory → Overview** and **Inventory → Hosts**
give you a searchable asset list — you can ask "show every Database host" or "who is
the contact for demo-postgres?" and get an answer without leaving Zabbix.

![Host inventory: type, name, and contact populated for the Online Shop hosts](assets/module-28/01-inventory.png)

### Business service monitoring

Inventory answers "what do we have?". The harder and more valuable question is whether
the *thing the business sells* is working — and that thing rarely maps to one host. The
Online Shop is "up" only when the website, the API, and the database are all doing
their jobs together; no single host represents it. Zabbix models this with a
**service**, an abstraction that represents something the business cares about —
*"the Online Shop"* — independent of how many hosts happen to implement it.

Services are organized into a **tree**, and the tree shape mirrors how you would
explain the system to a colleague: the root is the whole shop, and its children are the
parts that make it work. For this course the tree looks like this:

```text
Online Shop
├── Web Frontend        (demo-nginx)
├── API Service         (demo-api)
├── Database            (demo-postgres)
└── Notification Service
```

The reason a tree is the right structure, rather than a flat list, is that a parent's
health depends on its children, and Zabbix computes that dependency for you. Each
parent's **status** is calculated from its children by an **algorithm** — and for the
Online Shop we choose *most critical of child services*, which means the shop is
considered as unhealthy as its single worst part. If the Database is on fire, the
Online Shop is on fire, because a shop that cannot reach its database is not selling
anything. That is precisely the behavior a manager expects, and it is why this
algorithm is the default choice for "is the whole thing up?".

### Mapping services to problems with tags

A service tree is just a picture until something connects each leaf to the real
problems firing underneath it. In Zabbix 7.x that connection is made by **tags**, not
by pointing a service at a specific trigger. This is a deliberate design choice worth
understanding: tagging is loose coupling. The service does not need to know which
trigger exists today or which one you add tomorrow; it simply declares *the kinds of
problems I care about* as **problem tags**, and any problem event carrying a matching
tag counts against it.

To make every problem on a host automatically carry the right tag, we attach a **host
tag** to each host. A host tag propagates to all problems generated on that host, so we
never have to tag triggers one by one:

- `demo-nginx` → `service=web` → **Web Frontend** service
- `demo-api` → `service=api` → **API Service**
- `demo-postgres` → `service=db` → **Database**

The result is that when any trigger on `demo-nginx` fires, the resulting problem is
born with `service=web` already attached, the **Web Frontend** service sees a matching
tag, and it turns red — with no per-trigger wiring on your part. Add a new trigger to
`demo-nginx` next month and it joins the service automatically.

### Service status, impact, and root cause

Now watch the whole machine move. Stop the web frontend and follow the chain link by
link: the *frontend is unavailable* trigger fires → the problem carries the tag
`service=web` → the **Web Frontend** service finds its matching problem tag and turns
**High** → and because the **Online Shop** root uses *most critical of children*, it
turns **High** too. Crucially, the Services view does not just color the root red; it
shows the **root cause** — the exact problem dragging the service down — so you go from
"the shop is unhealthy" to "because the frontend is unavailable" in one glance.

![The Online Shop service is High; the root cause is named](assets/module-28/02-service-tree.png)

Drill in and the value compounds. Every child shows its own status and its own root
cause — *Web Frontend: High (frontend unavailable)*, *API Service: Average (queue
backing up)* — while Database and Notification stay OK, telling you at a glance which
parts are fine and which are not. This is what is meant by **service impact**: one
screen that translates a pile of technical problems into business effect, readable by
someone who has never written a trigger expression in their life.

![The service tree: each child's status and root cause](assets/module-28/04-service-children.png)

### SLA and SLA reports

Service status tells you the state *right now*; an SLA tells you whether you have kept
your *promise over time*. An **SLA** (service-level agreement) turns a vague commitment
like "the shop should basically always be up" into something measurable: an **SLO**
(service-level objective) target — the number you promise, e.g. **99.5%** — a
**reporting period** over which it is judged (daily, weekly, or monthly), a schedule
that says when it counts (here, 24×7), and the **services** it covers, matched by
service tags. With those defined, Zabbix continuously computes the **SLI**
(service-level indicator) — the availability you actually achieved — from the recorded
service downtime, and the **SLA report** lays out uptime, downtime, and SLI per period
against the target so you can see at a glance whether you are keeping your word.

![The Online Shop SLA: 99.5% target, weekly, enabled](assets/module-28/03-sla.png)

> In this lab the freshly-created service had only minutes of history when we first
> stopped `demo-nginx`, so its SLI started low (downtime weighed heavily against a
> few minutes of uptime) and climbs as the service stays healthy. Over a real week it
> reflects true availability against the 99.5% target.

### Business dashboards

The last step is to put all of this in front of the people who do not live in the
Zabbix console. You already learned to build dashboards in Module 12; here you point
that skill at a business audience. A *Business SLA Dashboard* combines an **SLA
report** widget, a **Problems** widget filtered by the `tier=online-shop` service tag,
and a **Top hosts** widget — so leadership opens one page and sees the Online Shop's
health and SLA standing at a glance, with no item graphs to decode. The filter on the
service tag is what keeps the view business-scoped instead of drowning in every metric
in the lab.

## Docker-Based Demonstration

The instructor enables inventory on the Online Shop hosts, builds the service tree
with tag mappings, defines the 99.5% SLA, then **stops `demo-nginx`** to show Web
Frontend and the Online Shop root turn red with the root cause named — and starts it
to show recovery and the SLA report.

## Hands-On Lab

1. **Enable host inventory.** On `demo-nginx` (**Data collection → Hosts →
   demo-nginx → Inventory**), set mode **Manual** and fill **Type** `Web server`,
   **Name** `Online Shop — Web Frontend`, **Location** `Docker lab`, **Contact**
   `ops@online-shop.lab`. Repeat for `demo-api` and `demo-postgres`.
   **Expected:** **Inventory → Hosts** lists the three hosts with their fields.

2. **Tag the hosts for services.** Add a **host tag** to each (Host → Tags):
   `service=web` on demo-nginx, `service=api` on demo-api, `service=db` on
   demo-postgres. This is the step that makes every future problem on a host
   self-label, so the services can find them without any per-trigger work.
   **Expected:** future problems on each host carry the tag.

3. **Build the service tree.** **Monitoring → Services**, switch to **Edit**, and
   create the root **Online Shop** (status calculation *Most critical of child
   services*), then child services **Web Frontend**, **API Service**, **Database**,
   **Notification Service** under it. Give each a tag `tier=online-shop`. The
   `tier=online-shop` service tag is what the SLA will later use to know which
   services it covers.
   **Expected:** a four-child tree under Online Shop, all **OK**.

4. **Map services to problems.** On each leaf, add a **problem tag**: `service`
   equals `web` (Web Frontend), `api` (API Service), `db` (Database). This closes the
   loop opened in step 2 — the host tags emit `service=...`, and here each leaf
   declares which value it answers to.
   **Expected:** the leaves will react to their hosts' problems.

5. **Define an SLA.** **Services → SLA → Create SLA**: Name `Online Shop SLA`, SLO
   `99.5`, period **Weekly**, schedule 24×7, **Service tags** `tier` equals
   `online-shop`, and **enable** it.
   **Expected:** the SLA is **Enabled** and lists with an **SLA report** link.

6. **Simulate a web failure.** Stop the frontend:
   ```bash
   docker stop demo-nginx
   ```
   **Expected:** within ~1 min **Web Frontend** turns **High**, and the **Online
   Shop** root turns **High** with root cause *Online Shop frontend is unavailable*.

7. **Simulate a database failure (optional).** Stop the database so the *database is
   unreachable* trigger fires:
   ```bash
   docker stop demo-postgres
   ```
   **Expected:** **Database** turns red too; the root reflects the most critical
   child. Start both containers again to recover.

8. **Review SLA impact.** Open **Services → SLA report**, select **Online Shop
   SLA**.
   **Expected:** uptime, downtime, and SLI for the period — the outage you just
   caused is counted against the 99.5% target.

9. **Build a business dashboard (Module 12 technique).** Create a dashboard
   `Business SLA Dashboard` and add an **SLA report** widget and a **Problems**
   widget filtered by service tag `tier=online-shop`.
   **Expected:** a single business-facing view of Online Shop health and SLA.

## Expected Outcome

Participants can register hosts in inventory, model the Online Shop as a service
tree, drive service status from tagged problems, read service impact and root cause,
and define and report on an SLA — closing the loop from a single failing item to
"are we meeting our business promise?".
