# Module 13: Understanding Zabbix Queue

## Learning Objectives

By the end of this module you will be able to read the Zabbix **queue** with
confidence and explain, in plain operational terms, why some items fall behind
while others stay on time. You will be able to name the processes that actually
move data through the server — pollers, unreachable pollers, trappers, and
preprocessors — and say what each one does. You will learn to use the server's
**internal metrics** to judge whether your collection machinery has spare
capacity or is running flat out. And you will leave with a repeatable workflow
for investigating data-collection delays, so that when a queue starts to grow on
a real system you know exactly where to look first, second, and third.

## Topics

### What is the queue?

Up to this point in the course you have been adding things *to* watch — items,
triggers, hosts. The queue is the first tool that turns the lens around and lets
you watch the watcher. Think of it as the Online Shop's monitoring system taking
its own pulse.

The **queue** is the list of items that are **due to be collected but have not
been processed yet**. Open it at **Administration → Queue**. In a healthy system
the queue is **near zero** — everything is collected on time. A queue that grows,
especially into the **"More than 10 minutes"** column, means data is arriving late:
your graphs lag, and triggers evaluate on stale values. The queue is therefore an
early-warning gauge for the whole collection pipeline.

Why does lateness matter so much? Because everything else Zabbix does depends on
fresh data. A trigger that says "alert if the API response time exceeds two
seconds" is only as trustworthy as the last value it received. If that value is
ten minutes old, the trigger is effectively monitoring the past, and the Online
Shop could be on fire while your dashboard still shows green. A growing queue is
the earliest, cheapest signal that this kind of blind spot is forming.

![Queue overview — item types (rows) × how long they have waited (columns)](assets/module-13/01-queue-overview.png)

### How to read it

**Queue overview** is a matrix: each **row** is an item *type* (Zabbix agent,
Zabbix agent active, SNMP, HTTP agent, Zabbix internal, Calculated, …) and each
**column** is a delay bucket (5s, 10s, 30s, 1m, 5m, **>10m**). A number tells you
*how many* items of that type are *that* far behind. **Queue details** drills into
the individual delayed items — the exact item, host, and how long it is delayed —
so you can see *what* is stuck, not just *how much*.

The split between the two views maps neatly onto two different questions you will
ask in that order. Overview answers "is there a problem, and what *kind* of
collection is it affecting?" — the answer is a column of counts you can scan in a
second. Details answers "*which specific* checks are the offenders?" — the answer
is a list you can act on. You almost always read overview first to narrow the
search, then open details to find the culprits.

![Queue details — each delayed item, its delay, and host](assets/module-13/02-queue-details.png)

### Why items become delayed

A delayed item is always a symptom, and there is a short, finite list of root
causes behind it. Learning this list is most of the diagnostic battle, because
once you know what *can* go wrong you know what to check. Each cause below has a
distinct fingerprint in the queue, and each maps to a real situation you might
meet on the Online Shop.

- **Unreachable hosts.** When the server cannot reach a host, its checks cannot
  complete; while the server retries, those items sit in the queue.
- **Slow checks.** A check that takes longer than its interval (a slow HTTP
  endpoint, a heavy SQL query, an SNMP device that responds slowly) falls behind.
- **Not enough collectors.** Too few pollers for the number/frequency of items —
  the classic capacity problem.
- **A slow proxy.** A proxy that cannot keep up delays everything behind it
  (Module 14).
- **Preprocessing backlog.** If values arrive faster than preprocessing can
  transform them, the **preprocessing queue** grows.

Notice that these causes live at different layers: a network problem, a
slow-target problem, a server-capacity problem, a proxy problem, and a
data-transformation problem. That variety is exactly why the queue is such a
useful gauge — it catches trouble no matter which layer it starts in.

### The processes that move data

To understand the queue you have to understand the workers that drain it. Inside
the `zabbix-server` process there is not one monolithic "collector" but a team of
specialized worker types, each handling a different style of data movement. When
the queue backs up, it is one of these workers that has run short of capacity, so
knowing who they are tells you who to add more of.

- **Pollers** actively *pull* values (passive agent, SNMP, HTTP, …). In modern
  Zabbix many pollers are **asynchronous**, so one slow check no longer blocks the
  others — but limited poller capacity still bounds throughput.
- **Unreachable pollers** handle hosts that are currently unreachable, retrying
  them separately so they do not starve healthy hosts.
- **Trappers** receive *pushed* values (`zabbix_sender`, active agents) — there is
  no polling delay, but a trapper backlog can still form under very high volume.
- **Preprocessors** apply preprocessing steps (JSONPath, JavaScript, change-per-
  second from Module 9) before values are stored.

The pull-versus-push distinction is worth holding onto. Pollers reach *out* on a
schedule, which means a slow or dead target costs them time; that is why the
unreachable pollers exist as a separate pool, so a handful of dead hosts cannot
tie up the workers that healthy hosts depend on. Trappers, by contrast, sit and
wait for data to be pushed *in*, so they have no polling delay of their own — but
hand them a firehose and even they will form a backlog.

### Internal Zabbix metrics

The queue tells you *that* something is behind. The internal metrics tell you
*how hard* your server is working, which is what you need to decide whether to add
capacity or look elsewhere. Helpfully, Zabbix monitors itself the same way it
monitors everything else — through ordinary items on an ordinary host.

The server measures *itself*. The **Zabbix server** host carries internal
`zabbix[...]` items (from the *Zabbix server health* template) that quantify
capacity:

- `zabbix[process,<type>,avg,busy]` — how **busy** each collector/process is
  (e.g. agent poller, history syncer). Sustained high values mean that process is
  a bottleneck — add more of it.
- `zabbix[preprocessing_queue]` — items waiting for preprocessing.
- `zabbix[wcache,...]`, `zabbix[rcache,...]`, `zabbix[vcache,...]` — cache usage.
- `zabbix[requiredperformance]` — required new values per second.

These are the numbers you trend and alert on for performance (Module 30).

Read the `busy` metric like a thermometer for each worker pool. A poller sitting
at 5% busy has enormous headroom; one pinned near 100% for minutes on end is your
bottleneck, and the queue growing behind it is the direct consequence. This is
why the queue and the internal metrics are best read together: the queue shows
the symptom, the busy percentages show the cause.

![Internal metrics: per-process busy %, the quantitative health view](assets/module-13/03-internal-metrics.png)

### Unsupported items and delayed checks

**Unsupported** items (Module 9) are retried on a separate, slower schedule, so a
flood of them wastes collector time and can indirectly delay healthy items —
another reason to keep items supported.

This is the kind of second-order effect that surprises people. A broken item —
say, an Online Shop check pointing at a key the agent no longer understands — does
not just fail quietly; it keeps consuming a slice of collector time on every retry.
Multiply that by hundreds of unsupported items across a large estate and you have
a self-inflicted capacity drain that shows up as delays on *other*, perfectly
healthy checks. A tidy item set is a fast item set.

### Performance bottlenecks

A growing queue is a *symptom*; the cause is one of the above. The diagnosis is
always "**which** item type is delayed (queue overview) → **which** items (queue
details) → **why** (unreachable? slow? under-resourced?) → fix the cause."

Commit that chain to memory, because it is the entire method of the module
compressed into one sentence. You start wide (which type?), narrow to specifics
(which items?), reason about the root cause from the short list you learned above,
and only then act. Resist the temptation to jump straight to "add more pollers" —
that fixes a capacity problem but does nothing for a dead host or a broken item,
and you want your remedy to match the actual cause.

## Docker-Based Demonstration

The instructor opens **Administration → Queue** and shows the healthy near-zero
baseline, explains the matrix, then introduces a delay by adding an **unreachable
host** and watching it go unavailable. Finally the **internal metrics** in Latest
data show poller utilization — proving the lab has plenty of headroom (which is
*why* the queue stays empty).

## Hands-On Lab

In this lab you will see the queue in its healthy state, deliberately break
something to make the queue react, read what it tells you, confirm against the
internal metrics that the server has spare capacity, and then put everything back
the way you found it. Work the steps in order — the point is to watch cause and
effect, not just to land on a final screen.

1. **Open the queue screen.** Go to **Administration → Queue → Queue overview**.
   **Expected:** a matrix of item types and delay buckets, almost all **zero** —
   the healthy state. Note the **"More than 10 minutes"** column: anything there
   is a red flag.

2. **Look at queue details.** Switch to **Queue details**.
   **Expected:** the list of individual delayed items (likely *No data found* in
   our healthy lab) with columns *Scheduled check*, *Delayed by*, *Host*, *Name*.

3. **Create an unreachable host to cause delays.** In **Data collection → Hosts →
   Create host**, add `demo-unreachable` in *Docker Lab*, with an **Agent
   interface** to the IP `10.123.123.123` (an unroutable address) and link
   **Linux by Zabbix agent**. Save. Pointing the host at an address nothing will
   ever answer on is the cleanest way to simulate the "unreachable host" cause
   from the topics above, without touching anything real in the lab.
   **Expected:** the server tries to poll ~150 items it cannot reach; within
   ~1 minute the host's **Availability** turns red (ZBX) in the Hosts list.

   ![An unreachable host — the classic cause of delays](assets/module-13/04-unreachable-host.png)

4. **Observe the delayed items.** Re-open **Administration → Queue** straight after
   creating the host. The timing matters here — you want to look while the server
   is still trying, before it gives up on the host.
   **Expected:** briefly, the host's items appear in the queue under *Zabbix
   agent* while the unreachable poller retries them. *(In Zabbix 7.4, async
   pollers and the unavailable-host back-off keep this from snowballing — the
   spike is short-lived, and once the host is flagged unavailable its checks are
   suspended. A queue that **stays** high is the real warning sign.)*

5. **Review internal metrics.** In **Monitoring → Latest data**, filter Hosts to
   `Zabbix server` and Name to `Utilization of`. This is the other half of the
   diagnosis: it shows you how much of each worker pool the lab is actually using.
   **Expected:** the per-process busy percentages — agent poller, history syncer,
   preprocessing, etc. In our small lab these are tiny (well under 1%), which is
   exactly why the queue stays empty: lots of spare capacity.

6. **Fix the problem.** Delete the `demo-unreachable` host (Data collection →
   Hosts → select → Delete). Removing the cause is the last step of the workflow,
   and it returns the reference lab to the exact state you started from.
   **Expected:** the unreachable checks stop, and the queue returns to its
   near-zero baseline.

## Expected Outcome

You can open and read the Zabbix queue in both its overview and details forms, and
explain the team of server processes — pollers, unreachable pollers, trappers, and
preprocessors — that collect and preprocess your data. You can name the handful of
reasons items get delayed and recognize each one's fingerprint, use the server's
internal metrics to judge whether pollers and preprocessors have headroom to
spare, and follow a clear, repeatable workflow to investigate a collection delay
and fix it at the root rather than at the symptom.
