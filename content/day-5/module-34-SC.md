# Module 34: Advanced Visualization

## Learning Objectives

By the end of this module participants can design monitoring views for **different
audiences**: build a status-aware **infrastructure map**, embed it and live data in
an **operations dashboard**, contrast it with a **management dashboard**, customize
graphs, and explain when to use Zabbix's native dashboards versus an **external tool
like Grafana**.

## Topics

### Visualization is about the audience, not the data

It is tempting to think of a dashboard as a place to display everything you have
collected, as if the goal were to leave no metric off the screen. That instinct
produces wall-of-numbers panels that look impressive in a demo and help no one
during an actual incident. The better mental model is that visualization is a
service you provide to a specific reader, and the same monitoring data serves very
different people. A good view answers **one question for one audience**:

- **Operations** need *"what is broken right now and where?"* — a live map, current
  problems, host availability.
- **Management** need *"is the service healthy and meeting its SLA?"* — service
  status, SLA attainment, trends.

Those are genuinely different questions. The engineer holding the pager at 3 a.m.
does not care about quarterly SLA attainment; the executive reviewing the month does
not want to read individual trigger names. Putting everything on one screen serves
no one. The skill is choosing the right widgets for the right viewer — which is what
this module practises, using the same Online Shop data we have been collecting all
week to build two deliberately different screens.

### Infrastructure maps

A list of red host names tells you *what* is broken but not *where it sits* or *what
it drags down with it*. That second question — impact — is what a map answers. A
**map** (Monitoring → Maps) is a picture of your environment where each element is a
live object that **colours by status**. Rather than reading a table and
reconstructing the topology in your head, you see the topology drawn out and watch it
change color as the state of the world changes. We build one for the Online Shop:
`demo-snmp-device` (the network edge) → `demo-nginx` (web) → `demo-api` → the
`demo-postgres` database and `demo-java-jmx` service, with the Zabbix server watching
over it.

![The rendered infrastructure map — green = OK, highlighted = problem](assets/module-34/01-map-view.png)

Elements with active problems light up and show the problem name (here **API
Service** and the **Zabbix Server** are highlighted), so one glance tells you both
*what* is wrong and *where it sits* in the topology. That last part is the payoff: if
the database element lights up, your eye immediately follows the links to everything
downstream of it, and you understand the blast radius without anyone explaining it.

#### Building a map, step by step

A map is assembled in the **map constructor** (Monitoring → Maps → *map* → **Edit
map**). Think of it as a small drawing canvas built for monitoring rather than for
art. The toolbar adds **map elements**, **shapes**, and **links**; a grid helps
alignment.

![The map constructor: add elements, links, and shapes on a grid](assets/module-34/02-map-constructor.png)

Each **element** is configured to a real object — its **Type** (Host), the **Host**
it represents, its **label** (we use `{HOST.NAME}` macros), and per-status **icons**
(Default / Problem / Maintenance / Disabled) so the picture changes as state changes.
The macro matters here: by labeling with `{HOST.NAME}` rather than typing a name, the
map stays correct if the host is ever renamed. Elements are joined by **links**,
which can themselves colour by a trigger, so a connection between two systems can turn
red when the relationship it represents is in trouble.

![Configuring a map element: linked to demo-api, with per-status icons and links](assets/module-34/03-map-element.png)

### Service maps

So far we have drawn physical hosts, but the Online Shop also has a logical shape — a
business-service tree — and sometimes that is the picture worth showing. The same map
tool can picture **business services** instead of hosts — element type **Trigger** or
links coloured by trigger let you draw the Online Shop's logical service flow (Module
28) rather than its physical hosts. The rule of thumb is simple: use a **host map**
for infrastructure and a **service/trigger map** for the business view.

### Advanced dashboards for two audiences

Dashboards combine **widgets** (Module 12) into a purpose-built screen, and a map is
only one of the ingredients available. The power is the **widget mix**, and a **map
widget** can embed the map you just built — so the topology you assembled becomes one
panel among several on a larger screen.

The **operations dashboard** answers "what's broken now": the infrastructure **map**,
**host availability**, **problems by severity**, and the live **problem list**.
Everything on it points toward action, and nothing on it requires interpretation by a
manager.

![The operations dashboard: map widget, availability, severity, live problems](assets/module-34/04-ops-dashboard.png)

The **management dashboard** (the Business SLA Dashboard, Module 32) answers "are we
healthy and meeting the SLA": the **SLA report** per service and the Online Shop's
problems — no engineering detail. A reader can tell at a glance whether the business
is keeping its promises, without needing to know what a trigger expression is.

![The management dashboard: SLA attainment per service](assets/module-34/05-mgmt-dashboard.png)

Same platform, same data, **two deliberately different screens** — that is the
lesson.

### Graph customization

A single item's history is fine for answering "how has this one number moved?", but
real understanding often comes from seeing two numbers together. Beyond simple item
history, a **custom graph** (Data collection → Hosts → Graphs) lets you place
**multiple items on one chart**, choose draw styles (line, filled, stacked), set
Y-axis scale and units, and add a legend — for example overlaying the API's response
time and queue length to see them correlate. When those two lines rise together, the
relationship jumps out in a way no table conveys. Dashboards then surface these via
the **Graph** and **Item value** widgets.

### External visualization: Grafana (concept)

Everything above stays inside Zabbix, and that is a deliberate strength worth naming.
Zabbix's dashboards are native, problem- and service-aware, and need no extra
infrastructure. But Zabbix is rarely the only data source a mature team has.
**Grafana** is an external dashboard tool with a **Zabbix data source plugin**; teams
use it to **combine Zabbix with other data sources** (logs, cloud metrics,
application traces) and for highly customised or public display panels.

> **Concept only:** this lab does not ship Grafana. The integration is a Grafana
> instance pointed at the Zabbix API via the Zabbix plugin — out of scope to build
> here, but important to know.

**When to use which:** stay in **Zabbix dashboards** for monitoring-native views
(problems, services, SLAs, maps) with zero extra moving parts; reach for **Grafana**
when you must blend Zabbix with **other systems** or need panel types Zabbix doesn't
offer.

## Docker-Based Demonstration

The instructor builds the infrastructure map (elements → icons → links → status),
embeds it in an operations dashboard alongside availability and problems, contrasts
that with the management SLA dashboard, customizes a graph, and discusses where
Grafana fits.

## Hands-On Lab

1. **Create an infrastructure map.** **Monitoring → Maps → Create map**: name
   `Online Shop — Infrastructure`, set a size, then **Edit map**.
   **Expected:** an empty constructor canvas with the element/link toolbar.

2. **Add elements.** **Map element → Add**, then configure each: Type **Host**, pick
   the host (`demo-nginx`, `demo-api`, `demo-postgres`, `demo-java-jmx`,
   `demo-snmp-device`, and the Zabbix server), set a **label** (`{HOST.NAME}`) and a
   fitting **icon** (router for the network device, server for the rest).
   **Expected:** six elements on the canvas, each tied to a host.

3. **Link them.** **Link → Add** between elements to draw the topology (edge → web →
   api → db/java). **Update** the map.
   **Expected:** a connected diagram; in **Monitoring → Maps** the elements are
   **green (OK)** and turn **red/orange** when their host has a problem.

4. **Build an operations dashboard.** **Dashboards → Create dashboard**, name `Online
   Shop — Operations`. Add a **Map** widget (the infrastructure map), a **Host
   availability** widget, a **Problems by severity** widget, and a **Problems**
   widget.
   **Expected:** a live "what's broken now" screen with the map embedded.

5. **Review the management dashboard.** Open the **Business SLA Dashboard** (Module
   32).
   **Expected:** SLA-per-service and service problems — the same data, shaped for
   leadership. Compare the two dashboards' intent.

6. **Customize a graph.** Create a custom graph combining two `demo-api` items (e.g.
   response time and queue length) with a legend.
   **Expected:** both series on one chart; add it to a dashboard via the **Graph**
   widget.

7. **Discuss external tools.** Note where a Grafana dashboard (Zabbix data source)
   would add value — blending Zabbix with other data sources.

## Expected Outcome

Participants can build a status-aware infrastructure map, assemble distinct
operations and management dashboards from the right widgets, customize graphs, and
decide between native Zabbix dashboards and an external tool like Grafana — designing
visualization that fits each audience.
