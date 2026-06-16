# Module 3: Zabbix User Interface

## Learning Objectives

By the end of this module participants can navigate the main sections of the
Zabbix 7.4 web interface, adjust their personal profile settings (time zone,
language, theme, and auto-refresh), find the built-in Zabbix server host and its
collected data, review problems and system status, and build a simple personal
dashboard.

## Topics

### Why the interface matters for the Online Shop

Everything you will ever do to the Online Shop — every host you add, every
trigger you write, every graph you read, every problem you acknowledge — happens
through one place: the Zabbix web interface. It is the cockpit. You configure the
monitoring through it, and you watch the results through it. That makes this
module less glamorous than the ones that follow, but more foundational than any
of them, because a few minutes spent now learning *where things live* pays for
itself in every later module. When Module 11 asks you to write a trigger, you do
not want to be hunting for the menu; you want to already know exactly which
section it lives under.

The encouraging news is that Zabbix 7.4 is laid out consistently. The interface
follows a small number of patterns, and once you internalize them you can find
almost anything without a manual. So rather than memorizing screens, your job in
this module is to learn the *map* — the handful of top-level sections and the one
mental model that tells you which section to reach for.

### The main menu (left sidebar)

The dark menu running down the left side of every page is your primary
navigation. It is always there, on every screen, which means you are never more
than one or two clicks from anywhere in the product. Each top-level section is a
heading that expands to reveal the pages beneath it. Here are the sections you
will use, with the exact 7.4 names — these were verified against the running
lab, not recalled from memory, because Zabbix does rename menus between versions
and the names below are specifically the 7.4 ones:

- **Dashboards** — at-a-glance views built from widgets (this is your home page).
- **Monitoring** — the *live* operational views: **Problems**, **Hosts**,
  **Latest data**, **Maps**, **Discovery**. This is where you look when you ask
  "what's happening right now?"
- **Services** — business-service monitoring and SLAs: **Services**, **SLA**,
  **SLA report** (Day 4–5).
- **Inventory** — hardware/asset inventory: **Overview**, **Hosts**.
- **Reports** — **System information**, **Scheduled reports**, **Availability
  report**, **Top 100 triggers**, **Audit log**, **Action log**, **Notifications**.
- **Data collection** — the *configuration* side: **Template groups**, **Host
  groups**, **Templates**, **Hosts**, **Maintenance**, **Event correlation**,
  **Discovery**. This is where you *build* monitoring. *(In older Zabbix this menu
  was called "Configuration" — in 7.4 it is "Data collection.")*
- **Alerts** — **Actions**, **Media types**, **Scripts** (Day 4).
- **Users** — **User groups**, **User roles**, **Users**, **API tokens**,
  **Authentication** (Day 4).
- **Administration** — global/system settings: **General**, **Audit log**,
  **Housekeeping**, **Proxy groups**, **Proxies**, **Macros**, **Queue**.

That is a long list, and you are not expected to absorb all of it today. Most of
those sections belong to later days, and they are listed here only so you have
seen the whole sidebar once and know roughly where each kind of work lives. What
you *do* need to take away today is a single distinction that beginners stumble
over more than any other:

> **The key mental model:** **Data collection** is where you *configure* what to
> monitor; **Monitoring** is where you *see* the results. Beginners often hunt
> for live data under Data collection (config only) or try to add items under
> Monitoring (views only). Configure under **Data collection**, observe under
> **Monitoring**.

Hold onto that one sentence and the rest of the menu falls into place. If your
question is "how do I set this up?" you are heading for **Data collection**. If
your question is "what is it doing right now?" you are heading for
**Monitoring**. Nearly every navigation mistake a new user makes is a confusion
between those two halves of the product.

![Main menu and the Global view dashboard](assets/module-03/01-navigation.png)
*The left sidebar is the main menu; the collapse arrows at the top shrink it to
icons when you need more screen space.*

### Personal profile settings

Before we tour the live data, there is a small but worthwhile detour: making the
interface yours. At the bottom of the menu, **User settings → Profile** holds
*your* personal preferences. The important word there is *personal* — these
settings attach to your account and your account only, so changing them affects
nothing for anyone else who logs in. That means you can experiment freely. Here
is what lives on that page and why each one matters:

- **Language** and **Time zone** — Zabbix shows timestamps in your chosen time
  zone, which matters when you correlate a problem with a real-world event.
- **Theme** — light (blue/"Blue"), **Dark**, or **System default**.
- **Auto-login** / **Auto-logout** — stay signed in, or expire idle sessions.
- **Refresh** — how often live pages reload (default 30 s).
- **Rows per page** — list page size (default 50).

Of these, the time zone deserves a second of thought, because it is the one that
quietly causes confusion later. When the Online Shop has a problem at, say, 2:14
in the afternoon, you want Zabbix to report that problem in *your* local time, so
that you can line it up against a deployment, a traffic spike, or a phone call
from a colleague. Set it correctly now and every timestamp you read for the rest
of the course will make sense at a glance.

![User settings → Profile](assets/module-03/05-profile.png)
*The Profile page. The same page hosts the Change password button you used in
Module 2.*

## Docker-Based Demonstration

With the map in hand, the instructor signs in to **<http://localhost:8080>** and
walks the interface live, so you can watch the sections in motion before you try
them yourself:

- expands **Monitoring** and opens **Problems**, then **Latest data**;
- opens **Data collection → Hosts** to show the built-in *Zabbix server* host;
- opens **Reports → System information** to show overall status;
- opens **User settings → Profile** to show time zone / theme;
- finishes by creating a one-widget dashboard under **Dashboards**.

Notice how careful this tour is to touch nothing. No configuration is changed
except each participant's own profile and a personal practice dashboard. That is
deliberate: the whole point of this module is to learn to *move around* safely,
so the demonstration models exactly the kind of harmless exploration you are
about to do.

## Hands-On Lab

Now it is your turn. Work through these steps in order; each one builds your
familiarity with one corner of the interface, and together they trace the same
path the instructor just walked.

1. **Sign in** at **<http://localhost:8080>** with `Admin` and your password
   (the one you set in Module 2).
   **Expected:** you land on **Dashboards → Global view**.

2. **Set your profile preferences.** Open **User settings → Profile** (bottom of
   the left menu). Set your **Time zone** to your local zone, optionally switch
   **Theme** to **Dark**, then click **Update**. This is the personal touch from
   the Topics section — and a quick way to confirm that these settings really are
   yours alone.
   **Expected:** a green "User updated" message; if you chose Dark, the interface
   immediately switches to the dark theme. Timestamps now display in your time
   zone.

3. **Explore dashboards.** Click **Dashboards**, then open **Global view**. This
   is the page you were dropped onto at login, and it is worth a proper look,
   because it previews the kind of summary view you will eventually build for the
   Online Shop.
   **Expected:** you see widgets such as *System information*, *Host
   availability*, *Problems by severity*, and *Current problems*.

4. **Open Latest data.** Go to **Monitoring → Latest data**. In the filter, click
   the **Hosts** field, type `Zabbix server`, select it, and click **Apply**.
   This is your first encounter with the *Monitoring* half of the product — raw
   measurements rather than configuration.
   **Expected:** a list of collected items appears for the Zabbix server host —
   for example *Available memory* and *Configuration cache, % used* — each with a
   **Last check** time and **Last value**. This is live data the server is
   collecting about itself.

   ![Latest data for the Zabbix server host](assets/module-03/03-latest-data.png)
   *Latest data is filter-driven: choose a host group or host to display its
   metrics. The colored tags (component: memory, cpu, …) come from the linked
   template.*

5. **Find the built-in Zabbix server host.** Go to **Data collection → Hosts**.
   You are now crossing into the *Data collection* half — the same Zabbix server
   you just watched reporting data, but seen from the configuration side.
   **Expected:** one host, **Zabbix server**, is listed with its item, trigger,
   and graph counts, the templates *Linux by Zabbix agent* and *Zabbix server
   health*, and an interface of `127.0.0.1:10050`. Its **Availability** shows a
   red **ZBX** — that is expected in this lab (the built-in host's agent address
   points inside the server container, which has no agent). We add real,
   reachable hosts starting in Module 5.

   ![Data collection → Hosts](assets/module-03/04-data-collection-hosts.png)
   *The Hosts configuration list. Note the Host Wizard, Create host, and Import
   buttons top-right — you will use these later.*

6. **Review problems.** Go to **Monitoring → Problems**. This is the page your
   team will live on once the Online Shop is fully monitored — the single screen
   that answers "is anything wrong right now?"
   **Expected:** the current problems list. In a fresh lab this may be empty or
   show only internal/self-monitoring problems — that is fine; we generate real
   problems in later modules.

   ![Monitoring → Problems](assets/module-03/02-problems.png)

7. **Review system status.** Go to **Reports → System information**. Think of this
   as the health check for Zabbix itself, separate from the health of the things
   Zabbix watches.
   **Expected:** **Zabbix server is running: Yes**, the server/frontend versions
   (7.4.11), and counts of hosts, items, and triggers — a quick health summary of
   the whole installation.

8. **Create a personal dashboard.** Finally, you will build something of your own.
   A dashboard is a page assembled from *widgets*, each widget a small panel that
   shows one kind of information; here you add a single, simple one just to learn
   the mechanics.
   1. Go to **Dashboards**, click **All dashboards**, then **Create dashboard**.
   2. In **Dashboard properties**, set **Name** to `My First Dashboard` and click
      **Apply**.
      ![Dashboard properties dialog](assets/module-03/06-create-dashboard-properties.png)
   3. Click **+ Add** (top-right) to open **Add widget**. Set **Type** to
      **Clock**, leave the defaults, and click **Add**.
      ![Add widget dialog (Clock)](assets/module-03/07-add-widget.png)
   4. Click **Save changes**.

   **Expected:** a green "Dashboard created" message and your new dashboard shows
   a working clock widget. It now appears under **All dashboards**.

   ![The finished personal dashboard](assets/module-03/08-personal-dashboard.png)

## Expected Outcome

Participants can confidently move around the Zabbix 7.4 interface: they know that
**Data collection** is for configuration and **Monitoring** is for live views,
they have personalised their profile (time zone/theme), they can locate a host
and its latest data, they can check overall status under Reports, and they have
built and saved a personal dashboard.
