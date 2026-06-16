# Module 6: Basic Zabbix Agent Setup

## Learning Objectives

By the end of this module you will be able to explain, without hand-waving, the
difference between the classic Zabbix agent and Zabbix agent 2 — not just that
one is written in C and the other in Go, but what that difference buys you in
practice. You will understand the handful of configuration parameters that govern
every agent on every platform (`Server`, `ServerActive`, `Hostname`) and exactly
how passive and active checks lean on each of them. You will add the agent 2 host
to the lab and watch its built-in Docker plugin answer questions the classic agent
cannot. And — perhaps most usefully of all — you will learn to read an agent's log
and diagnose a broken connection from the error message alone, which is the skill
that separates someone who *runs* Zabbix from someone who merely installed it.

## Topics

### Why two agents — and why it matters for the Online Shop

In Module 5 you monitored `zabbix-agent-basic` with the **classic Zabbix agent** —
the C-based agent that has shipped with Zabbix for years. The lab also runs a
second monitored host, `zabbix-agent2-docker`, and it uses a different program
entirely: **Zabbix agent 2**, the newer Go-based agent. Both are legitimate
choices, and a real part of operating Zabbix is knowing which one to deploy where,
how to configure it, and how to troubleshoot it when it goes quiet.

This matters for us because the agent is the workhorse of the whole platform. Most
of the Online Shop's hosts — the API server, the host running the database, the
machines producing logs — will eventually report in through an agent. Get
comfortable with agents now, while you have exactly two of them and can compare
them side by side, and every later module that adds a monitored host becomes
routine instead of mysterious.

### Zabbix agent vs Zabbix agent 2

Start from what the two agents have in common, because it is most of the picture.
They speak the same wire protocol to the server, and they serve the same set of
built-in item keys. For ordinary operating-system metrics — CPU, memory,
filesystems, network counters — they are interchangeable; a host monitored by one
collects the same data as a host monitored by the other. The differences are about
how the agent is built and what it can be extended to do:

| | Zabbix agent (classic) | Zabbix agent 2 |
|---|---|---|
| Language | C | Go |
| Plugins | none (built-in keys only) | **built-in plugins** (Docker, PostgreSQL, MySQL, Redis, …) |
| Connections | one per check | can **multiplex / keep persistent** connections |
| Extending | UserParameters / loadable modules | UserParameters **and** Go plugins |
| Footprint | smallest | slightly larger, more capable |

In our lab both agents are the same release, and you can prove it directly. The
`agent.version` item key asks an agent to report its own version string, so
querying each one is a quick way to confirm they are on equal footing:

```bash
docker exec zabbix-server zabbix_get -s zabbix-agent-basic   -k agent.version   # 7.4.11
docker exec zabbix-server zabbix_get -s zabbix-agent2-docker -k agent.version   # 7.4.11
```

The single feature that justifies agent 2's existence for most teams is the bottom
row of that table made concrete: **plugins**. A plugin is a piece of monitoring
logic compiled into the agent that knows how to talk to a specific kind of
software. Because `zabbix-agent2-docker` runs with the Docker socket mounted into
it, its built-in Docker plugin can interrogate the Docker engine and answer item
keys that the classic agent has never heard of:

```bash
docker exec zabbix-server zabbix_get -s zabbix-agent2-docker -k docker.ping   # 1
docker exec zabbix-server zabbix_get -s zabbix-agent2-docker -k docker.info
# {"ID":"...","Containers":19,"ContainersRunning":16,"Images":32,...}

# The classic agent has no Docker plugin:
docker exec zabbix-server zabbix_get -s zabbix-agent-basic -k docker.ping
# ZBX_NOTSUPPORTED: Unsupported item key.
```

That last line is worth pausing on: `ZBX_NOTSUPPORTED: Unsupported item key` is
not a network failure or a typo. It is the classic agent correctly reporting that
it has no idea what `docker.ping` means, because it ships with no Docker plugin.
Agent 2 returns `1` for the same key. That is the whole argument for agent 2 in a
single contrast.

### Agent configuration: the parameters that matter

However an agent is deployed, its behavior is driven by one small text file —
`zabbix_agentd.conf` for the classic agent, `zabbix_agent2.conf` for agent 2. The
file has many possible settings, but only a handful control whether an agent works
at all, and you should know each one by heart:

- **`Server`** — the IP(s)/name(s) allowed to connect for **passive** checks
  (an allow-list). If the poller's address is not here, the agent refuses it.
- **`ServerActive`** — where the agent connects to fetch and submit **active**
  checks.
- **`Hostname`** — the name the agent uses for active checks; it **must exactly
  match the host name in Zabbix** or active checks fail.
- **`ListenPort`** — the passive port (default **10050**).

Notice the pattern: the first two parameters draw the line between *passive* and
*active* checks (the next section unpacks that), and `Hostname` is the identity the
agent claims when it pushes data. Get `Hostname` wrong and the server quietly
ignores everything the agent sends, which is one of the most common and most
confusing failures in all of Zabbix.

> **In this Docker lab you don't edit files** — the images take environment
> variables that generate the config: `ZBX_SERVER_HOST` sets both `Server` and
> `ServerActive` (here, `zabbix-server`), and `ZBX_HOSTNAME` sets `Hostname`
> (here, `zabbix-agent-basic` / `zabbix-agent2-docker`). In production you would
> set these in the `.conf` file on each machine.

The thing to carry away from the lab-versus-production note is that nothing
conceptual changes between the two. The parameters and their meanings are
identical; the container images simply translate friendly environment variables
into the same config lines you would otherwise write by hand.

### Passive vs active checks (mapped to the parameters)

Zabbix collects agent data in two directions, and the direction decides which
parameter is in charge:

- **Passive check:** the server connects **to the agent** on port 10050 and asks
  for a value. Governed by the agent's **`Server`** allow-list. (This is what
  `zabbix_get` does.)
- **Active check:** the agent connects **to the server** on port 10051, downloads
  its list of checks, and pushes values. Governed by **`ServerActive`**, and the
  agent identifies itself by **`Hostname`**.

The mental model that keeps this straight: in a passive check the server is the
caller and the agent must trust it (hence the `Server` allow-list); in an active
check the agent is the caller and must know both where to call (`ServerActive`) and
what name to announce itself under (`Hostname`). Reverse the direction and you
reverse which parameter matters.

This is not abstract. You can watch active checks come to life in the agent log,
which the next section covers. Before the matching host existed in Zabbix, agent 2
logged *"host … not found"* — it was knocking on the server's door and being told
nobody by that name was expected. Once we created the host with a name that exactly
matched the agent's `Hostname`, the log flipped to *"active checks on server are
active again."* The agent was finally recognized.

### Simple checks, and SSH/Telnet checks (agentless, conceptually)

It is tempting, after two modules of agents, to assume everything needs one. It
does not. **Simple checks** are basic network checks the **server performs
directly**, with no agent on the target at all — for example
`net.tcp.service[http,demo-nginx,80]` to test whether an HTTP service answers,
`net.tcp.port[…]` to test a raw port, or `icmpping` to test reachability. In the
same agentless spirit, the **SSH** and **Telnet** check item types let the server
log in to a target and run a command, again with nothing installed on the far end.

We lean on these agentless types later for the web, database, and SNMP demos. For
now the lesson is just a habit of mind: "agent vs agentless" is a *choice you make
per check*, not a fixed property of a whole host. A single Online Shop host might
report its CPU through an agent and its open ports through a simple check at the
same time.

### Agent logs

When an agent misbehaves, its log is the first place to look — before the
frontend, before guessing. In a normal install the log is a file on disk; in
Docker the agent writes to the container's stdout, so you read it with `docker
logs`:

```bash
docker logs zabbix-agent2-docker --tail 8
# ... active check configuration update from [zabbix-server:10051] is working again
# ... active checks on server are active again
```

Those two lines are the agent narrating its own active-check handshake: it reached
`zabbix-server` on port 10051, pulled its configuration, and is now allowed to send
data. Lines like these are reassuring when present and conspicuously missing when
something is wrong, which is exactly what makes the log such a fast diagnostic.

### Troubleshooting agent connectivity

Almost every agent problem you will meet is one of three things, and the good news
is that `zabbix_get` reports each of them with a distinctive, recognizable error.
Learn to read these and you can diagnose most agent failures in seconds:

- **Nothing listening / wrong port / agent down:**
  `cannot connect to [[zabbix-agent2-docker]:9999]: connection error (POLLERR,POLLHUP)`
- **Name doesn't resolve (wrong DNS/host):**
  `getaddrinfo() failed for 'does-not-exist'`
- **Connected but refused:** the agent's `Server` allow-list does not include the
  caller (you would see a refusal rather than data).

This is why `zabbix_get` is the single most useful tool in your agent-debugging kit:
it isolates *where* the problem lives. If `zabbix_get` returns a value, the agent
is healthy and reachable, so the fault is somewhere in Zabbix's own configuration —
a wrong host name, a missing template, an interface set up incorrectly. If
`zabbix_get` errors, the problem is on the network or the agent side, and the
specific error tells you which. That split — *value means look at Zabbix, error
means look at the network* — will save you hours over the rest of the course.

## Docker-Based Demonstration

Both agents are already running. The instructor contrasts them live: `agent.version`
on each, then the Docker plugin (`docker.ping`, `docker.info`) on agent 2 versus
`ZBX_NOTSUPPORTED` on the classic agent — proving the plugin advantage — and
finally `docker logs zabbix-agent2-docker` to show the active-check messages.

## Hands-On Lab

You already added the classic-agent host in Module 5; now add the agent 2 host and
compare them.

1. **Confirm both agents answer.** From a terminal:
   ```bash
   docker exec zabbix-server zabbix_get -s zabbix-agent-basic   -k agent.version
   docker exec zabbix-server zabbix_get -s zabbix-agent2-docker -k agent.version
   ```
   This is your baseline: before comparing what the agents *can* do differently,
   confirm both are alive and on the same version.
   **Expected:** both print `7.4.11`.

2. **See agent 2's Docker plugin (classic agent can't).**
   ```bash
   docker exec zabbix-server zabbix_get -s zabbix-agent2-docker -k docker.ping   # 1
   docker exec zabbix-server zabbix_get -s zabbix-agent-basic   -k docker.ping   # ZBX_NOTSUPPORTED
   ```
   The same key, asked of two agents, gives two different answers — this is the
   plugin advantage made concrete.
   **Expected:** agent 2 returns `1`; the classic agent reports the key
   unsupported.

3. **Add the agent 2 host.** In **Data collection → Hosts → Create host**, set:
   - **Host name:** `zabbix-agent2-docker`
   - **Host groups:** `Docker Lab`, `Linux Servers`
   - **Agent interface:** DNS `zabbix-agent2-docker`, **Connect to: DNS**, port
     `10050`
   - **Templates:** `Linux by Zabbix agent`

   Notice that the host name you type here must match the agent's `Hostname` exactly
   — that is what lets active checks find their home.

   ![The agent 2 host configuration form](assets/module-06/04-agent2-host-form.png)
   *The completed host form — identical layout to the classic-agent host from
   Module 5; only the name and DNS differ. Connect to is set to DNS.*

   Click **Add**.
   **Expected:** within a minute the host shows a green **ZBX** in the Hosts list,
   next to the classic-agent host.

   ![Both agent hosts, available (green ZBX)](assets/module-06/01-hosts-both.png)
   *`zabbix-agent-basic` (classic) and `zabbix-agent2-docker` (agent 2) side by
   side; the built-in *Zabbix server* host stays red (its agent points inside the
   server container).*

4. **Compare collected metrics.** Open **Monitoring → Latest data** and filter to
   `zabbix-agent2-docker`.
   The point of this step is to confirm the claim from the Topics section: for
   ordinary OS metrics, the two agents are interchangeable.
   **Expected:** the same families of Linux metrics you saw for the classic agent
   (CPU, memory, filesystems, network) — confirming both agents collect the same
   built-in keys.

   ![Latest data for the agent 2 host](assets/module-06/02-latest-agent2.png)

5. **Add an agent 2 plugin item.** On the `zabbix-agent2-docker` host, create an
   item:
   - **Name:** `Docker engine reachable (Agent 2 plugin)`
   - **Type:** `Zabbix agent`
   - **Key:** `docker.ping`
   - **Type of information:** `Numeric (unsigned)`
   - **Tags:** `component=docker`, `plugin=agent2`

   The item type is just a plain `Zabbix agent` item — there is no special "plugin"
   type — because from the server's point of view it is asking for a key like any
   other. The magic is that agent 2's Docker plugin knows how to answer it.

   ![The docker.ping item form](assets/module-06/05-docker-item-form.png)
   *Creating the `docker.ping` item — a plain Zabbix agent item, but the key is
   served by agent 2's built-in Docker plugin.*

   Use **Test → Get value and test** before saving.

   ![Test item returns 1 — the Docker engine is reachable](assets/module-06/06-docker-item-test.png)

   **Expected:** Test returns **`1`**; after saving, Latest data shows the item =
   `1`. This metric is impossible on the classic agent.

   ![The Docker-plugin item collecting in Latest data](assets/module-06/03-docker-item.png)

6. **Read the agent log.**
   ```bash
   docker logs zabbix-agent2-docker --tail 8
   ```
   Now that the host exists with a matching name, the log should show the agent
   happily talking to the server for active checks.
   **Expected:** lines about active-check configuration updates to
   `zabbix-server:10051` "working again" / "active again" — the agent talking to
   the server for active checks.

7. **Break it, then fix it (troubleshooting).** Simulate an agent outage and watch
   the diagnosis:
   ```bash
   docker stop zabbix-agent2-docker
   docker exec zabbix-server zabbix_get -s zabbix-agent2-docker -k agent.ping
   ```
   Stopping the container is the cleanest way to reproduce the most common real-world
   agent failure: the agent simply isn't there to answer.
   **Expected:** the value request fails with a connection error
   (`connection error (POLLERR,POLLHUP)`), and within a few minutes the host's
   **Availability** stops being green in the Hosts list (it goes unavailable).

   ![zabbix-agent2-docker availability is no longer green after the agent is stopped](assets/module-06/07-host-unavailable.png)
   *Compare the three hosts: `zabbix-agent-basic` is green (available),
   `zabbix-agent2-docker` has gone unavailable, and the built-in *Zabbix server*
   host is red as usual.*

   Now recover:
   ```bash
   docker start zabbix-agent2-docker
   docker exec zabbix-server zabbix_get -s zabbix-agent2-docker -k agent.ping   # 1
   ```
   **Expected:** `agent.ping` returns `1` again and availability returns to green.
   You just reproduced and fixed the most common agent problem: the agent wasn't
   reachable.

## Expected Outcome

You can now articulate when to reach for agent 2 over the classic agent and why,
explain `Server`, `ServerActive`, and `Hostname` and how passive and active checks
each depend on them, and you have a second monitored host — `zabbix-agent2-docker` —
collecting the full set of Linux metrics alongside a Docker-plugin item the classic
agent could never provide. Just as importantly, you can take a broken agent, read
the `zabbix_get` error and the agent log, and say with confidence whether the fault
lies in the network, the agent, or the Zabbix configuration.
