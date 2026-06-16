# Module 32: Practical Lab — Day 4

## Learning Objectives

By the end of this module participants can **operate and troubleshoot** the
monitored Online Shop end to end: confirm the Day-4 administration, security,
alerting, and business-monitoring setup is in place, build a **Business SLA
Dashboard** that presents it to leadership, and **diagnose and fix three injected
failures** — documenting findings and fixes like an on-call engineer.

## Topics

### What Day 4 built — now run it

Every day so far has added another stack of capabilities to the Online Shop's
monitoring platform, and Day 4 is where that platform stopped being a collection
of features and became something you *operate*. Look back at what you built this
week. You gave it **users, roles, and permissions** so different people see
different things (Module 25). You **hardened, audited, and maintained** it so it
behaves like a system someone is responsible for (Module 26). You wired up **email
alerting with escalation** so a problem reaches a human (Module 27). You modeled
the business itself as a **service tree with an SLA** so leadership has a number to
care about (Module 28). You learned to **import and export** configuration so the
work is portable and version-controllable (Module 29), to **tune performance** so
it stays fast under load (Module 30), and to follow a **structured troubleshooting
method** when something goes wrong (Module 31). Each of those was taught on its
own. This practical lab is where they stop being separate lessons and become a
single skill — because the actual job of running Zabbix is doing all of them at
once: administer, secure, alert, present, and fix.

Concretely, the lab has three parts, and they mirror the three things an operator
of the Online Shop does every day. First you **operate** — you walk the platform
and confirm each Day-4 piece is genuinely in place and working, not just
configured. Then you **present** — you build a business dashboard so that the
people who fund the shop can see its health without reading a single trigger.
Finally you **troubleshoot** — three failures get injected into the running
system, and you diagnose each, fix it, and document what you found, exactly as you
would during an on-call shift.

### Presenting monitoring to the business

There is a translation problem at the heart of operations work, and it is worth
naming because Day 4 is where you finally solve it. Engineers and managers do not
read the same things. An engineer looks at an item graph and reads a story in the
line — the CPU ramp, the response-time spike, the queue that won't drain. A
manager looks at that same graph and sees noise. What a manager needs is a far
simpler answer: *is the Online Shop up, and are we keeping the promise we made to
customers?* That promise — the **service-level agreement**, or SLA — is the
contract that says, for example, the shop will be available 99.5% of the time.

A **Business SLA Dashboard** is how you answer that question on one screen. It uses
the very same dashboard-building technique you learned back in Module 12, but
points it at business data instead of raw items. On a single page it puts the
**SLA report** (am I hitting 99.5%?), the Online Shop's current **problems**, and a
**severity overview** — so leadership can glance at it and know the answer without
ever touching a trigger or learning what an item key is. We build this dashboard
in Part B, and it is a real deliverable: it carries forward into the final project
as the executive view of the shop.

![The Business SLA Dashboard: SLA report, problems, and severity overview](assets/module-32/01-business-dashboard.png)

### Diagnosing injected failures

Here is the uncomfortable truth that separates a lab from real operations: in
production, things break in ways you did not cause and cannot predict. A colleague
flips a setting, a secret expires, a network blip swallows a check. You will not
have written the failure, so you cannot just remember the fix — you have to *find*
it. This drill rehearses exactly that. The instructor injects **three failures
across the Day-4 domains**, and your job is to find and fix each one using the
Module 31 method: *symptom → layer → test → fix → verify*. You start from what you
can observe, narrow to the layer at fault, test a hypothesis, apply the fix, and
confirm recovery.

And then — this is the part beginners skip and operators never do — you **write it
down**. The discipline of documenting each finding is what turns a lucky fix into a
repeatable runbook. "I clicked around and it works now" helps nobody the next time.
A written record of *symptom, layer, root cause, fix, and how you verified it* is
something another engineer can follow at 3 a.m. without you on the phone.

## Docker-Based Demonstration

The instructor confirms the Day-4 platform (users, alerting, services, SLA, exported
template), builds the Business SLA Dashboard, then injects three failures —
**disable the alert action**, **deny the viewer's host-group permission**, and
**break the SNMP community** — and walks the diagnosis and fix of each.

## Hands-On Lab

### Part A — Operate: verify the platform

Before you can present or troubleshoot, you confirm the foundation is solid. Each
step below revisits one Day-4 module and checks not that it was *configured* but
that it actually *works* — which are different things, as Part C will make
painfully clear.

1. **Users and permissions (Module 25).** Confirm `shop.viewer` exists with the
   `Online Shop Viewer` role and the `Online Shop Viewers` group (Read on **Web
   Services**). Log in as the viewer.
   **Expected:** a trimmed menu and only the Web Services hosts.

2. **Maintenance (Module 26).** Confirm you can create a maintenance window for a
   host and that it suppresses its problems while active (remove it afterward).
   **Expected:** the host shows the maintenance (wrench) icon.

3. **Email alerting (Module 27).** Confirm the `Online Shop problem notifications`
   action is **enabled**, the Email (Mailpit) media type has message templates, and
   Admin has email media.
   **Expected:** a problem on a Web Services host produces an email in Mailpit
   (http://localhost:8025).

4. **Business service tree + SLA (Module 28).** Confirm the `Online Shop` service
   tree (Web Frontend, API Service, Database, Notification) and the `Online Shop SLA`
   (99.5%, enabled).
   **Expected:** the services reflect their hosts; the SLA reports an SLI.

5. **Exported template (Module 29).** Confirm
   `content/lab/templates/online-shop-api-by-http.yaml` exists and re-imports cleanly.
   **Expected:** import reports "No changes" (already in sync).

### Part B — Present: build the Business SLA Dashboard

With the platform verified, you turn its data into something a non-engineer can
read. This single step assembles the executive view of the Online Shop — the same
dashboard skill from Module 12, now aimed at the SLA and the shop's problems rather
than at raw metrics.

6. **Create the dashboard.** **Dashboards → Create dashboard**, name `Business SLA
   Dashboard`. Add widgets:
   - **SLA report** — SLA `Online Shop SLA`.
   - **Problems** — host group `Web Services`.
   - **Problems by severity** — host group `Docker Lab`.
   - a **Clock**.

   **Expected:** one business-facing page showing SLA attainment per service and
   current Online Shop problems.

### Part C — Troubleshoot: diagnose three injected failures

Now the platform breaks. The three failures below are chosen deliberately to land
in three different Day-4 domains — alerting, security, and SNMP monitoring — so you
cannot solve all three with one tool or one habit. Each also has a *silent* symptom:
problems still appear, the UI still loads, the host still exists, so nothing
screams the answer at you. That is the point. The diagnosis is the lesson.

The instructor injects three failures. For each, find the cause, fix it, and
**document** the finding — then verify recovery.

7. **Failure 1 — "alerts stopped arriving."** Problems still appear in *Monitoring →
   Problems*, but no email reaches Mailpit.
   **Diagnose:** walk the alerting chain (Module 27). **Alerts → Actions → Trigger
   actions** shows `Online Shop problem notifications` is **Disabled**.
   **Fix:** enable the action. **Verify:** the next problem emails again.

   ![Finding 1: the alert action is disabled](assets/module-32/02-failure-alerting.png)

8. **Failure 2 — "the viewer can't see anything."** `shop.viewer` logs in but
   **Monitoring → Hosts** is empty.
   **Diagnose:** capability vs visibility (Module 25). The `Online Shop Viewers`
   group's **Web Services** permission was changed to **Deny**.
   **Fix:** set it back to **Read**. **Verify:** the viewer sees demo-api and
   demo-nginx again.

   ![Finding 2: the viewer sees "No data found"](assets/module-32/03-failure-permission.png)

9. **Failure 3 — "the network device went silent."** `demo-snmp-device` SNMP items
   stopped updating.
   **Diagnose:** test the check (Modules 20/31). The item **Test → Get value** returns
   **`Timeout while connecting to "demo-snmp-device:161"`** — the **SNMP community**
   is wrong (`wrongcommunity`).
   **Fix:** set `{$SNMP_COMMUNITY}` back to `public`. **Verify:** SNMP items collect
   again.

   ![Finding 3: SNMP times out — wrong community](assets/module-32/04-failure-snmp.png)

10. **Document.** Record each finding in a short runbook table: *symptom → layer →
    root cause → fix → how verified*.
    **Expected:** a written record another engineer could follow.

## Expected Outcome

Participants can administer, secure, alert on, present, and troubleshoot a Zabbix
environment: a verified Day-4 platform, a business dashboard for non-engineers, and a
documented diagnosis-and-fix of three independent failures — the full operational
skill set of a Zabbix specialist.
