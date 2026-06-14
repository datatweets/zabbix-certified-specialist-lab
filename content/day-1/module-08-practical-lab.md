# Module 8: Practical Lab — Day 1

## Learning Objectives

By the end of this module participants can perform a complete, end-to-end basic
monitoring workflow on their own: confirm the lab is running, access the
frontend, ensure a host is monitored by an agent and a linked template, verify
its data, build a simple dashboard, create a trigger, deliberately cause a
problem, confirm it is detected, and recover it. This capstone ties together
everything from Modules 1–7.

## Topics

### The capstone scenario

This is a hands-on checkpoint, not new theory. You will prove the Day 1 skills by
running the full monitoring loop for the Online Shop's Linux host
(`zabbix-agent-basic`):

> **collect → store → visualize → detect → alert → recover**

You build a small dashboard, add a trigger that watches the monitoring agent, then
take the agent down and watch Zabbix detect the problem and clear it when the
agent returns. If you completed Modules 2–7, the host and data already exist —
here you assemble them into one workflow and add the missing detect/recover piece.

## Docker-Based Demonstration

The instructor runs the whole loop start to finish: shows the stack is up
(`docker compose -f compose_lab.yaml ps`), opens the frontend, confirms
`zabbix-agent-basic` is collecting in **Latest data**, builds a Problems
dashboard, creates the agent-down trigger, then runs `docker stop
zabbix-agent-basic` and narrates the problem appearing in **Monitoring →
Problems** and on the dashboard — followed by `docker start` and the recovery.

## Hands-On Lab

Steps 1–5 confirm the foundation you built earlier (do them quickly — if anything
is missing, the referenced module shows how). Steps 6–10 are the new capstone
work, each with an Expected Result.

1. **Start / confirm the Docker lab.**
   ```bash
   docker compose -f compose_lab.yaml ps
   ```
   **Expected:** all 15 containers are `running` (`zabbix-db`, `zabbix-web`
   healthy). If not, `docker compose -f compose_lab.yaml up -d` (Module 2).

2. **Access the frontend.** Open **<http://localhost:8080>** and sign in.
   **Expected:** the **Global view** dashboard loads.

3. **Confirm the Linux host is monitored.** Go to **Data collection → Hosts**.
   **Expected:** `zabbix-agent-basic` is listed with a green **ZBX** and an agent
   interface. (If it is missing, add it per Module 5.)

4. **Confirm the Linux template is linked.** On that host's row, check the
   **Templates** column.
   **Expected:** *Linux by Zabbix agent* is linked (≈150 items).

5. **Verify latest data.** Go to **Monitoring → Latest data**, filter to
   `zabbix-agent-basic`.
   **Expected:** live metrics (CPU, memory, filesystems) with recent **Last
   check** times.

6. **Create a simple dashboard.** Go to **Dashboards → All dashboards → Create
   dashboard**, name it `Day 1 Lab — Online Shop Health`, and add a **Problems**
   widget (set its **Host groups** filter to *Linux Servers* so it shows only your
   lab hosts). Optionally add **Host availability** and **Problems by severity**
   widgets. **Save changes.**
   **Expected:** an all-clear dashboard — the Problems widget shows "No data
   found" while everything is healthy, and Host availability shows your hosts
   available.

   ![The Day 1 capstone dashboard, all hosts healthy](assets/module-08/01-dashboard-healthy.png)

7. **Create a simple trigger.** Go to **Data collection → Hosts**, click
   **Triggers** on the `zabbix-agent-basic` row, then **Create trigger**:
   - **Name:** `Lab: monitoring agent on {HOST.NAME} is down`
   - **Severity:** **High**
   - **Expression:** `nodata(/zabbix-agent-basic/agent.ping,2m)=1`

   Click **Add**.
   **Expected:** the trigger is saved and enabled. The expression reads "if
   `agent.ping` has reported no data for 2 minutes, this is a problem" — exactly
   what happens when the agent stops. *(The `{HOST.NAME}` macro fills in the host
   name in problem text.)*

   ![The trigger form — 7.x expression and High severity](assets/module-08/02-trigger-form.png)

8. **Simulate a problem by stopping the agent.**
   ```bash
   docker stop zabbix-agent-basic
   ```
   **Expected:** the command returns immediately. The agent is now down, so it
   stops answering — `agent.ping` will go stale within ~2 minutes.

9. **Confirm the problem appears.** Watch **Monitoring → Problems** (filter Host
   groups to *Linux Servers*). After up to ~2 minutes:
   **Expected:** a **High** problem appears — *Lab: monitoring agent on
   zabbix-agent-basic is down* — with status **PROBLEM** and a growing Duration.
   Your dashboard's Problems widget shows it too, and Host availability flips the
   host to **Not available**.

   ![The problem in Monitoring → Problems](assets/module-08/03-problem-firing.png)

   ![The same problem live on your dashboard](assets/module-08/04-dashboard-problem.png)

10. **Recover by restarting the agent.**
    ```bash
    docker start zabbix-agent-basic
    ```
    **Expected:** within ~1–2 minutes `agent.ping` resumes, the `nodata`
    condition clears, and the trigger returns to OK — the problem leaves the
    Problems list (or shows as **RESOLVED**) and your dashboard goes all-clear
    again. You have completed the full monitoring loop.

## Expected Outcome

Participants have independently run a complete monitoring workflow: a host
collected and stored data, a dashboard visualized it, a trigger detected a
deliberately-induced failure, the problem surfaced in Problems and on the
dashboard, and recovery cleared it automatically. This is the core operational
loop every later module builds on.

## Instructor Notes

- **Lab vs production.** The loop is identical in production; only the trigger of
  the failure differs (a real host crash, a network cut) and recovery is rarely a
  `docker start`. The detect → alert → recover mechanics are exactly these.
- **Two agent-down triggers may fire.** The *Linux by Zabbix agent* template
  already ships a "Zabbix agent is not available" trigger, so stopping the agent
  can raise both it and the student's custom trigger. That is realistic
  "defense in depth" — point it out rather than treat it as a mistake; it also
  shows why you check whether a template already covers something (Module 18)
  before writing your own.
- **The built-in "Zabbix server" host shows a permanent agent-down problem.** Its
  agent interface points at `127.0.0.1` inside the server container (no agent
  there), so it always reads unavailable. That is why step 9 filters Problems to
  *Linux Servers* — to isolate the problem you caused. Mention it so students do
  not chase it.
- **`nodata` timing.** The 2-minute window plus the 1-minute `agent.ping` interval
  means the problem appears 1–2 minutes after the stop, not instantly. Use the
  wait to explain that triggers evaluate over time, not on a single sample.
- **`zabbix_get` for instant feedback.** While waiting, `docker exec zabbix-server
  zabbix_get -s zabbix-agent-basic -k agent.ping` fails immediately when the agent
  is down and returns `1` the moment it is back — faster than the UI.
- **Reset.** Ensure everyone runs `docker start zabbix-agent-basic` and sees
  recovery before Day 2; a left-stopped agent will look like a fault later.
- **Timing (~45 min).** ~10 min steps 1–5 (recap/verify), ~10 min dashboard,
  ~10 min trigger, ~10 min simulate + confirm + recover, ~5 min discussion.

## Lab-State Delta

Added in Module 8 (kept as Day 1 capstone artifacts):

- **Trigger:** `Lab: monitoring agent on {HOST.NAME} is down` (triggerid `32831`)
  on `zabbix-agent-basic` (10780) — expression
  `nodata(/zabbix-agent-basic/agent.ping,2m)=1`, severity **High**.
- **Dashboard:** `Day 1 Lab — Online Shop Health` (dashboardid `408`) — widgets:
  Problems (filtered to *Linux Servers*), Host availability, Problems by severity.
- **Verified the problem lifecycle:** stopping `zabbix-agent-basic` raised the
  trigger (PROBLEM, High) within ~80 s; restarting it cleared the problem
  automatically. Agent left **running**. Screenshots in
  `content/day-1/assets/module-08/`.
