# Module 21: Web Monitoring

## Learning Objectives

By the end of this module participants can monitor a website the way a user
experiences it: build a **web scenario** with ordered **steps**, check
**availability** (status code + required string) and **performance** (response
time, download speed), alert when the site fails, and explain when to use a **web
scenario** versus an **HTTP agent** item.

## Topics

### Why web monitoring

Pinging a port tells you the web server process is up; it does **not** tell you the
**Online Shop** actually serves its pages. Web monitoring makes Zabbix act like a
visitor: it requests real URLs, follows a multi-step journey, checks that each
page returns the right **status code** and contains the right **content**, and
measures how long each step takes. That is *availability* and *performance* from
the customer's side — exactly what an SLA is written against (Module 28).

We monitor `demo-nginx`, the Online Shop's web frontend.

### Web scenarios vs. HTTP agent items

Zabbix has two ways to talk HTTP, and choosing right is half of this module:

- **HTTP agent item** (Module 18) — **one request → one value**. Perfect for a
  JSON API: fetch `/metrics`, store the body, extract numbers with JSONPath. It is
  an *item*, lives in Latest data, and is single-shot.
- **Web scenario** (this module) — an **ordered, multi-step user journey**. Open
  the home page, then log in, then load the dashboard — each a **step**. Zabbix
  measures every step, keeps a session (cookies) across them, and reports the
  scenario as **OK** or **which step failed**. It is built for *websites and
  availability*, not for scraping a single number.

Rule of thumb: **a number from an endpoint → HTTP agent; a page (or flow) a user
visits → web scenario.**

### Anatomy of a web scenario

A scenario lives on a host (here `demo-nginx`) under **Data collection → Hosts →
Web**. It has scenario-level settings and a list of **steps**:

- **Update interval** — how often the whole scenario runs (we use `30s`).
- **Attempts (retries)** — retry a failing step before declaring failure (`2`).
- **Agent / HTTP proxy / Authentication / SSL** — identity and transport options.

Each **step** is one HTTP request:

- **URL** — we use a macro `{$WEB.URL}/` so the address is set once per host.
- **Required status codes** — e.g. `200`; anything else fails the step.
- **Required string** — text that **must** appear in the response body
  (`Online Shop`); its absence fails the step even on a 200.
- **Post / Variables / Headers** — for forms, tokens, and carrying values between
  steps.

![The web scenario's two steps: URL, required string, status code](assets/module-21/01-web-scenario-steps.png)

### The items a scenario creates for you

You do **not** create web items by hand — saving the scenario auto-generates them
(query them via the API with `webitems:true`). For our scenario `Online Shop
Frontend`:

- `web.test.fail[Online Shop Frontend]` — **0 = all steps passed**, otherwise the
  number of the failed step. This is the availability signal.
- `web.test.error[Online Shop Frontend]` — the last failure message.
- `web.test.in[Online Shop Frontend,<step>,bps]` — download speed (per step + total).
- `web.test.time[Online Shop Frontend,<step>,resp]` — **response time** per step.
- `web.test.rspcode[Online Shop Frontend,<step>]` — the HTTP status code returned.

![The nine auto-created web items in Latest data](assets/module-21/03-web-items.png)

### Watching availability and performance

**Monitoring → Web** lists every scenario with its step count, last check, and a
green **OK** (or a red failed-step message). It is the at-a-glance website health
view.

![Monitoring → Web: the scenario reporting OK](assets/module-21/02-web-monitoring.png)

### Alerting on web problems

Because the scenario produces normal items, triggers work exactly as elsewhere
(Module 10), using the 7.x `/host/key` syntax:

```text
last(/demo-nginx/web.test.fail[Online Shop Frontend])>0
avg(/demo-nginx/web.test.time[Online Shop Frontend,Home page,resp],5m)>2
```

The first fires when **any step fails** (site unavailable); the second when the
home page is **consistently slow** (performance degraded) — two different SLA
breaches from one scenario.

### Configuring HTTP agents (the other half)

For completeness: the Online Shop's **API** is monitored with **HTTP agent**
items, built in Module 18 as the `Online Shop API by HTTP` template — one request
to `/metrics`, then JSONPath preprocessing into queue/response/orders metrics.
That is the right tool for an API returning JSON; the web scenario here is the
right tool for the **web frontend**. Together they cover both faces of the Online
Shop over HTTP.

## Docker-Based Demonstration

`demo-nginx` already serves the Online Shop frontend page. The instructor creates
a web scenario with two steps (home page + an API health check), shows it turning
**OK** in Monitoring → Web, points out the auto-created items, adds availability
and performance triggers, then **stops `demo-nginx`** to show the scenario report
the exact failed step and raise a problem — then starts it and watches it recover.

## Hands-On Lab

1. **Confirm the site serves its page.** From the server's vantage point:
   ```bash
   docker exec zabbix-server wget -qO- http://demo-nginx/ | grep -i "Online Shop"
   ```
   **Expected:** the line containing `<h1>Online Shop</h1>` — the content our
   scenario will require.

2. **Add a host macro for the URL.** On host `demo-nginx`
   (**Data collection → Hosts → demo-nginx → Macros**), add
   `{$WEB.URL}` = `http://demo-nginx`.
   **Expected:** the macro is saved; steps can now reference it.

3. **Create the web scenario.** On `demo-nginx`, open the **Web** tab →
   **Create web scenario**:
   - **Name:** `Online Shop Frontend`
   - **Update interval:** `30s`, **Attempts:** `2`

   Then add two **Steps**:

   | # | Name | URL | Required string | Status codes |
   | --- | --- | --- | --- | --- |
   | 1 | `Home page` | `{$WEB.URL}/` | `Online Shop` | `200` |
   | 2 | `Health check` | `http://demo-api:5000/health` | `ok` | `200` |

   **Add.**
   **Expected:** the scenario is created; Zabbix auto-generates its items.

4. **Watch it go OK.** Open **Monitoring → Web**, filter to `demo-nginx`.
   **Expected:** `Online Shop Frontend`, 2 steps, **Status OK** (green) within
   ~30 s.

5. **See the auto-created items.** Go to **Monitoring → Latest data**, filter to
   `demo-nginx`, name `Online Shop Frontend`.
   **Expected:** nine items — *Failed step* = `0`, *Response code* = `200`,
   *Response time* ≈ a few ms, *Download speed* for each step.

6. **Add the availability and performance triggers.** On `demo-nginx`:
   - `Online Shop frontend is unavailable` — **High** —
     `last(/demo-nginx/web.test.fail[Online Shop Frontend])>0`
   - `Online Shop frontend home page slow (>2s)` — **Warning** —
     `avg(/demo-nginx/web.test.time[Online Shop Frontend,Home page,resp],5m)>2`

   **Expected:** both triggers save; no problem yet (the site is healthy).

7. **Break it — simulate an outage.** Stop the web frontend:
   ```bash
   docker stop demo-nginx
   ```
   **Expected:** within ~30 s `web.test.fail` becomes `1`, and **Monitoring → Web**
   shows the red message
   **`Step "Home page" [1 of 2] failed: Could not resolve host: demo-nginx`** — the
   scenario tells you *which step* failed and *why*. **Monitoring → Problems** shows
   *Online Shop frontend is unavailable* (High).

   ![The scenario pinpoints the failed step](assets/module-21/04-web-down.png)

8. **Recover.** Bring the site back:
   ```bash
   docker start demo-nginx
   ```
   **Expected:** within ~30 s the scenario returns to **OK**, `web.test.fail` is
   `0` again, and the problem resolves automatically.

## Expected Outcome

Participants have a working web scenario monitoring the Online Shop frontend:
availability (status code + required string), per-step performance, alerting on
failure and slowness, and the troubleshooting view that names the failed step.
They can also articulate when to reach for a web scenario versus an HTTP agent item.

## Instructor Notes

- **Lab vs production.** We watch a local Nginx container; in production you point
  the same scenario at a public URL (often through a **proxy**, Module 14, so the
  check runs from the user's region). The scenario mechanics are identical — only
  the URL and network path change. Use **HTTPS** and verify the certificate in
  production (SSL fields on the scenario).
- **Required string is the real test.** A site can return `200 OK` and still be
  broken (blank page, error template, "maintenance"). The **required string** is
  what proves the *right* page loaded — always set it. Our outage demo failed on
  resolution, but a wrong-content failure looks the same in Monitoring → Web.
- **Web scenario vs HTTP agent — say it twice.** Students conflate them. Page/flow
  + availability → **web scenario**; single JSON value → **HTTP agent** (Module 18).
- **Steps keep a session.** Cookies and variables carry across steps, which is how
  you script *log in → do something → log out*. That is the feature an HTTP agent
  item cannot give you.
- **You don't make the items — the scenario does.** A common "where are my items?"
  moment: web items are hidden unless you ask for them (`webitems:true` in the API;
  they appear normally in Latest data and Monitoring → Web). Don't try to create
  `web.test.*` by hand.
- **Mind the load.** Each step is a real HTTP request on every interval. A 10 s
  interval on a heavy multi-step scenario across many hosts adds up — size the
  interval to the SLA, not to vanity.
- **Timing (~45 min).** ~10 min why + web-scenario-vs-HTTP-agent, ~15 min build
  scenario + steps + see OK + items, ~10 min triggers, ~10 min break/troubleshoot/
  recover + production framing.

## Lab-State Delta

Added in Module 21 (kept — frontend web monitoring is permanent):

- **Host macro on `demo-nginx` (10785):** `{$WEB.URL}` = `http://demo-nginx`.
- **Web scenario:** `Online Shop Frontend` (httptestid `1`), update `30s`,
  attempts `2`, 2 steps — *Home page* (`{$WEB.URL}/`, required `Online Shop`, 200)
  and *Health check* (`http://demo-api:5000/health`, required `ok`, 200). Auto-
  creates 9 `web.test.*` items.
- **Triggers:** `Online Shop frontend is unavailable` (triggerid `33040`,
  `last(/demo-nginx/web.test.fail[Online Shop Frontend])>0`, High) and
  `Online Shop frontend home page slow (>2s)` (triggerid `33041`,
  `avg(/demo-nginx/web.test.time[Online Shop Frontend,Home page,resp],5m)>2`,
  Warning).
- Demonstrated then reverted: `docker stop demo-nginx` → scenario reported
  *Step "Home page" [1 of 2] failed* and raised the problem → `docker start
  demo-nginx` → recovered (fail back to 0). Screenshots in
  `content/day-3/assets/module-21/`.
