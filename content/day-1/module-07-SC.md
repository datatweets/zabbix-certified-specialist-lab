# Module 7: Agent Configuration Best Practices

## Learning Objectives

By the end of this module you will be able to look at a given situation and make a
deliberate choice between passive and active agent mode rather than reaching for
whichever one you happened to use last. You will be able to name the agent's
performance-tuning parameters — the timeout, and the buffering that active checks
rely on — and say what each one actually does. You will understand, at a level
deep enough to debug it, why the agent's `Hostname` must match the host name in
Zabbix, and how to lock an agent down with the `Server` allow-list. You will set
up **auto-registration** so that new agents add *themselves* to Zabbix instead of
waiting for someone to click through a form. And, just as importantly, you will be
able to diagnose agent connectivity problems quickly by reading what the logs and
error messages are telling you.

## Topics

### From "make it work" to "make it right"

Modules 5 and 6 got agents reporting. That was the "make it work" stage, and it is
a real milestone — data flowing from a host into Zabbix for the first time always
feels like progress. This module is about the next stage, "make it right," and the
distinction matters more as the environment grows. Anyone can wire up a single
agent by hand; doing it *well* across many hosts is a different skill. So here we
focus on the decisions that keep a fleet manageable: when to pull versus push, how
to tune and secure an agent, how to onboard many hosts without clicking through a
form for each one, and how to troubleshoot fast when something stops reporting.

Keep the storyline in view. The Online Shop will not stay a handful of containers
forever — it will grow to many hosts, and the practices in this module are exactly
what keep that growth from turning into a maintenance burden.

### Active vs passive — when to use which

Both modes are agent-based — the same `zabbix_agentd` (or agent 2) process does
the work in either case. What differs is the *direction* of the conversation, a
point you first met in Modules 4 and 6: in passive mode the server reaches out and
pulls a value; in active mode the agent reaches out and pushes its values in. That
sounds like a small detail, but the choice has real consequences in practice, and
the table below is the cheat sheet you will come back to:

| Prefer **passive** when… | Prefer **active** when… |
|---|---|
| Few hosts, simple setup | Many hosts (offloads work from the server) |
| You want on-demand polling / `zabbix_get` testing | Agents are behind NAT/firewall (only outbound 10051 needed) |
| Server can reach every agent on 10050 | You need **log monitoring** (active-only) |
| | You want the agent to batch and push efficiently |

Read down the right-hand column and a pattern emerges: active mode wins whenever
scale, network boundaries, or efficiency are in play, which is most of the time in
the real world. That is why a common production pattern is **mostly active**
checks — they scale better and they are friendlier to firewalls, since the agent
only ever makes an outbound connection — with passive kept around for quick
diagnostics when you want to poke a single value by hand. For active checks to
work, the agent needs two things set correctly: its `ServerActive` must point at
the server, and its `Hostname` must match a host that exists in Zabbix. Hold on to
that second requirement; it comes back as the number-one gotcha a few sections
from now.

### Agent performance tuning

You will not touch most of the agent's settings, but a small handful are worth
knowing by name because they are the ones you reach for when a check is slow or
when active checks are not keeping up. In this lab they are set via environment
variables on the container; in production the very same parameters live in the
`.conf` file. The lab defaults are shown alongside each:

- **`Timeout`** (`ZBX_TIMEOUT`, default **3s**) — how long the agent waits for a
  check to return. Raise it only for genuinely slow checks. In 7.4 you can also
  **override timeout per item** (the item form's Timeout → Override) instead of
  raising it globally.
- **Active-check buffering** — the agent collects active values and sends them in
  batches:
  - **`BufferSize`** (`ZBX_BUFFERSIZE`, default **100**) — max values held before
    a forced send.
  - **`BufferSend`** (`ZBX_BUFFERSEND`, default **5s**) — max seconds a value
    waits before being sent.

  Buffering is why active checks scale: one connection ships many values.

The two buffer parameters work together as a "send when either is reached" rule:
whichever limit the agent hits first — a hundred values queued, or five seconds
elapsed — triggers a send. That is the mechanical reason active mode is so much
lighter on the network than passive: instead of one connection per value, the
agent opens a single connection and ships a batch.

### Hostname matching (the #1 active-check gotcha)

This is the single mistake that catches almost everyone the first time they set up
active checks, so it is worth understanding precisely rather than just memorizing
the rule. In passive mode the server already knows which host it is talking to —
it dialed the address itself. In active mode the agent is the one initiating
contact, so it has to announce *who it is*, and it does that by sending its
**`Hostname`**. The server then looks for a host with exactly that name to attach
the incoming data to. If the names do not match — even by a stray character — the
server has nowhere to put the data and simply discards it.

The agent log tells you this story plainly. Before the matching host existed,
agent 2 logged:

```text
no active checks on server [zabbix-server:10051]: host [zabbix-agent2-docker] not found
```

and after the matching host was created:

```text
active checks on server are active again
```

Those two lines are worth recognizing on sight: the first means "I announced
myself but Zabbix has no host by that name," and the second is the confirmation
that the name now lines up and data is flowing again.

### Allowed-server configuration and basic agent security

An agent sitting on a host is, by nature, a small service listening for
instructions, so a few guardrails come standard:

- **`Server`** is a passive-check **allow-list**: only listed addresses may pull
  values. Everything else is dropped. You can prove it — a `zabbix_get` from a
  host that is *not* `zabbix-server` is refused:

  ```text
  ZBX_NOTSUPPORTED: Received empty response from Zabbix Agent at
  [zabbix-agent-basic]. Assuming that agent dropped connection because of
  access permissions.
  ```

- **`AllowKey` / `DenyKey`** restrict which item keys an agent will run — used to
  forbid dangerous keys such as `system.run[...]` on hardened agents.
- **Encryption (PSK / certificate)** secures agent↔server traffic. It is *off* in
  this lab for simplicity; we cover it in depth in Module 26 (Security). For now,
  know that production agents are usually encrypted with at least a **PSK**.

Notice the layering here. The `Server` allow-list controls *who* may ask;
`AllowKey`/`DenyKey` control *what* they are allowed to ask for; and encryption
protects the traffic in transit. Each addresses a different threat, and a hardened
production agent typically uses all three. In the lab we keep encryption off so you
can see the mechanics clearly, but treat that as a teaching simplification rather
than a model to copy onto a real host.

### Auto-registration (onboarding agents automatically)

Now to the part that turns "make it work" into "make it scale." Clicking "Create
host" for hundreds of machines does not scale. **Active-agent auto-registration**
lets a new agent add *itself*:

1. The agent is configured with **`ServerActive`** and, optionally,
   **`HostMetadata`** (here via `ZBX_METADATA=lab-autoreg`) describing what it is.
2. An **Autoregistration action** (Alerts → Actions → Autoregistration actions)
   matches on that metadata and performs operations: **add host**, **add to host
   group**, **link template**.

The metadata is the clever piece. It is a free-form label the agent volunteers
about itself — "I am a lab machine," "I am a web server," "I belong to the finance
team" — and the action uses it to decide how to treat the newcomer. Send the right
metadata and the agent lands in the right group with the right template attached,
no human judgment required.

When the agent first connects, the server runs the action and the host appears —
fully templated — with no manual clicks. (Network discovery and richer
auto-registration are covered in Module 15; here we use it as an agent
best-practice.)

### Troubleshooting agent connectivity (a workflow)

When an agent goes quiet, resist the urge to guess. Work the problem in the same
order every time, because a consistent workflow finds the fault faster than a hunch
ever will:

1. **Isolate with `zabbix_get`** (passive). Value returned → agent healthy, look
   at Zabbix config. Error → network/agent side.
2. **Read the error:**
   - `connection error (POLLERR,POLLHUP)` → nothing listening / wrong port / agent
     down.
   - `getaddrinfo() failed for '<name>'` → DNS/name wrong.
   - `dropped connection because of access permissions` → caller not in `Server`.
3. **Read the agent log** (`docker logs <agent>`): active-check and connection
   messages explain hostname/server issues.

The logic of step 1 is what makes the whole workflow work: `zabbix_get` is a
direct, manual poll, so a clean value proves the agent and the network are fine and
points you back at the Zabbix configuration, while an error tells you the trouble
is on the network or agent side — and steps 2 and 3 then tell you *which* side, and
roughly where.

## Docker-Based Demonstration

The instructor contrasts the four states from the outline — passive check,
active check, wrong hostname, and wrong server address:

```bash
# passive check (server pulls) — works:
docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k agent.ping            # 1

# wrong server address (name doesn't resolve):
docker exec zabbix-server zabbix_get -s no-such-agent -k agent.ping
# getaddrinfo() failed for 'no-such-agent'

# allowed-server enforcement (caller not in Server allow-list):
docker exec zabbix-agent2-docker zabbix_get -s zabbix-agent-basic -k agent.ping
# ...dropped connection because of access permissions
```

Seeing all three side by side is the point: a healthy poll, a name that does not
resolve, and a caller that is rejected by the allow-list each produce a distinct,
recognizable signature. For an **active** check the instructor shows the agent log
line `active checks on server are active again`, and the wrong-hostname case via
the `host [...] not found` log line.

## Hands-On Lab

1. **Confirm a passive check** (baseline):
   ```bash
   docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k agent.ping   # 1
   ```
   **Expected:** `1`.

2. **Configure an active check.** On the `zabbix-agent2-docker` host, create an
   item with **Type = `Zabbix agent (active)`**:
   - **Name:** `API port reachable (active check)`
   - **Key:** `net.tcp.service[http,demo-api,5000]`
   - **Type of information:** `Numeric (unsigned)`, **interval** `1m`
   - **Tags:** `component=api`, `check=active`

   The disabled Test button here is not a bug — it is the active model showing
   through: because the agent owns the schedule and pushes the value, the server
   has nothing to poll on demand.

   **Expected:** the form has **no Host interface** field, and **Test/Execute now
   are greyed out** — active items are pushed by the agent, not polled. After a
   couple of minutes the value is **1** in Latest data.

   ![An active item — note no interface, Test disabled](assets/module-07/04-active-item.png)

   ![The active item's Tags tab](assets/module-07/06-active-item-tags.png)
   *Tags identify this as an active API check (`component: api`, `check: active`).*

3. **Set up auto-registration.**
   1. Go to **Alerts → Actions → Autoregistration actions → Create action**.

      ![Autoregistration actions list](assets/module-07/01-autoreg-action.png)

   2. **Name:** `Lab auto-registration`. Add a **Condition**: *Host metadata
      contains* `lab-autoreg`.

      ![The autoregistration action condition](assets/module-07/02-autoreg-action-detail.png)

   3. On the **Operations** tab, add: **Add host**, **Add to host groups** →
      `Docker Lab`, **Link templates** → `Linux by Zabbix agent`. Save.

      ![The three autoregistration operations](assets/module-07/05-autoreg-operations.png)

4. **Trigger auto-registration** with a brand-new agent that carries the matching
   metadata. This is the moment of truth: you start a container that has never been
   defined in Zabbix and watch it appear on its own.
   ```bash
   docker run -d --name auto-demo-agent --network zabbix-lab \
     -e ZBX_SERVER_HOST=zabbix-server \
     -e ZBX_HOSTNAME=auto-demo-agent \
     -e ZBX_METADATA=lab-autoreg \
     zabbix/zabbix-agent:alpine-7.4-latest
   ```
   **Expected:** within ~1–2 minutes a new host **`auto-demo-agent`** appears in
   **Data collection → Hosts**, already in *Docker Lab* and linked to *Linux by
   Zabbix agent* — created with **zero** manual configuration.

   ![The auto-registered host alongside the others](assets/module-07/03-hosts-autoreg.png)

5. **Simulate an unreachable agent and diagnose it.** Stopping the container is the
   most common real-world failure — a host that has gone away — so practice reading
   what Zabbix shows when it happens.
   ```bash
   docker stop auto-demo-agent
   docker exec zabbix-server zabbix_get -s auto-demo-agent -k agent.ping
   ```
   **Expected:** a connection error, and after a short delay the host's
   availability is no longer green (it goes unavailable). Use the workflow:
   `zabbix_get` errors → it's network/agent-side; the agent is stopped.

6. **Clean up the demo agent.**
   ```bash
   docker rm -f auto-demo-agent
   ```
   Then delete the `auto-demo-agent` host in Zabbix (Data collection → Hosts →
   select → Delete) — it was only to demonstrate the mechanism.
   **Expected:** the throwaway host and container are gone; your real hosts remain.

## Expected Outcome

You can now justify passive versus active for a given scenario instead of guessing,
tune the timeout and explain how active-check buffering keeps the data flowing
efficiently, and both explain and demonstrate the two requirements that trip people
up most — the `Hostname`-match rule and the `Server` allow-list. You can stand up
auto-registration so new agents onboard themselves, and you can follow a
repeatable workflow to troubleshoot agent connectivity when a host stops
reporting.
