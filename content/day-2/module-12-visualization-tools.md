# Module 12: Visualization Tools

## Learning Objectives

By the end of this module participants can turn collected metrics into useful
visual views: ad-hoc and **classic graphs**, **dashboards** built from widgets
(Problems, Host availability, Item value, Graph, Problems by severity), and a
status-aware **network map** — and can explain the difference between an
**operational** and a **management** dashboard.

## Topics

### From numbers to a view

So far the Online Shop's data lives in Latest data as rows of numbers. People
absorb *pictures* far faster than tables. Visualization is how monitoring becomes
*useful*: a glance at one screen should answer "is everything OK, and if not,
where?". This module builds the Online Shop's first real dashboards, graphs, and
map.

### Latest data and graphs

**Latest data** is the raw table (Module 3). From it you can select numeric items
and **Display graph** for a quick **ad-hoc graph** — the fastest way to eyeball a
metric over time (you used this in Module 4).

A **classic graph** is a *saved, configured* chart: you pick several items, give
each a colour, draw style (line/filled/bars), and Y-axis side, and Zabbix renders
them together. Classic graphs are defined per host under **Data collection →
Hosts → Graphs** and reused on dashboards and in reports.

![A classic graph combines several items with colours and draw styles](assets/module-12/03-classic-graph.png)

### Dashboards and widgets

A **dashboard** is a grid of **widgets**, each showing one thing. Zabbix ships
many widget types — the ones you will use constantly:

- **Problems** — the live problem list (what is wrong now).
- **Problems by severity** — counts per severity (the health "traffic lights").
- **Host availability** — how many hosts are up / down / unknown.
- **Item value** — one metric as a big number (a KPI).
- **Graph** — an SVG time-series chart (one or more items).
- plus Clock, Gauge, Geomap, Top hosts, Maps, and more.

![The Add widget dialog — Zabbix's widget types](assets/module-12/02-widget-types.png)

### Maps

A **map** (Monitoring → Maps) is a picture of your infrastructure — icons for
hosts, lines for links — that **colours itself by status**: a host with an active
problem highlights, and its problem text appears. Maps answer "what is the
topology, and where is the red?" at a glance, which is invaluable for network and
service overviews.

### Dashboard design: operational vs management

The same data serves two very different audiences:

- An **operational dashboard** is for the people fixing things: dense, live,
  detailed — current problems, graphs, queues, host availability. Refreshes
  often; optimised for *action*.
- A **management dashboard** is for stakeholders: sparse, high-level — SLA %,
  service status, trends. Optimised for *reassurance and decisions*.

Good design rules: one purpose per dashboard, most important top-left, group
related widgets, don't cram, and use severity colours consistently. The course's
canonical dashboards (*Docker Lab Overview*, *Web and API Monitoring*, *Zabbix
Health*, *Business SLA*, *Troubleshooting*) each have one clear job.

## Docker-Based Demonstration

The instructor builds an **operational** dashboard for the lab — *Docker Lab
Overview* — combining Host availability, Problems by severity, an Item value KPI
(API response time), a live Problems list, and an SVG Graph of the API's response
time and queue. Then a classic graph and a network map of the lab hosts, showing
how each visual answers a different question.

## Hands-On Lab

> We visualise data that already exists (agent metrics, the `demo-api` metrics,
> and the triggers from Modules 9–11). Database and business-service dashboards
> come once that data exists (Modules 22 and 28).

1. **Make an ad-hoc graph.** In **Monitoring → Latest data**, filter to `demo-api`,
   tick **Online Shop API: response time** and **queue length**, and click
   **Display graph**.
   **Expected:** a quick line graph of both metrics over the last hour.

2. **Create a classic graph.** Go to **Data collection → Hosts**, click **Graphs**
   on `demo-api`, then **Create graph**:
   - **Name:** `Online Shop API — response time and queue`
   - Add two **Items**: *response time* (colour green) and *queue length*
     (colour blue), both **Draw style: Line**.

   **Add.**
   **Expected:** a saved graph you can reuse on dashboards (see the graph builder
   above).

3. **Create an operational dashboard.** Go to **Dashboards → All dashboards →
   Create dashboard**, name it `Docker Lab Overview`, then **+ Add** these widgets:
   - **Host availability**
   - **Problems by severity**
   - **Item value** → the `demo-api` *response time* item (a KPI number)
   - **Problems** (filter to your lab host groups)
   - **Graph** → a data set for the `demo-api` *response time* and *queue* items

   **Save changes.**
   **Expected:** a single screen answering "is everything OK?" — availability,
   severity counts, a KPI, the live problem list, and a trend graph.

   ![The Docker Lab Overview operational dashboard](assets/module-12/01-dashboard.png)

4. **Create a network map.** Go to **Monitoring → Maps → Create map**, name it
   `Online Shop — Network Map`, open it, and add host elements for `zabbix-server`,
   `demo-api`, `zabbix-agent-basic`, and `zabbix-agent2-docker`; link each demo/
   agent host to the server. **Update.**
   **Expected:** a topology that colours itself by status — hosts with active
   problems highlight and show their problem text; healthy hosts read **OK** in
   green.

   ![A status-aware network map of the lab](assets/module-12/04-map.png)

5. **Compare the audiences.** Look at your *Docker Lab Overview* (operational) and
   sketch what a *management* version would show instead (SLA %, service status,
   fewer widgets).
   **Expected:** you can articulate why the same data needs two different views.

## Expected Outcome

Participants can build ad-hoc and classic graphs, assemble a multi-widget
operational dashboard (Problems, Host availability, Item value, Graph, Problems by
severity), create a status-aware network map, and explain operational-vs-management
dashboard design — turning the Online Shop's metrics into views people actually
use.

## Instructor Notes

- **Lab vs production.** Identical UI; production dashboards just have more hosts
  and are often shown on wall displays (kiosk mode — the expand icon top-right).
  Maps in production are drawn over real network/rack diagrams via background
  images.
- **SVG Graph vs classic graph.** The dashboard **Graph** widget (SVG) is the
  modern, interactive chart and is configured by *item patterns* (great for
  "all hosts matching X"). **Classic graphs** are saved per-host objects, handy
  when you want the exact same chart in several places or in reports. Show both;
  let students pick per need.
- **Don't cram.** The most common beginner mistake is a wall of 20 widgets nobody
  reads. Enforce "one dashboard, one question." Top-left is prime real estate.
- **Maps need icons and links.** Map building is click-heavy (drag icons, draw
  links). In this lab the map is provided pre-built; in class, walk one host +
  one link live so students see the mechanics, then show the finished map.
- **Deferred dashboards.** The outline's *database* and *business-service*
  dashboards need data we collect later — build them in Modules 22 (DB) and 28
  (business services). Note this so students don't expect DB widgets yet.
- **Timing (~45 min).** ~12 min graphs (ad-hoc + classic), ~18 min dashboard +
  widget types, ~10 min map, ~5 min design discussion (operational vs management).

## Lab-State Delta

Added in Module 12 (all kept):

- **Classic graph:** `Online Shop API — response time and queue` (graphid `5423`)
  on `demo-api` — items *response time* (green) + *queue length* (blue).
- **Dashboard:** `Docker Lab Overview` (dashboardid `410`) — widgets: Host
  availability, Problems by severity, Item value (API response time), Problems,
  and an SVG Graph (response time + queue).
- **Map:** `Online Shop — Network Map` (sysmapid `2`) — host elements for
  `zabbix-server`, `demo-api`, `zabbix-agent-basic`, `zabbix-agent2-docker`, linked
  in a star to the server; colours by live status. Screenshots in
  `content/day-2/assets/module-12/`.
