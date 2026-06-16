# Module 16: Practical Lab — Day 2

## Learning Objectives

By the end of this capstone participants can assemble everything from Day 2 into a
realistic monitoring setup for the Online Shop's application tier: monitor the API
with HTTP agent items and JSON extraction, alert on it with triggers, visualise it
on a consolidated dashboard, collect a host through a proxy, onboard hosts with
discovery/auto-registration, and **troubleshoot a broken item end to end**.

## Lab Scenario

Up to now, each Day 2 module has taught one capability in its own session, with the
instructor close at hand and the next step always spelled out for you. Real
operations work is not like that. On a real team, the skills arrive separately but
have to be used *together*, on your own, the moment something breaks. This module
is where the two worlds meet.

Day 2 added the application layer to the Online Shop monitoring. This lab is the
**checkpoint**: you confirm each capability works together and produce a single
dashboard a team could actually watch — then prove you can diagnose and fix a
broken check, the real test of an operator.

Notice the shift in emphasis. The first several modules of the day were about
*building*; this one is about *operating*. A monitoring platform that only its
author can use is not finished — it has to be legible to whoever is on call at 3
a.m., and the person on call has to be able to look at a red item and reason their
way back to the cause. That second skill, troubleshooting, is the one this lab
exists to exercise, and it is the single hardest thing to fake.

Everything you need was built in Modules 9–15; here you tie it together:

| Capstone task | Built in | Verify |
|---|---|---|
| Monitor an API container | Module 9 | `demo-api` host collecting |
| HTTP agent items + JSON extraction | Module 9 | master `api.metrics.raw` + dependent items |
| Create triggers | Module 10 | API unreachable / queue / failed-payments |
| Create dashboards | Module 12 | build *Web and API Monitoring* |
| Add a proxy + monitor a host through it | Module 14 | `demo-nginx` via `zabbix-proxy-branch` |
| Discovery / auto-registration | Module 15 | discovery rule + autoreg action |
| **Troubleshoot one broken item** | this lab | diagnose + fix the health check |

Read that table as a map of Day 2 in miniature. Each row is a technique you have
already practiced once in isolation; the "Verify" column tells you what proof of it
should already be sitting in your lab. Nothing in the table is new — and that is the
point. A capstone tests whether the earlier lessons stuck, not whether you can
absorb yet another feature in the final hour.

## Docker-Based Demonstration

Before you work through the steps yourself, the instructor walks the whole picture
once, so you can see how the separate pieces of Day 2 form a single operating
environment rather than a pile of unrelated configuration.

The instructor walks the assembled picture: `demo-api`'s JSON metrics and triggers,
`demo-nginx` collected through the proxy, the discovery/auto-registration paths,
then builds the consolidated **Web and API Monitoring** dashboard and finishes with
a live troubleshooting exercise on a deliberately broken HTTP item.

That last demonstration is the one to watch closely. It is easy to follow a recipe
that ends in success; it is harder to watch someone meet a failure and reason out
of it. The broken-item walkthrough is your model for the loop you will perform in
section C.

## Hands-On Lab

The lab is organized into four movements: first you confirm that everything Day 2
built is still working, then you fold it into one dashboard, then you repair a
deliberately broken check, and finally you present what you have. Work through them
in order — each leans on the one before.

### A. Confirm the Day 2 monitoring (Modules 9–15)

Start by taking inventory. Before you build anything new or fix anything broken,
you want to be sure the foundation from Modules 9–15 is intact, because a missing
piece here would quietly undermine everything downstream. Each of the next four
steps is a quick "is it still there?" check against one of the day's capabilities.

1. **API monitoring + JSON extraction.** In **Monitoring → Latest data**, filter to
   `demo-api`.
   **Expected:** the master `Online Shop API: raw metrics (JSON)` plus the
   dependent items extracted from it (orders, queue length, response time,
   orders/second) — one HTTP request feeding many metrics.

2. **Triggers.** In **Data collection → Hosts → Triggers** on `demo-api`.
   **Expected:** your Module 10 triggers exist — *API is unreachable* (High),
   *queue is backing up* (Warning, with recovery expression + dependency),
   *failed-payment rate is high* (Average).

3. **A host through the proxy.** In **Administration → Proxies**.
   **Expected:** `zabbix-proxy-branch` is **Online** and shows host `demo-nginx`,
   which it monitors on the server's behalf.

4. **Discovery / auto-registration.** In **Data collection → Discovery** and
   **Alerts → Actions**.
   **Expected:** the `Docker network — Zabbix agents` discovery rule and the
   discovery/auto-registration actions are configured (the onboarding automation
   from Module 15).

### B. Build the consolidated dashboard

With the data confirmed to be flowing, the next job is to make it watchable. Raw
items in *Latest data* are fine for spot checks, but no one runs operations by
scrolling a list. A dashboard answers a single operational question at a glance —
*is the Online Shop's application tier healthy right now?* — and that is what you
assemble here, pulling the day's most important signals onto one screen.

5. **Create the *Web and API Monitoring* dashboard.** Combine the day's data into
   one operational view: **Item value** widgets for *API orders*, *API response
   time*, and *Nginx active connections (via proxy)*; a **Host availability**
   widget; a **Problems** widget filtered to *Web Services*; and an **SVG Graph**
   of the API *response time* and *queue length*.
   **Expected:** a single screen showing the Online Shop's application health.

   ![The consolidated Web and API Monitoring dashboard](assets/module-16/01-dashboard.png)

### C. Troubleshoot a broken item

Here is the heart of the lab. A dashboard tells you *that* something is wrong; it
does not tell you *why*. Closing that gap — turning a red "Not supported" indicator
into a root cause and then a fix — is the skill that separates an operator from a
spectator. A deliberately broken item has been planted on `demo-api` so you can
practice the full diagnostic loop on a safe, known failure.

6. **Reproduce the failure.** A new item, `API: health endpoint` (HTTP agent), has
   been added to `demo-api` but shows **Not supported**. Open it and click
   **Test → Get value and test**.
   **Expected:** a red error — `Response code "404" did not match any of the
   required status codes "200"` — and the 404 page body. The check is hitting the
   wrong URL.

   ![Diagnosing the broken item: a 404 in the Test dialog](assets/module-16/02-broken-item-test.png)

   The **Test** button is your most reliable diagnostic tool because it asks Zabbix
   to run the check *right now* and show you the raw result, rather than leaving you
   to guess from a stale "Not supported" label. Read the error literally: a 404 is
   the web server telling you the path does not exist, which points at the URL, not
   at the network or the item type.

7. **Fix it.** The URL is `http://demo-api:5000/healthz` — a typo. Confirm the real
   endpoint (`http://demo-api:5000/health` returns `{"status":"ok",…}`), correct
   the item's **URL**, and **Update**.
   **Expected:** within ~30 s the item leaves *Not supported* and collects the
   health JSON. You followed the troubleshooting loop: **read the error → check the
   source → fix → confirm recovery.**

   ![The item recovered after fixing the URL](assets/module-16/03-fixed-item.png)

   That four-step loop is worth memorizing, because it is the same one you will use
   on a misbehaving agent, a stuck queue, or any other check that goes dark. The
   discipline is to confirm recovery rather than assume it — an item that *should*
   work and one that *does* work are not the same thing until you have seen fresh
   data arrive.

### D. Present the result

The final movement asks you to explain your own work out loud. Being able to narrate
what each widget means, and how you reached the fix, is the proof that you
understand the environment rather than merely having clicked through it — and it is
exactly the kind of handoff a real team expects when you go off-shift.

8. **Show the monitored environment.** Open **Data collection → Hosts**.
   **Expected:** the Day 2 environment — `demo-api` (HTTP/JSON), `demo-nginx`
   (via the proxy), and the agent hosts — all monitored. Walk your dashboard and
   explain what each widget tells an operator, where a problem would show, and how
   you diagnosed the broken item.

   ![The Day 2 monitored environment](assets/module-16/04-hosts-overview.png)

## Expected Outcome

Participants have a working, realistic application-monitoring setup for the Online
Shop: JSON-based API metrics with dependent items, meaningful triggers, a
consolidated dashboard, a host collected through a proxy, discovery/auto-
registration in place, and the demonstrated ability to diagnose and fix a broken
check — the core competencies of Day 2.
