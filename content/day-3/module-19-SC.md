# Module 19: Monitoring Logs

## Learning Objectives

By the end of this module participants can monitor a log file with Zabbix:
create a **log item** (which requires an **active** agent), pull a log into Zabbix,
filter it with **regular expressions** to detect ERROR/WARNING lines, and fire a
**trigger** when matching messages appear — turning the Online Shop's application
log into alerts.

## Topics

### Why log monitoring

Up to now in this course you have measured the Online Shop mostly in numbers: CPU
percentages, response times, queue depths. Numbers are excellent at telling you
*that* something is wrong — the API got slow, the disk filled up — but they are
often silent about *why*. That second question is where logs come in. A metric is
a thermometer; a log is the patient describing exactly where it hurts.

The Online Shop's app (`demo-log-app`) writes lines like:

```text
2026-…  INFO    Request handled endpoint=/products status=200
2026-…  WARNING Slow request detected (latency=820ms) endpoint=/checkout
2026-…  ERROR   Database connection failed: timeout after 5000ms
```

Read those three lines and you can already see the value. The INFO line is the
shop working normally. The WARNING line is the same checkout flow you might
monitor with a response-time item, except now you also have the precise endpoint
and latency in plain text. And the ERROR line tells you, in a way no graph can,
*what* failed: a database timeout after five seconds. Log monitoring watches that
file, ships new lines to Zabbix, and lets you alert on the ones that matter — so
the story the application is already telling itself in its log ends up on the
same screen as everything else you watch.

### Log items require an active agent

Here is the first thing that trips people up, so it is worth understanding before
you touch a form. Every other item you have built so far could be a *passive*
check: the server reaches out, asks the agent a question, and the agent answers.
Logs do not work that way, and the reason is mechanical. A **log item** reads a
file line by line and remembers its position between checks — it needs to know
where it left off so it does not re-send lines it already sent or skip lines that
arrived in between. That bookkeeping lives on the agent's side, which means the
agent has to do the reading and *push* new lines to the server on its own
schedule. In Zabbix terms, a log item must be an **active** check; passive polling
cannot do it.

Because the agent now initiates the conversation, it has to know where to send the
data. That is why the agent needs **`ServerActive`** set and its **`Hostname`**
matching the host in Zabbix — the same active-agent wiring you met in Module 7.
If either is wrong, the lines simply never arrive. Finally, the item's **Type of
information** is **Log**, which tells Zabbix to store each entry as a timestamped
text record rather than a number.

![A log item: Zabbix agent (active), key log[...], type Log](assets/module-19/01-log-item-form.png)

### The log[] key and file path

The key is **`log[file,<regexp>,<encoding>,<maxlines>,<mode>,<output>,…]`**. The
first parameter is the only one you always need; the rest are filters and tuning
knobs you reach for as the situation demands:

- **file** — the path *as seen by the agent* (here `/var/log/demo/app.log`).
- **regexp** — only lines matching this are collected (omit for *all* lines).
- **mode** — `all` or `skip` (skip existing content and read only new lines).
- **output** — extract part of the line (capture groups) instead of the whole line.

The phrase "as seen by the agent" deserves emphasis, because it is the second
classic stumbling point. The path is not where the file lives on the Zabbix
server, and it is not where you see it from your laptop — it is the path the agent
process can open. In our lab the log volume is mounted into the agent at
`/var/log/demo` by `compose_lab.yaml`, so the agent can read it. On a real host
you would simply install the agent where the log already lives and point the key
at its real path.

### Detecting errors and warnings with regular expressions

A raw log stream is mostly noise — thousands of INFO lines for every one that
matters. The regexp parameter is how you turn that firehose into something useful:
it is the filter that decides which lines the item bothers to collect at all. To
make the distinction concrete, we run two items side by side:

- `log[/var/log/demo/app.log]` — **all** lines (the full stream, in Latest data).
- `log[/var/log/demo/app.log,WARNING]` — only **WARNING** lines.

The first gives you the complete record to read through when you are
investigating. The second is a pre-filtered view that contains nothing but the
warnings, so you can scan severity at a glance. You would add `log[…,ERROR]` to
isolate errors the same way. Regular expressions are not unique to this one
parameter, either — the same pattern language shows up in **triggers** (below) and
in **global regular expressions** (reusable named patterns under Administration),
so the time you spend getting comfortable with them here pays off across Zabbix.

![Log lines flowing into Zabbix — full stream and a WARNING-filtered item](assets/module-19/02-latest-data.png)

### Viewing the log in Zabbix

Once the lines are flowing, a quiet but genuinely useful thing has happened. A log
item's **history** is the captured lines with timestamps — which means you read
the application's log *inside* Zabbix, alongside its metrics, instead of SSH-ing to
the host. When the API response-time graph spikes, the application log that
explains the spike is one click away in the same interface, on the same timeline.
No jumping between a monitoring tool and a terminal, no hunting for which host to
log into.

![The application log streaming into Zabbix history](assets/module-19/03-log-history.png)

### Triggering from log messages

Reading logs in Zabbix is convenient, but the real goal is to stop reading them at
all and let Zabbix watch for you. To alert on errors, a trigger counts matching
lines over a window:

```text
count(/zabbix-agent-basic/log[/var/log/demo/app.log],30s,"regexp","ERROR")>0
```

Walk through what this says: over the last 30 seconds, count the lines in the
all-lines log item whose text matches the regular expression `ERROR`, and if that
count is greater than zero, raise a problem. So it fires when **any ERROR line**
arrived in the last 30 seconds and recovers when they age out of the window. That
window-and-count shape is deliberate — it gives you one problem for a burst of
errors rather than a separate alert per line. If your situation genuinely demands
the opposite, where every single occurrence needs its own problem, set the item's
*PROBLEM event generation* to **Multiple** (Module 10).

### Log preprocessing and dependent items

A log line is text, but text often hides a number you would rather track on a
graph. That WARNING line earlier carried `latency=820ms` — a perfectly good metric
trapped inside a sentence. Zabbix can free it. A log item can carry
**preprocessing** (regex extract, replace, JavaScript) and feed **dependent
items** — for example, a dependent item that extracts the latency number from a
WARNING line into a numeric metric, or counts errors per minute. The
master+dependent pattern from Module 9 works on logs too, so the same building
blocks you already know let you turn a noisy text stream into clean numbers
without collecting the data twice.

## Docker-Based Demonstration

`demo-log-app` is already writing INFO/WARNING/ERROR lines to a volume the agent
reads. The instructor creates the active log item, shows the lines arriving in
Latest data and history, adds the ERROR trigger, and waits for the next ERROR line
to raise the problem.

## Hands-On Lab

1. **Confirm the log source.** The `demo-log-app` container writes to a volume
   mounted into `zabbix-agent-basic` at `/var/log/demo/app.log`:
   ```bash
   docker exec zabbix-agent-basic tail -5 /var/log/demo/app.log
   ```
   **Expected:** recent INFO lines (and the occasional WARNING/ERROR). *(In our
   lab the mount is pre-wired in `compose_lab.yaml`; on a real host the agent runs
   where the log lives.)*

2. **Create the log item.** On host `zabbix-agent-basic`, create an item:
   - **Name:** `Online Shop app log`
   - **Type:** **`Zabbix agent (active)`**
   - **Key:** `log[/var/log/demo/app.log]`
   - **Type of information:** **`Log`**
   - **Update interval:** `5s`

   The active type is the non-negotiable part here — pick anything else and the
   item will collect nothing.
   **Add.**
   **Expected:** after the agent refreshes its active checks (up to ~2 min), the
   item starts collecting log lines.

3. **Add a regexp-filtered item.** Create another log item
   `log[/var/log/demo/app.log,WARNING]` (*WARNING lines*).
   **Expected:** this item collects **only** WARNING lines — the regexp is the
   filter.

4. **Watch the log in Zabbix.** Go to **Monitoring → Latest data**, filter to
   `zabbix-agent-basic`, find the log items, and click **History**. This is the
   moment the application's own log shows up inside the monitoring tool.
   **Expected:** the application's log lines, with timestamps, streaming into
   Zabbix — INFO/WARNING/ERROR as the app writes them.

5. **Create a trigger for ERROR messages.** On the all-lines log item, add a
   trigger:
   - **Name:** `ERROR in Online Shop app log`
   - **Severity:** **High**, **Allow manual close**
   - **Expression:**
     `count(/zabbix-agent-basic/log[/var/log/demo/app.log],30s,"regexp","ERROR")>0`

   **Expected:** the trigger is saved.

6. **View the problem.** `demo-log-app` logs an ERROR roughly once a minute. Watch
   **Monitoring → Problems**.
   **Expected:** within ~1 minute *ERROR in Online Shop app log* appears as a
   **High** problem, then recovers ~30 s after the error (when no new ERROR is in
   the window).

   ![The ERROR trigger firing from a log line](assets/module-19/04-error-problem.png)

## Expected Outcome

Participants can configure log monitoring with an active agent, read an
application log inside Zabbix, filter it with regular expressions to isolate
errors and warnings, and alert on log patterns — connecting "what the app says" to
Zabbix's problem workflow.
