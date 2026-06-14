# Module 2: Deploying Zabbix with Docker Compose

## Learning Objectives

By the end of this module participants can describe the major components of a
Zabbix deployment and how they fit together, deploy the complete course lab with
a single Docker Compose command, open and log in to the Zabbix 7.4 frontend,
change the default administrator password, and confirm that the Zabbix server is
running.

## Topics

### Why this module matters for the Online Shop

Before we can monitor anything, we need the monitoring platform itself. In this
module we stand up the entire lab — the Zabbix platform *and* the Online Shop
systems we will spend the week watching — and verify it is healthy. Everything in
the remaining 38 modules runs on top of what you deploy here.

### Zabbix architecture — the components you are deploying

A Zabbix deployment is several cooperating services, not one program. Our lab
runs each as its own container so you can see the boundaries clearly:

- **Zabbix server** (`zabbix-server`) — the "brain." It collects metrics,
  evaluates triggers, generates problems and events, and runs actions
  (e.g. sends alerts). It is the only component that writes monitoring logic
  decisions.
- **Database** (`zabbix-db`, MySQL) — the system of record. All configuration
  (hosts, items, triggers, templates) **and** all collected history and trends
  live here. If the database is down, Zabbix cannot function.
- **Frontend / web interface** (`zabbix-web`, nginx + PHP) — what humans use. It
  reads and writes configuration in the database and queries the server for live
  status. Served on **port 8080** in our lab.
- **Zabbix agent** (`zabbix-agent-basic`) and **Zabbix agent 2**
  (`zabbix-agent2-docker`) — lightweight collectors that run on (or beside)
  monitored hosts and report metrics such as CPU, memory, disk, and processes.
  Zabbix agent 2 (written in Go) adds built-in plugins (Docker, databases, and
  more).
- **Zabbix proxy** (`zabbix-proxy-branch`) — an optional remote collector that
  gathers data on behalf of the server for a remote site, then forwards it. We
  configure it on Day 2 (Module 14); it is already running here, ready to use.
- **Java gateway** (`zabbix-java-gateway`) — a helper the server uses to poll
  Java applications over JMX (Module 22).
- **Web service** (`zabbix-web-service`) — a helper that renders dashboards to
  PDF for scheduled reports (Module 33).

### Docker Compose overview

**Docker** packages each service and its dependencies into a *container* — a
self-contained, isolated process that runs identically on any machine.
**Docker Compose** describes a *set* of containers, their configuration, volumes,
and the network that connects them, in a single YAML file. One command
(`docker compose up`) starts the whole set; another (`docker compose down`) stops
it. For us, that single file is **`compose_lab.yaml`** — it defines all eight
platform containers and all seven Online Shop demo systems on one shared network
named `zabbix-lab`, so every container can reach the others by name (for example
the server reaches the database at `zabbix-db`).

### Why Docker is ideal for a training lab

- **Identical for everyone.** Every participant runs the exact same versions and
  configuration — no "works on my machine."
- **Resettable.** A broken lab is fixed with `down` then `up`; a clean slate is
  one command away.
- **Self-contained.** The platform *and* the systems being monitored live in one
  file, so cloning this repository gives you the complete environment.

### Training deployment vs production deployment

This single-host, all-in-one Docker stack is perfect for learning, but it is
**not** how Zabbix is run in production. In production:

- the **server** and **database** are usually on dedicated, sized hosts (the
  database especially, because it grows with history and trends);
- the **frontend** runs behind a hardened web server with **TLS** and real
  certificates (here we use plain HTTP on port 8080);
- **agents** are installed on each monitored machine (VM, bare-metal, cloud
  instance) rather than as sidecar containers;
- a **proxy** runs at each remote site/branch office or DMZ;
- credentials come from a secrets manager — **not** the plain, well-known
  passwords we use here for convenience.

The *components and the way they cooperate are identical*; only the packaging,
sizing, and hardening differ. Keep that mapping in mind every time we take a lab
shortcut.

## Docker-Based Demonstration

The instructor deploys the whole lab from a clean clone of the course repository.

```bash
# 1. Clone the course repository (contains the lab AND the course content)
git clone https://github.com/datatweets/zabbix-certified-specialist-lab.git
cd zabbix-certified-specialist-lab

# 2. Start the entire lab (first run builds the demo images — a few minutes)
docker compose -f compose_lab.yaml up -d

# 3. List the stack
docker compose -f compose_lab.yaml ps
```

> **Note:** the default branch `main` already contains everything — no
> `git checkout` is needed. The first `up` **builds** the custom demo images
> (`demo-api`, `demo-snmp-device`, `demo-log-app`) and **pulls** the rest, so it
> takes a few minutes. Later starts are nearly instant.

Verified output — all 15 containers report `running`, and the platform database,
frontend, and mail sink report `healthy`:

```text
NAME                   STATUS
demo-api               Up (running)
demo-java-jmx          Up (running)
demo-log-app           Up (running)
demo-mailhog           Up (running) (healthy)
demo-nginx             Up (running)
demo-postgres          Up (running)
demo-snmp-device       Up (running)
zabbix-agent-basic     Up (running)
zabbix-agent2-docker   Up (running)
zabbix-db              Up (running) (healthy)
zabbix-java-gateway    Up (running)
zabbix-proxy-branch    Up (running)
zabbix-server          Up (running)
zabbix-web-service     Up (running)
zabbix-web             Up (running) (healthy)
```

The instructor then opens **<http://localhost:8080>**, logs in, and shows
**Reports → System information** confirming the server is running on Zabbix 7.4.

## Hands-On Lab

Each step states what confirms success. If a step fails, stop and fix it before
moving on — later modules assume a healthy lab.

1. **Install Docker Desktop** (if not already installed) and confirm it is
   running.
   ```bash
   docker --version
   docker compose version
   ```
   **Expected:** both commands print a version (Docker Engine and the Compose
   v2 plugin). Docker Desktop's whale icon shows "running."

2. **Clone the course repository and enter it.**
   ```bash
   git clone https://github.com/datatweets/zabbix-certified-specialist-lab.git
   cd zabbix-certified-specialist-lab
   ```
   **Expected:** the clone completes and `ls` shows `compose_lab.yaml` and a
   `content/` folder.

3. **Start the lab.**
   ```bash
   docker compose -f compose_lab.yaml up -d
   ```
   **Expected:** Docker builds/pulls images, then prints `Started` for each
   container. The first run may take several minutes.

4. **Check the running containers.**
   ```bash
   docker compose -f compose_lab.yaml ps
   ```
   **Expected:** 15 containers listed, all `running`; `zabbix-db`, `zabbix-web`,
   and `demo-mailhog` additionally show `(healthy)`. (If `zabbix-web` is still
   `starting`, wait ~30 s and re-run.)

5. **Open the Zabbix web interface** at **<http://localhost:8080>** in your
   browser.
   **Expected:** the Zabbix sign-in page appears with the **ZABBIX** logo and
   **Username** / **Password** fields.

   ![Zabbix 7.4 sign-in page](assets/module-02/01-login.png)
   *The login page. The "Online Shop Monitoring Lab" label top-right comes from
   the lab's configured server name.*

6. **Log in with the default administrator account.**
   - Username: `Admin` (capital A)
   - Password: `zabbix`
   - Click **Sign in**.

   **Expected:** you land on **Dashboards → Global view** with widgets such as
   *System information*, *Host availability*, and *Problems by severity*.

   ![Global view dashboard after login](assets/module-02/02-dashboard.png)
   *The default dashboard. The left-hand menu is your main navigation:
   Dashboards, Monitoring, Services, Inventory, Reports, Data collection, Alerts,
   Users, Administration.*

7. **Verify the Zabbix server is running.** In the left menu go to
   **Reports → System information**.
   **Expected:** the table shows **Zabbix server is running: Yes** (details
   `zabbix-server:10051`), **Zabbix server version: 7.4.11**, and **Zabbix
   frontend version: 7.4.11**. You will also see 1 host, 360 templates, and a
   non-zero "Required server performance" — proof the server is collecting.

   ![Reports → System information](assets/module-02/03-system-information.png)
   *System information confirms the server↔database↔frontend chain is healthy.*

8. **Change the default administrator password.** In the left menu open
   **User settings → Profile**.

   ![User settings → Profile](assets/module-02/04-user-profile.png)
   *Your personal profile page — language, time zone, theme, and auto-refresh
   live here too. Click **Change password** to reveal the password fields.*

   Click **Change password** and fill in:
   - **Current password:** `zabbix`
   - **Password:** a new password of your choice
   - **Password (once again):** the same new password

   Click **Update**.

   **Expected:** a green "User updated" confirmation. The default `zabbix`
   password no longer works; your new password does on the next sign-in.

   ![The Profile page with the password fields revealed](assets/module-02/05-change-password.png)

9. **Confirm the new password works.** Sign out (**User settings → Sign out**),
   then sign back in with `Admin` and your new password.
   **Expected:** you log in successfully with the new password.

## Expected Outcome

Participants have the complete course lab running locally — all 15 containers
healthy — can log in to the Zabbix 7.4 frontend at `http://localhost:8080`, have
changed the default administrator password, and have confirmed via **Reports →
System information** that the Zabbix server is running on version 7.4.11.

## Instructor Notes

- **Lab vs production.** Reiterate that this all-in-one, single-host stack is a
  *training* deployment. In production the server, database, and frontend are
  separate, sized hosts; the frontend is fronted by TLS; agents are installed on
  the machines they monitor; and passwords come from a secrets store. The plain
  `Admin` / `zabbix` default and HTTP-on-8080 are lab conveniences only.
- **The password change vs automation.** Module 36 (API automation) and the
  course's verification scripts authenticate as `Admin`. If students change the
  `Admin` password here (recommended for good hygiene), they must use their new
  password later, or create a dedicated API token under **User settings → API
  tokens**. For a throwaway lab some instructors leave the default; for teaching
  security habits, change it.
- **First-run time / resources.** The first `up` builds three demo images and
  pulls ~10 more; on a slow connection this can take 5–10 minutes. Ensure
  students meet the minimum (8 GB RAM, ideally 16 GB; ~20 GB free disk). If
  `zabbix-web` shows `starting`, it is waiting on the database's first-run schema
  import — give it a minute.
- **Common student mistakes.** Using lowercase `admin` (the username is `Admin`);
  forgetting `-f compose_lab.yaml` (Compose then loads the upstream
  `compose.yaml` instead); a port-8080 conflict with another local service
  (stop the other service or change the published port); running `up` from the
  wrong directory.
- **Reset recipe.** To wipe and start fresh:
  `docker compose -f compose_lab.yaml down -v` then
  `docker compose -f compose_lab.yaml up -d`. The `-v` flag also deletes the
  database volume, returning Zabbix to the default `Admin` / `zabbix` login.
- **Timing.** ~45 minutes: ~15 min architecture/Compose concepts, ~20 min guided
  deploy + login + password change, ~10 min troubleshooting stragglers.

## Lab-State Delta

Module 2 brings the lab online but adds **no monitoring configuration** of its
own. Reference-lab state after this module:

- **Stack deployed** via `docker compose -f compose_lab.yaml up -d` — 15
  containers running (see `lab-state.md` §0).
- **Frontend:** `http://localhost:8080`; **Zabbix server is running: Yes**;
  server & frontend **7.4.11** (verified in Reports → System information).
- **Administrator password:** students change `Admin`'s password from the default
  `zabbix`. *The reference/verification lab keeps `Admin` / `zabbix` so the API
  helper scripts continue to work; this is noted, not a configuration object.*
- No hosts, items, triggers, templates, or dashboards were created.
