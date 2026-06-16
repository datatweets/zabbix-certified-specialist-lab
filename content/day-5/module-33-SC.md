# Module 33: System Reports

## Learning Objectives

By the end of this module participants can use Zabbix's reporting: read the **System
information** and **Availability** reports, find noisy triggers with **Top 100
triggers**, and configure and generate a **scheduled PDF report** of a dashboard via
the **Zabbix Web Service** — delivered by email — understanding what reporting
requires and who each report is for.

## Topics

### Two audiences, several reports

For four days you and I have been building the machinery of monitoring: collecting
measurements, raising triggers, drawing dashboards, sending alerts. Day 5 turns that
machinery toward a different purpose. Up to now everything has been *live* —
something happens, someone looks at a screen, someone reacts. Reporting is about
producing *deliverables*: artifacts that summarize what the monitoring has seen and
hand them to a person who is not staring at Zabbix all day.

The reason reports exist at all is that monitoring serves two very different
audiences, and those audiences ask very different questions. The first is
**Operations** — the engineers who keep the Online Shop running. What they want to
know is *where the pain is right now*: which triggers fire most often, which hosts
have been least available, what is eating their time this week. They live inside
Zabbix and they want raw, actionable detail. The second audience is **Management** —
the people who promised customers an uptime number and now have to show they kept the
promise. What they want is a *periodic summary*: an SLA report that lands in their
inbox every Monday morning, readable at a glance, with no login required and no
expectation that they understand item keys.

Zabbix's **Reports** menu covers both ends of that spectrum, and the **Zabbix Web
Service** is the piece that lets you turn any dashboard into an emailed PDF — which is
exactly the format management lives in. The rest of this module walks each report in
turn, from the operational snapshots an engineer glances at to the scheduled PDF a
manager receives.

### System information

The first report is the one you check before trusting any of the others. **Reports →
System information** is the platform's vital-signs snapshot, the same view you met in
Module 30: it tells you whether the server is running, what version you are on and
whether an update is available, the host/item/trigger counts, the **not-supported**
count, and **Required server performance (NVPS)** — the number of new values per
second Zabbix is being asked to process. Think of it as taking the monitoring
system's own pulse. If Zabbix itself is unhealthy — server stopped, items piling up
as not-supported, NVPS pinned far above what the box can sustain — then every other
report is built on shaky data, which is why this screen is the first one to glance at:
*is Zabbix itself healthy?* before you ask it anything about the Online Shop.

### Availability report

**Reports → Availability report** answers the question that sits underneath every
uptime promise: *"how available has this been?"* For each trigger it shows the
percentage of the chosen period spent in **Problem** versus **OK** — and that split is
the raw material of an uptime SLA. If a trigger says "the Online Shop frontend is
down," then the fraction of last week that trigger spent in OK *is* the frontend's
availability for last week. You filter by host group or by trigger over a time range,
and Zabbix gives you a number you can put in a sentence: "the Online Shop frontend was
OK 99.x% of last week." That sentence is what an SLA conversation is built from.

![The availability report: per-trigger OK/Problem percentages](assets/module-33/01-availability-report.png)

### Top 100 triggers

Where the availability report tells you *how much* something was broken, **Reports →
Top 100 triggers** tells you *what* breaks most often. It ranks triggers by the
**number of problems** they generated over a period — in effect, a map of your noise
and instability. In our lab the *ERROR in Online Shop app log* trigger leads the
ranking, because the demo app logs errors continuously, followed by the demo-api queue
and failed-payment triggers. The value of this report is diagnostic: a trigger sitting
at the top of the list is telling you something demands attention, but it does not tell
you *which kind* of attention. Either it is a real chronic problem worth fixing, or it
is a threshold set too tightly and firing far more often than the underlying condition
warrants. Top 100 triggers is where you decide what to **fix or tune** — it points your
effort at the loudest part of the system instead of leaving you to guess.

![Top 100 triggers: the most active problems, ranked](assets/module-33/02-top-triggers.png)

### Scheduled reports and the Zabbix Web Service

The reports so far are things an engineer opens on demand. A **scheduled report** is
different in kind: it renders a **dashboard** to **PDF** and emails it on a cycle, with
nobody having to remember to do it. This is the management deliverable — the Monday SLA
PDF that arrives without anyone logging in.

There is a small technical wrinkle that explains why scheduled reports need an extra
container. A dashboard is a live web page, full of widgets that fetch and render data
in a browser. To turn that page into a static PDF, *something* has to actually open the
page, let it render, and print it. Zabbix cannot do that with the server process
alone; it needs a headless browser. That is the job of the **Zabbix Web Service**
container (`zabbix-web-service`): it loads the frontend, lets the dashboard render, and
exports the result as a PDF. When you hear "the web service," picture a robot that
opens the dashboard in a browser and hits Print.

The report definition itself ties everything together. It names the **dashboard** to
render, the **period** it should cover (previous day, week, or month), the **cycle**
and **start time** that schedule it, the **subject/message** that frames the email, and
the **subscribers** who receive it. For the Online Shop we report the **Business SLA
Dashboard** built in Module 32, and we report it weekly — which matches how management
thinks about the service: not minute to minute, but week over week.

![A scheduled report of the Business SLA Dashboard, weekly](assets/module-33/03-scheduled-report.png)

When the report runs, the web service renders the dashboard and the report is emailed
with the **PDF attached**. In our lab that email is delivered to the on-call address
through the Module 27 email media type and caught by Mailpit, so you can see exactly
what a subscriber would receive.

![The rendered report email with the PDF attachment in Mailpit](assets/module-33/04-report-email.png)

### What report generation requires

Scheduled reporting is one of those features that works perfectly or fails silently,
and the difference comes down to a short chain of prerequisites. If any link is
missing, the report simply doesn't arrive, with no obvious error in front of the user —
the same trap you learned to avoid with alerting. So it is worth knowing the whole
chain. Scheduled reports only work when **all** of these are in place:

- The **`zabbix-web-service`** container is running and reachable from the server.
- The server is configured with **`ZBX_WEBSERVICEURL`** and at least one
  **report writer** (`ZBX_STARTREPORTWRITERS ≥ 1`) — both set in `compose_lab.yaml`.
- A **Frontend URL** is set in **Administration → General → Other configuration
  parameters**, pointing at a URL the web service can reach
  (`http://zabbix-web:8080/` on the lab network).
- The recipient has **email media** and the **Email** media type works (Module 27).

Miss any one and reports silently fail to send — the same "walk the chain" discipline
as alerting.

## Docker-Based Demonstration

The instructor reviews System information and the Availability and Top-100-triggers
reports, confirms the Frontend URL and the running `zabbix-web-service`, then creates
a scheduled report of the Business SLA Dashboard and **tests** it — showing the PDF
arrive in Mailpit.

## Hands-On Lab

1. **Review system information.** Open **Reports → System information**.
   This is your "is the monitoring itself healthy?" check, and a sensible habit before
   reading any other report.
   **Expected:** server running, version up to date, host/item/trigger counts, NVPS —
   the platform health snapshot (Module 30).

2. **Open the availability report.** **Reports → Availability report**, pick a host
   group/trigger and a time range. The OK percentage you get back is the raw number
   behind any uptime claim about the Online Shop.
   **Expected:** per-trigger **OK%** and **Problem%** for the period — e.g. how
   available the Online Shop frontend was.

3. **Review top triggers.** **Reports → Top 100 triggers** over the last day. Reading
   the ranking, ask of each leader whether it is a real fault or a noisy threshold.
   **Expected:** the most-active triggers ranked by problem count — *ERROR in Online
   Shop app log* at the top, then the demo-api triggers. Identify what to fix or tune.

4. **Check report prerequisites.** Confirm the **Frontend URL** is set in
   **Administration → General → Other configuration parameters**
   (`http://zabbix-web:8080/`) and that `zabbix-web-service` is running. Remember the
   URL has to be reachable from the web service *container*, which is why it uses a
   container name and not `localhost`:
   ```bash
   docker ps | grep zabbix-web-service
   docker exec zabbix-server nc -zv zabbix-web-service 10053
   ```
   **Expected:** the URL is set and the web service port is open.

5. **Create a scheduled report.** **Reports → Scheduled reports → Create report**:
   Name `Online Shop Weekly SLA Report`, **Dashboard** `Business SLA Dashboard`,
   **Period** *Previous week*, **Cycle** *Weekly*, **Start time** `09:00`, **Repeat
   on** Monday, a **Subject/Message**, and add **Admin** as a subscriber. Enable it.
   Each field here is one of the report-definition choices from the Topics section made
   concrete.
   **Expected:** the report is saved and **Enabled**.

6. **Test it.** Open the report and click **Test**. Testing exercises the whole chain —
   web service render, PDF generation, email delivery — without waiting for Monday.
   **Expected:** within a few seconds the web service renders the dashboard and an
   email **`Online Shop — Weekly SLA Report`** with a **PDF attachment** arrives in
   Mailpit (http://localhost:8025). On Monday at 09:00 it would send automatically.

## Expected Outcome

Participants can read Zabbix's operational reports (system information, availability,
top triggers) and produce a management-ready **scheduled PDF report** of a dashboard
via the Zabbix Web Service — and they know the prerequisites that make report
generation work.
